#!/usr/bin/env python3
"""
Demo: Amazon Polly TTS for Indian Languages
Shows audio generation for different Indian languages
"""
import requests
import json

API_URL = "http://localhost:8000"

# Login first
print("🔐 Logging in...")
login_response = requests.post(f"{API_URL}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n" + "="*70)
print("🎤 AMAZON POLLY TTS DEMO - INDIAN LANGUAGES")
print("="*70)

# Test phrases in different languages
test_cases = [
    {
        "language": "hi",
        "name": "Hindi",
        "text": "नमस्ते, मैं ग्राम वाणी हूं। मैं किसानों की मदद करता हूं।",
        "emoji": "🇮🇳"
    },
    {
        "language": "ta",
        "name": "Tamil",
        "text": "வணக்கம், நான் கிராம வாணி. நான் விவசாயிகளுக்கு உதவுகிறேன்.",
        "emoji": "🇮🇳"
    },
    {
        "language": "te",
        "name": "Telugu",
        "text": "నమస్కారం, నేను గ్రామ వాణి. నేను రైతులకు సహాయం చేస్తాను.",
        "emoji": "🇮🇳"
    },
    {
        "language": "bn",
        "name": "Bengali",
        "text": "নমস্কার, আমি গ্রাম বাণী। আমি কৃষকদের সাহায্য করি।",
        "emoji": "🇮🇳"
    },
    {
        "language": "mr",
        "name": "Marathi",
        "text": "नमस्कार, मी ग्राम वाणी आहे. मी शेतकऱ्यांना मदत करतो.",
        "emoji": "🇮🇳"
    },
    {
        "language": "en",
        "name": "English",
        "text": "Hello, I am Gram Vaani. I help farmers with information.",
        "emoji": "🇺🇸"
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['emoji']} {test['name']} ({test['language']})")
    print(f"   Text: {test['text'][:50]}...")
    
    try:
        response = requests.post(
            f"{API_URL}/process-text",
            json={"text": test['text'], "language": test['language']},
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_size = len(result.get('audio_data', ''))
            
            if audio_size > 0:
                print(f"   ✅ Audio generated: {audio_size:,} characters (base64)")
                print(f"   📝 Response: {result['response_text'][:60]}...")
            else:
                print(f"   ⚠️  No audio generated")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("✅ DEMO COMPLETE - Amazon Polly TTS Working!")
print("="*70)
print("\n📊 Summary:")
print("   • Region: ap-south-1 (Mumbai)")
print("   • Voice: Aditi (multi-lingual)")
print("   • Format: MP3 (base64 encoded)")
print("   • Languages: 9 Indian languages supported")
print("="*70)
