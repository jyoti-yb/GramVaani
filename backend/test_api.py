#!/usr/bin/env python3
"""
Simple test script for Gram Vaani API
Run this to test the backend functionality
"""

import requests
import json
import os

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        print("✅ API Health Check:", response.json())
        return True
    except Exception as e:
        print("❌ API Health Check Failed:", str(e))
        return False

def test_audio_processing():
    """Test audio processing with a sample audio file"""
    # This is a placeholder - in real testing, you'd use an actual audio file
    print("📝 To test audio processing:")
    print("1. Start the backend server")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Click the microphone and speak")
    print("4. Try asking: 'Delhi mein mausam kaisa hai?'")

def main():
    print("Gram Vaani API Test")
    print("=" * 30)
    
    if test_health():
        print("\nBackend is running successfully!")
        print("API Documentation: http://localhost:8000/docs")
        print("Frontend: http://localhost:3000")
    else:
        print("\nBackend is not running!")
        print("Make sure to run: python main.py")
    
    print("\n" + "=" * 30)
    test_audio_processing()

if __name__ == "__main__":
    main()
