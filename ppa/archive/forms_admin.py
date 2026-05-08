"""Custom forms for Django Admin."""

from django import forms
from ppa.archive.models import Collection
from ppa.archive.widgets import AdapterFieldSelectorWidget


class CollectionAdminForm(forms.ModelForm):
    """Custom form for Collection admin with visual field selector."""

    class Meta:
        model = Collection
        fields = "__all__"
        widgets = {
            "list_view_fields": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 80,
                    "placeholder": '[\n  {"field": "cookbook_cook_time", "label": "Cook Time"},\n  {"field": "cookbook_ingredients", "label": "Ingredients"}\n]',
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields["list_view_fields"].help_text = (
            "Configure which fields to display in the list view. "
            "Leave empty to use adapter defaults. "
            'Format: JSON array of objects with "field" and "label" properties.'
        )

        # If adapter is set, use visual selector
        if self.instance and self.instance.adapter_name:
            self.fields["list_view_fields"].widget = AdapterFieldSelectorWidget(
                adapter_name=self.instance.adapter_name
            )
