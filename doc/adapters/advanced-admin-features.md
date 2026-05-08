# Advanced Admin Features for List View Field Configuration

This document describes the advanced features added to the Django Admin for configuring list view fields.

## Overview

We've added four major enhancements to make it easier for administrators to configure which fields are displayed in the archive list view:

1. **JSON Schema Validation** - Automatic validation of field configuration
2. **Visual Field Selector** - User-friendly interface for selecting fields
3. **Field Preview** - Preview how fields will appear before saving
4. **Bulk Operations** - Configure multiple collections at once

## Feature 1: JSON Schema Validation

### What It Does

Automatically validates the `list_view_fields` JSON configuration to ensure:
- The value is a JSON array (list)
- Each item has required properties: `field` and `label`
- Field names follow the correct naming convention (adapter prefix)
- Common fields (title, author, etc.) are allowed without prefix

### How It Works

Validation happens automatically when saving a collection in Django Admin. Invalid configurations are rejected with clear error messages.

### Examples

**Valid Configuration:**
```json
[
  {"field": "cookbook_cook_time", "label": "Cook Time"},
  {"field": "cookbook_ingredients", "label": "Ingredients"}
]
```

**Invalid - Not a List:**
```json
{"field": "cookbook_cook_time", "label": "Cook Time"}
```
❌ Error: "Must be a JSON array (list)"

**Invalid - Missing Required Property:**
```json
[
  {"label": "Cook Time"}
]
```
❌ Error: "Item 1 is missing required property 'field'"

**Invalid - Wrong Prefix:**
```json
[
  {"field": "wrong_prefix_field", "label": "Wrong"}
]
```
❌ Error: "Field 'wrong_prefix_field' should start with adapter prefix 'cookbook_'"

**Valid - Common Field:**
```json
[
  {"field": "title", "label": "Title"}
]
```
✅ Common fields (title, author, pub_date, pub_place, publisher) are allowed without prefix

### Testing

```python
from ppa.archive.models import Collection
from django.core.exceptions import ValidationError

collection = Collection.objects.first()
collection.adapter_name = 'cookbook'

# Test invalid configuration
collection.list_view_fields = {'field': 'test'}  # Not a list
try:
    collection.full_clean()
except ValidationError as e:
    print(f"Validation error: {e}")

# Test valid configuration
collection.list_view_fields = [
    {'field': 'cookbook_cook_time', 'label': 'Cook Time'}
]
collection.full_clean()  # No error
collection.save()
```

## Feature 2: Visual Field Selector

### What It Does

Provides a user-friendly visual interface for configuring fields instead of manually writing JSON. Features include:
- Add/remove fields with buttons
- Reorder fields with up/down arrows
- Edit field labels inline
- Live JSON preview
- Drag-and-drop support (future enhancement)

### How It Works

When editing a collection with an adapter assigned, the `list_view_fields` input is replaced with a visual selector widget that:
1. Shows currently selected fields
2. Allows adding new fields via a dialog
3. Provides buttons to reorder and remove fields
4. Updates the hidden JSON input automatically

### User Interface

```
┌─────────────────────────────────────────────────┐
│ Select Fields to Display          [+ Add Field] │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ 1  cookbook_cook_time          [↑] [↓] [×] │ │
│ │    Field Name: cookbook_cook_time           │ │
│ │    Display Label: [Cook Time____________]   │ │
│ └─────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ 2  cookbook_ingredients        [↑] [↓] [×] │ │
│ │    Field Name: cookbook_ingredients         │ │
│ │    Display Label: [Ingredients__________]   │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ ▼ JSON Preview                                  │
│ [                                               │
│   {"field": "cookbook_cook_time", ...},         │
│   {"field": "cookbook_ingredients", ...}        │
│ ]                                               │
└─────────────────────────────────────────────────┘
```

### Usage

1. **Navigate to Collection Admin**
   ```
   http://localhost:8000/admin/archive/collection/
   ```

2. **Edit a Collection**
   - Click on a collection name
   - Set "Adapter Name" (e.g., `cookbook`)
   - The visual selector will appear for "List View Fields"

3. **Add Fields**
   - Click "+ Add Field" button
   - Enter field name (e.g., `cookbook_cook_time`)
   - Enter display label (e.g., `Cook Time`)
   - Field is added to the list

4. **Reorder Fields**
   - Use ↑ and ↓ buttons to move fields up or down
   - Order determines display order in list view

5. **Edit Labels**
   - Click in the "Display Label" input
   - Type new label
   - Changes are saved automatically to JSON

6. **Remove Fields**
   - Click × button
   - Confirm removal
   - Field is removed from configuration

7. **Preview JSON**
   - Expand "JSON Preview" section
   - See the generated JSON configuration
   - Useful for debugging or copying

## Feature 3: Field Preview

### What It Does

Allows administrators to preview how configured fields will appear in the archive list view before saving changes.

### How It Works

A new admin action "Preview field configuration" shows:
- Collection name and adapter
- List of configured fields with labels
- Sample display showing how fields will appear
- Whether using default or custom configuration

### Usage

1. **Select Collections**
   - Go to Collection admin list
   - Check boxes next to collections to preview
   - Can select multiple collections

2. **Run Preview Action**
   - Select "Preview field configuration" from Actions dropdown
   - Click "Go"

3. **View Preview**
   - See detailed preview for each selected collection
   - Shows field order, labels, and sample display
   - Indicates if using adapter defaults or custom config

### Preview Display

```
┌──────────────────────────────────────────────────┐
│ Historic American Cookbooks    [Cookbook Adapter]│
├──────────────────────────────────────────────────┤
│ ℹ️ Using adapter default fields (not customized) │
│                                                   │
│ 1  cookbook_cook_time                            │
│    Cook Time                                      │
│    Source: metadata.cook_time                     │
│                                                   │
│ 2  cookbook_ingredients                           │
│    Ingredients                                    │
│    Source: metadata.ingredients                   │
│                                                   │
│ 📄 How it will appear in list view:              │
│ ┌────────────────────────────────────────────┐   │
│ │ Sample Work Title                          │   │
│ │ Author: Sample Author                      │   │
│ │ Date: 2024                                 │   │
│ │ Cook Time: [cookbook_cook_time]            │   │
│ │ Ingredients: [cookbook_ingredients]        │   │
│ └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

## Feature 4: Bulk Operations

### What It Does

Provides three bulk actions for managing multiple collections at once:
1. **Bulk Set Adapter** - Assign the same adapter to multiple collections
2. **Bulk Copy Fields** - Copy field configuration from one collection to others
3. **Preview Fields** - Preview multiple collections at once (described above)

### Bulk Set Adapter

**Use Case:** You have 12 sci-fi collections and want to assign the `scifi` adapter to all of them.

**Steps:**
1. Select all sci-fi collections in the list
2. Choose "Set adapter for selected collections" from Actions
3. Click "Go"
4. Select adapter from dropdown (e.g., `scifi`)
5. Click "Apply"
6. All selected collections now have the adapter assigned

**Example:**
```
Selected Collections (12):
- Science Fiction - Aliens
- Science Fiction - Cyberpunk
- Science Fiction - Dystopia
...

Select Adapter: [scifi ▼]

[Apply] [Cancel]
```

### Bulk Copy Fields

**Use Case:** You've configured perfect field settings for one cookbook collection and want to apply the same settings to other cookbook collections.

**Steps:**
1. Select target collections (where you want to copy TO)
2. Choose "Copy field configuration to selected collections" from Actions
3. Click "Go"
4. Select source collection (where you want to copy FROM)
5. Click "Copy Configuration"
6. All selected collections now have the same field configuration

**Example:**
```
Target Collections (3):
- Historic American Cookbooks
- Feeding America Cookbooks
- Regional Cookbooks

Copy from: [Historic American Cookbooks ▼]

[Copy Configuration] [Cancel]
```

### Testing Bulk Operations

```python
from ppa.archive.models import Collection

# Get sci-fi collections
scifi_collections = Collection.objects.filter(name__startswith='Science Fiction')
print(f"Found {scifi_collections.count()} sci-fi collections")

# Bulk set adapter
scifi_collections.update(adapter_name='scifi')
print("✓ Adapter set for all sci-fi collections")

# Copy field configuration
source = Collection.objects.get(name='Historic American Cookbooks')
target_collections = Collection.objects.filter(adapter_name='cookbook')

for collection in target_collections:
    collection.list_view_fields = source.list_view_fields
    collection.save()

print(f"✓ Copied configuration to {target_collections.count()} collections")
```

## Implementation Details

### Files Created/Modified

**New Files:**
- `ppa/archive/widgets.py` - Visual field selector widget
- `ppa/archive/forms_admin.py` - Custom admin form
- `ppa/archive/templates/admin/collection_bulk_adapter.html` - Bulk adapter template
- `ppa/archive/templates/admin/collection_bulk_copy_fields.html` - Bulk copy template
- `ppa/archive/templates/admin/collection_preview_fields.html` - Preview template

**Modified Files:**
- `ppa/archive/models.py` - Enhanced `Collection.clean()` with validation
- `ppa/archive/admin.py` - Added bulk actions and custom form

### Database Schema

No database changes required. All features use the existing `list_view_fields` JSONField.

### Dependencies

No new dependencies required. Uses standard Django admin features.

## Best Practices

1. **Always Preview First**
   - Use the preview action before saving changes
   - Verify fields will display correctly

2. **Use Bulk Operations for Consistency**
   - Set adapters in bulk for related collections
   - Copy configurations to maintain consistency

3. **Validate Before Bulk Copy**
   - Test configuration on one collection first
   - Then copy to others once verified

4. **Document Custom Configurations**
   - Add notes in collection description explaining why custom fields were chosen
   - Helps future administrators understand decisions

5. **Regular Audits**
   - Periodically review all collections
   - Use preview to verify configurations are still appropriate

## Troubleshooting

### Visual Selector Not Appearing

**Problem:** Still seeing plain JSON textarea

**Solution:**
- Ensure adapter_name is set for the collection
- Save the collection first, then edit again
- Visual selector only appears when adapter is assigned

### Validation Errors

**Problem:** Getting validation errors when saving

**Solution:**
- Check field names have correct adapter prefix
- Verify JSON is a valid array
- Ensure all required properties (field, label) are present

### Bulk Actions Not Working

**Problem:** Bulk action doesn't appear or fails

**Solution:**
- Ensure you've selected at least one collection
- Check that you have permission to edit collections
- Verify the action is enabled in CollectionAdmin

## Future Enhancements

Potential improvements for future versions:

1. **Drag-and-Drop Reordering**
   - Visual drag-and-drop instead of up/down buttons
   - More intuitive for reordering many fields

2. **Field Library**
   - Dropdown of available fields from adapter
   - No need to type field names manually

3. **Live Preview**
   - Real-time preview in the admin form
   - See changes immediately without saving

4. **Field Templates**
   - Save common field configurations as templates
   - Quick apply to new collections

5. **Bulk Edit**
   - Edit field labels for multiple collections at once
   - Mass update operations

6. **Import/Export**
   - Export field configurations as JSON
   - Import configurations from file

---

**Last Updated**: March 11, 2026
