from django.core.management.base import BaseCommand, CommandError

from ppa.adapters.loader import load_adapter


class Command(BaseCommand):
    help = "Validate the specified adapter directory (adapter name or path)."

    def add_arguments(self, parser):
        parser.add_argument("adapter", nargs="?", help="Adapter name or path to validate")

    def handle(self, *args, **options):
        adapter = options.get("adapter")
        if not adapter:
            from django.conf import settings

            adapter = getattr(settings, "ARCHIVE_ADAPTER", None)
            if not adapter:
                raise CommandError("No adapter specified and ARCHIVE_ADAPTER not configured.")
        try:
            load_adapter(adapter)
        except Exception as err:
            raise CommandError(f"Adapter validation failed: {err}")
        self.stdout.write(self.style.SUCCESS(f"Adapter '{adapter}' validated successfully."))
