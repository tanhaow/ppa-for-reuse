# Configuring List View Fields in Django Admin

This guide explains how to configure which adapter fields are displayed in the archive list view using Django Admin.

## Overview

When users browse the archive and filter by a single collection, the system can display collection-specific fields in the search results. You can configure these fields in two ways:

1. **Adapter defaults** - Defined in `adapter.yaml` (automatic)
2. **Collection overrides** - Configured in Django Admin (manual, per-collection)

## Quick Start

### Access Django Admin

1. Navigate to: `http://localhost:8000/admin/archive/collection/`
2. Login with your admin credentials
3. Click on a collection to edit it

### Configure List View Fields

In the collection edit page, you'll see:

- **Adapter Name**: The adapter to use (e.g., `cookbook`, `scifi`)
- **List View Fields**: Custom fields configuration (JSON format)

## Configuration Methods

### Method 1: Use Adapter Defaults (Recommended)

**When to use:** For most collections, the adapter's default fields are sufficient.

**How it works:**
- Leave the "List View Fields" field **empty**
- The system automatically uses the `list_view` fields defined in the adapter's YAML file

**Example:**

For a collection with `adapter_name = "cookbook"`, the system will use:

```yaml
# From examples/adapters/cookbook/adapter.yaml
display_fields:
  list_view:
    - field: cookbook_cook_time
      label: "Cook Time"
    - field: cookbook_ingredients
      label: "Ingredients"
```

### Method 2: Custom Configuration (Advanced)

**When to use:** When you want to:
- Show different fields than the adapter defaults
- Customize field labels
- Show only a subset of available fields
- Reorder fields

**How it works:**
- Enter a JSON array in the "List View Fields" field
- This overrides the adapter defaults for this specific collection

**JSON Format:**

```json
[
  {"field": "field_name", "label": "Display Label"},
  {"field": "another_field", "label": "Another Label"}
]
```

## Examples

### Example 1: Cookbook Collection

**Scenario:** Show only cook time (hide ingredients)

**Configuration:**

```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"}
]
```

**Result:** Only "Cook Time" will be displayed in the list view for this collection.

### Example 2: Sci-Fi Collection

**Scenario:** Show subgenre and rating, but not genres

**Configuration:**

```json
[
  {"field": "scifi_subgenre", "label": "Subgenre"},
  {"field": "scifi_rating_score", "label": "Rating"}
]
```

**Result:** Only "Subgenre" and "Rating" will be displayed.

### Example 3: Custom Labels

**Scenario:** Use different labels than the adapter defaults

**Configuration:**

```json
[
  {"field": "cookbook_cook_time", "label": "Preparation Time"},
  {"field": "cookbook_ingredients", "label": "Main Ingredients"}
]
```

**Result:** Fields will be displayed with custom labels.

### Example 4: Reorder Fields

**Scenario:** Show ingredients before cook time

**Configuration:**

```json
[
  {"field": "cookbook_ingredients", "label": "Ingredients"},
  {"field": "cookbook_cook_time", "label": "Cook Time"}
]
```

**Result:** Ingredients will appear before cook time in the list.

## Using Django Admin

### Step-by-Step Guide

1. **Navigate to Collections Admin**
   ```
   http://localhost:8000/admin/archive/collection/
   ```

2. **Select a Collection**
   - Click on the collection name you want to configure
   - Example: "Historic American Cookbooks"

3. **Set Adapter Name** (if not already set)
   - In the "Adapter Name" field, enter: `cookbook`
   - This tells the system which adapter to use

4. **Configure List View Fields** (optional)
   - Leave empty to use adapter defaults
   - Or enter custom JSON configuration:

   ```json
   [
     {"field": "cookbook_cook_time", "label": "Cook Time"},
     {"field": "cookbook_ingredients", "label": "Ingredients"}
   ]
   ```

5. **Save**
   - Click "Save" or "Save and continue editing"
   - Changes take effect immediately (no restart needed)

## Using Django Shell

You can also configure fields programmatically:

```python
from ppa.archive.models import Collection

# Get collection
collection = Collection.objects.get(name='Historic American Cookbooks')

# Set adapter
collection.adapter_name = 'cookbook'

# Set custom fields
collection.list_view_fields = [
    {'field': 'cookbook_cook_time', 'label': 'Cook Time'},
    {'field': 'cookbook_ingredients', 'label': 'Ingredients'}
]

# Save
collection.save()
```

## Available Fields by Adapter

### Cookbook Adapter

Available fields:
- `cookbook_cook_time` - Cooking time
- `cookbook_ingredients` - List of ingredients

### Sci-Fi Adapter

Available fields:
- `scifi_subgenre` - Science fiction subgenre
- `scifi_rating_score` - Goodreads rating score
- `scifi_rating_votes` - Number of rating votes
- `scifi_genres` - List of genres
- `scifi_description` - Book description
- `scifi_goodreads_url` - Goodreads URL

### Feeding America Adapter

Available fields:
- `feeding_america_source_info` - Source information
- `feeding_america_dataset` - Dataset name
- `feeding_america_recipes` - Recipe information

## Viewing Results

After configuring fields:

1. **Navigate to Archive List**
   ```
   http://localhost:8000/archive/
   ```

2. **Filter by Your Collection**
   - Select the collection from the filters
   - Example: Check "Historic American Cookbooks"

3. **View Results**
   - Search results will show your configured fields
   - Each work will display the custom fields below the standard fields (title, author, date)

## Troubleshooting

### Fields Not Showing

**Problem:** Configured fields don't appear in the list view

**Solutions:**

1. **Check adapter is assigned:**
   ```python
   collection = Collection.objects.get(name='Your Collection')
   print(collection.adapter_name)  # Should not be empty
   ```

2. **Check field names are correct:**
   - Field names must match exactly (case-sensitive)
   - Must include adapter prefix (e.g., `cookbook_`, not just `cook_time`)

3. **Check data is indexed in Solr:**
   ```bash
   curl "http://localhost:8983/solr/ppa/select?q=source_id:cookbook_001&fl=cookbook_cook_time,cookbook_ingredients"
   ```

4. **Reindex if needed:**
   ```bash
   python manage.py index --index work
   ```

### JSON Format Errors

**Problem:** "Invalid JSON" error when saving

**Solution:** Validate your JSON format:

```json
[
  {"field": "field_name", "label": "Label"}
]
```

Common mistakes:
- Missing commas between objects
- Using single quotes instead of double quotes
- Missing brackets `[]`
- Trailing commas

**Valid:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"},
  {"field": "cookbook_ingredients", "label": "Ingredients"}
]
```

**Invalid:**
```json
[
  {'field': 'cookbook_cook_time', 'label': 'Cook Time'},  // Single quotes
  {"field": "cookbook_ingredients", "label": "Ingredients"},  // Trailing comma
]
```

### Multiple Collections Selected

**Problem:** Fields don't show when multiple collections are selected

**Explanation:** This is by design. Adapter fields only show when:
- Exactly **one** collection is selected
- That collection has an `adapter_name` configured

**Solution:** Filter by a single collection to see adapter-specific fields.

## Best Practices

1. **Start with Adapter Defaults**
   - Leave "List View Fields" empty initially
   - Only customize if you need different behavior

2. **Use Meaningful Labels**
   - Labels should be clear and user-friendly
   - Example: "Cook Time" instead of "Time"

3. **Limit Number of Fields**
   - Show 2-4 fields maximum in list view
   - Too many fields make the list cluttered

4. **Test After Changes**
   - Always test the list view after configuration
   - Check that fields display correctly

5. **Document Custom Configurations**
   - Keep notes on why you customized fields
   - Helps future maintainers understand decisions

## Advanced: Field Options

The field configuration supports additional options:

```json
[
  {
    "field": "cookbook_ingredients",
    "label": "Ingredients",
    "separator": " • "
  }
]
```

**Available options:**
- `field` (required) - The Solr field name
- `label` (required) - Display label
- `separator` (optional) - For array fields, how to join values (default: ", ")

## Related Documentation

- [Creating Adapters](creating-adapters.md) - How to create new adapters
- [Adapter CLI Reference](adapter-cli.md) - Command-line tools for adapters
- [Multi-Adapter Support](creating-adapters.md#multi-adapter-support) - Using multiple adapters

---

**Last Updated**: March 11, 2026
