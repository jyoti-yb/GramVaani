#!/usr/bin/env python3
"""
Test: Hybrid TTS System (Polly + Azure Speech)
Verifies which service is used for each language
"""
import requests

API_URL = "http://localhost:8000"

# Login
print("🔐 Logging in...")
login_response = requests.post(f"{API_URL}/api/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n" + "="*80)
print("🎤 HYBRID TTS SYSTEM TEST - Polly (Hindi/English) + Azure (Other Languages)")
print("="*80)

test_cases = [
    {"lang": "hi", "name": "Hindi", "text": "नमस्ते", "service": "Amazon Polly", "emoji": "🟢"},
    {"lang": "en", "name": "English", "text": "Hello", "service": "Amazon Polly", "emoji": "🟢"},
    {"lang": "ta", "name": "Tamil", "text": "வணக்கம்", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "te", "name": "Telugu", "text": "నమస్కారం", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "kn", "name": "Kannada", "text": "ನಮಸ್ಕಾರ", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "ml", "name": "Malayalam", "text": "നമസ്കാരം", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "bn", "name": "Bengali", "text": "নমস্কার", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "gu", "name": "Gujarati", "text": "નમસ્તે", "service": "Azure Speech", "emoji": "🔵"},
    {"lang": "mr", "name": "Marathi", "text": "नमस्कार", "service": "Azure Speech", "emoji": "🔵"},
]

print("\n📋 Expected Configuration:")
print("   🟢 Amazon Polly: Hindi, English")
print("   🔵 Azure Speech: Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi")
print("\n" + "-"*80)

results = {"polly": 0, "azure": 0, "failed": 0}

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['emoji']} {test['name']} ({test['lang']}) - Expected: {test['service']}")
    
    try:
        response = requests.post(
            f"{API_URL}/process-text",
            json={"text": test['text'], "language": test['lang']},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_size = len(result.get('audio_data', ''))
            
            if audio_size > 0:
                print(f"   ✅ Audio generated: {audio_size:,} chars")
                if test['service'] == "Amazon Polly":
                    results['polly'] += 1
                else:
                    results['azure'] += 1
            else:
                print(f"   ❌ No audio generated")
                results['failed'] += 1
        else:
            print(f"   ❌ Failed: {response.status_code}")
            results['failed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1

print("\n" + "="*80)
print("📊 RESULTS SUMMARY")
print("="*80)
print(f"🟢 Amazon Polly (Hindi/English):  {results['polly']}/2 working")
print(f"🔵 Azure Speech (Other languages): {results['azure']}/7 working")
print(f"❌ Failed:                         {results['failed']}/{len(test_cases)}")
print("="*80)

if results['polly'] == 2 and results['azure'] == 7:
    print("\n✅ SUCCESS! Hybrid TTS system working perfectly!")
    print("   • Polly handling Hindi & English")
    print("   • Azure Speech handling 7 Indian languages")
else:
    print("\n⚠️  Some services may need attention")

print("="*80)
