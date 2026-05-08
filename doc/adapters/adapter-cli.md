# Adapter CLI Reference

The adapter CLI provides commands for creating, validating, testing, and managing adapters in PPA Django Reuse.

## Overview

The adapter CLI is implemented as a Django management command with multiple subcommands:

```bash
python manage.py adapter <subcommand> [options]
```

## Available Commands

### `adapter create`

Create a new adapter with interactive prompts or command-line arguments.

#### Usage

```bash
# Interactive mode (recommended for first-time users)
python manage.py adapter create my_collection --interactive

# Non-interactive mode with defaults
python manage.py adapter create my_collection

# With display name
python manage.py adapter create my_collection --display-name "My Collection"
```

#### Options

- `name` (required): Adapter name (e.g., `cookbook`, `newspaper`)
- `--display-name`: Human-readable display name
- `--interactive`, `-i`: Enable interactive mode with prompts

#### Interactive Mode

When using `--interactive`, you'll be prompted for:

1. **Display name**: Human-readable name for the adapter
2. **Description**: Optional description of the collection
3. **Field mapping**: Map Solr fields to model paths
4. **Solr schema**: Define custom Solr fields

#### Example Interactive Session

```
$ python manage.py adapter create cookbook --interactive

Creating adapter: cookbook
Location: /path/to/examples/adapters/cookbook

Display name [Cookbook]: Historical Cookbook Adapter
Description (optional): Adapter for historical cookbook archives

📋 Configure Your Data Fields
============================================================
These fields control what information appears in:
  • Search results (title, author, date, etc.)
  • Detail pages (full description, images, metadata)
  • Filters and sorting options

How it works:
  1. Choose a field name (e.g., 'title', 'author', 'date')
  2. Tell us where to find this data in your records

Examples:
  • Basic field:    title → title
  • Custom data:    ingredients → metadata.ingredients
  • Nested data:    cook_time → metadata.recipe.time

Tip: Start with basic fields like 'title' and 'author',
     you can always add more later!

Press Enter on empty field name to finish.

Field name (e.g., 'title', 'author', 'date'): title
  Where is "title" stored in your data?
  (e.g., "title" for basic field, "metadata.title" for custom data)
  Data location: title
  ✅ Added: title will show data from title

Field name (e.g., 'title', 'author', 'date'): ingredients
  Where is "ingredients" stored in your data?
  (e.g., "title" for basic field, "metadata.ingredients" for custom data)
  Data location: metadata.ingredients
  ✅ Added: ingredients will show data from metadata.ingredients

Field name (e.g., 'title', 'author', 'date'): cook_time
  Where is "cook_time" stored in your data?
  (e.g., "title" for basic field, "metadata.cook_time" for custom data)
  Data location: metadata.cook_time
  ✅ Added: cook_time will show data from metadata.cook_time

Field name (e.g., 'title', 'author', 'date'): [Enter to finish]

🔍 Advanced Search Configuration (Optional)
============================================================
Do you need special search features?
  • Exact matching (e.g., find exact ingredient names)
  • Multiple values (e.g., a book with multiple authors)
  • Numeric sorting (e.g., sort by year or page count)

Most users can skip this and add it later if needed.

Add advanced search fields now? [y/N]: y

Field types:
  • string - Text (names, titles)
  • plong - Numbers (years, counts)
  • text_general - Full-text search

Press Enter on empty field name to finish.

Field name (e.g., 'ingredients_exact', 'year'): ingredients_exact
  Type (string/plong/text_general) [string]: string
  Can this field have multiple values?
  (e.g., a book with multiple authors = yes)
  Multiple values? [y/N]: y
  ✅ Added search field: ingredients_exact (string)

Field name (e.g., 'ingredients_exact', 'year'): [Enter to finish]

✅ Adapter created: /path/to/examples/adapters/cookbook

Next steps:
  1. Edit adapter.yaml
  2. python manage.py adapter validate cookbook
  3. python manage.py adapter test cookbook
```

#### Generated Files

The `create` command generates:

- `adapter.yaml` - Configuration file with field_map and solr_schema
- `README.md` - Documentation with usage instructions
- `templates/` - Directory for template overrides
- `static/` - Directory for static assets

### `adapter validate`

Validate adapter configuration with detailed checks.

#### Usage

```bash
# Validate configured adapter (from settings)
python manage.py adapter validate

# Validate specific adapter
python manage.py adapter validate cookbook

# Strict mode (fail on warnings)
python manage.py adapter validate cookbook --strict
```

#### Options

- `adapter` (optional): Adapter name or path (defaults to `ARCHIVE_ADAPTER` setting)
- `--strict`: Fail on warnings, not just errors

#### Validation Checks

1. **YAML syntax and structure**: Ensures adapter.yaml is valid
2. **Required fields**: Checks for `name` and `field_map`
3. **Field mapping**: Tests field paths with dummy model instance
4. **Templates directory**: Verifies templates directory exists
5. **Solr schema**: Validates field definitions
6. **Recommended fields**: Warns if common fields are missing

#### Example Output

```
🔍 Validating adapter: cookbook

✅ Adapter loaded: Historical Cookbook Adapter
✅ Field map: 3 fields
✅ Templates: 1 found
✅ Solr schema: 1 custom fields

🧪 Testing field resolution...
  ✅ title -> title
  ✅ ingredients -> metadata.ingredients
  ✅ cook_time -> metadata.cook_time

==================================================

⚠️  1 warning(s):
  - Missing recommended fields: author, pub_date

✅ Validation passed with warnings
```

### `adapter test`

Test adapter functionality with sample data.

#### Usage

```bash
# Test configured adapter
python manage.py adapter test

# Test specific adapter
python manage.py adapter test cookbook

# Create sample data for testing
python manage.py adapter test cookbook --create-sample
```

#### Options

- `adapter` (optional): Adapter name or path
- `--create-sample`: Create sample DigitizedWork records

#### Test Coverage

1. **Field mapping**: Tests Solr document generation
2. **Template resolution**: Checks template override paths
3. **Sample data creation**: Creates test records (with `--create-sample`)

#### Example Output

```
🧪 Testing adapter: Historical Cookbook Adapter

Test 1: Field Mapping
  Mapped 3 fields:
    title: Test Cookbook
    ingredients: ['flour', 'sugar']
    cook_time: 30 minutes

Test 2: Template Resolution
  ✅ archive/snippets/search_result.html: /adapters/cookbook/templates/...
  ⚠️  archive/digitizedwork_detail.html: using default

Test 3: Creating Sample Data
  ✅ Created: Sample Historical Cookbook Adapter Item
     ID: 42
     Admin URL: /admin/archive/digitizedwork/42/change/

✅ All tests passed!
```

### `adapter list`

List all available adapters in the adapters directory.

#### Usage

```bash
# List adapters
python manage.py adapter list

# List with detailed information
python manage.py adapter list --verbose
```

#### Options

- `--verbose`, `-v`: Show detailed information

#### Example Output

```
📦 Available Adapters:

  cookbook (Historical Cookbook Adapter)
    Location: /path/to/examples/adapters/cookbook
    Fields: 3 mapped
    Status: ✅ Valid

  newspaper (Newspaper Archive Adapter)
    Location: /path/to/examples/adapters/newspaper
    Fields: 8 mapped
    Status: ⚠️  Validation warnings

Use 'python manage.py adapter info <name>' for details
```

### `adapter info`

Show detailed information about a specific adapter.

#### Usage

```bash
python manage.py adapter info cookbook
```

#### Example Output

```
📦 Historical Cookbook Adapter

Name: cookbook
Location: /path/to/examples/adapters/cookbook
Status: ✅ Valid

Field Mapping (3 fields):
  title → title
  ingredients → metadata.ingredients
  cook_time → metadata.cook_time

Solr Schema (1 custom fields):
  ingredients_exact (string, multi-valued)

Templates (1 overrides):
  search_results.html

Usage:
  Set in settings: ARCHIVE_ADAPTER = 'cookbook'
  Or environment: export ARCHIVE_ADAPTER=cookbook
```

## Common Workflows

### Creating a New Adapter

```bash
# 1. Create adapter interactively
python manage.py adapter create my_collection -i

# 2. Validate configuration
python manage.py adapter validate my_collection

# 3. Test adapter
python manage.py adapter test my_collection

# 4. Configure in settings
echo "ARCHIVE_ADAPTER = 'my_collection'" >> ppa/settings/local_settings.py

# 5. Restart server
python manage.py runserver
```

### Debugging an Adapter

```bash
# 1. Validate with detailed output
python manage.py adapter validate my_collection

# 2. Test field mapping
python manage.py adapter test my_collection

# 3. Check adapter info
python manage.py adapter info my_collection

# 4. Create sample data
python manage.py adapter test my_collection --create-sample
```

### Listing All Adapters

```bash
# Quick list
python manage.py adapter list

# Detailed list
python manage.py adapter list -v
```

## Configuration

### Adapter Directory

By default, adapters are stored in `examples/adapters/`. You can configure this in settings:

```python
# ppa/settings/local_settings.py
ADAPTERS_DIR = BASE_DIR / 'examples' / 'adapters'
```

Or via environment variable:

```bash
export ADAPTERS_DIR=/path/to/adapters
```

### Active Adapter

Set the active adapter in settings:

```python
# ppa/settings/local_settings.py
ARCHIVE_ADAPTER = 'cookbook'
```

Or via environment variable:

```bash
export ARCHIVE_ADAPTER=cookbook
```

## Field Mapping Patterns

### Direct Field Mapping

Map Solr field directly to model attribute:

```yaml
field_map:
  title: title
  author: author
  pub_date: pub_date
```

### Nested JSON Mapping

Map Solr field to nested JSON in metadata:

```yaml
field_map:
  ingredients: metadata.ingredients
  cook_time: metadata.cook_time
  cuisine: metadata.cuisine
```

### Deep Nesting

Access deeply nested values:

```yaml
field_map:
  recipe_author: metadata.recipe.author
  recipe_source: metadata.recipe.source.name
```

## Solr Schema Configuration

### Field Types

Common Solr field types:

- `string`: Exact string matching
- `text_general`: Full-text search
- `plong`: Long integer
- `boolean`: True/false
- `pdate`: Date/time

### Multi-valued Fields

For fields that can have multiple values:

```yaml
solr_schema:
  fields:
    - name: ingredients_exact
      type: string
      multiValued: true
```

### Indexed vs Stored

- `indexed: true`: Field can be searched
- `stored: true`: Field value is returned in results

## Template Overrides

Place custom templates in the adapter's `templates/` directory:

```
examples/adapters/cookbook/
├── adapter.yaml
├── templates/
│   ├── archive/
│   │   ├── snippets/
│   │   │   └── search_result.html
│   │   └── digitizedwork_detail.html
│   └── base.html
└── static/
    ├── css/
    │   └── cookbook.css
    └── js/
        └── cookbook.js
```

Templates in the adapter directory take precedence over default templates.

## Best Practices

### Naming Conventions

- Use lowercase with underscores: `historical_cookbooks`
- Keep names short and descriptive
- Avoid special characters

### Field Mapping

- Always include `title` field
- Include `author` and `pub_date` when available
- Use consistent naming across adapters

### Validation

- Always validate after creating or modifying an adapter
- Use `--strict` mode in CI/CD pipelines
- Test field resolution with sample data

### Documentation

- Update adapter README.md with usage instructions
- Document custom fields and their purposes
- Include example data format

## Troubleshooting

### Adapter Not Found

```bash
# Check adapters directory
ls -la examples/adapters/

# Verify ADAPTERS_DIR setting
python manage.py shell -c "from django.conf import settings; print(settings.ADAPTERS_DIR)"
```

### Field Resolution Fails

```bash
# Test field path manually
python manage.py shell
>>> from ppa.archive.models import DigitizedWork
>>> work = DigitizedWork(metadata={'test': 'value'})
>>> work.get_adapter_field('metadata.test')
'value'
```

### Template Not Loading

```bash
# Check template directory
ls -la examples/adapters/cookbook/templates/

# Verify template loader
python manage.py shell -c "from django.template.loader import get_template; print(get_template('archive/digitizedwork_detail.html').origin.name)"
```

## See Also

- [Creating Adapters Guide](creating-adapters.md)
- [Cookbook Example](cookbook-example.md)
- [Adapter System Architecture](../architecture/adapter-system.md)
