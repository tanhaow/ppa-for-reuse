#!/bin/bash

# 🧪 Admin Metadata Display - Verification Script
# This script verifies that the metadata display fix is working correctly

echo "🧪 Admin Metadata Display - Verification Test"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Test 1: Check if admin.py has metadata_display method
echo "Test 1: Checking admin.py for metadata_display method..."
if grep -q "def metadata_display" ppa/archive/admin.py; then
    echo -e "${GREEN}✅ metadata_display method found${NC}"
else
    echo -e "${RED}❌ metadata_display method NOT found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test 2: Check if metadata_display is in fields
echo "Test 2: Checking if metadata_display is in admin fields..."
if grep -q '"metadata_display"' ppa/archive/admin.py; then
    echo -e "${GREEN}✅ metadata_display in fields${NC}"
else
    echo -e "${RED}❌ metadata_display NOT in fields${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test 3: Check if metadata_display is in readonly_fields
echo "Test 3: Checking if metadata_display is in readonly_fields..."
if grep -A 1 "readonly_fields" ppa/archive/admin.py | grep -q "metadata_display"; then
    echo -e "${GREEN}✅ metadata_display in readonly_fields${NC}"
else
    echo -e "${RED}❌ metadata_display NOT in readonly_fields${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Test 4: Check if server is running
echo "Test 4: Checking if Django server is running..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${YELLOW}⚠️  Server is NOT running${NC}"
    echo "   Run: devbox run dev"
fi

# Test 5: Check if admin is accessible
echo "Test 5: Checking if admin interface is accessible..."
if curl -s http://localhost:8000/admin/ | grep -q "Django"; then
    echo -e "${GREEN}✅ Admin interface accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Admin interface not accessible${NC}"
    echo "   Make sure server is running"
fi

# Test 6: Check if there's data in database
echo "Test 6: Checking if there's data in database..."
DATA_COUNT=$(python manage.py shell -c "from ppa.archive.models import DigitizedWork; print(DigitizedWork.objects.count())" 2>/dev/null || echo "0")
if [ "$DATA_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Database has $DATA_COUNT records${NC}"
else
    echo -e "${YELLOW}⚠️  No data in database${NC}"
    echo "   Import some data first"
fi

# Test 7: Check if documentation is updated
echo "Test 7: Checking if documentation is updated..."
DOCS_UPDATED=0
if [ -f "ADMIN_METADATA_FIX.md" ]; then
    DOCS_UPDATED=$((DOCS_UPDATED + 1))
fi
if [ -f "ADMIN_METADATA_BEFORE_AFTER.md" ]; then
    DOCS_UPDATED=$((DOCS_UPDATED + 1))
fi
if [ -f "DEMO_READY_SUMMARY.md" ]; then
    DOCS_UPDATED=$((DOCS_UPDATED + 1))
fi
if [ -f "修复完成总结.md" ]; then
    DOCS_UPDATED=$((DOCS_UPDATED + 1))
fi

if [ $DOCS_UPDATED -eq 4 ]; then
    echo -e "${GREEN}✅ All documentation files created${NC}"
else
    echo -e "${YELLOW}⚠️  Some documentation files missing ($DOCS_UPDATED/4)${NC}"
fi

echo ""
echo "=============================================="

# Summary
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart server: devbox run dev"
    echo "2. Open admin: http://localhost:8000/admin/archive/digitizedwork/"
    echo "3. Click on a record and scroll to 'Metadata (JSON)'"
    echo "4. Verify formatted JSON display"
else
    echo -e "${RED}❌ $ERRORS test(s) failed${NC}"
    echo ""
    echo "Please check the errors above and fix them."
fi

echo ""
echo "📚 Documentation:"
echo "  - Technical details: ADMIN_METADATA_FIX.md"
echo "  - Before/After comparison: ADMIN_METADATA_BEFORE_AFTER.md"
echo "  - Demo preparation: DEMO_READY_SUMMARY.md"
echo "  - Chinese summary: 修复完成总结.md"
echo ""
echo "🎬 Demo materials:"
echo "  - Practical script: ADAPTER_DEMO_PRACTICAL_SCRIPT.md"
echo "  - Cheat sheet: ADAPTER_DEMO_CHEAT_SHEET.md"
echo "  - 1-page card: ADAPTER_DEMO_1PAGE_CARD.md"
echo ""
