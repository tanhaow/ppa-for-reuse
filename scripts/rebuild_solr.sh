#!/bin/bash

# 🚨 Quick Recovery Script - Rebuild Solr Index
# Use this script if the search page shows no results

echo "🚨 Solr Index Quick Recovery"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Check database
echo "Step 1: Checking database..."
DB_COUNT=$(source .venv/bin/activate && python manage.py shell -c "from ppa.archive.models import DigitizedWork; print(DigitizedWork.objects.count())" 2>/dev/null | tail -1)

if [ -z "$DB_COUNT" ] || [ "$DB_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ Database is empty or inaccessible${NC}"
    echo "Cannot recover - no data to index"
    exit 1
else
    echo -e "${GREEN}✅ Database has $DB_COUNT records${NC}"
fi

# Step 2: Check Solr index
echo ""
echo "Step 2: Checking Solr index..."
SOLR_COUNT=$(curl -s "http://localhost:8983/solr/ppa/select?q=*:*&rows=0" 2>/dev/null | grep -o '"numFound":[0-9]*' | cut -d: -f2)

if [ -z "$SOLR_COUNT" ]; then
    echo -e "${RED}❌ Cannot connect to Solr${NC}"
    echo "Make sure Solr is running: docker compose -f docker/docker-compose.dev.yml up -d"
    exit 1
fi

echo -e "${YELLOW}Current Solr index: $SOLR_COUNT records${NC}"

if [ "$SOLR_COUNT" -lt 100 ]; then
    echo -e "${RED}⚠️  Solr index is empty or very low!${NC}"
    echo "Rebuilding index..."
else
    echo -e "${GREEN}Solr index looks OK${NC}"
    read -p "Rebuild anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi
fi

# Step 3: Rebuild Solr index
echo ""
echo "Step 3: Rebuilding Solr index..."
echo "This may take a few seconds..."
echo ""

source .venv/bin/activate && python manage.py index -i work

# Step 4: Verify
echo ""
echo "Step 4: Verifying recovery..."
NEW_SOLR_COUNT=$(curl -s "http://localhost:8983/solr/ppa/select?q=*:*&rows=0" 2>/dev/null | grep -o '"numFound":[0-9]*' | cut -d: -f2)

echo ""
echo "=============================="
echo "Recovery Summary:"
echo "  Database: $DB_COUNT records"
echo "  Solr (before): $SOLR_COUNT records"
echo "  Solr (after): $NEW_SOLR_COUNT records"
echo ""

if [ "$NEW_SOLR_COUNT" -gt 1000 ]; then
    echo -e "${GREEN}✅ Recovery successful!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart server if needed: devbox run dev"
    echo "2. Visit: http://localhost:8000/archive/"
    echo "3. Verify search results appear"
else
    echo -e "${RED}❌ Recovery may have failed${NC}"
    echo "Solr index still has very few records"
    echo ""
    echo "Try:"
    echo "1. Check Solr is running: docker compose -f docker/docker-compose.dev.yml ps"
    echo "2. Check logs: docker compose -f docker/docker-compose.dev.yml logs solr"
    echo "3. Restart Solr: docker compose -f docker/docker-compose.dev.yml restart solr"
fi

echo ""
