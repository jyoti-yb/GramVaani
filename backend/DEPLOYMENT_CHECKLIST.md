# AWS App Runner Deployment Checklist

## ✅ Pre-Deployment Checklist

### Code Changes Verified
- [x] Removed `azure-cognitiveservices-speech` from requirements.txt
- [x] Updated main.py to make Azure Speech SDK optional
- [x] Added AWS Polly fallback for all languages
- [x] Updated Dockerfile with health check
- [x] Created deployment documentation

### Local Testing (Optional but Recommended)
- [ ] Run `python test_apprunner_compatibility.py` - All tests pass
- [ ] Run `test_local.bat` (Windows) or `uvicorn main:app` - Server starts successfully
- [ ] Test `/health` endpoint - Returns healthy status
- [ ] Test `/docs` endpoint - Swagger UI loads
- [ ] Test TTS with English - Audio generated
- [ ] Test TTS with Hindi - Audio generated

### Environment Variables Ready
- [ ] AZURE_OPENAI_ENDPOINT
- [ ] AZURE_OPENAI_API_KEY
- [ ] AZURE_OPENAI_DEPLOYMENT
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_DEFAULT_REGION (set to ap-south-1)
- [ ] MONGO_URL
- [ ] OPENWEATHER_API_KEY
- [ ] SECRET_KEY
- [ ] WHATSAPP_ACCESS_TOKEN (if using WhatsApp)
- [ ] WHATSAPP_PHONE_NUMBER_ID (if using WhatsApp)
- [ ] WHATSAPP_VERIFY_TOKEN (if using WhatsApp)

### AWS Permissions Verified
- [ ] IAM role has DynamoDB access (gramvaani_* tables)
- [ ] IAM role has Polly access (synthesize_speech)
- [ ] IAM role has Transcribe access (start_transcription_job)
- [ ] IAM role has Translate access (translate_text)
- [ ] MongoDB connection accessible from AWS (whitelist AWS IPs if needed)

## 🚀 Deployment Steps

### Step 1: Commit and Push Changes
```bash
cd "d:\aws ai for bharath\deploy\GramVaani"
git add .
git commit -m "Fix: Remove azure-cognitiveservices-speech for App Runner compatibility"
git push origin main
```
- [ ] Changes committed
- [ ] Changes pushed to repository

### Step 2: Deploy to AWS App Runner

#### Option A: GitHub Auto-Deploy
- [ ] Go to AWS App Runner console
- [ ] Service automatically detects new commit
- [ ] Build starts automatically
- [ ] Wait for deployment to complete (~5-10 minutes)

#### Option B: Manual Deploy
- [ ] Go to AWS App Runner console
- [ ] Click "Deploy" or "Create new deployment"
- [ ] Select source (GitHub/ECR/Source code)
- [ ] Configure build settings:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
- [ ] Set environment variables
- [ ] Click "Deploy"

### Step 3: Monitor Deployment
- [ ] Check build logs for errors
- [ ] Verify all dependencies install successfully
- [ ] Wait for "Running" status
- [ ] Note the App Runner URL

## ✅ Post-Deployment Verification

### Health Checks
```bash
# Replace YOUR_APP_URL with actual App Runner URL
curl https://YOUR_APP_URL.awsapprunner.com/health
```
- [ ] Health endpoint returns: `{"status":"healthy","database":"connected"}`
- [ ] Response time < 2 seconds

### API Endpoints Testing

#### 1. Authentication
```bash
# Signup
curl -X POST https://YOUR_APP_URL.awsapprunner.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9999999999","password":"test123","language":"en","location":"Delhi, India"}'

# Login
curl -X POST https://YOUR_APP_URL.awsapprunner.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9999999999","password":"test123"}'
```
- [ ] Signup works (or returns "already registered")
- [ ] Login returns access token

#### 2. Text Processing with TTS
```bash
# Save token from login
TOKEN="your_access_token_here"

# Test English
curl -X POST https://YOUR_APP_URL.awsapprunner.com/process-text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"What is the weather today?","language":"en"}'

# Test Hindi
curl -X POST https://YOUR_APP_URL.awsapprunner.com/process-text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"आज मौसम कैसा है?","language":"hi"}'
```
- [ ] English TTS works (audio_data returned)
- [ ] Hindi TTS works (audio_data returned)
- [ ] Response includes query_id and response_text

#### 3. Weather API
```bash
curl -X POST https://YOUR_APP_URL.awsapprunner.com/api/weather \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language":"en"}'
```
- [ ] Weather data returned
- [ ] Audio data included

#### 4. Crop Calendar
```bash
curl -X GET https://YOUR_APP_URL.awsapprunner.com/api/crop-calendar?language=en \
  -H "Authorization: Bearer $TOKEN"
```
- [ ] Crop calendar data returned
- [ ] Recommended crops listed

#### 5. WhatsApp Webhook (if configured)
```bash
# Verify webhook
curl "https://YOUR_APP_URL.awsapprunner.com/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=YOUR_VERIFY_TOKEN"
```
- [ ] Returns challenge token
- [ ] WhatsApp webhook verified in Meta dashboard

### Performance Checks
- [ ] Average API response time < 2 seconds
- [ ] TTS generation time < 1 second
- [ ] No timeout errors
- [ ] Memory usage stable

### Database Checks
- [ ] DynamoDB tables accessible
- [ ] MongoDB connection working
- [ ] User data persists correctly
- [ ] Query history saved

## 🔍 Troubleshooting

### If Build Fails
1. [ ] Check App Runner build logs
2. [ ] Verify requirements.txt has no azure-cognitiveservices-speech
3. [ ] Check for Python version compatibility (should be 3.11)
4. [ ] Verify all dependencies are available on PyPI

### If Health Check Fails
1. [ ] Check CloudWatch logs
2. [ ] Verify MongoDB connection string
3. [ ] Check DynamoDB table names and region
4. [ ] Verify IAM permissions

### If TTS Doesn't Work
1. [ ] Check IAM role has Polly permissions
2. [ ] Verify AWS region supports Polly (ap-south-1 does)
3. [ ] Check CloudWatch logs for Polly errors
4. [ ] Test with simple text first

### If Authentication Fails
1. [ ] Verify SECRET_KEY is set
2. [ ] Check DynamoDB gramvaani_users table exists
3. [ ] Verify user was created successfully
4. [ ] Check token expiration (30 minutes default)

## 📊 Monitoring Setup

### CloudWatch Alarms (Recommended)
- [ ] Set up alarm for 5xx errors
- [ ] Set up alarm for high latency (>3s)
- [ ] Set up alarm for failed health checks
- [ ] Set up alarm for high memory usage (>80%)

### Logging
- [ ] Enable CloudWatch Logs
- [ ] Set log retention period (7-30 days)
- [ ] Create log insights queries for common issues

## 🎉 Success Criteria

Deployment is successful when:
- [x] Build completes without errors
- [ ] Health endpoint returns healthy status
- [ ] Authentication works (signup/login)
- [ ] Text processing with TTS works
- [ ] Weather API works
- [ ] Crop calendar loads
- [ ] WhatsApp webhook verified (if configured)
- [ ] No errors in CloudWatch logs
- [ ] Response times acceptable (<2s)

## 📝 Notes

### What Changed
- Removed Azure Speech SDK dependency
- Now using AWS Polly for all TTS
- Azure Speech SDK is optional (can be added later if needed)

### What Didn't Change
- All API endpoints work the same
- Authentication unchanged
- Database operations unchanged
- WhatsApp integration unchanged
- Translation still uses Azure OpenAI

### Known Limitations
- Regional languages (Tamil, Telugu, etc.) use Hindi voice (Aditi) instead of native voices
- This is acceptable for MVP and can be enhanced later if needed

## 🔄 Rollback Plan

If deployment fails and you need to rollback:
1. [ ] Revert to previous App Runner deployment
2. [ ] Check what went wrong in logs
3. [ ] Fix issues locally
4. [ ] Test locally before redeploying
5. [ ] Deploy again

Note: The old code with Azure Speech SDK won't work in App Runner, so rollback would need a different solution (EC2/ECS).

## 📞 Support

If you encounter issues:
1. Check AWS_APP_RUNNER_DEPLOYMENT.md for detailed troubleshooting
2. Review CloudWatch logs for specific errors
3. Test locally using test_local.bat
4. Verify all environment variables are set correctly

## ✅ Final Sign-off

- [ ] All pre-deployment checks completed
- [ ] Deployment successful
- [ ] Post-deployment verification passed
- [ ] Monitoring set up
- [ ] Documentation updated
- [ ] Team notified of new deployment

**Deployment Date**: _______________
**Deployed By**: _______________
**App Runner URL**: _______________
**Status**: _______________
