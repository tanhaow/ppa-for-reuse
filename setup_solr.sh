#!/bin/bash
# Setup Solr for PPA Django Reuse (homebrew Solr, no Docker)

set -e

SOLR_URL="http://localhost:8983/solr"
SOLR_BIN="/opt/homebrew/bin/solr"

echo "🚀 Setting up Solr for PPA Django Reuse"
echo "========================================"
echo ""

# Start Solr if not running
if ! curl -s -o /dev/null -w "%{http_code}" "$SOLR_URL/" 2>/dev/null | grep -q "200"; then
    echo "📦 Starting Solr..."
    SOLR_MODULES=analysis-extras "$SOLR_BIN" start -p 8983
    echo "⏳ Waiting for Solr to be ready..."
    for i in $(seq 1 30); do
        if curl -s -o /dev/null -w "%{http_code}" "$SOLR_URL/" 2>/dev/null | grep -q "200"; then
            break
        fi
        sleep 1
    done
else
    echo "✅ Solr already running"
fi

# Verify Solr is up
if ! curl -s -o /dev/null -w "%{http_code}" "$SOLR_URL/" 2>/dev/null | grep -q "200"; then
    echo "❌ Solr failed to start"
    exit 1
fi
echo "✅ Solr is running on $SOLR_URL"
echo ""

# Create ppa core if it doesn't exist
CORES=$(curl -s "$SOLR_URL/admin/cores?action=STATUS&wt=json" | python3 -c "import sys,json; print(','.join(json.load(sys.stdin)['status'].keys()))" 2>/dev/null)
if echo "$CORES" | grep -q "ppa"; then
    echo "✅ Core 'ppa' already exists"
else
    echo "📋 Creating 'ppa' core..."
    SOLR_MODULES=analysis-extras "$SOLR_BIN" create -c ppa
    echo "✅ Core 'ppa' created"
fi
echo ""

# Helper: add field, ignore if already exists
add_field() {
    curl -s -X POST -H 'Content-type:application/json' \
        --data-binary "$1" "$SOLR_URL/ppa/schema" > /dev/null 2>&1 || true
}

echo "📋 Configuring Solr schema fields..."

add_field '{"add-field":{"name":"source_id","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"title","type":"text_general","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"author","type":"text_general","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"pub_date","type":"plongs","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"item_type","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"collections","type":"string","stored":true,"indexed":true,"multiValued":true}}'
add_field '{"add-field":{"name":"collections_str","type":"string","stored":true,"indexed":true,"multiValued":true}}'
add_field '{"add-field":{"name":"cluster_id_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"group_id_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"source_t","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"source_url","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"pub_place","type":"text_general","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"publisher","type":"text_general","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"subtitle","type":"text_general","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"enumcron","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"order","type":"plongs","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"label","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"image_id_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"first_page_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"last_page_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"work_type_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"book_journal_s","type":"string","stored":true,"indexed":true,"multiValued":false}}'
add_field '{"add-field":{"name":"sort_title","type":"string","stored":true,"indexed":true,"multiValued":false}}'

echo "✅ Fields configured"
echo ""

echo "📋 Configuring copyFields..."
add_field '{"add-copy-field":{"source":"collections","dest":"collections_str"}}'
add_field '{"add-copy-field":{"source":"title","dest":"sort_title"}}'
echo "✅ copyFields configured"
echo ""

echo "📊 Indexing all works to Solr..."
.venv/bin/python manage.py index --index work
echo ""

echo "🎉 Solr setup complete!"
echo ""
echo "  Solr Admin: http://localhost:8983/solr/"
echo "  App:        http://localhost:8000/archive/"
echo ""
