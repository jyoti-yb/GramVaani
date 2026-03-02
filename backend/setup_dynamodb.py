import boto3
from botocore.exceptions import ClientError

def setup_dynamodb_tables():
    """
    Setup DynamoDB tables for Gram Vaani application
    """
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    
    # Create users table
    try:
        users_table = dynamodb.create_table(
            TableName='gramvaani_users',
            KeySchema=[
                {
                    'AttributeName': 'phone_number',
                    'KeyType': 'HASH'  # Partition key
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
        print("Creating users table...")
        users_table.wait_until_exists()
        print("✓ Users table created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ Users table already exists")
        else:
            print(f"✗ Error creating users table: {e}")
    
    # Create queries table
    try:
        queries_table = dynamodb.create_table(
            TableName='gramvaani_user_querie',
            KeySchema=[
                {
                    'AttributeName': 'query_id',
                    'KeyType': 'HASH'  # Partition key
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
        print("Creating queries table...")
        queries_table.wait_until_exists()
        print("✓ gramvaani_user_querie table created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ gramvaani_user_querie table already exists")
        else:
            print(f"✗ Error creating queries table: {e}")
    
    # Create sessions table
    try:
        sessions_table = dynamodb.create_table(
            TableName='gramvaani_sessions',
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
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
        print("Creating sessions table...")
        sessions_table.wait_until_exists()
        print("✓ gramvaani_sessions table created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ gramvaani_sessions table already exists")
        else:
            print(f"✗ Error creating sessions table: {e}")
    
    # Create village trust table
    try:
        trust_table = dynamodb.create_table(
            TableName='gramvaani_village_trust',
            KeySchema=[
                {
                    'AttributeName': 'village_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'village_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating village trust table...")
        trust_table.wait_until_exists()
        print("✓ gramvaani_village_trust table created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✓ gramvaani_village_trust table already exists")
        else:
            print(f"✗ Error creating village trust table: {e}")
    
    print("\n✓ DynamoDB setup complete!")

if __name__ == "__main__":
    setup_dynamodb_tables()
