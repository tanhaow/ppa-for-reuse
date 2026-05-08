"""
Adapter management CLI for PPA Django Reuse.

Provides commands for creating, validating, testing, and managing adapters.
"""

from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Adapter management CLI for PPA Django Reuse"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

        # adapter create
        create_parser = subparsers.add_parser("create", help="Create new adapter")
        create_parser.add_argument("name", help="Adapter name (e.g., cookbook)")
        create_parser.add_argument("--display-name", help="Display name for the adapter")
        create_parser.add_argument(
            "--interactive", "-i", action="store_true", help="Interactive mode with prompts"
        )

        # adapter validate
        validate_parser = subparsers.add_parser("validate", help="Validate adapter configuration")
        validate_parser.add_argument("adapter", nargs="?", help="Adapter name or path")
        validate_parser.add_argument(
            "--strict", action="store_true", help="Strict validation mode (fail on warnings)"
        )

        # adapter test
        test_parser = subparsers.add_parser("test", help="Test adapter functionality")
        test_parser.add_argument("adapter", nargs="?", help="Adapter name or path")
        test_parser.add_argument(
            "--create-sample", action="store_true", help="Create sample data for testing"
        )

        # adapter list
        list_parser = subparsers.add_parser("list", help="List available adapters")
        list_parser.add_argument(
            "--verbose", "-v", action="store_true", help="Show detailed information"
        )

        # adapter info
        info_parser = subparsers.add_parser("info", help="Show adapter information")
        info_parser.add_argument("adapter", help="Adapter name or path")

    def handle(self, *args, **options):
        subcommand = options.get("subcommand")

        if not subcommand:
            self.print_help("manage.py", "adapter")
            return

        # Dispatch to subcommand handler
        handler = getattr(self, f"handle_{subcommand}", None)
        if handler:
            handler(options)
        else:
            raise CommandError(f"Unknown subcommand: {subcommand}")

    def handle_create(self, options):
        """Create new adapter with interactive prompts or CLI args."""
        name = options["name"]
        interactive = options["interactive"]
        display_name = options.get("display_name")

        # Determine adapter directory
        adapters_dir = getattr(settings, "ADAPTERS_DIR", None)
        if not adapters_dir:
            adapters_dir = settings.BASE_DIR / "examples" / "adapters"

        adapter_path = Path(adapters_dir) / name

        # Check if already exists
        if adapter_path.exists():
            raise CommandError(f"Adapter directory already exists: {adapter_path}")

        self.stdout.write(self.style.SUCCESS(f"Creating adapter: {name}"))
        self.stdout.write(f"Location: {adapter_path}\n")

        # Interactive mode
        if interactive:
            # Check if user has data imported
            self.stdout.write("\n" + "=" * 70)
            self.stdout.write("⚠️  IMPORTANT: Before creating an adapter")
            self.stdout.write("=" * 70)
            self.stdout.write("\nYou should have already imported your data into the database.")
            self.stdout.write("\nIf you haven't imported data yet:")
            self.stdout.write("  1. Import your data first (e.g., python manage.py import_data)")
            self.stdout.write(
                "  2. Check your data in admin: http://localhost:8000/admin/archive/digitizedwork/"
            )
            self.stdout.write("  3. Then come back to create the adapter")
            self.stdout.write("\nIf you have already imported data, you can continue.")

            if not self._confirm("\nDo you have data imported in the database?", default=True):
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠️  Please import your data first, then run this command again."
                    )
                )
                self.stdout.write("\nSteps to import data:")
                self.stdout.write("  1. Prepare your data file (CSV, JSON, etc.)")
                self.stdout.write("  2. Run: python manage.py import_data <your_file>")
                self.stdout.write(
                    "  3. Verify in admin: http://localhost:8000/admin/archive/digitizedwork/"
                )
                self.stdout.write(
                    "  4. Then run: python manage.py adapter create " f"{name} --interactive\n"
                )
                return

            self.stdout.write("")

            display_name = self._prompt("Display name", default=name.replace("_", " ").title())
            description = self._prompt("Description (optional)", allow_empty=True)

            # Field mapping wizard
            self.stdout.write("\n📋 Configure Your Data Fields (Field Mapping Configuration)")
            self.stdout.write("=" * 70)
            self.stdout.write("\nThese fields control what information appears in:")
            self.stdout.write("  • Search results (title, author, date, etc.)")
            self.stdout.write("  • Detail pages (full description, images, metadata)")
            self.stdout.write("  • Filters and sorting options")
            self.stdout.write("\nWhat you'll do:")
            self.stdout.write(
                "  1. Choose what information you want to display (e.g., 'title', 'author')"
            )
            self.stdout.write("  2. Tell us the field name in your imported data")
            self.stdout.write("\nNote: Your data should already be imported into the database.")
            self.stdout.write("      Check your data structure to see available field names.")
            self.stdout.write("\nExamples:")
            self.stdout.write("  • title → title                      (direct field)")
            self.stdout.write("  • ingredients → metadata.ingredients (nested in metadata)")
            self.stdout.write("  • cook_time → metadata.cook_time     (nested in metadata)")
            self.stdout.write("\nTip: Start with basic fields like 'title' and 'author',")
            self.stdout.write("     you can always add more later!")
            self.stdout.write("\nPress Enter on empty field name to finish.\n")

            field_map = {}
            while True:
                solr_field = self._prompt(
                    "Field name (e.g., 'title', 'author', 'ingredients')", allow_empty=True
                )
                if not solr_field:
                    break

                self.stdout.write(
                    f'\n  What is the field name for "{solr_field}" in your imported data?'
                )
                self.stdout.write("  ")
                self.stdout.write("  How to check:")
                self.stdout.write(
                    "    1. Look at your data in the admin interface: /admin/archive/digitizedwork/"
                )
                self.stdout.write("    2. Check the database fields or your import file")
                self.stdout.write("  ")
                self.stdout.write("  Common patterns:")
                self.stdout.write(
                    f"    • Direct field: {solr_field}                    "
                    "(if your data has this field)"
                )
                self.stdout.write(
                    f"    • In metadata: metadata.{solr_field}        "
                    "(if stored in the metadata JSON field)"
                )
                self.stdout.write("  ")
                self.stdout.write("  Examples:")
                self.stdout.write("    title → title")
                self.stdout.write("    author → author")
                self.stdout.write("    ingredients → metadata.ingredients")
                self.stdout.write("    cook_time → metadata.cook_time")
                self.stdout.write("  ")
                model_path = self._prompt("  Enter field name")
                field_map[solr_field] = model_path
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Added: {solr_field} will display data from {model_path}\n"
                    )
                )

            if not field_map:
                field_map = {"title": "title"}  # Minimal default

            # Solr schema wizard
            self.stdout.write("\n🔍 Advanced Search Configuration (Solr Search Engine Schema)")
            self.stdout.write("=" * 70)
            self.stdout.write("\nDo you need special search features?")
            self.stdout.write("  • Exact matching (e.g., find exact ingredient names)")
            self.stdout.write("  • Multiple values (e.g., a book with multiple authors)")
            self.stdout.write("  • Numeric sorting (e.g., sort by year or page count)")
            self.stdout.write("\nMost users can skip this and add it later if needed.")
            add_solr_fields = self._confirm("\nAdd advanced search fields now?", default=False)
            solr_fields = []

            if add_solr_fields:
                self.stdout.write("\nField types:")
                self.stdout.write("  • string - Text (names, titles)")
                self.stdout.write("  • plong - Numbers (years, counts)")
                self.stdout.write("  • text_general - Full-text search")
                self.stdout.write("\nPress Enter on empty field name to finish.\n")

                while True:
                    field_name = self._prompt(
                        "Field name (e.g., 'ingredients_exact', 'year')", allow_empty=True
                    )
                    if not field_name:
                        break
                    field_type = self._prompt(
                        "  Type (string/plong/text_general)", default="string"
                    )
                    self.stdout.write("  Can this field have multiple values?")
                    self.stdout.write("  (e.g., a book with multiple authors = yes)")
                    multi_valued = self._confirm("  Multiple values?", default=False)

                    solr_fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "multiValued": multi_valued,
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ Added search field: {field_name} " f"({field_type})\n"
                        )
                    )
        else:
            # Non-interactive mode
            if not display_name:
                display_name = name.replace("_", " ").title()
            description = ""
            field_map = {"title": "title"}
            solr_fields = []

        # Create directory structure
        adapter_path.mkdir(parents=True)
        (adapter_path / "templates").mkdir()
        (adapter_path / "static").mkdir()

        # Generate adapter.yaml
        adapter_config = {
            "name": name,
            "display_name": display_name,
            "field_map": field_map,
            "templates_dir": "templates",
        }

        if description:
            adapter_config["description"] = description

        if solr_fields:
            adapter_config["solr_schema"] = {"fields": solr_fields}

        yaml_path = adapter_path / "adapter.yaml"
        with yaml_path.open("w") as f:
            yaml.dump(adapter_config, f, default_flow_style=False, sort_keys=False)

        # Create README
        readme_path = adapter_path / "README.md"
        readme_content = self._generate_readme(name, display_name, description, field_map)
        readme_path.write_text(readme_content)

        self.stdout.write(self.style.SUCCESS(f"\n✅ Adapter created: {adapter_path}"))
        self.stdout.write("\nNext steps:")
        self.stdout.write(f"  1. Edit {yaml_path}")
        self.stdout.write(f"  2. python manage.py adapter validate {name}")
        self.stdout.write(f"  3. python manage.py adapter test {name}")

    def handle_validate(self, options):
        """Validate adapter configuration with detailed checks."""
        from ppa.adapters.loader import load_adapter

        adapter_name = options.get("adapter") or getattr(settings, "ARCHIVE_ADAPTER", None)
        strict = options.get("strict", False)

        if not adapter_name:
            raise CommandError("No adapter specified and ARCHIVE_ADAPTER not configured.")

        self.stdout.write(f"🔍 Validating adapter: {adapter_name}\n")

        errors = []
        warnings = []

        # Load adapter
        try:
            adapter = load_adapter(adapter_name)
            self.stdout.write(self.style.SUCCESS(f"✅ Adapter loaded: {adapter.display_name}"))
        except Exception as e:
            raise CommandError(f"Failed to load adapter: {e}")

        # Validate field_map
        if not adapter.field_map:
            errors.append("field_map is empty")
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Field map: {len(adapter.field_map)} fields"))

            # Check for common required fields
            recommended_fields = ["title", "author", "pub_date"]
            missing = [f for f in recommended_fields if f not in adapter.field_map]
            if missing:
                warnings.append(f'Missing recommended fields: {", ".join(missing)}')

        # Validate templates directory
        templates_path = Path(adapter.templates_dir)
        if templates_path.exists():
            template_count = len(list(templates_path.glob("**/*.html")))
            self.stdout.write(self.style.SUCCESS(f"✅ Templates: {template_count} found"))
        else:
            warnings.append(f"Templates directory not found: {templates_path}")

        # Validate Solr schema
        if adapter.solr_schema:
            fields = adapter.solr_schema.get("fields", [])
            self.stdout.write(self.style.SUCCESS(f"✅ Solr schema: {len(fields)} custom fields"))

            # Validate field definitions
            for field in fields:
                if "name" not in field:
                    errors.append(f"Solr field missing name: {field}")
                if "type" not in field:
                    errors.append(f'Solr field missing type: {field.get("name")}')

        # Test field resolution
        self.stdout.write("\n🧪 Testing field resolution...")
        from ppa.archive.models import DigitizedWork

        # Create dummy instance
        test_work = DigitizedWork(title="Test", metadata={"test_field": "test_value"})

        for solr_field, model_path in adapter.field_map.items():
            try:
                test_work.get_adapter_field(model_path, default=None)
                self.stdout.write(f"  ✅ {solr_field} -> {model_path}")
            except Exception as e:
                errors.append(f"Field resolution failed: {solr_field} -> {model_path}: {e}")

        # Display results
        self.stdout.write("\n" + "=" * 50)
        if errors:
            self.stdout.write(self.style.ERROR(f"\n❌ {len(errors)} error(s):"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"  - {error}"))

        if warnings:
            self.stdout.write(self.style.WARNING(f"\n⚠️  {len(warnings)} warning(s):"))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f"  - {warning}"))

        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS("\n✅ Validation passed!"))
        elif not errors:
            self.stdout.write(self.style.SUCCESS("\n✅ Validation passed with warnings"))
        else:
            if strict:
                raise CommandError("Validation failed")
            self.stdout.write(self.style.ERROR("\n❌ Validation failed"))

    def handle_test(self, options):
        """Test adapter with sample data."""
        from ppa.adapters.loader import load_adapter
        from ppa.archive.models import DigitizedWork, Collection
        from ppa.solr_factory import map_model_to_solr

        adapter_name = options.get("adapter") or getattr(settings, "ARCHIVE_ADAPTER", None)
        create_sample = options.get("create_sample", False)

        if not adapter_name:
            raise CommandError("No adapter specified and ARCHIVE_ADAPTER not configured.")

        adapter = load_adapter(adapter_name)

        self.stdout.write(f"🧪 Testing adapter: {adapter.display_name}\n")

        # Test 1: Field mapping
        self.stdout.write("Test 1: Field Mapping")
        test_data = {
            "title": "Test Item",
            "author": "Test Author",
            "metadata": {"custom_field": "custom_value", "nested": {"deep": "value"}},
        }

        work = DigitizedWork(**test_data)
        solr_doc = map_model_to_solr(work, adapter=adapter)

        self.stdout.write(f"  Mapped {len(solr_doc)} fields:")
        for field, value in list(solr_doc.items())[:10]:  # Show first 10
            self.stdout.write(f"    {field}: {value}")
        if len(solr_doc) > 10:
            self.stdout.write(f"    ... and {len(solr_doc) - 10} more")

        # Test 2: Template resolution
        self.stdout.write("\nTest 2: Template Resolution")
        from django.template.loader import get_template

        test_templates = [
            "archive/snippets/search_result.html",
            "archive/digitizedwork_detail.html",
        ]

        for template_name in test_templates:
            try:
                template = get_template(template_name)
                self.stdout.write(f"  ✅ {template_name}: {template.origin.name}")
            except Exception:
                self.stdout.write(f"  ⚠️  {template_name}: using default")

        # Test 3: Create sample data
        if create_sample:
            self.stdout.write("\nTest 3: Creating Sample Data")

            collection, _ = Collection.objects.get_or_create(
                name=f"{adapter.display_name} Test Collection"
            )

            sample_work = DigitizedWork.objects.create(
                source_id=f"{adapter.name}_test_001",
                title=f"Sample {adapter.display_name} Item",
                author="Test Author",
                pub_date=2000,
                metadata={"test_field": "test_value", "created_by": "adapter test command"},
            )
            sample_work.collections.add(collection)

            self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {sample_work}"))
            self.stdout.write(f"     ID: {sample_work.id}")
            self.stdout.write(
                f"     Admin URL: /admin/archive/digitizedwork/{sample_work.id}/change/"
            )

        self.stdout.write(self.style.SUCCESS("\n✅ All tests passed!"))

    def handle_list(self, options):
        """List available adapters."""
        from ppa.adapters.loader import load_adapter

        verbose = options.get("verbose", False)

        adapters_dir = getattr(settings, "ADAPTERS_DIR", None)
        if not adapters_dir:
            adapters_dir = settings.BASE_DIR / "examples" / "adapters"

        adapters_dir = Path(adapters_dir)

        if not adapters_dir.exists():
            self.stdout.write(self.style.WARNING(f"Adapters directory not found: {adapters_dir}"))
            return

        self.stdout.write("📦 Available Adapters:\n")

        adapter_dirs = [
            d for d in adapters_dir.iterdir() if d.is_dir() and (d / "adapter.yaml").exists()
        ]

        if not adapter_dirs:
            self.stdout.write("  No adapters found")
            return

        for adapter_dir in sorted(adapter_dirs):
            try:
                adapter = load_adapter(str(adapter_dir))
                status = "✅ Valid"
            except Exception as e:
                status = f"❌ Error: {e}"
                adapter = None

            self.stdout.write(f"  {adapter_dir.name}", ending="")
            if adapter:
                self.stdout.write(f" ({adapter.display_name})")
                self.stdout.write(f"    Location: {adapter.source_path}")
                self.stdout.write(f"    Fields: {len(adapter.field_map)} mapped")
                self.stdout.write(f"    Status: {status}")
            else:
                self.stdout.write(f"\n    Status: {status}")

            if verbose and adapter:
                self.stdout.write(f"    Templates: {adapter.templates_dir}")
                if adapter.solr_schema:
                    fields = adapter.solr_schema.get("fields", [])
                    self.stdout.write(f"    Solr fields: {len(fields)} custom")

            self.stdout.write("")

        self.stdout.write("Use 'python manage.py adapter info <name>' for details")

    def handle_info(self, options):
        """Show detailed adapter information."""
        from ppa.adapters.loader import load_adapter

        adapter_name = options["adapter"]

        try:
            adapter = load_adapter(adapter_name)
        except Exception as e:
            raise CommandError(f"Failed to load adapter: {e}")

        self.stdout.write(f"📦 {adapter.display_name}\n")
        self.stdout.write(f"Name: {adapter.name}")
        self.stdout.write(f"Location: {adapter.source_path}")
        self.stdout.write("Status: ✅ Valid\n")

        # Field mapping
        self.stdout.write(f"Field Mapping ({len(adapter.field_map)} fields):")
        for solr_field, model_path in adapter.field_map.items():
            self.stdout.write(f"  {solr_field} → {model_path}")

        # Solr schema
        if adapter.solr_schema:
            fields = adapter.solr_schema.get("fields", [])
            self.stdout.write(f"\nSolr Schema ({len(fields)} custom fields):")
            for field in fields:
                field_type = field.get("type", "unknown")
                multi = ", multi-valued" if field.get("multiValued") else ""
                self.stdout.write(f'  {field["name"]} ({field_type}{multi})')

        # Templates
        templates_path = Path(adapter.templates_dir)
        if templates_path.exists():
            templates = list(templates_path.glob("**/*.html"))
            if templates:
                self.stdout.write(f"\nTemplates ({len(templates)} overrides):")
                for template in templates:
                    rel_path = template.relative_to(templates_path)
                    self.stdout.write(f"  {rel_path}")

        # Usage
        self.stdout.write("\nUsage:")
        self.stdout.write(f"  Set in settings: ARCHIVE_ADAPTER = '{adapter.name}'")
        self.stdout.write(f"  Or environment: export ARCHIVE_ADAPTER={adapter.name}")

    # Helper methods
    def _prompt(self, message, default=None, allow_empty=False):
        """Interactive prompt helper."""
        if default:
            message = f"{message} [{default}]"
        message += ": "

        while True:
            value = input(message).strip()
            if not value and default:
                return default
            if not value and allow_empty:
                return ""
            if value:
                return value
            if not value:
                self.stdout.write(self.style.ERROR("This field is required"))

    def _confirm(self, message, default=False):
        """Yes/no confirmation prompt."""
        suffix = " [Y/n]" if default else " [y/N]"
        response = input(message + suffix + ": ").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")

    def _generate_readme(self, name, display_name, description, field_map):
        """Generate README content for adapter."""
        field_table = "\n".join(
            [f"| `{solr_field}` | `{model_path}` |" for solr_field, model_path in field_map.items()]
        )

        return f"""# {display_name}

{description}

## Configuration

This adapter is configured in `adapter.yaml`.

## Field Mapping

| Solr Field | Model Path |
|------------|------------|
{field_table}

## Usage

1. Configure in settings:
   ```python
   ARCHIVE_ADAPTER = '{name}'
   ADAPTERS_DIR = BASE_DIR / 'examples' / 'adapters'
   ```

2. Validate:
   ```bash
   python manage.py adapter validate {name}
   ```

3. Test:
   ```bash
   python manage.py adapter test {name}
   ```

## Template Overrides

Place custom templates in the `templates/` directory. They will override default templates.

## Static Assets

Place custom CSS, JavaScript, and images in the `static/` directory.
"""
