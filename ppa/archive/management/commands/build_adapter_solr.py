from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ppa.adapters.loader import load_adapter


class Command(BaseCommand):
    help = "Emit adapter Solr schema fragment or inferred field list from field_map."

    def add_arguments(self, parser):
        parser.add_argument("adapter", nargs="?", help="Adapter name or path to inspect")

    def handle(self, *args, **options):
        adapter_name = options.get("adapter") or getattr(settings, "ARCHIVE_ADAPTER", None)
        if not adapter_name:
            raise CommandError("No adapter specified and ARCHIVE_ADAPTER not configured.")
        adapter = load_adapter(adapter_name)
        if adapter.solr_schema:
            # Print full solr schema fragment
            import json

            self.stdout.write(json.dumps(adapter.solr_schema, indent=2))
            return
        # Otherwise infer fields from field_map
        fields = []
        for solr_field in adapter.field_map.keys():
            fields.append({"name": solr_field, "type": "string"})
        import json

        self.stdout.write(json.dumps({"fields": fields}, indent=2))
