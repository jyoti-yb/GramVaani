import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

def create_community_reports_table():
    try:
        table = dynamodb.create_table(
            TableName='gramvaani_community_reports',
            KeySchema=[
                {'AttributeName': 'report_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'report_id', 'AttributeType': 'S'},
                {'AttributeName': 'village_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'report_type', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'village_id-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'village_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'report_type-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'report_type', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print("✅ Community reports table created successfully")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("✅ Community reports table already exists")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_community_reports_table()
