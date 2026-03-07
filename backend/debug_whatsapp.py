#!/usr/bin/env python3
"""Quick debug script for WhatsApp issues"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

print("🔍 WhatsApp Configuration Debug")
print("=" * 50)

# Check credentials
print(f"\n📱 Phone Number ID: {PHONE_ID}")
print(f"🔑 Access Token: {TOKEN[:20]}...{TOKEN[-10:] if TOKEN else 'MISSING'}")

# Test API access
print("\n🧪 Testing WhatsApp API access...")
url = f"https://graph.facebook.com/v22.0/{PHONE_ID}"
headers = {"Authorization": f"Bearer {TOKEN}"}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Access OK")
        print(f"   Display Phone: {data.get('display_phone_number', 'N/A')}")
        print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
        print(f"   Quality Rating: {data.get('quality_rating', 'N/A')}")
    else:
        print(f"❌ API Error: {response.text}")
        print("\n💡 Common fixes:")
        print("   1. Get new WHATSAPP_PHONE_NUMBER_ID from Meta Dashboard")
        print("   2. Generate new WHATSAPP_ACCESS_TOKEN (old one may be expired)")
        print("   3. Ensure app is in Live mode")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")

print("\n📋 Next Steps:")
print("1. Go to: https://developers.facebook.com/apps")
print("2. Select your app > WhatsApp > API Setup")
print("3. Copy 'Phone number ID' (should match above)")
print("4. Copy 'Temporary access token' or generate permanent one")
print("5. Update .env file with new values")
print("6. Restart backend: ./start_whatsapp.sh")
