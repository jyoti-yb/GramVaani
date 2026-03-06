import os
from pymongo import MongoClient
from datetime import datetime
from hyperlocal_data import HYPERLOCAL_DATA, SUCCESS_STORIES
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)
db = client.gramvani

# Collections
hyperlocal_collection = db.hyperlocal_context
success_stories_collection = db.success_stories
pest_outbreaks_collection = db.pest_outbreaks

def seed_hyperlocal_data():
    """Seed hyperlocal agricultural data"""
    print("Seeding hyperlocal data...")
    
    # Clear existing data
    hyperlocal_collection.delete_many({})
    
    for state, state_data in HYPERLOCAL_DATA.items():
        for district, district_data in state_data["districts"].items():
            doc = {
                "state": state,
                "district": district,
                "soil_type": district_data["soil_type"],
                "rainfall": district_data["rainfall"],
                "crops": district_data["crops"],
                "pest_alerts": district_data.get("pest_alerts", []),
                "created_at": datetime.utcnow()
            }
            hyperlocal_collection.insert_one(doc)
            print(f"✓ Added {district}, {state}")
    
    # Create indexes
    hyperlocal_collection.create_index([("state", 1), ("district", 1)])
    print(f"✓ Seeded {hyperlocal_collection.count_documents({})} locations")

def seed_success_stories():
    """Seed farmer success stories"""
    print("\nSeeding success stories...")
    
    success_stories_collection.delete_many({})
    
    for story in SUCCESS_STORIES:
        story["created_at"] = datetime.utcnow()
        story["verified"] = True
        success_stories_collection.insert_one(story)
        print(f"✓ Added story: {story['farmer']} - {story['location']}")
    
    success_stories_collection.create_index([("location", 1)])
    print(f"✓ Seeded {success_stories_collection.count_documents({})} success stories")

if __name__ == "__main__":
    print("🌾 Setting up Hyperlocal Context Database\n")
    seed_hyperlocal_data()
    seed_success_stories()
    print("\n✅ Setup complete!")
