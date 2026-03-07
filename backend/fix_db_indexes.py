from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_indexes():
    MONGO_URL = os.getenv("MONGO_URL")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.gramvani
    users_collection = db.user
    
    try:
        # List all indexes
        indexes = await users_collection.list_indexes().to_list(length=100)
        print("Current indexes:")
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # Drop phone_number index if it exists
        try:
            await users_collection.drop_index("phone_number_1")
            print("\n✅ Dropped phone_number_1 index")
        except Exception as e:
            print(f"\n⚠️  phone_number_1 index not found or already dropped: {e}")
        
        # Recreate only email index
        await users_collection.drop_indexes()
        await users_collection.create_index("email", unique=True)
        print("✅ Recreated email index")
        
        print("\n✅ Database indexes fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())
