import boto3
from boto3.dynamodb.conditions import Key

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
queries_table = dynamodb.Table('gramvaani_user_querie')

# Your phone number
user_phone = "+919876543210"  # Replace with your phone number

print(f"\n🔍 Checking queries for: {user_phone}\n")

try:
    # Query using the GSI
    response = queries_table.query(
        IndexName='user_phone-index',
        KeyConditionExpression=Key('user_phone').eq(user_phone)
    )
    
    items = response.get('Items', [])
    
    if items:
        print(f"✅ Found {len(items)} queries:\n")
        for i, item in enumerate(items, 1):
            print(f"Query #{i}:")
            print(f"  Query ID: {item.get('query_id')}")
            print(f"  Query: {item.get('query')}")
            print(f"  Response: {item.get('response')[:100]}...")
            print(f"  Type: {item.get('query_type', 'N/A')}")
            print(f"  Time: {item.get('timestamp')}")
            print()
    else:
        print("❌ No queries found in database")
        print("\nPossible reasons:")
        print("1. You haven't sent any queries yet")
        print("2. You're using main.py (MongoDB) instead of main_dynamodb.py")
        print("3. The table was just created and is empty")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("1. Table 'gramvaani_user_querie' exists")
    print("2. AWS credentials are correct")
    print("3. Run: python setup_dynamodb.py first")
