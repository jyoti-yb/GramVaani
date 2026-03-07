#!/bin/bash

echo "🚀 Starting Gram Vaani Backend Server..."
cd backend

# Start server in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Run tests
echo ""
echo "🧪 Running API tests..."
python test_all_endpoints.py

# Keep server running
echo ""
echo "✅ Server is running on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for Ctrl+C
trap "kill $SERVER_PID; exit" INT
wait $SERVER_PID
