# Waffle Switches Quick Reference

This guide explains what each switch controls and when to use it.

## 🎛️ All Switches Overview

| Switch | Default | Category | Impact |
|--------|---------|----------|--------|
| `enable_solr_indexing` | ✅ ON | Search | High |
| `enable_analytics` | ✅ ON | Tracking | Low |
| `enable_import_export` | ✅ ON | Admin | Medium |
| `enable_wagtail_pages` | ✅ ON | CMS | High |
| `enable_hathi` | ❌ OFF | Integration | Medium |
| `enable_corppa` | ❌ OFF | NLP | Low |

## 📊 Detailed Explanations

### 1. `enable_solr_indexing` (Search Engine)

**What it controls:**
- Solr search indexing
- Full-text search functionality
- Search results
- Faceted search (filters)

**When ON:**
- ✅ Content is indexed to Solr
- ✅ Search works normally
- ✅ Users can search and filter

**When OFF:**
- ❌ No indexing happens
- ❌ Search returns no results
- ⚠️ Existing index remains (not deleted)

**When to turn OFF:**
- During bulk data imports (for performance)
- When debugging search issues
- When Solr is down for maintenance

**Related URLs:**
- Search: http://localhost:8000/archive/
- Solr Admin: http://localhost:8983/solr/

---

### 2. `enable_analytics` (Tracking)

**What it controls:**
- Google Analytics tracking
- Plausible Analytics tracking
- User behavior tracking
- Page view statistics

**When ON:**
- ✅ Analytics scripts load
- ✅ User visits are tracked
- ✅ Statistics are collected

**When OFF:**
- ❌ No analytics scripts
- ❌ No tracking
- ✅ Better privacy
- ✅ Faster page load

**When to turn OFF:**
- Development environment
- Testing environment
- Privacy compliance requirements
- Performance testing

**Configuration:**
```python
# In local_settings.py
GTAGS_ANALYTICS_ID = 'UA-XXXXXXX-X'  # Google Analytics
PLAUSIBLE_ANALYTICS_SCRIPT = "https://plausible.io/js/script.js"  # Plausible
```

---

### 3. `enable_import_export` (Admin Tools)

**What it controls:**
- Import/Export buttons in Django Admin
- Data export functionality
- Bulk data operations

**When ON:**
- ✅ Import/Export buttons visible
- ✅ Can export data to CSV/Excel
- ✅ Can import data from files

**When OFF:**
- ❌ Import/Export buttons hidden
- ❌ Cannot export data
- ✅ Prevents accidental data leaks

**When to turn OFF:**
- Production environment (security)
- When you want to prevent data exports
- Compliance requirements

**Related URLs:**
- Admin: http://localhost:8000/admin/archive/digitizedwork/

---

### 4. `enable_wagtail_pages` (CMS)

**What it controls:**
- Wagtail CMS editorial pages
- Content management functionality
- Page creation and editing

**When ON:**
- ✅ Wagtail pages accessible
- ✅ Can edit content
- ✅ CMS features work

**When OFF:**
- ❌ Wagtail pages not accessible
- ❌ Cannot edit content
- ✅ Archive features still work

**When to turn OFF:**
- If you only need archive functionality
- To simplify the system
- If you don't need CMS features

**Related URLs:**
- Wagtail Admin: http://localhost:8000/cms/
- Pages: http://localhost:8000/ (various editorial pages)

**Current Status:**
- 27 pages configured
- Editorial section active
- Multiple article pages

---

### 5. `enable_hathi` (HathiTrust Integration)

**What it controls:**
- HathiTrust API access
- HathiTrust data import
- HathiTrust-specific features

**When ON:**
- ✅ Can import HathiTrust data
- ✅ HathiTrust commands work
- ✅ API access enabled

**When OFF:**
- ❌ Cannot import HathiTrust data
- ❌ HathiTrust commands disabled
- ✅ Other features unaffected

**When to turn ON:**
- If you have HathiTrust data access
- If you need to import HathiTrust books
- If using HathiTrust API

**Requirements:**
- HathiTrust API credentials
- HATHI_DATA path configured
- HathiTrust rsync access

**Configuration:**
```python
# In local_settings.py
HATHI_DATA = '/path/to/hathi/data'
```

---

### 6. `enable_corppa` (NLP Features)

**What it controls:**
- CorpPA (Corpus PPA) features
- NLP utilities
- Poetry detection
- Corpus analysis

**When ON:**
- ✅ CorpPA features available
- ✅ NLP utilities work
- ✅ Poetry detection enabled

**When OFF:**
- ❌ CorpPA features disabled
- ❌ NLP utilities unavailable
- ✅ Core features unaffected

**When to turn ON:**
- If corppa package is installed
- If you need NLP features
- If doing corpus analysis

**Requirements:**
- corppa package installed
- Additional dependencies

**Installation:**
```bash
pip install -r requirements.txt  # includes corppa
```

---

## 🎯 Common Scenarios

### Scenario 1: Development Environment

```
✅ enable_solr_indexing    (for testing search)
❌ enable_analytics        (no tracking needed)
✅ enable_import_export    (for data management)
✅ enable_wagtail_pages    (for content editing)
❌ enable_hathi           (unless testing HathiTrust)
❌ enable_corppa          (unless testing NLP)
```

### Scenario 2: Production Environment

```
✅ enable_solr_indexing    (search is critical)
✅ enable_analytics        (track usage)
❌ enable_import_export    (security)
✅ enable_wagtail_pages    (content management)
✅ enable_hathi           (if using HathiTrust)
❌ enable_corppa          (unless needed)
```

### Scenario 3: Bulk Data Import

```
❌ enable_solr_indexing    (disable for performance)
❌ enable_analytics        (not needed)
✅ enable_import_export    (for importing)
✅ enable_wagtail_pages    (keep CMS working)
❌ enable_hathi           (unless importing HathiTrust)
❌ enable_corppa          (not needed)
```

### Scenario 4: Archive-Only Mode

```
✅ enable_solr_indexing    (search needed)
❌ enable_analytics        (optional)
❌ enable_import_export    (not needed)
❌ enable_wagtail_pages    (no CMS needed)
❌ enable_hathi           (not needed)
❌ enable_corppa          (not needed)
```

---

## 🔄 How to Change Switches

### Via Django Admin

1. Go to: http://localhost:8000/admin/waffle/switch/
2. Click on the switch you want to change
3. Check/uncheck "Active"
4. Click "Save"
5. Changes take effect immediately (no restart needed)

### Via Django Shell

```python
from waffle.models import Switch

# Turn ON a switch
switch = Switch.objects.get(name='enable_analytics')
switch.active = True
switch.save()

# Turn OFF a switch
switch = Switch.objects.get(name='enable_analytics')
switch.active = False
switch.save()
```

### Via Management Command

```bash
# Check current status
.venv/bin/python manage.py shell -c "
from waffle.models import Switch
for s in Switch.objects.all():
    print(f'{s.name}: {\"ON\" if s.active else \"OFF\"}')"
```

---

## ⚠️ Important Notes

### Dependencies Between Switches

Some switches depend on others:

- `enable_wagtail_pages` doesn't affect `enable_solr_indexing`
- `enable_analytics` is independent of all others
- `enable_hathi` requires proper configuration even when ON
- `enable_corppa` requires the corppa package installed

### Performance Impact

| Switch | Performance Impact |
|--------|-------------------|
| `enable_solr_indexing` | High (indexing is CPU intensive) |
| `enable_analytics` | Low (just loads a script) |
| `enable_import_export` | None (only affects admin UI) |
| `enable_wagtail_pages` | Low (only when accessing CMS) |
| `enable_hathi` | Medium (when importing data) |
| `enable_corppa` | Medium (NLP is CPU intensive) |

### Security Considerations

- `enable_import_export`: Turn OFF in production to prevent data leaks
- `enable_analytics`: Consider privacy laws (GDPR, CCPA)
- `enable_hathi`: Requires proper API credentials
- `enable_wagtail_pages`: Ensure proper user permissions

---

## 📚 See Also

- [Feature Switches Documentation](feature-switches.md)
- [CLI Commands Reference](cli-commands.md)
- [Deployment Guide](../operations/deployment.md)
- [Wagtail Documentation](https://docs.wagtail.org/)
- [Django Waffle Documentation](https://waffle.readthedocs.io/)
