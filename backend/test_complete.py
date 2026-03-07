#!/usr/bin/env python3
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 TESTING GRAM VAANI API")
print("=" * 60)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Database: {response.json().get('database')}")
        print(f"   Users: {response.json().get('users')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Health check error: {e}")

# Test 2: Login with existing user
print("\n2️⃣ Testing Login...")
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

try:
    response = requests.post(f"{API_URL}/api/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        token = None
except Exception as e:
    print(f"❌ Login error: {e}")
    token = None

# Test 3: Get user profile
if token:
    print("\n3️⃣ Testing User Profile...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print("✅ Profile retrieved")
            print(f"   Email: {user['email']}")
            print(f"   Language: {user['language']}")
            print(f"   Location: {user['location']}")
        else:
            print(f"❌ Profile failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile error: {e}")

# Test 4: Test Polly TTS
if token:
    print("\n4️⃣ Testing Polly TTS (Hindi)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        tts_data = {
            "text": "नमस्ते, मैं ग्राम वाणी हूं। आपकी कैसे मदद कर सकता हूं?",
            "language": "hi"
        }
        response = requests.post(f"{API_URL}/process-text", json=tts_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Polly TTS successful")
            print(f"   Response: {result['response_text'][:50]}...")
            if result.get('audio_data'):
                print(f"   Audio: Generated ({len(result['audio_data'])} chars)")
            else:
                print("   ⚠️  No audio generated")
        else:
            print(f"❌ TTS failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ TTS error: {e}")

# Test 5: Test signup with new user
print("\n5️⃣ Testing Signup...")
import time
signup_data = {
    "email": f"test{int(time.time())}@test.com",
    "password": "Test@123",
    "language": "hi",
    "location": "Mumbai, Maharashtra"
}

try:
    response = requests.post(f"{API_URL}/api/signup", json=signup_data)
    if response.status_code == 200:
        print("✅ Signup successful")
        print(f"   Email: {signup_data['email']}")
    else:
        print(f"❌ Signup failed: {response.status_code}")
        print(f"   Error: {response.json()}")
except Exception as e:
    print(f"❌ Signup error: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)
print("\n📝 LOGIN CREDENTIALS:")
print("   Email: test@example.com")
print("   Password: password123")
print("=" * 60)
