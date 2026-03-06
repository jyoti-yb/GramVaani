import boto3
import os
from dotenv import load_dotenv
from govt_api_integration import fetch_all_govt_reports
import uuid

load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
community_reports_table = dynamodb.Table('gramvaani_community_reports')

def load_govt_reports_to_db():
    """Load government pest/disease reports into DynamoDB"""
    print("🌾 Loading Government Agricultural Reports into Database\n")
    print("="*60)
    
    # Fetch reports from government sources
    reports = fetch_all_govt_reports()
    
    print("\n" + "="*60)
    print("💾 Storing reports in DynamoDB...")
    print("="*60 + "\n")
    
    loaded_count = 0
    
    for report in reports:
        # Add required fields
        report['report_id'] = str(uuid.uuid4())
        report['user_phone'] = 'govt_api'
        report['language'] = 'en'
        report['description_english'] = report.get('description', '')
        report['validation_count'] = 0
        report['validators'] = []
        
        try:
            community_reports_table.put_item(Item=report)
            loaded_count += 1
            
            if loaded_count % 10 == 0:
                print(f"  ✓ Loaded {loaded_count} reports...")
        except Exception as e:
            print(f"  ✗ Error loading report: {e}")
    
    print(f"\n✅ Successfully loaded {loaded_count} government reports!")
    print("\n📊 Report Breakdown:")
    
    # Count by type
    pest_count = sum(1 for r in reports if r.get('report_type') == 'pest')
    disease_count = sum(1 for r in reports if r.get('report_type') == 'disease')
    market_count = sum(1 for r in reports if r.get('report_type') == 'market_observation')
    
    print(f"   • Pest Reports: {pest_count}")
    print(f"   • Disease Reports: {disease_count}")
    print(f"   • Market Observations: {market_count}")
    print(f"   • Total: {loaded_count}")
    
    print("\n🎯 Data is now available in Community Intelligence page!")

if __name__ == "__main__":
    load_govt_reports_to_db()
