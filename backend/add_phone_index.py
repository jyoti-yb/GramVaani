import boto3
from botocore.exceptions import ClientError

def add_phone_number_index():
    """
    Add phone_number Global Secondary Index to gramvaani_users table
    """
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    
    try:
        # Add GSI for phone_number
        response = dynamodb.update_table(
            TableName='gramvaani_users',
            AttributeDefinitions=[
                {
                    'AttributeName': 'phone_number',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': 'phone_number-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'phone_number',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                }
            ]
        )
        print("✓ Adding phone_number index to gramvaani_users table...")
        print("✓ Index creation in progress (takes ~5 minutes)")
        print("✓ You can start using the app, index will be ready soon")
    except ClientError as e:
        if 'ResourceInUseException' in str(e) or 'already exists' in str(e):
            print("✓ phone_number index already exists")
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_phone_number_index()
