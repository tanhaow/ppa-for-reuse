from django.contrib.admin.apps import AdminConfig


class LocalAdminConfig(AdminConfig):
    default_site = "ppa.admin.LocalAdminSite"

    def ready(self):
        super().ready()
        # Unregister Waffle Flag and Sample models to keep admin interface clean
        # We only use Switches for simple on/off feature toggles
        try:
            from django.contrib import admin
            from waffle.models import Flag, Sample

            admin.site.unregister(Flag)
            admin.site.unregister(Sample)
        except Exception:
            # Models might not be registered yet or waffle might not be installed
            pass
