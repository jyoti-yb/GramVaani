# 🔧 Complete Setup Guide - Phone Number Authentication with DynamoDB

## ✅ What's Been Done

1. ✅ Backend updated to use `phone_number` instead of `email`
2. ✅ Frontend updated to accept phone numbers
3. ✅ DynamoDB tables configured for phone-based auth
4. ✅ All queries stored with `user_phone` field

## 🚀 Setup Steps

### Step 1: Create DynamoDB Tables

```bash
cd backend
python setup_dynamodb.py
```

**Expected Output:**
```
Creating users table...
✓ Users table created successfully
Creating queries table...
✓ gramvaani_user_querie table created successfully

✓ DynamoDB setup complete!
```

### Step 2: Start Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
DynamoDB connection initialized
DynamoDB tables ready
INFO:     Application startup complete.
```

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Step 4: Test the Application

1. Open http://localhost:5173
2. Click "Sign Up"
3. Enter:
   - Phone: `+919876543210`
   - Password: `test123`
   - Language: Hindi
   - Location: (auto-detected or manual)
4. Click "Create Account"

## 🧪 Testing Backend Directly

```bash
cd backend
./test_phone_auth.sh
```

Or manually:

```bash
# Test Signup
curl -X POST http://localhost:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "test123",
    "language": "hi",
    "location": "Mumbai, Maharashtra"
  }'

# Test Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "test123"
  }'
```

## 📊 Database Schema

### gramvaani_users
```
{
  phone_number: "+919876543210" (Primary Key),
  password: "$2b$12$...",
  language: "hi",
  location: "Mumbai, Maharashtra",
  created_at: "2026-03-02T..."
}
```

### gramvaani_user_querie
```
{
  query_id: "uuid-here" (Primary Key),
  user_phone: "+919876543210" (GSI),
  query: "What's the weather?",
  response: "The weather is...",
  query_type: "text" or "audio",
  timestamp: "2026-03-02T..."
}
```

## 🔍 Verify Queries are Stored

Edit `check_queries.py` and set your phone:
```python
user_phone = "+919876543210"
```

Then run:
```bash
python check_queries.py
```

## ❌ Troubleshooting

### Error: 422 Unprocessable Entity

**Cause:** Backend not restarted after changes

**Fix:**
```bash
# Stop backend (Ctrl+C)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Error: Table does not exist

**Cause:** DynamoDB tables not created

**Fix:**
```bash
cd backend
python setup_dynamodb.py
```

### Error: Frontend validation error

**Cause:** Browser cache

**Fix:**
1. Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Or clear browser cache
3. Restart frontend: `npm run dev`

### Error: Module import failed

**Cause:** Syntax error in Auth.jsx

**Fix:**
```bash
cd frontend
# Stop frontend (Ctrl+C)
npm run dev
```

## 📝 Phone Number Format

✅ **Correct:**
- `+919876543210` (with country code)
- `+911234567890`

❌ **Incorrect:**
- `9876543210` (missing +91)
- `919876543210` (missing +)

## 🔐 Security Notes

- Passwords are hashed with bcrypt
- JWT tokens expire in 30 minutes
- DynamoDB uses IAM authentication
- No credentials stored in code

## 📂 Files Modified

### Backend:
- ✅ `main.py` - All auth endpoints
- ✅ `setup_dynamodb.py` - Table schemas
- ✅ `check_queries.py` - Query verification

### Frontend:
- ✅ `Auth.jsx` - Login/Signup form

## 🎯 Next Steps

1. ✅ Tables created
2. ✅ Backend running
3. ✅ Frontend running
4. ⏳ Test signup with phone number
5. ⏳ Test login
6. ⏳ Send a query
7. ⏳ Verify query stored in DynamoDB

## 📞 Support

If issues persist:

1. Check backend logs for errors
2. Check browser console for errors
3. Verify AWS credentials in `.env`
4. Ensure DynamoDB tables exist in AWS Console
5. Test backend directly with curl

---

**Status:** ✅ Ready to Use
**Last Updated:** March 2, 2026
