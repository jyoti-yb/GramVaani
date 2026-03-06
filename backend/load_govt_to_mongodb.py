import os
from pymongo import MongoClient
from dotenv import load_dotenv
from govt_api_integration import fetch_all_govt_reports
from datetime import datetime

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URL"))
db = mongo_client.gramvani

# MongoDB collections
pest_reports_collection = db.pest_reports
disease_reports_collection = db.disease_reports
market_reports_collection = db.market_reports

def load_govt_data_to_mongodb():
    """Load government agricultural data into MongoDB"""
    print("🌾 Loading Government Data into MongoDB\n")
    print("="*60)
    
    # Fetch all reports
    reports = fetch_all_govt_reports()
    
    print("\n" + "="*60)
    print("💾 Storing in MongoDB...")
    print("="*60 + "\n")
    
    # Clear existing data
    pest_reports_collection.delete_many({})
    disease_reports_collection.delete_many({})
    market_reports_collection.delete_many({})
    
    pest_count = 0
    disease_count = 0
    market_count = 0
    
    for report in reports:
        report['created_at'] = datetime.utcnow()
        
        if report['report_type'] == 'pest':
            pest_reports_collection.insert_one(report)
            pest_count += 1
        elif report['report_type'] == 'disease':
            disease_reports_collection.insert_one(report)
            disease_count += 1
        elif report['report_type'] == 'market_observation':
            market_reports_collection.insert_one(report)
            market_count += 1
    
    # Create indexes for fast querying
    pest_reports_collection.create_index([("state", 1), ("crop", 1)])
    disease_reports_collection.create_index([("state", 1), ("crop", 1)])
    market_reports_collection.create_index([("state", 1), ("crop", 1)])
    
    print(f"✅ Pest Reports: {pest_count}")
    print(f"✅ Disease Reports: {disease_count}")
    print(f"✅ Market Reports: {market_count}")
    print(f"\n✅ Total: {pest_count + disease_count + market_count} reports loaded!")
    
    print("\n🎯 Data is now available for LLM responses!")
    
    return {
        'pest': pest_count,
        'disease': disease_count,
        'market': market_count,
        'total': pest_count + disease_count + market_count
    }

if __name__ == "__main__":
    load_govt_data_to_mongodb()
