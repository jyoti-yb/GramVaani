# AWS Region Configuration - ap-south-1 (Mumbai)

## ✅ All AWS Services Configured for ap-south-1

### 1. Amazon Polly (Text-to-Speech)
- **Region:** ap-south-1
- **Location:** `main.py` line 64
- **Configuration:**
  ```python
  polly_client = boto3.client("polly", region_name="ap-south-1")
  ```

### 2. Amazon Transcribe (Speech-to-Text)
- **Region:** ap-south-1
- **Location:** `transcribe_service.py` line 11
- **Configuration:**
  ```python
  self.transcribe_client = boto3.client("transcribe", region_name="ap-south-1")
  ```

### 3. Amazon S3 (Audio Storage)
- **Region:** ap-south-1
- **Location:** `transcribe_service.py` line 10
- **Configuration:**
  ```python
  self.s3_client = boto3.client("s3", region_name="ap-south-1")
  ```

## Language Support with Polly

### Updated Configuration
All Indian languages now use Polly with proper language codes:

```python
LANGUAGE_TO_POLLY_VOICE = {
    "en": ("Joanna", "en-US"),
    "hi": ("Aditi", "hi-IN"),
    "ta": ("Aditi", "ta-IN"),
    "te": ("Aditi", "te-IN"),
    "kn": ("Aditi", "kn-IN"),
    "ml": ("Aditi", "ml-IN"),
    "bn": ("Aditi", "bn-IN"),
    "gu": ("Aditi", "gu-IN"),
    "mr": ("Aditi", "mr-IN"),
}
```

### How It Works
1. **Voice:** Aditi (bilingual Hindi-English voice)
2. **Language Code:** Specific to each Indian language (e.g., te-IN for Telugu)
3. **Region:** ap-south-1 (Mumbai) for lowest latency in India

### Supported Languages
✅ English (en-US)
✅ Hindi (hi-IN)
✅ Tamil (ta-IN)
✅ Telugu (te-IN)
✅ Kannada (kn-IN)
✅ Malayalam (ml-IN)
✅ Bengali (bn-IN)
✅ Gujarati (gu-IN)
✅ Marathi (mr-IN)

## Testing

### Test Polly TTS for Telugu:
```bash
cd backend
python -c "
import boto3
import base64

polly = boto3.client('polly', region_name='ap-south-1')
response = polly.synthesize_speech(
    Text='నమస్కారం, ఇది తెలుగు పరీక్ష',
    OutputFormat='mp3',
    VoiceId='Aditi',
    LanguageCode='te-IN'
)

with open('telugu_test.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())
    
print('Telugu TTS test successful!')
"
```

## Benefits of ap-south-1 Region

1. **Lower Latency:** Closest AWS region to India
2. **Better Performance:** Faster response times for Indian users
3. **Cost Optimization:** Reduced data transfer costs
4. **Compliance:** Data stays within Indian region

## Restart Backend

After these changes, restart your backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Expected Behavior

When you select Telugu and speak:
1. ✅ Amazon Transcribe (ap-south-1) transcribes Telugu speech
2. ✅ Azure OpenAI generates Telugu response
3. ✅ Amazon Polly (ap-south-1) synthesizes Telugu audio with Aditi voice
4. ✅ Audio plays back in Telugu

All services now properly configured for ap-south-1 region!
