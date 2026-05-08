# CLI Commands Reference

This document provides a comprehensive reference for all Django management commands available in PPA Django Reuse.

## Adapter Management

### `adapter`

Manage adapters (create, validate, test, list, info).

```bash
python manage.py adapter <subcommand> [options]
```

See [Adapter CLI Reference](../adapters/adapter-cli.md) for detailed documentation.

**Subcommands**:
- `create` - Create new adapter
- `validate` - Validate adapter configuration
- `test` - Test adapter functionality
- `list` - List available adapters
- `info` - Show adapter details

### `adapter_validate`

Legacy command to validate adapter configuration.

```bash
python manage.py adapter_validate [adapter_name]
```

**Note**: Use `python manage.py adapter validate` instead (new unified CLI).

### `build_adapter_solr`

Generate Solr schema JSON from adapter configuration.

```bash
python manage.py build_adapter_solr [adapter_name]
```

Outputs Solr field definitions that can be added to Solr schema.

## Database Management

### `migrate`

Apply database migrations.

```bash
python manage.py migrate [app_label] [migration_name]
```

**Examples**:
```bash
# Apply all pending migrations
python manage.py migrate

# Apply migrations for specific app
python manage.py migrate archive

# Migrate to specific migration
python manage.py migrate archive 0027
```

### `makemigrations`

Create new database migrations based on model changes.

```bash
python manage.py makemigrations [app_label]
```

### `showmigrations`

Show all migrations and their status.

```bash
python manage.py showmigrations
```

### `dbshell`

Open database shell.

```bash
python manage.py dbshell
```

## User Management

### `createsuperuser`

Create a superuser account.

```bash
python manage.py createsuperuser
```

**Interactive prompts**:
- Username
- Email address
- Password

### `changepassword`

Change user password.

```bash
python manage.py changepassword <username>
```

## Wagtail/CMS

### `setup_site_pages`

Set up initial Wagtail site pages.

```bash
python manage.py setup_site_pages
```

Creates default pages and site structure.

## Data Import

### `hathi_add`

Add HathiTrust volumes to the archive.

```bash
python manage.py hathi_add <htid> [<htid> ...]
```

**Example**:
```bash
python manage.py hathi_add njp.32101068970508
```

**Environment variables**:
- `HATHI_DATA`: Path to HathiTrust data directory

### `gale_import`

Import Gale/ECCO documents.

```bash
python manage.py gale_import <estc_id> [<estc_id> ...]
```

**Example**:
```bash
python manage.py gale_import CW0116618490
```

**Environment variables**:
- `MARC_DATA`: Path to MARC data
- `GALE_API_USERNAME`: Gale API username

### `import_csv`

Import data from CSV file.

```bash
python manage.py import_csv <csv_file>
```

**CSV format**:
- Must include `source_id`, `title` columns
- Optional: `author`, `pub_date`, `metadata` (JSON)

## Solr Management

### `index_solr`

Index or reindex content in Solr.

```bash
python manage.py index_solr [options]
```

**Options**:
- `--all`: Reindex all items
- `--clear`: Clear index before reindexing
- `--batch-size N`: Process N items at a time

**Example**:
```bash
# Reindex everything
python manage.py index_solr --all

# Clear and reindex
python manage.py index_solr --all --clear
```

### `solr_schema`

Manage Solr schema.

```bash
python manage.py solr_schema <action>
```

**Actions**:
- `show`: Display current schema
- `update`: Update schema from configuration

## Development

### `runserver`

Start development server.

```bash
python manage.py runserver [address:port]
```

**Examples**:
```bash
# Default (localhost:8000)
python manage.py runserver

# Custom port
python manage.py runserver 8080

# All interfaces
python manage.py runserver 0.0.0.0:8000
```

### `shell`

Open Python shell with Django environment loaded.

```bash
python manage.py shell
```

**Example usage**:
```python
from ppa.archive.models import DigitizedWork
from ppa.adapters.loader import get_adapter

# Get adapter
adapter = get_adapter()
print(adapter.display_name)

# Query works
works = DigitizedWork.objects.all()
print(works.count())
```

### `shell_plus`

Enhanced shell with auto-imports (requires django-extensions).

```bash
python manage.py shell_plus
```

### `check`

Check for common issues.

```bash
python manage.py check [options]
```

**Options**:
- `--deploy`: Check deployment settings
- `--tag <tag>`: Check specific tags (security, models, etc.)

**Example**:
```bash
# Basic check
python manage.py check

# Deployment check
python manage.py check --deploy

# Security check only
python manage.py check --tag security
```

### `test`

Run tests.

```bash
python manage.py test [app_label.TestCase.test_method]
```

**Examples**:
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test ppa.archive

# Run specific test case
python manage.py test ppa.archive.tests.test_models.TestDigitizedWork

# Run specific test method
python manage.py test ppa.archive.tests.test_models.TestDigitizedWork.test_get_adapter_field
```

## Static Files

### `collectstatic`

Collect static files for deployment.

```bash
python manage.py collectstatic [options]
```

**Options**:
- `--noinput`: Don't prompt for confirmation
- `--clear`: Clear existing files first

**Example**:
```bash
python manage.py collectstatic --noinput
```

### `findstatic`

Find static file locations.

```bash
python manage.py findstatic <path>
```

**Example**:
```bash
python manage.py findstatic css/main.css
```

## Maintenance

### `clearsessions`

Clear expired sessions from database.

```bash
python manage.py clearsessions
```

Run periodically (e.g., via cron) to clean up old sessions.

### `flush`

Remove all data from database.

```bash
python manage.py flush
```

**Warning**: This deletes all data! Use with caution.

## Custom Scripts

### Setup Script

Automated setup for development environment.

```bash
bash scripts/setup.sh
```

**What it does**:
- Starts Docker services
- Waits for PostgreSQL
- Runs migrations
- Creates admin user
- Configures feature flags
- Sets up Solr (optional)

### Verification Script

Verify setup is correct.

```bash
bash scripts/verify.sh
```

**What it checks**:
- Python version
- Node.js version
- Docker services
- Database connection
- Django configuration
- Static files
- Adapter validation
- Feature flags

## Devbox Commands

When using Devbox, these shortcuts are available:

```bash
# Full setup with Solr
devbox run setup

# Quick setup (skip Solr)
devbox run setup:quick

# Start development server
devbox run dev

# Run tests
devbox run test

# Verify setup
devbox run verify

# Clean all data
devbox run clean
```

## Common Workflows

### Initial Setup

```bash
# Start Docker services
docker compose -f docker/docker-compose.dev.yml up -d

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Set up site pages
python manage.py setup_site_pages

# Collect static files
python manage.py collectstatic --noinput
```

### Daily Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Start server
python manage.py runserver

# In another terminal: run tests
pytest

# Check for issues
python manage.py check
```

### Data Import

```bash
# Import from CSV
python manage.py import_csv data.csv

# Index in Solr
python manage.py index_solr --all

# Verify in admin
open http://localhost:8000/admin
```

### Adapter Development

```bash
# Create adapter
python manage.py adapter create my_collection -i

# Validate
python manage.py adapter validate my_collection

# Test
python manage.py adapter test my_collection --create-sample

# Configure
echo "ARCHIVE_ADAPTER = 'my_collection'" >> ppa/settings/local_settings.py

# Restart server
python manage.py runserver
```

### Troubleshooting

```bash
# Check configuration
python manage.py check --deploy

# Verify database
python manage.py dbshell --command="SELECT 1;"

# Check migrations
python manage.py showmigrations

# Test Solr connection
curl http://localhost:8983/solr/ppa/admin/ping

# Run verification
bash scripts/verify.sh
```

## Environment Variables

Commands respect these environment variables:

- `DJANGO_SETTINGS_MODULE`: Django settings module (default: `ppa.settings`)
- `DATABASE_URL`: Database connection string
- `SOLR_URL`: Solr connection URL
- `ARCHIVE_ADAPTER`: Active adapter name
- `ADAPTERS_DIR`: Adapters directory path
- `HATHI_DATA`: HathiTrust data directory
- `MARC_DATA`: MARC data directory
- `GALE_API_USERNAME`: Gale API username

**Example**:
```bash
export ARCHIVE_ADAPTER=cookbook
export SOLR_URL=http://localhost:8983/solr/ppa
python manage.py runserver
```

## Getting Help

For any command, use `--help`:

```bash
python manage.py <command> --help
```

**Example**:
```bash
python manage.py adapter --help
python manage.py migrate --help
python manage.py test --help
```
