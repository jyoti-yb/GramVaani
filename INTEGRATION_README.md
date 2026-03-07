# 🔄 DynamoDB Integration - Complete Guide

## 📋 Overview

Your friend implemented DynamoDB in the `sru` branch to replace MongoDB. This guide helps you integrate those changes into your `eshwar` branch without breaking your existing functionality.

## 🎯 What Was Done

I've analyzed both branches and created everything you need:

### ✅ Files Created

1. **backend/main_dynamodb.py** - Complete DynamoDB version of your application
2. **backend/setup_dynamodb.py** - Script to create DynamoDB tables
3. **backend/requirements_dynamodb.txt** - Updated dependencies with boto3
4. **DYNAMODB_MIGRATION_GUIDE.md** - Detailed migration instructions
5. **MONGODB_VS_DYNAMODB.md** - Side-by-side code comparison
6. **QUICK_START.md** - Quick start guide

## 🚀 Quick Start (3 Options)

### Option 1: Test DynamoDB Quickly ⚡
```bash
cd backend

# Install boto3 if not already installed
pip install boto3

# Setup DynamoDB tables
python setup_dynamodb.py

# Backup current version
cp main.py main_mongodb_backup.py

# Switch to DynamoDB
cp main_dynamodb.py main.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Rollback if needed:**
```bash
cp main_mongodb_backup.py main.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Run Both Side-by-Side 🔄 (Recommended)
```bash
cd backend

# Install boto3
pip install boto3

# Setup DynamoDB tables
python setup_dynamodb.py

# Terminal 1 - MongoDB version (your current)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - DynamoDB version (new)
uvicorn main_dynamodb:app --reload --host 0.0.0.0 --port 8001
```

Test both versions:
- MongoDB: http://localhost:8000
- DynamoDB: http://localhost:8001

### Option 3: Gradual Migration 🎯
Keep both databases and switch via environment variable.

Add to `.env`:
```env
DATABASE_TYPE=mongodb  # or dynamodb
```

This requires modifying `main.py` to support both (see DYNAMODB_MIGRATION_GUIDE.md).

## 🔍 Key Changes Summary

### Database Operations

| Operation | MongoDB (Current) | DynamoDB (New) |
|-----------|------------------|----------------|
| **Import** | `from motor.motor_asyncio import AsyncIOMotorClient` | `import boto3` |
| **Connect** | `AsyncIOMotorClient(MONGO_URL)` | `boto3.resource('dynamodb')` |
| **Find User** | `await users_collection.find_one({"email": email})` | `users_table.get_item(Key={'email': email})` |
| **Insert User** | `await users_collection.insert_one(user_doc)` | `users_table.put_item(Item=user_doc)` |
| **Log Query** | `await queries_collection.insert_one(query)` | `queries_table.put_item(Item=query)` |
| **Async** | Yes (`await`) | No (sync) |
| **Datetime** | `datetime.utcnow()` | `datetime.utcnow().isoformat()` |
| **Query ID** | Auto ObjectId | Manual UUID |

### Code Changes Example

**Before (MongoDB):**
```python
# Find user
user = await users_collection.find_one({"email": email})

# Insert query
await user_queries_collection.insert_one({
    "user_email": email,
    "query": text,
    "timestamp": datetime.utcnow()
})
```

**After (DynamoDB):**
```python
# Find user
response = users_table.get_item(Key={'email': email})
user = response.get('Item')

# Insert query
queries_table.put_item(Item={
    "query_id": str(uuid.uuid4()),
    "user_email": email,
    "query": text,
    "timestamp": datetime.utcnow().isoformat()
})
```

## ✅ What Stays the Same

- All API endpoints (no changes)
- Request/Response models
- JWT authentication
- Password hashing (bcrypt)
- Azure OpenAI integration
- Speech synthesis (Polly + Azure)
- Transcription service
- Weather API
- Crop prices
- Government schemes
- **Frontend code (no changes needed!)**

## 🔧 Prerequisites

### 1. AWS Credentials
Your `.env` already has these:
```env
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=ap-south-1
```
✅ You're good to go!

### 2. Install boto3
```bash
pip install boto3
```

### 3. Create DynamoDB Tables
```bash
python setup_dynamodb.py
```

This creates:
- `gramvaani_users` - User accounts
- `gramvaani_user_queries` - Query logs

## 📋 Testing Checklist

After switching to DynamoDB, test these:

- [ ] **POST /api/signup** - Create new user
- [ ] **POST /api/login** - Login with credentials
- [ ] **GET /api/me** - Get current user info
- [ ] **POST /process-text** - Send text query
- [ ] **POST /process-audio** - Send audio query
- [ ] **POST /api/weather** - Get weather info
- [ ] **POST /api/crop-prices** - Get crop prices
- [ ] **POST /api/gov-schemes** - Get government schemes
- [ ] **GET /health** - Health check

## 🎯 Recommended Approach

**I recommend Option 2 (Side-by-Side):**

1. ✅ No risk - your MongoDB version keeps running
2. ✅ Test DynamoDB thoroughly on port 8001
3. ✅ Compare performance and functionality
4. ✅ Switch when confident
5. ✅ Easy rollback if needed

## 💡 Benefits of DynamoDB

- **Performance**: Single-digit millisecond latency
- **Scalability**: Auto-scales without configuration
- **Cost**: Pay only for what you use (no idle costs)
- **Availability**: 99.99% SLA with multi-AZ replication
- **Integration**: Native AWS service integration
- **Maintenance**: No server management needed

## 🆘 Troubleshooting

### Error: "Table does not exist"
```bash
python setup_dynamodb.py
```

### Error: "Unable to locate credentials"
Check `.env` has AWS credentials:
```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### Error: "AccessDeniedException"
Verify IAM permissions for DynamoDB:
- dynamodb:GetItem
- dynamodb:PutItem
- dynamodb:CreateTable
- dynamodb:DescribeTable

### Want to rollback?
```bash
cp main_mongodb_backup.py main.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Additional Resources

- **DYNAMODB_MIGRATION_GUIDE.md** - Detailed migration steps
- **MONGODB_VS_DYNAMODB.md** - Complete code comparison
- **QUICK_START.md** - Quick reference guide

## 🔐 Security Notes

- DynamoDB uses IAM for authentication (more secure than connection strings)
- No database credentials in code
- Encryption at rest enabled by default
- VPC endpoints available for private access

## 📊 Cost Comparison

**MongoDB Atlas (Current):**
- M0 Free: Limited to 512MB
- M10 Shared: ~$57/month
- M30 Dedicated: ~$300/month

**DynamoDB (New):**
- Free tier: 25GB storage, 25 WCU, 25 RCU
- Pay-per-request: $1.25 per million writes, $0.25 per million reads
- Estimated cost for your app: ~$5-10/month

## 🎉 Next Steps

1. **Read** QUICK_START.md for immediate action
2. **Setup** DynamoDB tables: `python setup_dynamodb.py`
3. **Test** using Option 2 (side-by-side)
4. **Compare** both versions
5. **Switch** when confident
6. **Celebrate** 🎊

## 📞 Support

If you need help:
1. Check the error message
2. Review DYNAMODB_MIGRATION_GUIDE.md
3. Compare your code with MONGODB_VS_DYNAMODB.md
4. Test with the backup version to isolate issues

---

**Created by**: Amazon Q
**Date**: March 2, 2026
**Status**: Ready to integrate ✅
