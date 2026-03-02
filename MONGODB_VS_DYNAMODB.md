# 📊 MongoDB vs DynamoDB Implementation Comparison

## Import Changes

### MongoDB Version (Current - eshwar branch)
```python
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio
```

### DynamoDB Version (New - sru branch)
```python
import boto3
import uuid
```

---

## Database Initialization

### MongoDB
```python
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://...")
client_mongo = AsyncIOMotorClient(MONGO_URL)
db = client_mongo.gramvani
users_collection = db.user
user_queries_collection = db.user_queries

print("MongoDB connection initialized with gramvani_user")
```

### DynamoDB
```python
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
users_table = dynamodb.Table('gramvaani_users')
queries_table = dynamodb.Table('gramvaani_user_queries')

print("DynamoDB connection initialized")
```

---

## Startup Event

### MongoDB
```python
async def init_db():
    try:
        await client_mongo.admin.command('ping')
        print("MongoDB connection successful")
        
        await users_collection.create_index("email", unique=True)
        await user_queries_collection.create_index("user_email")
        
        test_user = await users_collection.find_one({"email": "test@example.com"})
        if not test_user:
            hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
            await users_collection.insert_one({
                "email": "test@example.com",
                "password": hashed_password.decode('utf-8'),
                "language": "en",
                "location": "Delhi, India",
                "created_at": datetime.utcnow()
            })
            print("Test user created with hashed password")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    await init_db()
```

### DynamoDB
```python
@app.on_event("startup")
async def startup_event():
    print("DynamoDB tables ready")
```

---

## Health Check Endpoint

### MongoDB
```python
@app.get("/health")
async def health():
    try:
        await client_mongo.admin.command('ping')
        user_count = await users_collection.count_documents({})
        test_user_exists = await users_collection.find_one({"email": "test@example.com"}) is not None
        
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "test_user_exists": test_user_exists
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
```

### DynamoDB
```python
@app.get("/health")
async def health():
    try:
        users_table.table_status
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

---

## User Authentication

### MongoDB - get_current_user
```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
```

### DynamoDB - get_current_user
```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## User Signup

### MongoDB
```python
@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "email": user.email,
            "password": hashed_password.decode('utf-8'),
            "language": user.language,
            "location": user.location,
            "created_at": datetime.utcnow()
        }
        
        await users_collection.insert_one(user_doc)
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### DynamoDB
```python
@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        response = users_table.get_item(Key={'email': user.email})
        if response.get('Item'):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        users_table.put_item(Item={
            "email": user.email,
            "password": hashed_password.decode('utf-8'),
            "language": user.language,
            "location": user.location,
            "created_at": datetime.utcnow().isoformat()
        })
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## User Login

### MongoDB
```python
@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        print(f"Login attempt for: {user.email}")
        db_user = await users_collection.find_one({"email": user.email})
        if not db_user:
            print(f"User not found: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = db_user["password"]
        
        if stored_password.startswith('$2b$'):
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                print(f"Invalid password for: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            if user.password != stored_password:
                print(f"Invalid password for: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        print(f"Login successful for: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### DynamoDB
```python
@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        print(f"Login attempt for: {user.email}")
        response = users_table.get_item(Key={'email': user.email})
        db_user = response.get('Item')
        if not db_user:
            print(f"User not found: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = db_user["password"]
        
        if stored_password.startswith('$2b$'):
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                print(f"Invalid password for: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            if user.password != stored_password:
                print(f"Invalid password for: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        print(f"Login successful for: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Query Logging (process-text endpoint)

### MongoDB
```python
@app.post("/process-text")
async def process_text(request: TextRequest, current_user: dict = Depends(get_current_user)):
    try:
        # ... AI processing code ...
        
        # Log query to MongoDB
        await user_queries_collection.insert_one({
            "user_email": current_user["email"],
            "query": request.text,
            "response": response_text,
            "timestamp": datetime.utcnow()
        })
        
        # ... rest of code ...
```

### DynamoDB
```python
@app.post("/process-text")
async def process_text(request: TextRequest, current_user: dict = Depends(get_current_user)):
    try:
        # ... AI processing code ...
        
        # Log query to DynamoDB
        queries_table.put_item(Item={
            "query_id": str(uuid.uuid4()),
            "user_email": current_user["email"],
            "query": request.text,
            "response": response_text,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # ... rest of code ...
```

---

## Query Logging (process-audio endpoint)

### MongoDB
```python
@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    try:
        # ... transcription and AI processing ...
        
        # Log query to MongoDB
        await user_queries_collection.insert_one({
            "user_email": current_user["email"],
            "query": transcript,
            "response": response_text,
            "query_type": "audio",
            "timestamp": datetime.utcnow()
        })
        
        # ... rest of code ...
```

### DynamoDB
```python
@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    try:
        # ... transcription and AI processing ...
        
        # Log query to DynamoDB
        queries_table.put_item(Item={
            "query_id": str(uuid.uuid4()),
            "user_email": current_user["email"],
            "query": transcript,
            "response": response_text,
            "query_type": "audio",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # ... rest of code ...
```

---

## Summary of Key Changes

| Aspect | MongoDB | DynamoDB |
|--------|---------|----------|
| **Import** | `motor.motor_asyncio` | `boto3` |
| **Connection** | `AsyncIOMotorClient` | `boto3.resource('dynamodb')` |
| **Operations** | Async (`await`) | Sync (no `await`) |
| **Insert** | `insert_one()` | `put_item()` |
| **Find** | `find_one()` | `get_item()` |
| **Primary Key** | Auto `_id` | Manual `email` or `query_id` |
| **Datetime** | `datetime.utcnow()` | `datetime.utcnow().isoformat()` |
| **Query ID** | Auto ObjectId | Manual UUID |
| **Indexes** | Created via code | Created via table schema |

---

## Files Modified

1. **backend/main.py** - Main application file
   - Database connection
   - All CRUD operations
   - Query logging

2. **backend/setup_dynamodb.py** - New file for table creation

3. **backend/.env** - AWS credentials needed

---

## No Changes Required

These parts remain the same:
- ✅ All API endpoints
- ✅ Request/Response models
- ✅ Authentication logic (JWT)
- ✅ Password hashing (bcrypt)
- ✅ Azure OpenAI integration
- ✅ Speech synthesis
- ✅ Transcription service
- ✅ Weather API
- ✅ Frontend code
