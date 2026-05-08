#!/bin/bash
set -e

echo "🔧 PPA Django Reuse Setup Script"
echo "================================"

# Check if services are running
echo "📡 Checking Docker services..."
if ! docker compose -f docker/docker-compose.dev.yml ps | grep -q "Up"; then
    echo "❌ Docker services not running. Starting..."
    docker compose -f docker/docker-compose.dev.yml up -d
    sleep 10
fi

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until docker compose -f docker/docker-compose.dev.yml exec -T db pg_isready -U ppa; do
    sleep 1
done

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Setup Wagtail pages
echo "📄 Setting up Wagtail pages..."
python manage.py setup_site_pages

# Create superuser if not exists
echo "👤 Creating admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️  Admin user already exists')
"

# Setup Waffle switches
echo "🎛️  Setting up feature flags..."
python manage.py shell -c "
from waffle.models import Switch
Switch.objects.update_or_create(name='enable_solr_indexing', defaults={'active': False})
Switch.objects.update_or_create(name='enable_hathi', defaults={'active': False})
Switch.objects.update_or_create(name='enable_corppa', defaults={'active': False})
print('✅ Feature flags configured')
"

# Setup Solr (optional)
if docker compose -f docker/docker-compose.dev.yml ps | grep -q "solr.*Up"; then
    echo "🔍 Setting up Solr..."
    ./setup_solr.sh || echo "⚠️  Solr setup failed (optional)"

    echo "📊 Indexing data to Solr..."
    python manage.py index --index work || echo "⚠️  Solr indexing failed (optional)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run: devbox run dev"
echo "  2. Visit: http://localhost:8000"
echo "  3. Admin: http://localhost:8000/admin (admin/admin123)"
