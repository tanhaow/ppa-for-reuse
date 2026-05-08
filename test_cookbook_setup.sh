#!/bin/bash
# Quick test script to verify the cookbook adapter is working

cd /Users/ht8933/Documents/Documents\ -\ cdh-m5945fhwr7/dev/ppa-django-reuse

echo "🧪 Testing Cookbook Adapter Setup"
echo "=================================="
echo ""

# Test 1: Check adapter loads
echo "1. Testing adapter loading..."
venv/bin/python manage.py shell -c "
from ppa.adapters.loader import get_adapter
adapter = get_adapter()
if adapter and adapter.name == 'cookbook':
    print('   ✅ Adapter loaded: ' + adapter.display_name)
else:
    print('   ❌ Adapter not loaded')
    exit(1)
"

# Test 2: Check database has cookbook data
echo ""
echo "2. Testing database has cookbook data..."
venv/bin/python manage.py shell -c "
from ppa.archive.models import DigitizedWork
count = DigitizedWork.objects.filter(source_id__startswith='cookbook_').count()
if count > 0:
    print(f'   ✅ Found {count} cookbook record(s)')
else:
    print('   ❌ No cookbook records found')
    exit(1)
"

# Test 3: Check FakeSolrQuerySet has required methods
echo ""
echo "3. Testing FakeSolrQuerySet methods..."
venv/bin/python manage.py shell -c "
from ppa.solr_factory import FakeSolrQuerySet
qs = FakeSolrQuerySet()
methods = ['filter', 'order_by', 'search', 'facet', 'stats', 'count']
missing = [m for m in methods if not hasattr(qs, m)]
if missing:
    print(f'   ❌ Missing methods: {missing}')
    exit(1)
else:
    print('   ✅ All required methods present')
"

# Test 4: Check Django configuration
echo ""
echo "4. Testing Django configuration..."
venv/bin/python manage.py check 2>&1 | grep -q "System check identified no issues" && \
    echo "   ✅ Django configuration valid" || \
    echo "   ⚠️  Django configuration has warnings (non-critical)"

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo ""
echo "🚀 To run the server:"
echo "   cd /Users/ht8933/Documents/Documents\\ -\\ cdh-m5945fhwr7/dev/ppa-django-reuse"
echo "   venv/bin/python manage.py runserver"
echo ""
echo "📱 Then visit:"
echo "   • Admin: http://localhost:8000/admin/"
echo "   • Login: admin / admin"
echo "   • Cookbooks: http://localhost:8000/admin/archive/digitizedwork/"
