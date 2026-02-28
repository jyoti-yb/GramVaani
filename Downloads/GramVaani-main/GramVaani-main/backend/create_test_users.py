import requests
import json

# API endpoint
API_URL = "http://localhost:8000"

# Multiple test users to try
test_users = [
    {
        "email": "telugu.farmer@test.com",
        "password": "Telugu@123",
        "language": "te",
        "location": "Hyderabad, Telangana"
    },
    {
        "email": "hindi.farmer@test.com",
        "password": "Hindi@123",
        "language": "hi",
        "location": "Delhi, India"
    },
    {
        "email": "tamil.farmer@test.com",
        "password": "Tamil@123",
        "language": "ta",
        "location": "Chennai, Tamil Nadu"
    }
]

print("Creating test users...\n")

for user in test_users:
    response = requests.post(f"{API_URL}/api/signup", json=user)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ User created successfully!")
        print("="*60)
        print(f"Email:    {user['email']}")
        print(f"Password: {user['password']}")
        print(f"Language: {user['language']}")
        print(f"Location: {user['location']}")
        print("="*60)
        print()
        break
    else:
        print(f"❌ Failed to create {user['email']}: {response.status_code}")
        if response.status_code == 400:
            print("   (User already exists, trying next...)\n")
        else:
            print(f"   Error: {response.json()}\n")
