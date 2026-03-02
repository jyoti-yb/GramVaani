# 🔄 MongoDB to DynamoDB Migration Guide

## Overview
This guide helps you integrate DynamoDB changes from the `sru` branch into your `eshwar` branch without breaking existing functionality.

## Key Changes Summary

### 1. Database Layer Changes
- **MongoDB** → **DynamoDB**
- Async operations → Sync operations
- Collection-based → Table-based
- ObjectId → UUID for query IDs

### 2. Main Changes in Code

#### Database Connection
**MongoDB (Current):**
```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL")
client_mongo = AsyncIOMotorClient(MONGO_URL)
db = client_mongo.gramvani
users_collection = db.user
user_queries_collection = db.user_queries
```

**DynamoDB (New):**
```python
import boto3
import uuid

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
users_table = dynamodb.Table('gramvaani_users')
queries_table = dynamodb.Table('gramvaani_user_queries')
```

#### User Signup
**MongoDB:**
```python
await users_collection.insert_one({
    "email": user.email,
    "password": hashed_password.decode('utf-8'),
    "language": user.language,
    "location": user.location,
    "created_at": datetime.utcnow()
})
```

**DynamoDB:**
```python
users_table.put_item(Item={
    "email": user.email,
    "password": hashed_password.decode('utf-8'),
    "language": user.language,
    "location": user.location,
    "created_at": datetime.utcnow().isoformat()
})
```

#### User Login
**MongoDB:**
```python
db_user = await users_collection.find_one({"email": user.email})
```

**DynamoDB:**
```python
response = users_table.get_item(Key={'email': user.email})
db_user = response.get('Item')
```

#### Query Logging
**MongoDB:**
```python
await user_queries_collection.insert_one({
    "user_email": current_user["email"],
    "query": request.text,
    "response": response_text,
    "timestamp": datetime.utcnow()
})
```

**DynamoDB:**
```python
queries_table.put_item(Item={
    "query_id": str(uuid.uuid4()),
    "user_email": current_user["email"],
    "query": request.text,
    "response": response_text,
    "timestamp": datetime.utcnow().isoformat()
})
```

## Migration Steps

### Option 1: Quick Switch (Recommended for Testing)

1. **Backup your current main.py:**
```bash
cd backend
cp main.py main_mongodb.py
```

2. **Setup DynamoDB tables:**
```bash
python setup_dynamodb.py
```

3. **Switch to DynamoDB version:**
```bash
cp main_dynamodb.py main.py
```

4. **Test the application:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **If issues occur, rollback:**
```bash
cp main_mongodb.py main.py
```

### Option 2: Gradual Migration (Recommended for Production)

Create a hybrid version that supports both databases with a configuration flag.

1. **Add to .env:**
```env
DATABASE_TYPE=mongodb  # or dynamodb
```

2. **Modify main.py to support both:**
```python
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mongodb")

if DATABASE_TYPE == "dynamodb":
    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    users_table = dynamodb.Table('gramvaani_users')
    queries_table = dynamodb.Table('gramvaani_user_queries')
else:
    # MongoDB setup
    MONGO_URL = os.getenv("MONGO_URL")
    client_mongo = AsyncIOMotorClient(MONGO_URL)
    db = client_mongo.gramvani
    users_collection = db.user
    user_queries_collection = db.user_queries
```

### Option 3: Side-by-Side Testing

1. **Keep both versions:**
   - `main.py` - MongoDB version (current)
   - `main_dynamodb.py` - DynamoDB version (new)

2. **Run on different ports:**
```bash
# Terminal 1 - MongoDB version
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - DynamoDB version
uvicorn main_dynamodb:app --reload --host 0.0.0.0 --port 8001
```

3. **Test both versions and compare**

## Prerequisites

### AWS Credentials
Ensure your `.env` has AWS credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
```

### DynamoDB Tables
Run the setup script to create tables:
```bash
python setup_dynamodb.py
```

## Key Differences to Note

### 1. Async vs Sync
- **MongoDB**: Uses `await` for all database operations
- **DynamoDB**: Synchronous operations (no `await`)

### 2. Date Handling
- **MongoDB**: Stores `datetime.utcnow()` directly
- **DynamoDB**: Requires `.isoformat()` conversion

### 3. Primary Keys
- **MongoDB**: Auto-generated `_id` (ObjectId)
- **DynamoDB**: Must specify partition key (email for users, query_id for queries)

### 4. Queries
- **MongoDB**: Flexible queries with find_one, find, etc.
- **DynamoDB**: Key-based access with get_item, query, scan

## Testing Checklist

After migration, test these endpoints:

- [ ] `POST /api/signup` - User registration
- [ ] `POST /api/login` - User authentication
- [ ] `GET /api/me` - Get current user
- [ ] `POST /process-text` - Text processing with query logging
- [ ] `POST /process-audio` - Audio processing with query logging
- [ ] `POST /api/weather` - Weather information
- [ ] `POST /api/crop-prices` - Crop prices
- [ ] `POST /api/gov-schemes` - Government schemes
- [ ] `GET /health` - Health check

## Rollback Plan

If you encounter issues:

1. **Stop the server** (Ctrl+C)
2. **Restore MongoDB version:**
```bash
cp main_mongodb.py main.py
```
3. **Restart server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Data Migration (Optional)

If you want to migrate existing MongoDB data to DynamoDB:

```python
# migration_script.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import boto3
from datetime import datetime

async def migrate_data():
    # MongoDB connection
    mongo_client = AsyncIOMotorClient("your_mongo_url")
    db = mongo_client.gramvani
    
    # DynamoDB connection
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    users_table = dynamodb.Table('gramvaani_users')
    
    # Migrate users
    async for user in db.user.find():
        users_table.put_item(Item={
            "email": user["email"],
            "password": user["password"],
            "language": user["language"],
            "location": user["location"],
            "created_at": user["created_at"].isoformat() if isinstance(user["created_at"], datetime) else user["created_at"]
        })
        print(f"Migrated user: {user['email']}")

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

## Benefits of DynamoDB

1. **Scalability**: Auto-scaling without manual intervention
2. **Performance**: Single-digit millisecond latency
3. **Cost**: Pay-per-request pricing (no idle costs)
4. **Availability**: Multi-AZ replication by default
5. **Integration**: Native AWS service integration

## Support

If you encounter issues:
1. Check AWS credentials in `.env`
2. Verify DynamoDB tables exist: `python setup_dynamodb.py`
3. Check CloudWatch logs for DynamoDB errors
4. Ensure IAM permissions for DynamoDB access

## Files Created

- `backend/main_dynamodb.py` - DynamoDB version of main.py
- `backend/setup_dynamodb.py` - DynamoDB table setup script
- `DYNAMODB_MIGRATION_GUIDE.md` - This guide

## Next Steps

1. Review the changes in `main_dynamodb.py`
2. Setup DynamoDB tables using `setup_dynamodb.py`
3. Choose a migration strategy (Option 1, 2, or 3)
4. Test thoroughly before deploying to production
5. Update your deployment scripts if needed
