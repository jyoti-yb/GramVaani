from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def create_test_user():
    MONGO_URL = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.gramvani
    users_collection = db.user
    
    try:
        # Check if test user exists
        test_user = await users_collection.find_one({"email": "test@example.com"})
        
        if test_user:
            print("✅ Test user already exists!")
            print("="*60)
            print("Email:    test@example.com")
            print("Password: password123")
            print("Language: en")
            print("Location: Delhi, India")
            print("="*60)
        else:
            # Create test user
            await users_collection.insert_one({
                "email": "test@example.com",
                "password": "password123",
                "language": "en",
                "location": "Delhi, India",
                "created_at": datetime.utcnow()
            })
            print("✅ Test user created!")
            print("="*60)
            print("Email:    test@example.com")
            print("Password: password123")
            print("Language: en")
            print("Location: Delhi, India")
            print("="*60)
        
        # Create Telugu test user
        telugu_user = await users_collection.find_one({"email": "telugu@test.com"})
        if not telugu_user:
            await users_collection.insert_one({
                "email": "telugu@test.com",
                "password": "Telugu@123",
                "language": "te",
                "location": "Hyderabad, Telangana",
                "created_at": datetime.utcnow()
            })
            print("\n✅ Telugu test user created!")
            print("="*60)
            print("Email:    telugu@test.com")
            print("Password: Telugu@123")
            print("Language: te (Telugu)")
            print("Location: Hyderabad, Telangana")
            print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
