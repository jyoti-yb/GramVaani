# ✅ WhatsApp Cloud API - Production Checklist

## 🎯 Pre-Deployment Verification

### Backend Code ✅
- [x] `load_dotenv()` called at startup
- [x] GET `/webhook` verification endpoint implemented
- [x] POST `/webhook` message handler implemented
- [x] Phone number normalization (removes country code)
- [x] Safe user creation for new WhatsApp users
- [x] Async message processing (prevents timeouts)
- [x] Error handling returns 200 OK always
- [x] Message length validation (<4096 chars)
- [x] Robust logging with emojis for easy debugging

### Environment Variables ✅
- [x] `WHATSAPP_ACCESS_TOKEN` - From Meta App Dashboard
- [x] `WHATSAPP_PHONE_NUMBER_ID` - Your WhatsApp Business number ID
- [x] `WHATSAPP_VERIFY_TOKEN` - Custom token (gramvani_token)
- [x] All other required variables (Azure, AWS, MongoDB)

### Database ✅
- [x] DynamoDB tables exist:
  - `gramvaani_users` - User profiles
  - `gramvaani_user_querie` - Query history
  - `gramvaani_sessions` - User sessions
- [x] MongoDB collections exist:
  - `hyperlocal_context` - Location data
  - `success_stories` - Farmer stories
  - `pest_outbreaks` - Pest reports

## 🚀 Deployment Steps

### 1. Local Testing
```bash
# Terminal 1: Start backend
cd backend
./start_whatsapp.sh

# Terminal 2: Run tests
python test_whatsapp.py
```

**Expected:** All tests pass ✅

### 2. Expose Backend
```bash
# Install ngrok (if not installed)
# Download from: https://ngrok.com/download

# Start tunnel
ngrok http 8000
```

**Copy:** Forwarding URL (e.g., `https://abc123.ngrok-free.app`)

### 3. Configure Meta App

**Navigate to:** [Meta for Developers](https://developers.facebook.com/apps)

**Steps:**
1. Select your WhatsApp Business App
2. Go to **WhatsApp > Configuration**
3. Click **Edit** next to Webhook
4. Enter:
   - **Callback URL:** `https://YOUR_NGROK_URL/webhook`
   - **Verify Token:** `gramvani_token`
5. Click **Verify and Save**
6. Subscribe to webhook field: **messages** ✅

**Verification:** Green checkmark appears ✅

### 4. Test with Real WhatsApp

**Send message to your WhatsApp Business number:**
```
What is the weather today?
```

**Check backend logs for:**
```
📱 WhatsApp webhook received
📨 Message from 919032611376, type: text
💬 Processing: 'What is the weather today?'
👤 Found existing user: 9032611376
✅ Response sent to 919032611376
```

**Check WhatsApp:** You should receive AI response ✅

## 🔍 Verification Tests

### Test 1: Webhook Verification
```bash
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=gramvani_token&hub.challenge=test123"
```
**Expected:** `test123`

### Test 2: Health Check
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "healthy", "database": "connected"}`

### Test 3: Message Processing
```bash
python test_whatsapp.py
```
**Expected:** `🎉 All tests passed!`

### Test 4: New User Creation
**Send WhatsApp message from new number**
**Check DynamoDB:** New user should be created with:
- `phone_number`: Normalized (without country code)
- `source`: "whatsapp"
- `language`: "en"
- `location`: "India"

### Test 5: Query Types
**Test each query type:**
- [ ] Weather: "What is the weather?"
- [ ] Crop Price: "What is the price of wheat?"
- [ ] Scheme: "Tell me about PM-KISAN"
- [ ] General: "How to grow tomatoes?"

## 🛡️ Security Checklist

- [x] Verify token is secret (not exposed in code)
- [x] Access token has minimal required permissions
- [x] Webhook always returns 200 OK (prevents retries)
- [x] User input is validated before processing
- [x] Error messages don't expose sensitive info
- [x] Phone numbers are normalized consistently
- [x] DynamoDB access uses IAM roles (not hardcoded keys)

## 📊 Monitoring Setup

### Backend Logs
**Monitor for:**
- 📱 Webhook received
- 📨 Message extracted
- 💬 Processing query
- 👤 User found/created
- ✅ Response sent
- ❌ Errors

### Meta App Dashboard
**Check:**
- Webhook status: Active ✅
- Message delivery rate
- Error rate
- Response time

### DynamoDB Metrics
**Monitor:**
- `gramvaani_users` - User growth
- `gramvaani_user_querie` - Query volume
- Read/Write capacity usage

## 🚨 Common Issues & Solutions

### Issue: Webhook verification fails
**Symptoms:** Red X in Meta dashboard
**Solutions:**
- [ ] Check `WHATSAPP_VERIFY_TOKEN` matches
- [ ] Ensure backend is running
- [ ] Verify ngrok tunnel is active
- [ ] Check URL format: `https://YOUR_URL/webhook`

### Issue: Messages not received
**Symptoms:** No webhook calls in logs
**Solutions:**
- [ ] Verify webhook subscription to "messages"
- [ ] Check Meta app is in Live mode
- [ ] Ensure phone number is verified
- [ ] Check ngrok tunnel hasn't expired

### Issue: No response sent
**Symptoms:** Webhook received but no reply
**Solutions:**
- [ ] Check `WHATSAPP_ACCESS_TOKEN` is valid
- [ ] Verify `WHATSAPP_PHONE_NUMBER_ID` is correct
- [ ] Check backend logs for API errors
- [ ] Ensure message isn't too long

### Issue: User not created
**Symptoms:** Error in logs about missing user
**Solutions:**
- [ ] Check DynamoDB connection
- [ ] Verify `gramvaani_users` table exists
- [ ] Check AWS credentials
- [ ] Review IAM permissions

## 🎉 Success Criteria

**Your WhatsApp integration is ready when:**

- ✅ Webhook verification shows green checkmark
- ✅ Test message receives AI response within 5 seconds
- ✅ New users are auto-created in DynamoDB
- ✅ All query types work (weather, crops, schemes)
- ✅ Backend logs show complete message flow
- ✅ No errors in Meta App dashboard
- ✅ Response messages are contextual and helpful
- ✅ Multi-language support works (Hindi, English, etc.)

## 📈 Production Deployment

### Option 1: AWS EC2
```bash
# Launch EC2 instance
# Install dependencies
# Configure security group (port 8000)
# Use Elastic IP (no ngrok needed)
# Set up systemd service for auto-restart
```

### Option 2: AWS Lambda + API Gateway
```bash
# Package FastAPI app
# Deploy to Lambda
# Create API Gateway
# Use API Gateway URL as webhook
```

### Option 3: Cloud Platform (Railway/Render)
```bash
# Connect GitHub repo
# Configure environment variables
# Deploy automatically
# Use provided URL as webhook
```

## 📞 Support Resources

- **Meta Documentation:** https://developers.facebook.com/docs/whatsapp
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **ngrok Docs:** https://ngrok.com/docs
- **Backend Logs:** Check terminal output
- **Test Script:** `python test_whatsapp.py`

---

## 🎯 Quick Commands

```bash
# Start backend
./start_whatsapp.sh

# Run tests
python test_whatsapp.py

# Check health
curl http://localhost:8000/health

# View logs
# (Check terminal where uvicorn is running)

# Start ngrok
ngrok http 8000
```

---

**Status:** ✅ PRODUCTION READY

**Last Updated:** 2024
**Version:** 1.0
