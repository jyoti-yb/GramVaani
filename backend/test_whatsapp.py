#!/usr/bin/env python3
"""
WhatsApp Cloud API Integration Test Script
Tests webhook verification and message handling
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

def test_webhook_verification():
    """Test GET /webhook verification endpoint"""
    print("\n🔍 Testing Webhook Verification...")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "test_challenge_12345"
    }
    
    response = requests.get(f"{BASE_URL}/webhook", params=params)
    
    if response.status_code == 200 and response.text == "test_challenge_12345":
        print("✅ Webhook verification PASSED")
        return True
    else:
        print(f"❌ Webhook verification FAILED: {response.status_code} - {response.text}")
        return False

def test_webhook_verification_fail():
    """Test webhook verification with wrong token"""
    print("\n🔍 Testing Webhook Verification (Wrong Token)...")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong_token",
        "hub.challenge": "test_challenge_12345"
    }
    
    response = requests.get(f"{BASE_URL}/webhook", params=params)
    
    if response.status_code == 403:
        print("✅ Webhook verification rejection PASSED")
        return True
    else:
        print(f"❌ Should reject wrong token: {response.status_code}")
        return False

def test_webhook_message():
    """Test POST /webhook message handling"""
    print("\n📨 Testing Webhook Message Handler...")
    
    # Sample WhatsApp webhook payload
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "919876543210",
                        "phone_number_id": "933004536573375"
                    },
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": "919032611376"
                    }],
                    "messages": [{
                        "from": "919032611376",
                        "id": "wamid.test123",
                        "timestamp": "1234567890",
                        "text": {"body": "What is the weather today?"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    response = requests.post(f"{BASE_URL}/webhook", json=payload)
    
    if response.status_code == 200:
        print("✅ Webhook message handler PASSED")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ Webhook message handler FAILED: {response.status_code}")
        return False

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check PASSED: {data}")
        return True
    else:
        print(f"❌ Health check FAILED: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🌾 Gram Vaani - WhatsApp Cloud API Integration Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Backend server not running at {BASE_URL}")
        print("   Start server: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Webhook Verification", test_webhook_verification()))
    results.append(("Webhook Rejection", test_webhook_verification_fail()))
    results.append(("Message Handler", test_webhook_message()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WhatsApp integration is ready.")
        print("\n📋 Next Steps:")
        print("   1. Expose backend via ngrok: ngrok http 8000")
        print("   2. Copy ngrok URL (e.g., https://abc123.ngrok.io)")
        print("   3. Configure in Meta App Dashboard:")
        print(f"      - Webhook URL: https://YOUR_NGROK_URL/webhook")
        print(f"      - Verify Token: {VERIFY_TOKEN}")
        print("   4. Subscribe to 'messages' webhook field")
        print("   5. Test by sending message to your WhatsApp Business number")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
