#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING GRAM VAANI API")
print("=" * 60)

# 1. Test Login
print("\n1. Testing Login...")
login_response = requests.post(f"{BASE_URL}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})
print(f"   Status: {login_response.status_code}")

if login_response.status_code != 200:
    print(f"   ✗ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   ✓ Login successful")

# 2. Test Get User
print("\n2. Testing Get User...")
me_response = requests.get(f"{BASE_URL}/api/me", headers=headers)
print(f"   Status: {me_response.status_code}")
if me_response.status_code == 200:
    user = me_response.json()
    print(f"   ✓ User: {user['email']}, Location: {user['location']}")
else:
    print(f"   ✗ Failed: {me_response.text}")

# 3. Test Weather
print("\n3. Testing Weather (My Location)...")
weather_response = requests.post(f"{BASE_URL}/api/weather", 
    json={"city": "current", "language": "en"}, 
    headers=headers
)
print(f"   Status: {weather_response.status_code}")
if weather_response.status_code == 200:
    print(f"   ✓ {weather_response.json()['text']}")
else:
    print(f"   ✗ Failed: {weather_response.text}")

# 4. Test Weather (Specific City)
print("\n4. Testing Weather (Mumbai)...")
weather_response = requests.post(f"{BASE_URL}/api/weather", 
    json={"city": "Mumbai", "language": "en"}, 
    headers=headers
)
print(f"   Status: {weather_response.status_code}")
if weather_response.status_code == 200:
    print(f"   ✓ {weather_response.json()['text']}")
else:
    print(f"   ✗ Failed: {weather_response.text}")

# 5. Test Crop Prices
print("\n5. Testing Crop Prices...")
crop_response = requests.post(f"{BASE_URL}/api/crop-prices", 
    json={"crop": "wheat", "language": "en"}, 
    headers=headers
)
print(f"   Status: {crop_response.status_code}")
if crop_response.status_code == 200:
    print(f"   ✓ {crop_response.json()['text']}")
else:
    print(f"   ✗ Failed: {crop_response.text}")

# 6. Test Government Schemes
print("\n6. Testing Government Schemes...")
schemes_response = requests.post(f"{BASE_URL}/api/gov-schemes", 
    json={"topic": "irrigation", "language": "en"}, 
    headers=headers
)
print(f"   Status: {schemes_response.status_code}")
if schemes_response.status_code == 200:
    text = schemes_response.json()['text']
    print(f"   ✓ {text[:100]}...")
else:
    print(f"   ✗ Failed: {schemes_response.text}")

# 7. Test Process Text
print("\n7. Testing Process Text...")
text_response = requests.post(f"{BASE_URL}/process-text", 
    json={"text": "What crops should I plant in monsoon?", "language": "en"}, 
    headers=headers
)
print(f"   Status: {text_response.status_code}")
if text_response.status_code == 200:
    text = text_response.json()['response_text']
    print(f"   ✓ {text[:100]}...")
else:
    print(f"   ✗ Failed: {text_response.text}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
