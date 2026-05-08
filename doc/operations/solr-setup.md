# Solr Setup

This project uses Solr 9 for full-text search and work indexing.

## Quick Setup

The fastest way to get Solr running is the provided script:

```bash
bash setup_solr.sh
```

This handles everything in one step:
1. Starts Solr with the `analysis-extras` module
2. Creates the `ppa` core if it doesn't exist
3. Configures all required schema fields and copyFields
4. Runs `manage.py index --index work`

## Prerequisites

Install Solr 9 via homebrew:

```bash
brew install solr
```

Verify the installation:

```bash
solr --version
# Solr version is: 9.x.x
```

## Manual Setup

If you need to set up Solr step by step:

### 1. Start Solr

The `analysis-extras` module is required for the ICU folding token filter used
in the schema:

```bash
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr start -p 8983
```

### 2. Create the `ppa` core

```bash
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr create -c ppa
```

### 3. Configure schema fields

Add the required fields via the Schema API:

```bash
curl -X POST -H 'Content-type:application/json' \
  --data-binary '{
    "add-field":[
      {"name":"source_id","type":"string","stored":true,"indexed":true,"multiValued":false},
      {"name":"title","type":"text_general","stored":true,"indexed":true,"multiValued":false},
      {"name":"author","type":"text_general","stored":true,"indexed":true,"multiValued":false},
      {"name":"pub_date","type":"plongs","stored":true,"indexed":true,"multiValued":false},
      {"name":"item_type","type":"string","stored":true,"indexed":true,"multiValued":false},
      {"name":"collections","type":"string","stored":true,"indexed":true,"multiValued":true},
      {"name":"collections_str","type":"string","stored":true,"indexed":true,"multiValued":true},
      {"name":"sort_title","type":"string","stored":true,"indexed":true,"multiValued":false}
    ]
  }' http://localhost:8983/solr/ppa/schema
```

### 4. Add copyFields

```bash
# collections → collections_str (required for collection facets/counts)
curl -X POST -H 'Content-type:application/json' \
  --data-binary '{"add-copy-field":{"source":"collections","dest":"collections_str"}}' \
  http://localhost:8983/solr/ppa/schema

# title → sort_title
curl -X POST -H 'Content-type:application/json' \
  --data-binary '{"add-copy-field":{"source":"title","dest":"sort_title"}}' \
  http://localhost:8983/solr/ppa/schema
```

### 5. Index works

```bash
.venv/bin/python manage.py index --index work
```

## Daily Usage

Start Solr:

```bash
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr start -p 8983
```

Stop Solr:

```bash
/opt/homebrew/bin/solr stop -p 8983
```

Or use devbox services (starts Solr automatically):

```bash
devbox services up
```

## Reindexing

After importing new data or changing adapter configuration, reindex:

```bash
.venv/bin/python manage.py index --index work
```

## Troubleshooting

### 404 Not Found on `/solr/ppa/select`

The `ppa` core doesn't exist. Run:

```bash
bash setup_solr.sh
```

### `icuFolding` SPI error when creating core

Solr was started without the `analysis-extras` module. Stop Solr and restart
with the module:

```bash
/opt/homebrew/bin/solr stop -p 8983
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr start -p 8983
```

### Collections showing 0 works

The `collections → collections_str` copyField is missing. Add it and reindex:

```bash
curl -X POST -H 'Content-type:application/json' \
  --data-binary '{"add-copy-field":{"source":"collections","dest":"collections_str"}}' \
  http://localhost:8983/solr/ppa/schema

.venv/bin/python manage.py index --index work
```

### Connection refused (port 8983)

Solr is not running. Start it:

```bash
SOLR_MODULES=analysis-extras /opt/homebrew/bin/solr start -p 8983
```

## Solr Admin UI

Browse the Solr admin interface at:

```
http://localhost:8983/solr/
```

Useful queries in the Query panel (select core `ppa`):

| Query | Purpose |
|-------|---------|
| `*:*` with `fq=item_type:work` | All indexed works |
| `source_id:cookbook_001` | Specific work by ID |
| `*:*` with `rows=0` | Count total documents |
