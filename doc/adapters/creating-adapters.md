# Creating and Using Adapters

This guide explains how to create and use adapters in the PPA Django Reuse system, including support for multiple adapters running simultaneously.

## What are Adapters?

Adapters allow you to customize the PPA Django application for different types of collections without modifying core code. They provide:

- **YAML-based configuration** - No code changes needed
- **Custom metadata fields** - Store collection-specific data
- **Template overrides** - Custom display for different record types
- **Solr field mapping** - Map metadata to searchable fields
- **Multi-adapter support** - Run multiple adapters simultaneously

## Multi-Adapter Support

**New in 2026:** The system now supports multiple adapters running simultaneously. Each collection can specify which adapter to use, and works automatically inherit the adapter from their collection.

### Key Features

- **Collection-level adapter assignment** - Each collection specifies its adapter
- **Automatic adapter selection** - Works inherit adapters from their collections
- **Field name prefixing** - Prevents conflicts between adapters (e.g., `cookbook_cook_time`, `scifi_rating_score`)
- **Context-aware display** - Show different fields based on which collection you're viewing from
- **Backward compatible** - Single-adapter deployments continue to work

### How It Works

```python
# Each collection has an adapter_name field
collection = Collection.objects.get(name='Science Fiction - Cyberpunk')
collection.adapter_name = 'scifi'
collection.save()

# Works automatically use their collection's adapter
work = DigitizedWork.objects.filter(collections=collection).first()
adapters = get_adapters_for_work(work)  # Returns ['scifi']

# When viewing from a specific collection, only that adapter's fields show
# URL: /archive/work/scifi_123/?collection=18
# Shows: scifi_subgenre, scifi_rating_score, scifi_genres

# When viewing directly (no collection parameter), all adapter fields show
# URL: /archive/work/scifi_123/
# Shows: All fields from all applicable adapters
```

## Quick Start

### 1. Create Adapter Directory

```bash
mkdir -p examples/adapters/your_adapter/templates
cd examples/adapters/your_adapter
```

### 2. Create adapter.yaml

**Important:** Use field name prefixes to avoid conflicts with other adapters.

```yaml
name: your_adapter
display_name: Your Collection Type
field_map:
  title: title
  author: author
  pub_date: pub_date
  # Use adapter name as prefix for custom fields
  your_adapter_custom_field: metadata.custom_field
  your_adapter_category: metadata.category
templates_dir: templates
display_fields:
  list_view:
    - field: your_adapter_category
      label: "Category"
  detail_view:
    - field: your_adapter_custom_field
      label: "Custom Field"
      source: "metadata.custom_field"
    - field: your_adapter_category
      label: "Category"
      source: "metadata.category"
solr_schema:
  fields:
    - name: your_adapter_custom_field_exact
      type: string
      multiValued: false
```

### 3. Assign Adapter to Collections

**Option A: Django Admin**
1. Go to http://localhost:8000/admin/archive/collection/
2. Edit a collection
3. Set "Adapter name" to `your_adapter`
4. Save

**Option B: Django Shell**
```python
from ppa.archive.models import Collection

collection = Collection.objects.get(name='Your Collection')
collection.adapter_name = 'your_adapter'
collection.save()
```

**Option C: Bulk Assignment**
```python
# Assign adapter to multiple collections
Collection.objects.filter(name__startswith='Science Fiction').update(
    adapter_name='scifi'
)
```

### 4. Reindex Solr

After creating a new adapter or changing adapter assignments:

```bash
python manage.py index --index work
```

## Field Naming Convention

**Critical:** Always prefix custom fields with your adapter name to prevent conflicts.

### Good Examples ✅

```yaml
# cookbook adapter
field_map:
  cookbook_cook_time: metadata.cook_time
  cookbook_ingredients: metadata.ingredients
  cookbook_cuisine: metadata.cuisine

# scifi adapter
field_map:
  scifi_subgenre: metadata.subgenre
  scifi_rating_score: metadata.rating_score
  scifi_genres: metadata.genres
```

### Bad Examples ❌

```yaml
# DON'T DO THIS - fields will conflict!
field_map:
  rating: metadata.rating  # Which adapter's rating?
  category: metadata.category  # Ambiguous!
```

## Example Adapters

### Cookbook Adapter

Location: `examples/adapters/cookbook/adapter.yaml`

```yaml
name: cookbook
display_name: Historical Cookbook Adapter
field_map:
  title: title
  cookbook_ingredients: metadata.ingredients
  cookbook_cook_time: metadata.cook_time
  cookbook_passage: metadata.passage
templates_dir: templates
display_fields:
  list_view:
    - field: cookbook_cook_time
      label: "Cook Time"
  detail_view:
    - field: cookbook_cook_time
      label: "Cook Time"
      source: "metadata.cook_time"
    - field: cookbook_ingredients
      label: "Ingredients"
      source: "metadata.ingredients"
    - field: cookbook_passage
      label: "Passage"
      source: "metadata.passage"
      type: passage
solr_schema:
  fields:
    - name: cookbook_ingredients_exact
      type: string
      multiValued: true
```

### Science Fiction Adapter

Location: `examples/adapters/scifi/adapter.yaml`

```yaml
name: scifi
display_name: Science Fiction Books
field_map:
  title: title
  author: author
  pub_date: pub_date
  scifi_subgenre: metadata.subgenre
  scifi_rating_score: metadata.rating_score
  scifi_rating_votes: metadata.rating_votes
  scifi_genres: metadata.genres
  scifi_description: metadata.description
  scifi_goodreads_url: metadata.goodreads_url
  scifi_passage: metadata.passage
templates_dir: templates
display_fields:
  list_view:
    - field: scifi_subgenre
      label: "Subgenre"
    - field: scifi_rating_score
      label: "Rating"
  detail_view:
    - field: scifi_subgenre
      label: "Subgenre"
      source: "metadata.subgenre"
    - field: scifi_rating_score
      label: "Goodreads Rating"
      source: "metadata.rating_score"
    - field: scifi_genres
      label: "Genres"
      source: "metadata.genres"
    - field: scifi_passage
      label: "Passage"
      source: "metadata.passage"
      type: passage
solr_schema:
  fields:
    - name: scifi_subgenre_exact
      type: string
      multiValued: false
    - name: scifi_genres_exact
      type: string
      multiValued: true
```

## Adding Data

### Create Works with Metadata

```python
from ppa.archive.models import DigitizedWork, Collection

# Get collection with adapter
collection = Collection.objects.get(adapter_name='scifi')

# Create work with adapter-specific metadata
work = DigitizedWork.objects.create(
    source_id="scifi_cyberpunk_001",
    title="Neuromancer",
    author="Gibson, William",
    pub_date=1984,
    source="O",
    metadata={
        "subgenre": "cyberpunk",
        "rating_score": 4.1,
        "rating_votes": 250000,
        "genres": ["Science Fiction", "Cyberpunk", "Fiction"],
        "description": "A groundbreaking cyberpunk novel...",
        "goodreads_url": "https://www.goodreads.com/book/show/22328.Neuromancer"
    }
)
work.collections.add(collection)
work.save()
```

## Viewing Works with Different Adapters

### From Collection Page

When you click a work from a collection page, the URL includes the collection ID:

```
http://localhost:8000/archive/work/scifi_123/?collection=18
```

The page will show only the fields from that collection's adapter.

### Direct Access

When you access a work directly without a collection parameter:

```
http://localhost:8000/archive/work/scifi_123/
```

The page will show fields from all applicable adapters, grouped by adapter.

## Adapter API Reference

### Field Map Syntax

```yaml
field_map:
  solr_field_name: model_path
```

**Model paths:**
- Direct field: `title`, `author`, `pub_date`
- Nested JSON: `metadata.field_name`
- Deep nesting: `metadata.nested.deep.field`

### Display Fields Configuration

```yaml
display_fields:
  list_view:  # Fields shown in search results
    - field: adapter_field_name
      label: "Display Label"
  detail_view:  # Fields shown on detail page
    - field: adapter_field_name
      label: "Display Label"
      source: "metadata.field_name"  # Path to resolve value from DB object
      separator: ", "               # Optional: join list values (default ", ")
      type: passage                 # Optional: render as standalone section
```

#### The `passage` field type

Setting `type: passage` on a `detail_view` field renders it as a standalone
section below the metadata table instead of as a table row. Use this for
longer text content such as descriptions, abstracts, or full passages.

```yaml
display_fields:
  detail_view:
    - field: scifi_description
      label: "Description"
      source: "metadata.description"
      type: passage
```

Fields with `type: passage` are excluded from the metadata table and rendered
in their own `<section>` element using the
`archive/snippets/passage_section.html` template.

### Solr Schema Types

Common field types:
- `string` - Exact match, not analyzed
- `text_general` - Full-text search, analyzed
- `pint` - Integer
- `plong` - Long integer
- `pfloat` - Float
- `pdate` - Date
- `boolean` - True/False

Field options:
- `multiValued: true` - Array of values
- `multiValued: false` - Single value (default)
- `stored: true` - Return in search results
- `indexed: true` - Searchable/sortable

## Management Commands

### Validate Adapter

```bash
python manage.py adapter validate your_adapter
```

### View Adapter Info

```bash
python manage.py adapter info your_adapter
```

### List All Adapters

```bash
python manage.py adapter list
```

## Troubleshooting

### Adapter Not Loading

Check adapter configuration:
```bash
python manage.py shell -c "from ppa.adapters.loader import get_adapter; print(get_adapter('your_adapter'))"
```

### Fields Not Showing

1. **Check collection has adapter assigned:**
```python
from ppa.archive.models import Collection
collection = Collection.objects.get(name='Your Collection')
print(f"Adapter: {collection.adapter_name}")
```

2. **Check work has metadata:**
```python
from ppa.archive.models import DigitizedWork
work = DigitizedWork.objects.first()
print(f"Metadata: {work.metadata}")
```

3. **Check Solr indexing:**
```bash
curl "http://localhost:8983/solr/ppa/select?q=source_id:your_work_id&fl=*"
```

### Field Name Conflicts

If two adapters define the same field name, the later adapter will overwrite the earlier one during indexing. **Always use prefixed field names** to avoid this.

## Best Practices

1. **Always prefix custom fields** with adapter name (e.g., `cookbook_cook_time`)
2. **Use metadata JSONField** for adapter-specific data
3. **Keep adapter.yaml simple** - only map fields you need
4. **Document your adapter** - Add comments in adapter.yaml
5. **Test without Solr first** - Verify adapter loads correctly
6. **Assign adapters to collections** - Don't rely on global ARCHIVE_ADAPTER
7. **Reindex after changes** - Run `python manage.py index --index work`

## Migration from Single Adapter

If you're upgrading from a single-adapter setup:

1. **Keep your existing adapter** - It will continue to work
2. **Assign adapter to collections:**
```python
Collection.objects.filter(name__contains='Cookbook').update(adapter_name='cookbook')
```
3. **Add field prefixes** to new adapters to avoid conflicts
4. **Reindex Solr** to include all adapter fields

---

**Last Updated**: March 11, 2026

1. Go to http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Navigate to:
   - **Archive > Digitized works** - see your cookbook entries
   - **Waffle > Switches** - manage feature flags
   - **Archive > Collections** - see the cookbook collection

## What to Expect

### Adapter Features Active:

1. **Template Override**: The cookbook adapter's `search_results.html` template will be used instead of the default
2. **Field Mapping**: The adapter's `field_map` in `adapter.yaml` maps:
   - `title` → `title`
   - `ingredients` → `metadata.ingredients`
   - `cook_time` → `metadata.cook_time`
3. **Metadata Storage**: Cookbook-specific data (ingredients, cook_time, cuisine) is stored in the `metadata` JSONField
4. **Solr Schema**: When Solr is enabled, the adapter defines custom fields like `ingredients_exact`

### Without Solr:

Since we have `enable_solr_indexing` set to `False`, the app will use the `FakeSolrClient` fallback, which means:
- Search functionality will be limited
- The homepage will render without errors
- You can still browse individual cookbook records
- Template overrides will still work

## Viewing Cookbook Data

### Via Django Admin:
http://localhost:8000/admin/archive/digitizedwork/

### Via Django Shell:
```bash
python manage.py shell
```

```python
from ppa.archive.models import DigitizedWork

# List all cookbooks
for work in DigitizedWork.objects.all():
    print(f"{work.title} ({work.pub_date})")
    print(f"  Ingredients: {work.metadata.get('ingredients', [])}")
    print(f"  Cook time: {work.metadata.get('cook_time', 'N/A')}")
    print()
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'waffle'"
**Solution**: Make sure you've installed requirements: `pip install -r requirements.txt`

### Issue: Database connection errors
**Solution**: Ensure PostgreSQL is running and credentials in `local_settings.py` match your database

### Issue: Template not found errors
**Solution**: Run `npm run build` to compile frontend assets

### Issue: Static files not loading
**Solution**: Run `python manage.py collectstatic` or ensure `DEBUG = True` in local_settings

## Next Steps

1. **Enable Solr** (optional): Start Solr with Docker Compose and set `enable_solr_indexing` switch to True
2. **Import Full Dataset**: Create a management command to import the full Feeding America XML data
3. **Customize Templates**: Edit templates in `examples/adapters/cookbook/templates/`
4. **Add More Fields**: Extend the `field_map` in `adapter.yaml` to include more cookbook-specific metadata

## Testing the Adapter System

To verify the adapter is working:

```bash
# Check which adapter is loaded
python manage.py shell -c "from ppa.adapters.loader import get_adapter; print(get_adapter())"

# Should output:
# Adapter(name='cookbook', display_name='Historical Cookbook Adapter', ...)
```

## File Locations

- **Adapter config**: `examples/adapters/cookbook/adapter.yaml`
- **Adapter templates**: `examples/adapters/cookbook/templates/`
- **Settings**: `ppa/settings/local_settings.py`
- **Models**: `ppa/archive/models.py` (DigitizedWork has the `metadata` JSONField)
- **Adapter loader**: `ppa/adapters/loader.py`
