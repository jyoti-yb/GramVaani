# 📱 WhatsApp Cloud API Integration Guide

## ✅ Current Status

Your FastAPI backend is **fully configured** for WhatsApp Cloud API with:

- ✅ Environment variables loaded via `python-dotenv`
- ✅ GET `/webhook` verification endpoint
- ✅ POST `/webhook` message handler
- ✅ Safe user creation for new WhatsApp users
- ✅ Phone number normalization (removes country code)
- ✅ Async message processing (prevents Meta timeouts)
- ✅ Robust error handling and logging

## 🚀 Quick Start

### 1. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Wait for: `Application startup complete`

### 2. Test Integration Locally

```bash
python test_whatsapp.py
```

Expected output: `🎉 All tests passed!`

### 3. Expose Backend via ngrok

```bash
# Install ngrok if not already installed
# Download from: https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000
```

Copy the **Forwarding URL** (e.g., `https://abc123.ngrok-free.app`)

### 4. Configure Meta App Dashboard

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your WhatsApp Business App
3. Navigate to **WhatsApp > Configuration**
4. Click **Edit** next to Webhook

**Webhook Configuration:**
```
Callback URL: https://YOUR_NGROK_URL/webhook
Verify Token: gramvani_token
```

5. Click **Verify and Save**
6. Subscribe to webhook field: **messages**

### 5. Test with Real WhatsApp

Send a message to your WhatsApp Business number:
```
What is the weather today?
```

Check backend logs for:
```
📱 WhatsApp webhook received: {...}
📨 Message from 919032611376, type: text
💬 Processing: 'What is the weather today?'
✅ Response sent to 919032611376
```

## 🔧 Environment Variables

Verify these are set in `.env`:

```bash
# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=EAAUoKvl9c3EBQ7StTd2ae6nOtLPnc4sOEcKjfw2KC1S1ZBz20GgHUQHrZA9PukThb19PTltTLttCbUMB25dU8aIuJD5HWF7eRMXZCgXWtcZAgUOkXzmnV8bVrAhvqdjKXguef2fCi2Y5XVLLfbcbdK2HmTOU4Rl6ht5xfOrJeatyjMw6cZCMZCuSQaHdHsqGNZCbbZCtZCkNgT3F5ISk4SlBtoaUZApdmbKjR81KCw9ewp9lZBvgYLpHFZArdrZBp1vWcgGZBiRNqZAf5NFguifOtYiLo4cVyQU
WHATSAPP_PHONE_NUMBER_ID=933004536573375
WHATSAPP_VERIFY_TOKEN=gramvani_token
```

## 📋 Webhook Endpoints

### GET `/webhook` - Verification

**Purpose:** Meta verifies your webhook URL

**Query Parameters:**
- `hub.mode` = "subscribe"
- `hub.verify_token` = Your verify token
- `hub.challenge` = Random string to echo back

**Response:** Returns `hub.challenge` as plain text (200 OK)

**Test:**
```bash
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=gramvani_token&hub.challenge=test123"
# Should return: test123
```

### POST `/webhook` - Message Handler

**Purpose:** Receives incoming WhatsApp messages

**Request Body:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "919032611376",
          "type": "text",
          "text": {"body": "Hello"}
        }]
      }
    }]
  }]
}
```

**Response:** `{"status": "received"}` (200 OK)

**Processing:**
1. Extracts sender phone number
2. Gets/creates user in DynamoDB
3. Processes message with AI
4. Sends response via WhatsApp API

## 🔄 Message Flow

```
User sends WhatsApp message
    ↓
Meta forwards to POST /webhook
    ↓
Backend responds 200 OK immediately
    ↓
Async processing starts:
  - Extract message & sender
  - Get/create user
  - Process with AI (weather/crops/schemes)
  - Send response via Graph API
    ↓
User receives AI response
```

## 🛡️ Safety Features

### 1. Phone Number Normalization
```python
# WhatsApp sends: 919032611376
# Stored in DB: 9032611376 (without country code)
```

### 2. New User Auto-Creation
```python
{
  "phone_number": "9032611376",
  "password": "",  # No password for WhatsApp users
  "language": "en",
  "location": "India",
  "source": "whatsapp",
  "whatsapp_id": "919032611376"
}
```

### 3. Error Handling
- Always returns 200 OK to prevent Meta retries
- Logs all errors with stack traces
- Fallback user object if DB fails

### 4. Message Validation
- Checks for required fields (entry, changes, messages)
- Only processes text messages
- Handles empty/missing data gracefully

## 🎯 Supported Queries

### Weather
```
"What is the weather today?"
"मौसम कैसा है?"
```

### Crop Prices
```
"What is the price of wheat?"
"गेहूं की कीमत क्या है?"
```

### Government Schemes
```
"Tell me about PM-KISAN scheme"
"सरकारी योजनाओं के बारे में बताओ"
```

### General Farming
```
"How to grow tomatoes?"
"टमाटर कैसे उगाएं?"
```

## 🐛 Troubleshooting

### Issue: Webhook verification fails

**Solution:**
1. Check `WHATSAPP_VERIFY_TOKEN` in `.env`
2. Ensure backend is running
3. Verify ngrok tunnel is active
4. Check Meta dashboard token matches

### Issue: Messages not received

**Solution:**
1. Check backend logs for webhook calls
2. Verify webhook subscription in Meta dashboard
3. Ensure `WHATSAPP_ACCESS_TOKEN` is valid
4. Check ngrok tunnel hasn't expired

### Issue: No response sent to user

**Solution:**
1. Check `WHATSAPP_PHONE_NUMBER_ID` is correct
2. Verify `WHATSAPP_ACCESS_TOKEN` has send permissions
3. Check backend logs for API errors
4. Ensure message isn't too long (>4096 chars)

### Issue: User not found in DB

**Solution:**
- Auto-creation is enabled
- Check DynamoDB connection
- Verify `gramvaani_users` table exists
- Check AWS credentials

## 📊 Monitoring

### Backend Logs

Look for these emojis in logs:
- 📱 Webhook received
- 📨 Message extracted
- 💬 Processing query
- 👤 User found/created
- ✅ Response sent
- ❌ Error occurred

### Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Webhook verification
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=gramvani_token&hub.challenge=test"

# Run full test suite
python test_whatsapp.py
```

## 🚀 Production Deployment

### Option 1: AWS EC2 + Elastic IP
```bash
# No ngrok needed - use permanent IP
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: AWS Lambda + API Gateway
- Deploy as serverless function
- Use API Gateway URL as webhook

### Option 3: Railway/Render
- Deploy backend to cloud platform
- Use provided URL as webhook

## 📝 Meta App Configuration Checklist

- [ ] App is in **Live** mode (not Development)
- [ ] Webhook URL configured: `https://YOUR_URL/webhook`
- [ ] Verify token matches: `gramvani_token`
- [ ] Subscribed to **messages** field
- [ ] Access token has **messages** permission
- [ ] Phone number is verified and active
- [ ] Business verification completed (if required)

## 🎉 Success Indicators

✅ Webhook verification shows green checkmark in Meta dashboard
✅ Test message receives AI response
✅ Backend logs show complete message flow
✅ New users auto-created in DynamoDB
✅ Responses are contextual (weather/crops/schemes)

## 📞 Support

If issues persist:
1. Check backend logs for detailed errors
2. Verify all environment variables
3. Test with `test_whatsapp.py`
4. Check Meta App dashboard for webhook status
5. Ensure ngrok tunnel is active (for local testing)

---

**Your backend is production-ready! 🚀**
