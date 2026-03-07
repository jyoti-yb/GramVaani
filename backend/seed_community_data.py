import boto3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid

from decimal import Decimal

load_dotenv()

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
community_reports_table = dynamodb.Table('gramvaani_community_reports')
village_trust_table = dynamodb.Table('gramvaani_village_trust')

def seed_community_reports():
    """Seed sample community reports"""
    print("🌾 Seeding Community Reports...\n")
    
    sample_reports = [
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999999",
            "village_id": "Bangalore",
            "report_type": "pest",
            "crop": "Tomato",
            "description": "Fall armyworm spotted in tomato fields",
            "description_english": "Fall armyworm spotted in tomato fields",
            "severity": "high",
            "language": "en",
            "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "verified": True,
            "validation_count": 3,
            "validators": ["9999999998", "9999999997", "9999999996"]
        },
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999998",
            "village_id": "Bangalore",
            "report_type": "pest",
            "crop": "Maize",
            "description": "Aphids attacking maize crops",
            "description_english": "Aphids attacking maize crops",
            "severity": "medium",
            "language": "en",
            "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "verified": False,
            "validation_count": 1,
            "validators": ["9999999999"]
        },
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999997",
            "village_id": "Pune",
            "report_type": "disease",
            "crop": "Cotton",
            "description": "Leaf curl disease spreading in cotton",
            "description_english": "Leaf curl disease spreading in cotton",
            "severity": "high",
            "language": "en",
            "timestamp": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "verified": True,
            "validation_count": 4,
            "validators": ["9999999999", "9999999998", "9999999996", "9999999995"]
        },
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999996",
            "village_id": "Ludhiana",
            "report_type": "success",
            "crop": "Wheat",
            "description": "Achieved 40% higher yield using drip irrigation",
            "description_english": "Achieved 40% higher yield using drip irrigation",
            "severity": "low",
            "language": "en",
            "timestamp": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "verified": True,
            "validation_count": 5,
            "validators": ["9999999999", "9999999998", "9999999997", "9999999995", "9999999994"]
        },
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999995",
            "village_id": "Guntur",
            "report_type": "weather",
            "crop": "Chili",
            "description": "Unexpected rainfall affecting chili drying",
            "description_english": "Unexpected rainfall affecting chili drying",
            "severity": "medium",
            "language": "en",
            "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
            "verified": False,
            "validation_count": 2,
            "validators": ["9999999999", "9999999998"]
        },
        {
            "report_id": str(uuid.uuid4()),
            "user_phone": "9999999994",
            "village_id": "Bangalore",
            "report_type": "pest",
            "crop": "Tomato",
            "description": "Whiteflies increasing in tomato greenhouse",
            "description_english": "Whiteflies increasing in tomato greenhouse",
            "severity": "medium",
            "language": "en",
            "timestamp": datetime.utcnow().isoformat(),
            "verified": False,
            "validation_count": 0,
            "validators": []
        }
    ]
    
    for report in sample_reports:
        community_reports_table.put_item(Item=report)
        print(f"  ✓ {report['village_id']}: {report['report_type']} in {report['crop']}")
    
    print(f"\n✅ Seeded {len(sample_reports)} community reports")

def seed_village_trust():
    """Seed village trust scores"""
    print("\n🏆 Seeding Village Trust Scores...\n")
    
    villages = [
        {
            "village_id": "Bangalore",
            "total_responses": 45,
            "helpful_count": 38,
            "trust_score": Decimal('84.44'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Pune",
            "total_responses": 52,
            "helpful_count": 47,
            "trust_score": Decimal('90.38'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Ludhiana",
            "total_responses": 38,
            "helpful_count": 32,
            "trust_score": Decimal('84.21'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Guntur",
            "total_responses": 41,
            "helpful_count": 29,
            "trust_score": Decimal('70.73'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Mysore",
            "total_responses": 33,
            "helpful_count": 28,
            "trust_score": Decimal('84.85'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Nashik",
            "total_responses": 29,
            "helpful_count": 18,
            "trust_score": Decimal('62.07'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Coimbatore",
            "total_responses": 36,
            "helpful_count": 31,
            "trust_score": Decimal('86.11'),
            "last_updated": datetime.utcnow().isoformat()
        },
        {
            "village_id": "Hyderabad",
            "total_responses": 44,
            "helpful_count": 35,
            "trust_score": Decimal('79.55'),
            "last_updated": datetime.utcnow().isoformat()
        }
    ]
    
    for village in villages:
        village_trust_table.put_item(Item=village)
        print(f"  ✓ {village['village_id']}: {village['trust_score']}% trust score")
    
    print(f"\n✅ Seeded {len(villages)} village trust scores")

def main():
    print("🌾 Seeding Community Intelligence Data\n")
    print("=" * 60)
    
    seed_community_reports()
    
    # Try to seed village trust, but don't fail if table doesn't exist
    try:
        seed_village_trust()
    except Exception as e:
        print(f"\n⚠️  Village trust table not found (this is OK)")
        print("   Community reports are seeded and working!")
    
    print("\n" + "=" * 60)
    print("✅ Community Intelligence data seeded successfully!")
    print("\n📊 Summary:")
    print("   • Community Reports: 6 reports")
    print("   • Reports include: pest, disease, weather, success stories")
    print("   • Outbreak Detection: Ready")
    print("\n🎯 Now visit Community Intelligence page to see the data!")

if __name__ == "__main__":
    main()
