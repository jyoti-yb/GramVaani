import boto3
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'ap-south-1')
)

community_reports_table = dynamodb.Table('gramvaani_community_reports')

# User details from the screenshot
user_phone = "test1772196375@test.com"  # Using email as phone in this case
village_id = "Mumbai"
language = "hi"

# Sample community reports
sample_reports = [
    {
        'report_type': 'pest_sighting',
        'crop': 'wheat',
        'description': 'गेहूं में टिड्डी का हमला देखा गया',
        'description_english': 'Locust attack observed in wheat',
        'severity': 'high',
        'timestamp_offset': 2  # 2 days ago
    },
    {
        'report_type': 'disease',
        'crop': 'rice',
        'description': 'धान में ब्लास्ट रोग के लक्षण',
        'description_english': 'Blast disease symptoms in rice',
        'severity': 'medium',
        'timestamp_offset': 5  # 5 days ago
    },
    {
        'report_type': 'weather_observation',
        'crop': 'general',
        'description': 'अगले सप्ताह भारी बारिश की संभावना',
        'description_english': 'Heavy rainfall expected next week',
        'severity': 'low',
        'timestamp_offset': 1  # 1 day ago
    },
    {
        'report_type': 'success_story',
        'crop': 'tomato',
        'description': 'जैविक खाद से टमाटर की उपज में 30% वृद्धि',
        'description_english': 'Organic fertilizer increased tomato yield by 30%',
        'severity': 'low',
        'timestamp_offset': 3  # 3 days ago
    },
    {
        'report_type': 'pest_sighting',
        'crop': 'cotton',
        'description': 'कपास में सफेद मक्खी का प्रकोप',
        'description_english': 'Whitefly infestation in cotton',
        'severity': 'high',
        'timestamp_offset': 4  # 4 days ago
    }
]

print("Inserting sample community reports...")

for report_data in sample_reports:
    report_id = str(uuid.uuid4())
    timestamp = (datetime.utcnow() - timedelta(days=report_data['timestamp_offset'])).isoformat()
    
    report_item = {
        'report_id': report_id,
        'user_phone': user_phone,
        'village_id': village_id,
        'report_type': report_data['report_type'],
        'crop': report_data['crop'],
        'description': report_data['description'],
        'description_english': report_data['description_english'],
        'severity': report_data['severity'],
        'language': language,
        'timestamp': timestamp,
        'verified': report_data['report_type'] == 'success_story',  # Success story pre-verified
        'validation_count': 3 if report_data['report_type'] == 'success_story' else 0,
        'validators': ['validator1', 'validator2', 'validator3'] if report_data['report_type'] == 'success_story' else []
    }
    
    community_reports_table.put_item(Item=report_item)
    print(f"✓ Inserted {report_data['report_type']} report: {report_data['description_english']}")

print(f"\n✅ Successfully inserted {len(sample_reports)} community reports for user {user_phone}")
print(f"📍 Village: {village_id}")
print("\nYou can now view these reports in the Community Intelligence page!")
