#!/bin/bash
# Test the server can start and handle requests without errors

cd /Users/ht8933/Documents/Documents\ -\ cdh-m5945fhwr7/dev/ppa-django-reuse

echo "🧪 Testing Server Startup and Archive Page"
echo "==========================================="
echo ""

# Start server in background
echo "Starting development server..."
venv/bin/python manage.py runserver > /tmp/django_server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Server failed to start"
    cat /tmp/django_server.log
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"
echo ""

# Test homepage
echo "Testing homepage..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Homepage accessible (HTTP $HTTP_CODE)"
else
    echo "❌ Homepage failed (HTTP $HTTP_CODE)"
fi

# Test archive page
echo "Testing archive page..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/archive/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Archive page accessible (HTTP $HTTP_CODE)"
else
    echo "❌ Archive page failed (HTTP $HTTP_CODE)"
    echo ""
    echo "Server log:"
    tail -20 /tmp/django_server.log
fi

# Test admin page
echo "Testing admin page..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Admin page accessible (HTTP $HTTP_CODE)"
else
    echo "❌ Admin page failed (HTTP $HTTP_CODE)"
fi

# Stop server
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "==========================================="
echo "✅ Server tests complete!"
echo ""
echo "To run the server manually:"
echo "  venv/bin/python manage.py runserver"
