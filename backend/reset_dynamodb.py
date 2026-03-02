import boto3
from botocore.exceptions import ClientError

def reset_dynamodb_tables():
    """
    Delete old tables and create new ones with phone_number schema
    """
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    client = boto3.client('dynamodb', region_name='ap-south-1')
    
    # Delete old tables
    print("🗑️  Deleting old tables...")
    
    for table_name in ['gramvaani_users', 'gramvaani_user_querie']:
        try:
            table = dynamodb.Table(table_name)
            table.delete()
            print(f"   Deleting {table_name}...")
            waiter = client.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
            print(f"   ✓ {table_name} deleted")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"   ✓ {table_name} doesn't exist (OK)")
            else:
                print(f"   ✗ Error deleting {table_name}: {e}")
    
    print("\n📦 Creating new tables with phone_number schema...")
    
    # Create users table with phone_number
    try:
        users_table = dynamodb.create_table(
            TableName='gramvaani_users',
            KeySchema=[
                {
                    'AttributeName': 'phone_number',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'phone_number',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("   Creating gramvaani_users...")
        users_table.wait_until_exists()
        print("   ✓ gramvaani_users created")
    except ClientError as e:
        print(f"   ✗ Error: {e}")
    
    # Create queries table
    try:
        queries_table = dynamodb.create_table(
            TableName='gramvaani_user_querie',
            KeySchema=[
                {
                    'AttributeName': 'query_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'query_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_phone',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'user_phone-index',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_phone',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("   Creating gramvaani_user_querie...")
        queries_table.wait_until_exists()
        print("   ✓ gramvaani_user_querie created")
    except ClientError as e:
        print(f"   ✗ Error: {e}")
    
    print("\n✅ DynamoDB reset complete!")
    print("\n⚠️  Note: All old user data has been deleted.")
    print("   You need to sign up again with phone numbers.")

if __name__ == "__main__":
    print("⚠️  WARNING: This will DELETE all existing data!")
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        reset_dynamodb_tables()
    else:
        print("Cancelled.")
