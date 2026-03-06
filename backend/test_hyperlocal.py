#!/usr/bin/env python3
"""Test hyperlocal context endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test user credentials (create a test user first)
TEST_USER = {
    "phone_number": "9999999999",
    "password": "test123",
    "language": "en",
    "location": "Bangalore, Karnataka"
}

def test_hyperlocal():
    print("🧪 Testing Hyperlocal Context API\n")
    
    # 1. Login
    print("1. Logging in...")
    response = requests.post(f"{BASE_URL}/api/login", json={
        "phone_number": TEST_USER["phone_number"],
        "password": TEST_USER["password"]
    })
    
    if response.status_code != 200:
        print("❌ Login failed. Creating test user...")
        signup_response = requests.post(f"{BASE_URL}/api/signup", json=TEST_USER)
        if signup_response.status_code == 200:
            token = signup_response.json()["access_token"]
            print("✅ Test user created")
        else:
            print(f"❌ Signup failed: {signup_response.text}")
            return
    else:
        token = response.json()["access_token"]
        print("✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get hyperlocal context
    print("\n2. Fetching hyperlocal context...")
    response = requests.get(f"{BASE_URL}/api/hyperlocal-context", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Hyperlocal context:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
    
    # 3. Get success stories
    print("\n3. Fetching success stories...")
    response = requests.get(f"{BASE_URL}/api/success-stories?limit=5", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} success stories")
        for story in data['stories']:
            print(f"   - {story['farmer']}: {story['achievement']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 4. Report pest outbreak
    print("\n4. Reporting pest outbreak...")
    response = requests.post(
        f"{BASE_URL}/api/report-pest-outbreak",
        headers=headers,
        params={
            "pest_name": "Fall Armyworm",
            "crop": "Maize",
            "severity": "high"
        }
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ Pest outbreak reported:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_hyperlocal()
