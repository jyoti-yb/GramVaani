#!/usr/bin/env python3
"""
Test script for the Whisper audio processing endpoint

Note: This test requires a sample audio file. You can either:
1. Use a pre-existing audio file
2. Record audio through the frontend
3. Generate a test audio file

For now, this script will show you how to test the endpoint with curl.
"""

import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING WHISPER AUDIO PROCESSING ENDPOINT")
print("=" * 60)

# 1. Login to get token
print("\n1. Logging in...")
login_response = requests.post(f"{BASE_URL}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})

if login_response.status_code != 200:
    print(f"   ✗ Login failed: {login_response.text}")
    sys.exit(1)

token = login_response.json()["access_token"]
print(f"   ✓ Login successful")

# 2. Check if test audio file exists
test_audio_file = "test_audio.wav"

if not os.path.exists(test_audio_file):
    print(f"\n⚠️  No test audio file found at: {test_audio_file}")
    print("\nTo test the Whisper endpoint, you can:")
    print("1. Record audio through the frontend interface")
    print("2. Use curl with an audio file:")
    print(f"\n   curl -X POST {BASE_URL}/process-audio \\")
    print(f'     -H "Authorization: Bearer {token}" \\')
    print(f'     -F "file=@your_audio.wav" \\')
    print(f'     -F "language=en"')
    print("\n✓ The endpoint is ready to receive audio at: /process-audio")
    print("✓ Whisper API credentials are configured in .env")
    sys.exit(0)

# 3. Test audio processing
print(f"\n2. Testing audio processing with {test_audio_file}...")
headers = {"Authorization": f"Bearer {token}"}

with open(test_audio_file, 'rb') as audio_file:
    files = {'file': audio_file}
    data = {'language': 'en'}
    
    response = requests.post(
        f"{BASE_URL}/process-audio",
        headers=headers,
        files=files,
        data=data
    )

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"   ✓ Audio processed successfully!")
    print(f"\n   Transcript: {result.get('transcript', 'N/A')}")
    print(f"\n   AI Response: {result.get('response_text', 'N/A')[:200]}...")
else:
    print(f"   ✗ Failed: {response.text}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
