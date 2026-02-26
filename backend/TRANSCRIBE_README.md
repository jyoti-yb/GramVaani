# Amazon Transcribe Integration

## Setup

### 1. Environment Variables
Add to `.env`:
```
AWS_S3_BUCKET=your-bucket-name-here
```

### 2. AWS Permissions
Ensure IAM user has:
- `AmazonTranscribeFullAccess`
- `AmazonS3FullAccess`

### 3. S3 Bucket
Create bucket in `ap-south-1` region or use existing one.

## API Endpoint

### POST `/api/transcribe`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Form Data:**
- `file`: Audio file (WAV or MP3)
- `language`: Language code (hi, en, mr, bn, ta, te)

**Response:**
```json
{
  "transcript": "transcribed text here"
}
```

**Error Responses:**
- 400: Invalid file format
- 408: Transcription timeout
- 500: AWS service error

## Usage Example

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"file": open("audio.wav", "rb")}
params = {"language": "hi"}

response = requests.post(
    "http://localhost:8000/api/transcribe",
    headers=headers,
    files=files,
    params=params
)

print(response.json()["transcript"])
```

## Architecture

1. **Upload**: Audio file → S3 bucket
2. **Transcribe**: Start AWS Transcribe job
3. **Poll**: Wait for completion (max 60s)
4. **Fetch**: Get transcript from result URI
5. **Cleanup**: Delete S3 file

## Supported Languages

- `en`: English (en-US)
- `hi`: Hindi (hi-IN)
- `mr`: Marathi (mr-IN)
- `bn`: Bengali (bn-IN)
- `ta`: Tamil (ta-IN)
- `te`: Telugu (te-IN)
