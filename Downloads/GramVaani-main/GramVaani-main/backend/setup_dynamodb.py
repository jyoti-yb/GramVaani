import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

# Create users table
try:
    users_table = dynamodb.create_table(
        TableName='gramvaani_users',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Creating users table...")
    users_table.wait_until_exists()
    print("Users table created!")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print("Users table already exists")

# Create queries table
try:
    queries_table = dynamodb.create_table(
        TableName='gramvaani_queries',
        KeySchema=[
            {'AttributeName': 'query_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'query_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("Creating queries table...")
    queries_table.wait_until_exists()
    print("Queries table created!")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print("Queries table already exists")

print("DynamoDB setup complete!")
