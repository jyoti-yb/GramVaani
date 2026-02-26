import requests
import os

# Test the transcribe endpoint
def test_transcribe():
    # Replace with your actual token
    token = "your-jwt-token-here"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test with a sample audio file
    with open("test_audio.wav", "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        params = {"language": "hi"}
        
        response = requests.post(
            "http://localhost:8000/api/transcribe",
            headers=headers,
            files=files,
            params=params
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_transcribe()
