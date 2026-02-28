#!/usr/bin/env python3
"""
Test MongoDB connectivity for Gram Vaani project
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def test_mongodb():
    """Test MongoDB connection and basic operations"""
    
    # Get MongoDB URL from environment or use default
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "gramvaani")
    
    print(f"Testing MongoDB connection to: {mongodb_url}")
    print(f"Database: {database_name}")
    
    try:
        # Create client
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test collections
        users_collection = db.users
        queries_collection = db.queries
        
        # Create indexes
        await users_collection.create_index("email", unique=True)
        await queries_collection.create_index("user_email")
        print("✅ Indexes created successfully!")
        
        # Test insert
        test_doc = {
            "test": True,
            "timestamp": datetime.utcnow(),
            "message": "MongoDB test successful"
        }
        
        result = await db.test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Test find
        found_doc = await db.test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test document retrieved: {found_doc['message']}")
        
        # Clean up test document
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Check existing collections
        collections = await db.list_collection_names()
        print(f"✅ Existing collections: {collections}")
        
        # Check user count
        user_count = await users_collection.count_documents({})
        print(f"✅ Current user count: {user_count}")
        
        client.close()
        print("✅ All MongoDB tests passed!")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run test
    success = asyncio.run(test_mongodb())
    exit(0 if success else 1)