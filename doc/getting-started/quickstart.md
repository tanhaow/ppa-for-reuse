# Quick Start Guide

Get PPA Django Reuse running locally. Two paths are available: **Docker + Devbox** (recommended, fully automated) or **manual** (if you prefer to manage services yourself).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — runs PostgreSQL and Solr
- Git

That's it for the Docker path. Devbox and Python/Node are optional if you use the manual path.

---

## Path A: Docker + Devbox (recommended)

Devbox pins Python 3.12 and Node 22, installs all dependencies, and wires up the environment automatically.

### 1. Install Devbox

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

### 2. Clone and enter the environment

```bash
git clone https://github.com/Princeton-CDH/ppa-django-reuse.git
cd ppa-django-reuse
devbox shell
```

`devbox shell` installs Python 3.12, Node 22, creates `.venv`, and runs `pip install` and `npm install` automatically on first entry.

### 3. Create local settings

```bash
cp ppa/settings/local_settings.py.sample ppa/settings/local_settings.py
```

Open the file and set a `SECRET_KEY`. Everything else works with the defaults for local development.

### 4. Run setup

```bash
devbox run setup
```

This single command:
- Starts PostgreSQL 15 and Solr 9 via Docker Compose
- Runs `manage.py migrate`
- Runs `manage.py setup_site_pages`
- Creates an admin user (`admin` / `admin123`)
- Creates waffle feature flag switches
- Uploads the project Solr schema into the container and reloads the core

### 5. Start the development server

```bash
devbox run dev
```

Visit **http://localhost:8000** — the archive is at **/archive/**, admin at **/admin/**.

---

## Path B: Manual setup

Use this if you already have Python 3.12 and Node 22 installed, or if you don't want to use Devbox.

### 1. Clone

```bash
git clone https://github.com/Princeton-CDH/ppa-django-reuse.git
cd ppa-django-reuse
```

### 2. Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r dev-requirements.txt
```

### 3. Frontend assets

```bash
npm install
npm run build
```

This generates `webpack-stats.json`, which Django requires at startup.

### 4. Local settings

```bash
cp ppa/settings/local_settings.py.sample ppa/settings/local_settings.py
```

Set a `SECRET_KEY` in the file. The defaults connect to the Docker services on their standard ports.

### 5. Start Docker services

```bash
docker compose -f docker/docker-compose.dev.yml up -d
```

Wait a few seconds for PostgreSQL to become healthy.

### 6. Database and Solr setup

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/bash scripts/setup.sh
```

Or step by step:

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py migrate
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py setup_site_pages
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py createsuperuser

# Upload Solr schema
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

### 7. Start the development server

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py runserver
```

---

## Daily development

```bash
# Devbox path
devbox shell          # re-enter environment after closing terminal
devbox run dev        # start server (Docker services must be running)

# Manual path
docker compose -f docker/docker-compose.dev.yml up -d   # start services if stopped
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py runserver
```

### Devbox commands

| Command | What it does |
|---------|-------------|
| `devbox run setup` | Full first-time setup (Docker + DB + Solr + admin user) |
| `devbox run dev` | Start Django development server on port 8000 |
| `devbox run test` | Run Python tests (`pytest`) and JS tests (`npm test`) |
| `devbox run verify` | Check that all components are configured correctly |
| `devbox run clean` | Stop Docker services and remove `.venv`, `node_modules`, built assets |

---

## Loading sample data

The repo includes three example datasets. After setup, load one or more:

```bash
# Historical cookbooks
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python load_cookbook_data.py

# Sci-fi books (imports from test_datasets/sci_fi_books/)
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python import_scifi.py

# Feeding America historical cookbooks
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python import_feeding_america.py

# Reindex after any import
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py index --index work
```

---

## Switching adapters

Edit `ppa/settings/local_settings.py`:

```python
ARCHIVE_ADAPTER = 'cookbook'   # or 'scifi', 'feeding_america', or None
```

Then reindex:

```bash
DJANGO_SETTINGS_MODULE=ppa.settings .venv/bin/python manage.py index --index work
```

See [Creating Adapters](../adapters/creating-adapters.md) to build your own.

---

## Common issues

**`webpack-stats.json` not found on startup**
Run `npm run build` to generate it. This is required before the first server start.

**Port 5432 already in use**
Your machine has a local PostgreSQL running (e.g. Homebrew). The Docker container still starts but maps to the same port. Django will connect to whichever process owns the port — if it's your local PostgreSQL, make sure the `ppa` database and user exist there, or stop the local service and let Docker own the port.

**Solr unhealthy / `solrconfig.xml` permission denied**
The Docker volume has stale data from a previous container. Remove it and restart:
```bash
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d
# then re-run scripts/setup.sh to re-upload the schema
```

**`manage.py check` warns about missing `bundles/` directory**
This is expected before running `npm run build`. It's a staticfiles warning, not an error, and doesn't prevent the server from starting.

**Devbox fails with path-contains-spaces error**
Devbox 0.16.x cannot handle project paths with spaces. Either move the project to a path without spaces, or use the manual setup path (Path B above).
