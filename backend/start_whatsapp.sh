#!/bin/bash
# WhatsApp Cloud API - Quick Start Script
# Run this to start your WhatsApp-enabled backend

echo "🌾 Gram Vaani - WhatsApp Cloud API Quick Start"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found"
    echo "   Copy .env.example to .env and configure"
    exit 1
fi

# Check required environment variables
echo "🔍 Checking environment variables..."
source .env

if [ -z "$WHATSAPP_ACCESS_TOKEN" ]; then
    echo "❌ WHATSAPP_ACCESS_TOKEN not set"
    exit 1
fi

if [ -z "$WHATSAPP_PHONE_NUMBER_ID" ]; then
    echo "❌ WHATSAPP_PHONE_NUMBER_ID not set"
    exit 1
fi

if [ -z "$WHATSAPP_VERIFY_TOKEN" ]; then
    echo "❌ WHATSAPP_VERIFY_TOKEN not set"
    exit 1
fi

echo "✅ Environment variables configured"
echo ""

# Check if Python dependencies are installed
echo "🔍 Checking Python dependencies..."
python3 -c "import fastapi, uvicorn, boto3, pymongo" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing dependencies..."
    pip install -r requirements.txt
fi
echo "✅ Dependencies installed"
echo ""

# Start the server
echo "🚀 Starting FastAPI backend..."
echo "   URL: http://localhost:8000"
echo "   Webhook: http://localhost:8000/webhook"
echo ""
echo "📋 Next Steps:"
echo "   1. Open new terminal and run: ngrok http 8000"
echo "   2. Copy ngrok URL (e.g., https://abc123.ngrok.io)"
echo "   3. Configure in Meta App Dashboard:"
echo "      - Webhook URL: https://YOUR_NGROK_URL/webhook"
echo "      - Verify Token: $WHATSAPP_VERIFY_TOKEN"
echo "   4. Test by sending WhatsApp message"
echo ""
echo "Press Ctrl+C to stop server"
echo "=============================================="
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
