# Feature Switches

PPA Django Reuse uses [Django Waffle](https://waffle.readthedocs.io/) for feature toggles. This allows you to enable or disable features without code changes or server restarts.

## Available Switches

All switches can be managed in the Django admin interface at `/admin/waffle/switch/`.

### Core Features

#### `enable_solr_indexing`
- **Default**: Active
- **Purpose**: Controls Solr search indexing
- **Impact**: When disabled, no content will be indexed to Solr
- **Use case**: Disable during bulk imports to improve performance

#### `enable_hathi`
- **Default**: Inactive
- **Purpose**: Controls HathiTrust integration features
- **Impact**: Enables/disables HathiTrust import commands and API access
- **Use case**: Enable only if you have HathiTrust data access

#### `enable_corppa`
- **Default**: Inactive
- **Purpose**: Controls CorpPA (Corpus PPA) NLP features
- **Impact**: Enables/disables corpus analysis and NLP utilities
- **Use case**: Enable only if corppa package is installed

### User Interface Features

#### `enable_analytics`
- **Default**: Active
- **Purpose**: Controls analytics tracking (Google Analytics, Plausible)
- **Impact**: When disabled, no analytics scripts are loaded
- **Use case**: Disable for development/testing or privacy compliance

#### `enable_wagtail_pages`
- **Default**: Active
- **Purpose**: Controls Wagtail CMS editorial pages
- **Impact**: When disabled, editorial pages are not accessible
- **Use case**: Disable if you don't need CMS functionality

### Admin Features

#### `enable_import_export`
- **Default**: Active
- **Purpose**: Controls data import/export functionality in admin
- **Impact**: Shows/hides import/export buttons in admin interface
- **Use case**: Disable to prevent accidental data exports in production

## Usage in Code

### Checking a Switch

```python
from ppa.flags import is_flag_enabled

# Simple check
if is_flag_enabled("ENABLE_SOLR_INDEXING"):
    index_to_solr(work)

# With request context (for future Flag support)
if is_flag_enabled("ENABLE_ANALYTICS", request=request):
    render_analytics_script()
```

### Direct Waffle Usage

```python
from waffle import switch_is_active

if switch_is_active('enable_solr_indexing'):
    # Do something
    pass
```

## Managing Switches

### Via Django Admin

1. Navigate to `/admin/waffle/switch/`
2. Click on a switch to edit
3. Toggle the "Active" checkbox
4. Save

Changes take effect immediately without server restart.

### Via Django Shell

```python
from waffle.models import Switch

# Activate a switch
switch = Switch.objects.get(name='enable_analytics')
switch.active = True
switch.save()

# Deactivate a switch
switch = Switch.objects.get(name='enable_hathi')
switch.active = False
switch.save()

# Create a new switch
Switch.objects.create(
    name='enable_new_feature',
    active=True,
    note='Description of the feature'
)
```

## Best Practices

1. **Use descriptive names**: Start with `enable_` for consistency
2. **Add notes**: Explain what the switch controls in the admin interface
3. **Default to safe**: New switches should default to inactive for production features
4. **Document impact**: Clearly document what happens when a switch is toggled
5. **Test both states**: Ensure your code works with the switch both on and off

## Why Only Switches?

PPA uses only Switches (not Flags or Samples) because:

- **Simplicity**: Switches provide simple on/off control
- **Global scope**: Features are either enabled for everyone or no one
- **No A/B testing needed**: This is an academic/research platform, not a consumer product
- **Easier to understand**: Researchers and administrators can easily manage switches

If you need user-specific or percentage-based feature rollouts in the future, you can add Flags or Samples back by removing the unregister code in `ppa/admin.py`.

## Troubleshooting

### Switch not taking effect

1. Check the switch is actually active in admin
2. Verify the switch name matches exactly (case-sensitive)
3. Clear Django cache if caching is enabled
4. Check for typos in `is_flag_enabled()` calls

### Switch not visible in admin

1. Ensure `waffle` is in `INSTALLED_APPS`
2. Run migrations: `python manage.py migrate`
3. Check that Flags and Samples are unregistered in `ppa/admin.py`

## See Also

- [Django Waffle Documentation](https://waffle.readthedocs.io/)
- [CLI Commands Reference](cli-commands.md)
- [Deployment Guide](../operations/deployment.md)
