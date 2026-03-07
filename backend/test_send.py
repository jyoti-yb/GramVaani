#!/usr/bin/env python3
"""Test WhatsApp message sending"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

print("🔍 WhatsApp Send Message Test")
print("=" * 50)
print(f"📱 Phone Number ID: {PHONE_ID}")
print(f"📱 Your Number: +91 94908 72665")

# Test sending capability
url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test message to your own number
payload = {
    "messaging_product": "whatsapp",
    "to": "919490872665",  # Your number
    "type": "text",
    "text": {"body": "✅ Test message from Gram Vaani backend! Your WhatsApp integration is working."}
}

print("\n🧪 Testing message send to +91 94908 72665...")
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Message sent.")
        print(f"Response: {response.json()}")
        print("\n📱 Check your WhatsApp - you should receive the test message!")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("If message sent successfully, your backend is ready!")
print("Send any message to +91 94908 72665 to test AI responses.")
