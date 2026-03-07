# 🚀 Quick Start: Integrating DynamoDB Changes

## What Your Friend Did
Your friend (sru branch) replaced MongoDB with DynamoDB for better scalability and AWS integration.

## What You Need to Do

### Option 1: Quick Test (5 minutes)
```bash
cd backend

# 1. Setup DynamoDB tables
python setup_dynamodb.py

# 2. Backup current version
cp main.py main_mongodb_backup.py

# 3. Use DynamoDB version
cp main_dynamodb.py main.py

# 4. Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Keep Both (Recommended)
```bash
cd backend

# 1. Setup DynamoDB tables
python setup_dynamodb.py

# 2. Run MongoDB version (Terminal 1)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Run DynamoDB version (Terminal 2)
uvicorn main_dynamodb:app --reload --host 0.0.0.0 --port 8001

# 4. Test both and choose
```

## What Changed?

### Simple Summary
- **MongoDB** (async) → **DynamoDB** (sync)
- `await users_collection.find_one()` → `users_table.get_item()`
- `await collection.insert_one()` → `table.put_item()`
- Auto ObjectId → Manual UUID for queries
- `datetime.utcnow()` → `datetime.utcnow().isoformat()`

### Files Created for You
1. ✅ `backend/main_dynamodb.py` - DynamoDB version of your app
2. ✅ `backend/setup_dynamodb.py` - Creates DynamoDB tables
3. ✅ `DYNAMODB_MIGRATION_GUIDE.md` - Detailed migration guide
4. ✅ `MONGODB_VS_DYNAMODB.md` - Side-by-side comparison

## Prerequisites Check

### 1. AWS Credentials in .env
```env
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_REGION=ap-south-1
```
✅ You already have these!

### 2. DynamoDB Tables
Run once:
```bash
python setup_dynamodb.py
```

## Testing Checklist
After switching to DynamoDB, test:
- [ ] Signup new user
- [ ] Login existing user
- [ ] Send text query
- [ ] Send audio query
- [ ] Check weather
- [ ] Check crop prices

## If Something Breaks
```bash
# Restore MongoDB version
cp main_mongodb_backup.py main.py

# Restart server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Why DynamoDB?
- ⚡ Faster (single-digit ms latency)
- 📈 Auto-scaling
- 💰 Pay only for what you use
- 🔒 Built-in AWS security
- 🌍 Multi-region replication

## Need Help?
1. Read `DYNAMODB_MIGRATION_GUIDE.md` for detailed steps
2. Check `MONGODB_VS_DYNAMODB.md` for code comparisons
3. Your current MongoDB version is safe in `main_mongodb_backup.py`

## Current Status
- ✅ Your eshwar branch: MongoDB (working)
- ✅ Friend's sru branch: DynamoDB (working)
- ✅ Migration files: Created
- ⏳ Your choice: Test and decide!

---

**Recommendation**: Use Option 2 (keep both) to test DynamoDB without risk. Once confident, switch to DynamoDB permanently.
