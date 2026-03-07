import os
from pymongo import MongoClient
from datetime import datetime
from andhra_pradesh_complete import ANDHRA_PRADESH_COMPLETE
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URL"))
db = mongo_client.gramvani
hyperlocal_collection = db.hyperlocal_context

def load_andhra_pradesh():
    """Load all 26 Andhra Pradesh districts"""
    print("🌾 Loading Complete Andhra Pradesh Data (26 Districts)\n")
    
    # Remove existing AP data
    hyperlocal_collection.delete_many({"state": "Andhra Pradesh"})
    
    count = 0
    for district, data in ANDHRA_PRADESH_COMPLETE.items():
        doc = {
            "state": "Andhra Pradesh",
            "district": district,
            "soil_type": data["soil"],
            "rainfall": data["rainfall"],
            "crops": data["crops"],
            "pest_alerts": [],
            "created_at": datetime.utcnow(),
            "data_source": "AP State Agriculture Department"
        }
        hyperlocal_collection.insert_one(doc)
        count += 1
        print(f"  ✓ {district}")
    
    print(f"\n✅ Loaded all {count} districts of Andhra Pradesh!")
    return count

if __name__ == "__main__":
    load_andhra_pradesh()
