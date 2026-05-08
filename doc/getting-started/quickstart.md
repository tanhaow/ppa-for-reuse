# PPA Django Reuse - Quick Start Guide

Get started with PPA Django Reuse in 3 simple steps.

## Prerequisites

- [Homebrew](https://brew.sh) - Required for Solr
- [Devbox](https://www.jetify.com/devbox/docs/installing_devbox/) - Manages Python and Node.js versions
- PostgreSQL 15 (via homebrew) - `brew install postgresql@15 && brew services start postgresql@15`

## Setup (First Time)

### Step 1: Install Devbox

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

### Step 2: Clone and enter the environment

```bash
git clone https://github.com/Princeton-CDH/ppa-django-reuse.git
cd ppa-django-reuse
devbox shell
```

### Step 3: Set up the database

```bash
createdb ppa
psql -c "CREATE USER ppa WITH PASSWORD 'ppa';" postgres
psql -c "GRANT ALL PRIVILEGES ON DATABASE ppa TO ppa;" postgres
.venv/bin/python manage.py migrate
.venv/bin/python manage.py setup_site_pages
.venv/bin/python manage.py createsuperuser
```

### Step 4: Set up Solr

```bash
brew install solr
bash setup_solr.sh
```

This will:
- Start Solr with the required `analysis-extras` module
- Create the `ppa` core
- Configure all schema fields and copyFields
- Index all works

### Step 5: Start Development Server

```bash
devbox run dev
```

Visit **http://localhost:8000** 🎉

**Admin Access**: http://localhost:8000/admin

## Daily Development

```bash
# Enter development environment
devbox shell

# Start Solr (if not already running)
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr start -p 8983

# Or start all services via devbox
devbox services up

# Start server
devbox run dev

# Run tests
devbox run test
```

## Available Commands

| Command | Description |
|---------|-------------|
| `devbox services up` | Start Solr (and PostgreSQL if configured) |
| `devbox run dev` | Start development server |
| `devbox run test` | Run all tests |
| `devbox run verify` | Verify setup is correct |
| `bash setup_solr.sh` | (Re)initialize Solr core, schema, and index |

## Loading Sample Data

```bash
# Cookbook dataset
.venv/bin/python load_cookbook_data.py

# Sci-fi books dataset
.venv/bin/python import_scifi.py

# Feeding America dataset
.venv/bin/python import_feeding_america.py

# Reindex after import
.venv/bin/python manage.py index --index work
```

## Switching Adapters

Edit `ppa/settings/local_settings.py`:

```python
ARCHIVE_ADAPTER = 'cookbook'   # or 'scifi', 'feeding_america'
ARCHIVE_TYPE = 'cookbook'
```

Then reindex:

```bash
.venv/bin/python manage.py index --index work
```

## Troubleshooting

### Solr 404 / core not found?

```bash
bash setup_solr.sh
```

### Collections showing 0 works?

The `collections_str` copyField may be missing. Re-run `setup_solr.sh` — it
adds the copyField and reindexes automatically.

### Port 5432 conflict?

If homebrew PostgreSQL is already running, remove `postgresql@15` from
`devbox.json` to prevent devbox from trying to start a second instance.

### Port 8983 conflict?

```bash
/opt/homebrew/bin/solr stop -p 8983
```

## More Help

- [Adapter Guide](../adapters/creating-adapters.md)
- [Solr Setup](../operations/solr-setup.md)
- [Developer Notes](../development/developer-notes.rst)
- [GitHub Issues](https://github.com/Princeton-CDH/ppa-django-reuse/issues)
