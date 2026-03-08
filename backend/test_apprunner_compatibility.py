"""
Test script to verify the application works without azure-cognitiveservices-speech
Run this before deploying to AWS App Runner
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        from fastapi import FastAPI
        print("✓ FastAPI imported")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import boto3
        print("✓ boto3 imported")
    except ImportError as e:
        print(f"✗ boto3 import failed: {e}")
        return False
    
    try:
        from openai import AzureOpenAI
        print("✓ Azure OpenAI imported")
    except ImportError as e:
        print(f"✗ Azure OpenAI import failed: {e}")
        return False
    
    try:
        from pymongo import MongoClient
        print("✓ PyMongo imported")
    except ImportError as e:
        print(f"✗ PyMongo import failed: {e}")
        return False
    
    # Test optional Azure Speech import
    try:
        import azure.cognitiveservices.speech as speechsdk
        print("✓ Azure Speech SDK imported (optional)")
        azure_speech_available = True
    except ImportError:
        print("ℹ Azure Speech SDK not available (will use AWS Polly)")
        azure_speech_available = False
    
    return True

def test_main_module():
    """Test that main.py can be imported"""
    print("\nTesting main.py import...")
    
    # Set dummy credentials for testing
    os.environ.setdefault('AZURE_OPENAI_ENDPOINT', 'https://dummy.openai.azure.com/')
    os.environ.setdefault('AZURE_OPENAI_API_KEY', 'dummy-key-for-testing')
    os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017/test')
    
    try:
        # Add backend directory to path if needed
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        import main
        print("✓ main.py imported successfully")
        
        # Check if Azure Speech is available in main
        if hasattr(main, 'AZURE_SPEECH_AVAILABLE'):
            print(f"✓ AZURE_SPEECH_AVAILABLE = {main.AZURE_SPEECH_AVAILABLE}")
        
        # Check if synthesize_speech function exists
        if hasattr(main, 'synthesize_speech'):
            print("✓ synthesize_speech function available")
        
        return True
    except Exception as e:
        print(f"✗ main.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_polly_voices():
    """Test that Polly voices are configured for all languages"""
    print("\nTesting Polly voice configuration...")
    
    # Set dummy credentials for testing
    os.environ.setdefault('AZURE_OPENAI_ENDPOINT', 'https://dummy.openai.azure.com/')
    os.environ.setdefault('AZURE_OPENAI_API_KEY', 'dummy-key-for-testing')
    os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017/test')
    
    try:
        import main
        
        required_languages = ["en", "hi", "ta", "te", "kn", "ml", "bn", "gu", "mr"]
        
        for lang in required_languages:
            if lang in main.LANGUAGE_TO_POLLY_VOICE:
                voice, locale = main.LANGUAGE_TO_POLLY_VOICE[lang]
                print(f"✓ {lang}: {voice} ({locale})")
            else:
                print(f"✗ {lang}: No Polly voice configured")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Polly voice test failed: {e}")
        return False

def main_test():
    """Run all tests"""
    print("=" * 60)
    print("AWS App Runner Compatibility Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Imports
    if not test_imports():
        all_passed = False
    
    # Test 2: Main module
    if not test_main_module():
        all_passed = False
    
    # Test 3: Polly voices
    if not test_polly_voices():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Ready for AWS App Runner deployment")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed. Please fix issues before deploying")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main_test())
