# AWS Console Setup Guide for GramVaani

## Prerequisites
- AWS Account with access to ap-south-1 (Mumbai) region
- Your IAM user: `gramvaani-app-user`

---

## Step 1: Create DynamoDB Tables

### 1.1 Create Users Table
1. Go to **AWS Console** → Search "DynamoDB" → Click **DynamoDB**
2. Click **"Create table"**
3. Configure:
   - **Table name**: `gramvaani_users`
   - **Partition key**: `phone` (String)
   - Leave sort key empty
4. Under **Table settings**, select **Default settings**
5. Click **"Create table"**

### 1.2 Create OTP Table
1. Click **"Create table"** again
2. Configure:
   - **Table name**: `gramvaani_otp`
   - **Partition key**: `phone` (String)
   - Leave sort key empty
3. Click **"Create table"**
4. After table is created, go to the table → **Additional settings** tab
5. Enable **TTL** on attribute: `expires_at`

### 1.3 Create User Queries Table
1. Click **"Create table"**
2. Configure:
   - **Table name**: `gramvaani_user_queries`
   - **Partition key**: `user_phone` (String)
   - **Sort key**: `timestamp` (String)
3. Click **"Create table"**

---

## Step 2: Setup SNS for SMS

### 2.1 Configure SMS Settings
1. Go to **AWS Console** → Search "SNS" → Click **Simple Notification Service**
2. In the left menu, click **"Text messaging (SMS)"**
3. Click **"Edit"** in the SMS sandbox section
4. Configure:
   - **Default message type**: `Transactional` (important for OTPs)
   - **Account spend limit**: Set a reasonable limit (e.g., $10)

### 2.2 Verify Phone Number (Sandbox Mode)
**Note**: In SMS sandbox mode, you can only send SMS to verified phone numbers.

1. In **Text messaging (SMS)**, click **"Add phone number"**
2. Enter your phone number with country code: `+919876543210`
3. Click **"Add phone number"**
4. Enter the verification code you receive
5. Your number is now verified for testing

### 2.3 Request Production Access (Optional - for production)
To send SMS to any phone number:
1. Go to **Text messaging (SMS)** → **"Request production access"**
2. Fill out the form with your business details
3. Wait for AWS approval (usually 1-2 business days)

---

## Step 3: Update IAM Permissions

Your IAM user needs these permissions. Go to IAM → Users → gramvaani-app-user → Add permissions:

### Policy: DynamoDB Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:ap-south-1:*:table/gramvaani_users",
                "arn:aws:dynamodb:ap-south-1:*:table/gramvaani_otp",
                "arn:aws:dynamodb:ap-south-1:*:table/gramvaani_user_queries"
            ]
        }
    ]
}
```

### Policy: SNS SMS Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": "*"
        }
    ]
}
```

### How to Add These Policies:
1. Go to **IAM** → **Users** → **gramvaani-app-user**
2. Click **"Add permissions"** → **"Create inline policy"**
3. Click **"JSON"** tab
4. Paste the policy above
5. Name it: `GramVaaniDynamoDBAccess` or `GramVaaniSNSAccess`
6. Click **"Create policy"**

---

## Step 4: Verify Setup

After completing all steps, test the health endpoint:

```bash
curl https://sns-phone-auth.preview.emergentagent.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "DynamoDB connected",
  "sms_service": "SNS configured",
  "region": "ap-south-1"
}
```

---

## Testing the Flow

1. **Open the app**: https://sns-phone-auth.preview.emergentagent.com
2. **Enter your verified phone number**: +91XXXXXXXXXX
3. **Click "Get OTP"**
4. **Check your phone** for the OTP
5. **Enter the OTP** and complete signup/login

---

## Troubleshooting

### "AccessDeniedException" errors
- Check IAM permissions are correctly attached
- Verify the table names match exactly

### SMS not received
- Confirm phone number is verified in SMS sandbox
- Check SNS spending limits
- Verify phone number format (+91XXXXXXXXXX)

### Table not found
- Verify table names: `gramvaani_users`, `gramvaani_otp`, `gramvaani_user_queries`
- Confirm tables are in `ap-south-1` region
