#!/usr/bin/env python3
"""Find correct Phone Number ID"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
BUSINESS_ACCOUNT_ID = "1609081963751287"  # From your message

print("🔍 Finding Correct Phone Number ID")
print("=" * 50)

# Get phone numbers from business account
url = f"https://graph.facebook.com/v22.0/{BUSINESS_ACCOUNT_ID}/phone_numbers"
headers = {"Authorization": f"Bearer {TOKEN}"}

print(f"\n📱 Business Account ID: {BUSINESS_ACCOUNT_ID}")
print(f"🔑 Access Token: {TOKEN[:20]}...{TOKEN[-10:]}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        phone_numbers = data.get('data', [])
        
        if phone_numbers:
            print(f"\n✅ Found {len(phone_numbers)} phone number(s):\n")
            for phone in phone_numbers:
                print(f"📱 Display Phone: {phone.get('display_phone_number')}")
                print(f"   Phone Number ID: {phone.get('id')}")
                print(f"   Verified Name: {phone.get('verified_name')}")
                print(f"   Quality Rating: {phone.get('quality_rating')}")
                print()
                
            print("=" * 50)
            print("✅ Update your .env file with the correct Phone Number ID above")
        else:
            print("❌ No phone numbers found in this business account")
    else:
        print(f"❌ Error: {response.text}")
        print("\n💡 Possible issues:")
        print("   1. Access token doesn't have permission for this business account")
        print("   2. Business Account ID is incorrect")
        print("   3. Token needs 'whatsapp_business_management' permission")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📋 To fix:")
print("1. Go to Meta Dashboard > WhatsApp > API Setup")
print("2. Look for 'Phone number ID' under your phone number")
print("3. Copy that exact ID")
print("4. Update WHATSAPP_PHONE_NUMBER_ID in .env")
