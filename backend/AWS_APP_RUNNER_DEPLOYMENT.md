# AWS App Runner Deployment Guide

## Issue Fixed
The deployment failure was caused by `azure-cognitiveservices-speech` package which requires system-level dependencies not available in AWS App Runner's build environment.

## Solution Applied
1. **Removed azure-cognitiveservices-speech** from requirements.txt
2. **Made Azure Speech SDK optional** in main.py - it will only be used if installed
3. **AWS Polly as default** - Now uses AWS Polly for all languages (with fallback support)
4. **Created clean requirements** - requirements-apprunner.txt for AWS-specific deployment

## Deployment Options

### Option 1: Using Updated requirements.txt (Recommended)
The main requirements.txt has been updated to remove azure-cognitiveservices-speech. Deploy as usual:

```bash
# AWS App Runner will use requirements.txt automatically
```

### Option 2: Using requirements-apprunner.txt
If you want to use the minimal requirements file:

1. Update apprunner.yaml to use requirements-apprunner.txt:
```yaml
build:
  commands:
    build:
      - pip install -r requirements-apprunner.txt
```

2. Or rename the file:
```bash
mv requirements-apprunner.txt requirements.txt
```

## Language Support After Fix

### Text-to-Speech (TTS)
- **English**: AWS Polly (Joanna voice)
- **Hindi**: AWS Polly (Aditi voice)
- **Other Indian languages** (Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi):
  - Primary: AWS Polly with Hindi voice (Aditi)
  - Optional: Azure Speech SDK (if credentials provided and SDK installed)

### Translation
- All languages supported via Azure OpenAI GPT-4o-mini
- Amazon Translate for crop calendar translations

## Environment Variables Required

Make sure these are set in AWS App Runner:

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# AWS Services (Required)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=ap-south-1

# MongoDB (Required)
MONGO_URL=your_mongodb_connection_string

# OpenWeather API (Required)
OPENWEATHER_API_KEY=your_key

# WhatsApp (Optional)
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Azure Speech (Optional - for better regional language support)
AZURE_SPEECH_KEY=your_key
AZURE_SPEECH_REGION=your_region

# Security
SECRET_KEY=your_secret_key
```

## Deployment Steps

1. **Push changes to your repository**
```bash
git add .
git commit -m "Fix: Remove azure-cognitiveservices-speech for App Runner compatibility"
git push
```

2. **Deploy to AWS App Runner**
   - If using GitHub: App Runner will auto-deploy on push
   - If using manual: Upload the updated code

3. **Verify deployment**
```bash
# Check health endpoint
curl https://your-app-runner-url.awsapprunner.com/health

# Expected response:
{"status":"healthy","database":"connected"}
```

## Testing TTS After Deployment

Test the TTS functionality:

```bash
# Test English TTS
curl -X POST https://your-app-runner-url.awsapprunner.com/api/weather \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Test Hindi TTS
curl -X POST https://your-app-runner-url.awsapprunner.com/api/weather \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "hi"}'
```

## Troubleshooting

### If build still fails:
1. Check App Runner build logs for specific error
2. Verify all environment variables are set
3. Ensure MongoDB connection string is accessible from AWS
4. Check AWS credentials have necessary permissions (DynamoDB, Polly, Translate, Transcribe)

### If TTS doesn't work:
1. Verify AWS Polly permissions in IAM
2. Check CloudWatch logs for Polly errors
3. Ensure region is set to ap-south-1 (or region with Polly support)

### If you need Azure Speech SDK:
1. Use EC2 or ECS instead of App Runner (more control over system dependencies)
2. Or keep current setup - Azure Speech is optional and will gracefully fall back to Polly

## Performance Notes

- AWS Polly is faster and more reliable in AWS environment
- No system dependencies required
- Better integration with other AWS services
- Lower latency for Indian users (ap-south-1 region)

## Cost Optimization

- Polly pricing: $4 per 1 million characters
- Azure Speech pricing: $1 per 1 million characters
- For AWS deployment, Polly is recommended for better integration and reliability
