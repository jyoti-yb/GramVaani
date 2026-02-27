import requests
import json

# API endpoint
API_URL = "http://localhost:8000"

# Test user credentials
test_user = {
    "email": "farmer@gramvaani.com",
    "password": "Test@123",
    "language": "te",  # Telugu
    "location": "Hyderabad, Telangana"
}

# Sign up the user
print("Creating test user...")
response = requests.post(f"{API_URL}/api/signup", json=test_user)

if response.status_code == 200:
    data = response.json()
    print("\n✅ User created successfully!")
    print("\n" + "="*50)
    print("TEST USER CREDENTIALS")
    print("="*50)
    print(f"Email:    {test_user['email']}")
    print(f"Password: {test_user['password']}")
    print(f"Language: Telugu (te)")
    print(f"Location: {test_user['location']}")
    print("="*50)
    print(f"\nAccess Token: {data['access_token'][:50]}...")
    print("\nYou can now login with these credentials!")
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.json())
