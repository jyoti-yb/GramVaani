import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

async def migrate_passwords():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client.gramvani
    users_collection = db.user
    
    users = await users_collection.find().to_list(length=1000)
    
    for user in users:
        password = user.get('password', '')
        
        # Skip if already hashed
        if password.startswith('$2b$'):
            print(f"✓ {user['email']} - already hashed")
            continue
        
        # Hash the plain text password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Update in database
        await users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'password': hashed.decode('utf-8')}}
        )
        
        print(f"✓ {user['email']} - password hashed")
    
    print(f"\n✅ Migration complete! {len(users)} users processed.")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_passwords())
