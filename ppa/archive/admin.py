from django.urls import re_path
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export import fields, resources
from import_export.admin import ExportActionMixin, ExportMixin
from ppa.solr_factory import SolrClient

from ppa.archive.models import (
    Cluster,
    Collection,
    DigitizedWork,
    ProtectedWorkFieldFlags,
)
from ppa.archive.views import ImportView
from ppa.archive.templatetags.ppa_tags import hathi_page_url, gale_page_url


# import/export resource
class DigitizedWorkResource(resources.ModelResource):
    # declare export fields to customize output
    # - get display value for choice fields
    item_type = fields.Field(
        attribute="get_item_type_display",
    )
    source = fields.Field(
        attribute="get_source_display",
    )
    status = fields.Field(
        attribute="get_status_display",
    )
    # output alpha cluster id instead of numeric database id
    cluster = fields.Field(attribute="cluster", column_name="cluster_id")

    class Meta:
        model = DigitizedWork
        exclude = ("protected_fields",)
        export_order = (
            "id",
            "source_id",
            "record_id",
            "title",
            "subtitle",
            "sort_title",
            "author",
            "item_type",  # display
            "book_journal",
            "pub_date",
            "pub_place",
            "publisher",
            "enumcron",
            "collections",  # multiple, names
            "cluster",
            "public_notes",
            "notes",
            "pages_orig",
            "pages_digital",
            "page_count",
            "status",
            "source",
            "added",
            "updated",
        )
        widgets = {
            # customize many-to-many output for collections
            "collections": {"separator": "; ", "field": "name"},
        }

    def get_queryset(self):
        # prefetch related object to make download more efficient
        return super().get_queryset().prefetch_related("collections", "cluster")


class DigitizedWorkAdmin(ExportActionMixin, ExportMixin, admin.ModelAdmin):
    resource_class = DigitizedWorkResource  # resource for export

    # enable "save as new" button to copy and create a new record
    save_as = True

    list_display = (
        "display_title",
        "subtitle",
        "source_link",
        "record_id",
        "cluster",
        "author",
        "item_type",
        "list_collections",
        "enumcron",
        "pub_place",
        "publisher",
        "pub_date",
        "is_public",
        "added",
        "updated",
    )
    fields = (
        ("source", "source_id"),
        "source_url",
        "item_type",
        "title",
        "subtitle",
        "sort_title",
        "enumcron",
        "author",
        "book_journal",
        ("pages_orig", "pages_digital"),
        "pub_place",
        "publisher",
        "pub_date",
        "page_count",
        "public_notes",
        "notes",
        "record_id",
        "collections",
        "cluster",
        "metadata_display",
        "protected_fields",
        "status",
        "added",
        "updated",
    )
    # fields that are always read only
    readonly_fields = ("added", "updated", "protected_fields", "metadata_display")
    # fields that are read only for HathiTrust records
    hathi_readonly_fields = (
        "source",
        "source_id",
        "source_url",
        "page_count",
        "record_id",
    )

    search_fields = (
        "source_id",
        "title",
        "subtitle",
        "author",
        "enumcron",
        "pub_date",
        "publisher",
        "public_notes",
        "notes",
        "record_id",
        "cluster__cluster_id",
    )
    filter_horizontal = ("collections",)
    autocomplete_fields = ["cluster"]
    # date_hierarchy = 'added'  # is this useful?
    list_filter = ["collections", "status", "source", "item_type", "cluster"]
    actions = ["add_works_to_collection", "suppress_works"]

    def get_readonly_fields(self, request, obj=None):
        """
        Determine read only fields based on item source, to prevent
        editing of HathiTrust fields that should not be changed.
        """
        if obj and obj.source == DigitizedWork.HATHI:
            return self.hathi_readonly_fields + self.readonly_fields

        if request.POST.get("_saveasnew"):
            # protected fields must not be read-only in order
            # to preserve/copy when saving as new
            return ("added", "updated")

        return self.readonly_fields

    def list_collections(self, obj):
        """Return a list of :class:ppa.archive.models.Collection object names
        as a comma separated list to populate a change_list column.
        """
        return ", ".join([coll.name for coll in obj.collections.all().order_by("name")])

    list_collections.short_description = "Collections"

    def source_link(self, obj):
        """source id as an html link to source record, when source url is available"""
        if not obj.source_url:
            return obj.source_id

        source_url = obj.source_url
        # hathi/gale excerpt links should include first page
        if obj.pages_digital:
            if obj.source == DigitizedWork.HATHI:
                # hathi page url method requires source id
                source_url = hathi_page_url(obj.source_id, obj.first_page_digital)
            if obj.source == DigitizedWork.GALE:
                # gale page url method requires source url
                source_url = gale_page_url(obj.source_url, obj.first_page_digital)
        return mark_safe('<a href="%s" target="_blank">%s</a>' % (source_url, obj.source_id))

    source_link.short_description = "Source id"
    source_link.admin_order_field = "source_id"

    def metadata_display(self, obj):
        """Display metadata JSON in a readable format"""
        if not obj.metadata:
            return "No metadata"

        import json
        from django.utils.html import escape

        # Format JSON with indentation for readability
        formatted_json = json.dumps(obj.metadata, indent=2, ensure_ascii=False)

        # Wrap in <pre> tag for proper formatting and escape HTML
        style = "background-color: #f5f5f5; padding: 10px; " "border-radius: 4px; overflow-x: auto;"
        return mark_safe(f'<pre style="{style}">{escape(formatted_json)}</pre>')

    metadata_display.short_description = "Metadata (JSON)"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # customize behavior when copying a record and saving as new
        if request.POST.get("_saveasnew"):
            # if source is unset, this means we are loading the "save as new"
            # form for a hathitrust record
            if not request.POST.get("source"):
                # customize save as new field contents
                instance = DigitizedWork.objects.get(pk=object_id)
                # make a copy of the querydict so we can update it
                post_params = request.POST.copy()
                # read-only fields should be preserved
                post_params["source"] = instance.source
                post_params["source_id"] = instance.source_id
                post_params["source_url"] = instance.source_url
                post_params["record_id"] = instance.record_id
                # copy protected wield flags in simple string format
                post_params["protected_fields"] = instance.protected_fields.to_simple_str()

                # clear out fields that should be changed when excerpting
                clear_fields = [
                    "title",
                    "sort_title",
                    "author",
                    "pages_orig",
                    "pages_digital",
                    # "page_count",  # read-only, does not automatically propagate
                    "notes",
                    "public_notes",
                    "collections",
                    "cluster",
                ]
                for field in clear_fields:
                    try:
                        del post_params[field]
                    except KeyError:
                        pass

                # update request with our modified post parameters
                request.POST = post_params

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def save_model(self, request, obj, form, change):
        """Note any fields in the protected list that have been changed in
        the admin and preserve in database."""

        # If new object, created from scratch, nothing to track and preserve
        # or if item is not a HathiTrust item, save and return
        if not change or obj.source != DigitizedWork.HATHI:
            super().save_model(request, obj, form, change)
            return
        # has_changes only works for objects that have been changed on their
        # instance -- obj is a new instance *not* a modified one,
        # so compare against database
        db_obj = DigitizedWork.objects.get(pk=obj.pk)
        changed_fields = obj.compare_protected_fields(db_obj)
        # iterate over changed fields and 'append' (OR) to flags
        for field in changed_fields:
            obj.protected_fields = obj.protected_fields | ProtectedWorkFieldFlags(field)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Ensure reindex is called when admin form is saved"""
        # m2m relations are handled separately by the admin form so the standard
        # save override will not help as the m2m relationship are not yet set when
        # model's save method is called. See the doc string for save_related at:
        # https://docs.djangoproject.com/en/1.11/_modules/django/contrib/admin/
        # options/#ModelAdmin.save_related

        super(DigitizedWorkAdmin, self).save_related(request, form, formsets, change)
        digwork = DigitizedWork.objects.get(id=form.instance.pk)
        digwork.index()

    def add_works_to_collection(self, request, queryset):
        """
        Bulk add a queryset of :class:`ppa.archive.DigitizedWork` to
        a :class:`ppa.archive.Collection`.
        """
        # Uses POST from admin rather than a database query to get the pks
        # per the suggested practices in Django documentation
        selected = list(queryset.order_by("id").values_list("id", flat=True))
        # encode the filter querystring so that the bulk add view can return
        # the user to the same admin list view upon completion.
        request.session["collection-add-filters"] = request.GET
        request.session["collection-add-ids"] = selected
        return HttpResponseRedirect(reverse("archive:add-to-collection"))

    add_works_to_collection.short_description = "Add selected digitized works to collections"
    add_works_to_collection.allowed_permissions = ("change",)

    def suppress_works(self, request, queryset):
        """Set status to suppressed for every item in the queryset
        that is not already suppressed."""
        non_suppressed = queryset.exclude(status=DigitizedWork.SUPPRESSED)
        # save the list of ids being suppressed to update the index after
        ids_to_suppress = list(non_suppressed.values_list("source_id", flat=True))
        # change status in the database
        updated = non_suppressed.update(status=DigitizedWork.SUPPRESSED)
        # queryset.update does not trigger save signals;
        # clear suppressed page + work content from the index
        # delete all pages and works associated with any of these source ids
        if ids_to_suppress:
            solr = SolrClient()
            solr.update.delete_by_query(
                "source_id:(%s)" % " OR ".join(['"%s"' % val for val in ids_to_suppress])
            )
        # report on what was done, including any skipped
        skipped = ""
        qs_total = queryset.count()
        if qs_total != updated:
            skipped = " Skipped %d (already suppressed)." % (qs_total - updated)
        self.message_user(
            request,
            "Suppressed %d digitized work%s.%s" % (updated, "" if updated == 1 else "s", skipped),
        )

    suppress_works.short_description = "Suppress selected digitized works"

    def get_urls(self):
        """Add url for import admin form"""
        urls = super(DigitizedWorkAdmin, self).get_urls()
        my_urls = [
            re_path(
                r"^import/$",
                self.admin_site.admin_view(ImportView.as_view()),
                name="import",
            ),
        ]
        return my_urls + urls


class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "adapter_name", "field_count", "exclude")
    list_editable = ("exclude",)
    list_filter = ("adapter_name", "exclude")
    search_fields = ("name",)
    actions = ["bulk_set_adapter", "bulk_copy_fields", "preview_fields"]

    fieldsets = (
        (None, {"fields": ("name", "exclude")}),
        (
            "Adapter Configuration",
            {
                "fields": ("adapter_name", "list_view_fields"),
                "description": """
                <p><strong>Adapter Name:</strong> The adapter to use for this collection (e.g., "cookbook", "scifi").</p>
                <p><strong>List View Fields:</strong> Custom fields to display in the archive list view.
                Leave empty to use adapter defaults.</p>
            """,
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Use custom form with visual field selector."""
        from ppa.archive.forms_admin import CollectionAdminForm

        kwargs["form"] = CollectionAdminForm
        return super().get_form(request, obj, **kwargs)

    @admin.display(description="Fields")
    def field_count(self, obj):
        """Display number of configured fields."""
        if obj.list_view_fields:
            return f"{len(obj.list_view_fields)} custom"
        elif obj.adapter_name:
            from ppa.adapters.loader import get_adapter

            adapter = get_adapter(obj.adapter_name)
            if adapter and adapter.display_fields and "list_view" in adapter.display_fields:
                return f"{len(adapter.display_fields['list_view'])} default"
        return "—"

    @admin.action(description="Set adapter for selected collections")
    def bulk_set_adapter(self, request, queryset):
        """Bulk action to set adapter for multiple collections."""
        from django.shortcuts import render
        from django import forms

        class BulkAdapterForm(forms.Form):
            adapter_name = forms.ChoiceField(
                choices=[
                    ("", "-- Select Adapter --"),
                    ("cookbook", "Cookbook"),
                    ("scifi", "Science Fiction"),
                    ("feeding_america", "Feeding America"),
                ],
                required=True,
            )

        if "apply" in request.POST:
            form = BulkAdapterForm(request.POST)
            if form.is_valid():
                adapter_name = form.cleaned_data["adapter_name"]
                count = queryset.update(adapter_name=adapter_name)
                self.message_user(
                    request, f"Successfully set adapter '{adapter_name}' for {count} collection(s)."
                )
                return

        form = BulkAdapterForm()
        return render(
            request,
            "admin/collection_bulk_adapter.html",
            {"form": form, "collections": queryset, "title": "Set Adapter for Collections"},
        )

    @admin.action(description="Copy field configuration to selected collections")
    def bulk_copy_fields(self, request, queryset):
        """Bulk action to copy field configuration from one collection to others."""
        from django.shortcuts import render
        from django import forms

        class BulkCopyFieldsForm(forms.Form):
            source_collection = forms.ModelChoiceField(
                queryset=Collection.objects.exclude(list_view_fields__isnull=True),
                required=True,
                label="Copy from",
            )

        if "apply" in request.POST:
            form = BulkCopyFieldsForm(request.POST)
            if form.is_valid():
                source = form.cleaned_data["source_collection"]
                count = 0
                for collection in queryset:
                    collection.list_view_fields = source.list_view_fields
                    collection.save()
                    count += 1

                self.message_user(
                    request, f"Successfully copied field configuration to {count} collection(s)."
                )
                return

        form = BulkCopyFieldsForm()
        return render(
            request,
            "admin/collection_bulk_copy_fields.html",
            {"form": form, "collections": queryset, "title": "Copy Field Configuration"},
        )

    @admin.action(description="Preview field configuration")
    def preview_fields(self, request, queryset):
        """Preview how fields will be displayed."""
        from django.shortcuts import render

        collections_data = []
        for collection in queryset:
            from ppa.adapters.loader import get_adapter

            adapter = None
            fields = None

            if collection.adapter_name:
                adapter = get_adapter(collection.adapter_name)

                if collection.list_view_fields:
                    fields = collection.list_view_fields
                elif adapter and adapter.display_fields:
                    fields = adapter.display_fields.get("list_view", [])

            collections_data.append(
                {"collection": collection, "adapter": adapter, "fields": fields}
            )

        return render(
            request,
            "admin/collection_preview_fields.html",
            {"collections_data": collections_data, "title": "Preview Field Configuration"},
        )


class DigitizedWorkInline(admin.TabularInline):
    model = DigitizedWork
    fields = ("source", "source_id", "title", "subtitle", "author")
    extra = 0


class ClusterAdmin(admin.ModelAdmin):
    list_display = ("cluster_id", "works")
    digwork_admin_url = "admin:archive_digitizedwork_changelist"
    inlines = [
        DigitizedWorkInline,
    ]
    search_fields = ("cluster_id",)

    def get_queryset(self, request):
        # The annotations we use for document count on the list view
        # make the search too slow for autocomplete.
        # Reset to original, unannotated queryset *only* for autocomplete
        qs = super().get_queryset(request)
        if request and request.path == "/admin/autocomplete/":
            # return without annotations
            return qs
        # otherwise, annotate with counts
        return qs.annotate(Count("digitizedwork"))

    @admin.display(
        ordering="digitizedwork__count",
        description="# works in this cluster",
    )
    def works(self, obj):
        """Custom property to display number of works in a cluster and link
        to a filtered view of the digitized works list."""
        return format_html(
            '<a href="{0}?cluster__id__exact={1!s}">{2}</a>',
            reverse(self.digwork_admin_url),
            str(obj.id),
            obj.digitizedwork__count,
        )


admin.site.register(DigitizedWork, DigitizedWorkAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Cluster, ClusterAdmin)
