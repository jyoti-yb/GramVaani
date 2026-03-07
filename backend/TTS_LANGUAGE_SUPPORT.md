# TTS Language Support Issue

## Current Limitation

Amazon Polly only supports **Hindi (Aditi voice)** for Indian languages. It does NOT support:
- Telugu
- Tamil
- Kannada
- Malayalam
- Bengali
- Gujarati
- Marathi

## Current Behavior

- **Hindi & English**: Full TTS support ✅
- **Other Indian languages**: Text response only, no audio ❌

## Solution Options

### Option 1: Google Cloud Text-to-Speech (Recommended)

Google Cloud TTS supports ALL Indian languages with high-quality voices:

**Supported Languages:**
- Hindi (hi-IN) - Multiple voices
- Telugu (te-IN) - Multiple voices
- Tamil (ta-IN) - Multiple voices
- Kannada (kn-IN) - Multiple voices
- Malayalam (ml-IN) - Multiple voices
- Bengali (bn-IN) - Multiple voices
- Gujarati (gu-IN) - Multiple voices
- Marathi (mr-IN) - Multiple voices

**Setup:**
```bash
pip install google-cloud-texttospeech
```

**Code Example:**
```python
from google.cloud import texttospeech

def synthesize_speech_google(text: str, language: str) -> Optional[str]:
    client = texttospeech.TextToSpeechClient()
    
    language_map = {
        "hi": "hi-IN",
        "te": "te-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "gu": "gu-IN",
        "mr": "mr-IN",
        "en": "en-IN"
    }
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_map.get(language, "en-IN"),
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    return base64.b64encode(response.audio_content).decode("utf-8")
```

### Option 2: Azure Speech Services

Azure also supports Indian languages but requires different setup.

### Option 3: Keep Current Setup

For now, the app works with:
- ✅ Transcription in all 9 languages (Amazon Transcribe)
- ✅ AI responses in all 9 languages (Azure OpenAI)
- ✅ TTS for Hindi and English only (Amazon Polly)
- ❌ No TTS for Telugu, Tamil, Kannada, Malayalam, Bengali, Gujarati, Marathi

## Recommendation

Switch to **Google Cloud Text-to-Speech** for complete Indian language support.

**Cost:** Google Cloud TTS pricing is similar to Amazon Polly (~$4 per 1 million characters).
