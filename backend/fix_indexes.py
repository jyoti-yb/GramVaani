import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def fix_indexes():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client.gramvani
    users_collection = db.user
    
    # Get all indexes
    indexes = await users_collection.index_information()
    print("Current indexes:")
    for name, info in indexes.items():
        print(f"  - {name}: {info}")
    
    # Drop phone_number index if it exists
    if 'phone_number_1' in indexes:
        await users_collection.drop_index('phone_number_1')
        print("\n✅ Dropped phone_number_1 index")
    
    # Ensure email index exists
    await users_collection.create_index("email", unique=True)
    print("✅ Email index ensured")
    
    print("\n✅ Index fix complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())
