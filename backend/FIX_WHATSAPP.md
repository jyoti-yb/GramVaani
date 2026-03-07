# 🔧 WhatsApp Configuration Fix Guide

## Issue
Your access token is valid but lacks the correct permissions or the Phone Number ID is incorrect.

## ✅ Solution (5 minutes)

### Step 1: Get Correct Phone Number ID

1. Go to: https://developers.facebook.com/apps
2. Select your app
3. Click **WhatsApp** → **API Setup** (left sidebar)
4. You should see your phone number: **+91 94908 72665**
5. Below it, find **"Phone number ID"** - it should look like: `123456789012345`
6. **Copy this exact number**

### Step 2: Generate New Access Token with Correct Permissions

**Option A: Temporary Token (Quick Test - 24 hours)**
1. On the same **API Setup** page
2. Click **"Generate access token"** or copy the existing one
3. Make sure it has these permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`

**Option B: Permanent Token (Recommended)**
1. Go to **Settings** → **System Users**
2. Create a System User (or use existing)
3. Assign your WhatsApp app to this user
4. Generate token with permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. Copy the permanent token

### Step 3: Update .env File

Open `/backend/.env` and update:

```bash
WHATSAPP_ACCESS_TOKEN=<YOUR_NEW_TOKEN_HERE>
WHATSAPP_PHONE_NUMBER_ID=<YOUR_CORRECT_PHONE_ID_HERE>
WHATSAPP_VERIFY_TOKEN=gramvani_token
```

### Step 4: Test Configuration

```bash
cd backend
python3 test_send.py
```

**Expected:** "✅ SUCCESS! Message sent."

### Step 5: Start Backend

```bash
./start_whatsapp.sh
```

### Step 6: Test with Real Message

Send a WhatsApp message to **+91 94908 72665**:
```
What is the weather today?
```

You should receive an AI response!

---

## 🎯 Quick Checklist

- [ ] Got correct Phone Number ID from Meta Dashboard
- [ ] Generated access token with correct permissions
- [ ] Updated `.env` file
- [ ] Ran `python3 test_send.py` - got success
- [ ] Started backend with `./start_whatsapp.sh`
- [ ] Sent test WhatsApp message
- [ ] Received AI response

---

## 🐛 Still Not Working?

### Check 1: Webhook Configuration
1. Meta Dashboard → WhatsApp → Configuration
2. Webhook URL should be: `https://YOUR_NGROK_URL/webhook`
3. Verify token: `gramvani_token`
4. Subscribed to: **messages** ✅

### Check 2: App Status
- App must be in **Live** mode (not Development)
- Phone number must be verified
- Business verification completed (if required)

### Check 3: Backend Logs
When you send a message, you should see:
```
📱 WhatsApp webhook received
📨 Message from 919490872665, type: text
💬 Processing: 'What is the weather today?'
✅ Response sent to 919490872665
```

If you don't see these logs, webhook is not configured correctly.

---

## 📞 Need Help?

Run these debug commands:

```bash
# Test token and phone ID
python3 test_send.py

# Check backend health
curl http://localhost:8000/health

# Test webhook verification
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=gramvani_token&hub.challenge=test"
```

---

## 🎉 Success Indicators

✅ `test_send.py` sends message successfully
✅ Backend logs show webhook received
✅ You receive AI responses on WhatsApp
✅ No errors in Meta Dashboard

**Your backend code is perfect - just need correct credentials!** 🚀
