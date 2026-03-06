import os
from pymongo import MongoClient
from datetime import datetime
from india_complete_data import INDIA_AGRICULTURAL_DATA, INDIA_SUCCESS_STORIES
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")
client = MongoClient(mongo_url)
db = client.gramvani

hyperlocal_collection = db.hyperlocal_context
success_stories_collection = db.success_stories

def setup_complete_india_data():
    """Load complete India agricultural data"""
    print("🌾 Loading Complete India Agricultural Data\n")
    
    # Clear existing
    hyperlocal_collection.delete_many({})
    success_stories_collection.delete_many({})
    
    # Load hyperlocal data
    print("Loading hyperlocal data...")
    count = 0
    for state, state_data in INDIA_AGRICULTURAL_DATA.items():
        for district, district_data in state_data["districts"].items():
            doc = {
                "state": state,
                "district": district,
                "soil_type": district_data["soil"],
                "rainfall": district_data["rainfall"],
                "crops": district_data["crops"],
                "pest_alerts": [],
                "created_at": datetime.utcnow(),
                "data_source": "ICAR + State Agriculture Departments"
            }
            hyperlocal_collection.insert_one(doc)
            count += 1
            print(f"  ✓ {district}, {state}")
    
    # Create indexes
    hyperlocal_collection.create_index([("state", 1), ("district", 1)])
    print(f"\n✅ Loaded {count} districts across India")
    
    # Load success stories
    print("\nLoading success stories...")
    for story in INDIA_SUCCESS_STORIES:
        story["created_at"] = datetime.utcnow()
        story["verified"] = True
        success_stories_collection.insert_one(story)
        print(f"  ✓ {story['farmer']} - {story['location']}")
    
    success_stories_collection.create_index([("location", 1)])
    print(f"\n✅ Loaded {len(INDIA_SUCCESS_STORIES)} success stories")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print(f"📊 Total Districts: {count}")
    print(f"📊 Total States: {len(INDIA_AGRICULTURAL_DATA)}")
    print(f"📊 Success Stories: {len(INDIA_SUCCESS_STORIES)}")
    print("="*60)

if __name__ == "__main__":
    setup_complete_india_data()
