#!/usr/bin/env python3
"""
Fix MongoDB duplicate key errors by cleaning up indexes and data.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://gramvani_user:GramVaani123!@firewall.jchsp.mongodb.net/gramvani?retryWrites=true&w=majority")


async def main():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.gramvani
    users_collection = db.user

    try:
        # List existing indexes
        print("\nExisting indexes:")
        async for index in users_collection.list_indexes():
            print(f"  - {index['name']}: {index['key']}")

        # Drop the email unique index if it exists
        print("\nDropping email_1 index if it exists...")
        try:
            await users_collection.drop_index("email_1")
            print("  ✓ Dropped email_1 index")
        except Exception as e:
            print(f"  - email_1 index not found or already dropped: {e}")

        # Remove documents with null or missing email
        print("\nRemoving documents with null/missing email...")
        result = await users_collection.delete_many({"email": None})
        print(f"  ✓ Deleted {result.deleted_count} documents with null email")

        result = await users_collection.delete_many({"email": {"$exists": False}})
        print(f"  ✓ Deleted {result.deleted_count} documents without email field")

        # Recreate the unique email index
        print("\nRecreating email unique index...")
        await users_collection.create_index("email", unique=True)
        print("  ✓ Created unique email index")

        # List indexes again
        print("\nUpdated indexes:")
        async for index in users_collection.list_indexes():
            print(f"  - {index['name']}: {index['key']}")

        print("\n✅ MongoDB index fix completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
