# Developer Setup

This page covers the development environment in detail — what each component does, how the pieces fit together, and how to work with them day-to-day.

For a quick first-time setup, see the [Quick Start Guide](../getting-started/quickstart.md).

---

## Environment overview

| Component | Version | How it runs |
|-----------|---------|-------------|
| Python | 3.12 | `.venv/` (virtualenv) |
| Node.js | 22 | system or Devbox |
| PostgreSQL | 15 | Docker (`docker-compose.dev.yml`) |
| Solr | 9 | Docker (`docker-compose.dev.yml`) |
| Django | 5.2 | via `.venv` |
| Wagtail | 7.0 | via `.venv` |

### Why Docker for services?

PostgreSQL and Solr run in Docker so you don't need to manage local installations or worry about version conflicts. The `docker-compose.dev.yml` file defines both services with persistent named volumes, so data survives container restarts.

### Why Devbox?

Devbox pins the exact Python and Node versions declared in `devbox.json` and sets up the virtualenv automatically on `devbox shell`. It's optional — if you already have Python 3.12 and Node 22, the manual path works fine.

---

## Repository layout (key paths)

```
ppa-for-reuse/
├── ppa/
│   ├── adapters/          # adapter loader and HathiTrust shim
│   ├── archive/           # main Django app (models, views, admin, solr)
│   ├── settings/
│   │   ├── components/    # split settings (base, logging, etc.)
│   │   ├── environments/  # test.py
│   │   └── local_settings.py   # gitignored, created from .sample
│   ├── flags.py           # waffle feature flag helpers
│   └── solr_factory.py    # real/fake Solr toggle
├── examples/adapters/     # cookbook, scifi, feeding_america examples
├── solr_conf/conf/        # Solr schema and config files
├── srcmedia/
│   ├── js/controllers/    # Stimulus controllers
│   ├── ts/                # TypeScript (searchWithin)
│   └── scss/              # Sass stylesheets
├── templates/             # Django templates
├── test_datasets/         # sample CSV/XML data for example adapters
├── docker/
│   └── docker-compose.dev.yml
├── scripts/               # setup.sh, verify.sh, etc.
└── doc/                   # this documentation
```

---

## First-time setup

### 1. Docker services

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

This starts:
- **PostgreSQL 15** on port 5432 (user: `ppa`, password: `ppa`, database: `ppa`)
- **Solr 9** on port 8983 with the `analysis-extras` and `scripting` modules

Check they're healthy:

```bash
docker compose -f docker/docker-compose.dev.yml ps
```

Both should show `(healthy)` within about 15 seconds.

### 2. Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r dev-requirements.txt
```

Or with Devbox (handles this automatically on `devbox shell`).

### 3. Frontend assets

```bash
npm install
npm run build
```

This generates `webpack-stats.json` and the compiled CSS/JS bundles in `bundles/`. Django's `django-webpack-loader` reads `webpack-stats.json` at startup — the server will raise an `OSError` if it's missing.

For active frontend development, use `npm run dev` instead (webpack dev server with hot reload).

### 4. Local settings

```bash
cp ppa/settings/local_settings.py.sample ppa/settings/local_settings.py
```

Minimum required change: set `SECRET_KEY`. The sample file has comments explaining every option. Key settings for local development:

```python
SECRET_KEY = 'your-secret-key-here'
DEBUG = True

# Adapter to activate (optional)
# ARCHIVE_ADAPTER = 'cookbook'

# Solr — defaults match the Docker service
SOLR_CONNECTIONS["default"].update({
    "URL": "http://localhost:8983/solr/",
})
```

### 5. Database migrations

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py migrate
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py setup_site_pages
```

### 6. Solr schema

The Solr container starts with a default schema. Upload the project's schema:

```bash
docker cp solr_conf/conf/managed-schema.xml docker-solr-1:/var/solr/data/ppa/conf/managed-schema.xml
docker cp solr_conf/conf/solrconfig.xml      docker-solr-1:/var/solr/data/ppa/conf/solrconfig.xml
docker cp solr_conf/conf/elevate.xml         docker-solr-1:/var/solr/data/ppa/conf/elevate.xml
docker cp solr_conf/conf/params.json         docker-solr-1:/var/solr/data/ppa/conf/params.json
docker cp solr_conf/conf/stemdict_ppa.txt    docker-solr-1:/var/solr/data/ppa/conf/stemdict_ppa.txt
docker cp solr_conf/conf/synonyms.txt        docker-solr-1:/var/solr/data/ppa/conf/synonyms.txt
docker cp solr_conf/conf/protwords.txt       docker-solr-1:/var/solr/data/ppa/conf/protwords.txt
docker cp solr_conf/conf/stopwords.txt       docker-solr-1:/var/solr/data/ppa/conf/stopwords.txt
curl -s "http://localhost:8983/solr/admin/cores?action=RELOAD&core=ppa"
```

`scripts/setup.sh` does all of this automatically.

### 7. Admin user

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py createsuperuser
```

Or use the shortcut in `scripts/setup.sh` which creates `admin` / `admin123`.

---

## Running the server

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py runserver
```

With Devbox:

```bash
devbox run dev
```

The `devbox run dev` script also kills any process already on port 8000 before starting.

---

## Feature flags (waffle switches)

Runtime behaviour is controlled by [django-waffle](https://waffle.readthedocs.io/) switches. Create them in the Django admin under **Waffle > Switches**, or via the shell:

```python
from waffle.models import Switch
Switch.objects.update_or_create(name='enable_solr_indexing', defaults={'active': True})
```

| Switch | Default | Effect |
|--------|---------|--------|
| `enable_solr_indexing` | off | When off, Solr queries return empty results (useful for DB-only development) |
| `enable_hathi` | off | Enables HathiTrust import commands |
| `enable_corppa` | off | Enables corppa NLP utilities |

`scripts/setup.sh` creates all three switches in the off state.

---

## Running tests

```bash
# Python tests
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python -m pytest

# JavaScript unit tests
npm run test:unit

# Both
devbox run test
```

The test settings in `ppa/settings/environments/test.py` use an in-memory SQLite database and a separate Solr test collection with aggressive `commitWithin` timing.

---

## Updating the Solr schema

After editing `solr_conf/conf/managed-schema.xml`:

```bash
docker cp solr_conf/conf/managed-schema.xml docker-solr-1:/var/solr/data/ppa/conf/managed-schema.xml
curl -s "http://localhost:8983/solr/admin/cores?action=RELOAD&core=ppa"
```

Then reindex:

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py index --index work
```

---

## Rebuilding from scratch

To wipe everything and start over:

```bash
# Stop and remove containers + volumes
docker compose -f docker/docker-compose.dev.yml down -v

# Remove Python and Node artifacts
rm -rf .venv node_modules bundles webpack-stats.json

# Re-run setup
devbox run setup        # or follow the manual steps above
```

---

## Port reference

| Port | Service |
|------|---------|
| 8000 | Django development server |
| 5432 | PostgreSQL (Docker) |
| 8983 | Solr (Docker) |

If port 5432 is already in use by a local PostgreSQL installation, Django will connect to whichever process owns the port. The Docker container will still start but its port mapping will be blocked. Either stop the local PostgreSQL service, or configure Django to connect to a different port by editing `DATABASES` in `local_settings.py`.
