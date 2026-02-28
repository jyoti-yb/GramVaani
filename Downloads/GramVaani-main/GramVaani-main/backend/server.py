from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
import os
import base64
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import requests
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import re
import uuid
from decimal import Decimal

# Optional imports
try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None
    print("OpenAI not installed - AI features disabled")

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None
    print("Azure Speech SDK not installed - TTS for regional languages disabled")

load_dotenv()

app = FastAPI()

# Import WebSocket handler
from websocket_server import websocket_endpoint

# AWS Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

# DynamoDB setup
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# DynamoDB Tables
users_table = dynamodb.Table('gramvaani_users')
user_queries_table = dynamodb.Table('gramvaani_user_queries')
otp_table = dynamodb.Table('gramvaani_otp')

# SNS Client for SMS
sns_client = boto3.client(
    'sns',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

print(f"AWS DynamoDB and SNS initialized in region: {AWS_REGION}")

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://lazypandaa.github.io",
    "https://eshwarkrishna.me",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI (optional - used for AI responses)
azure_client = None
if AzureOpenAI and os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
    try:
        azure_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        )
        print("Azure OpenAI initialized successfully")
    except Exception as e:
        print(f"Azure OpenAI initialization failed: {e}")
else:
    print("Azure OpenAI not configured - AI features will use mock responses")

# Amazon Polly
polly_client = boto3.client(
    "polly", 
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Amazon Transcribe (optional)
transcribe_service = None
try:
    from transcribe_service import TranscribeService
    if os.getenv("AWS_S3_BUCKET"):
        transcribe_service = TranscribeService()
        print("TranscribeService initialized")
    else:
        print("AWS_S3_BUCKET not set - TranscribeService disabled")
except Exception as e:
    print(f"TranscribeService not available: {e}")

LANGUAGE_TO_LOCALE = {
    "en": "en-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
}

# Polly for Hindi and English only
POLLY_LANGUAGES = {"en", "hi"}

LANGUAGE_TO_POLLY_VOICE = {
    "en": ("Joanna", "en-US"),
    "hi": ("Aditi", "hi-IN"),
}

# Azure Speech for other Indian languages
AZURE_SPEECH_VOICES = {
    "ta": "ta-IN-ValluvarNeural",
    "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-BashkarNeural",
    "gu": "gu-IN-DhwaniNeural",
    "mr": "mr-IN-AarohiNeural",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
}

# Phone number validation pattern: +91 followed by 10 digits
PHONE_PATTERN = r'^\+91[6-9]\d{9}$'

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number format: +91 followed by 10 digits"""
    return bool(re.match(PHONE_PATTERN, phone))

def generate_otp(length: int = 6) -> str:
    """Generate cryptographically secure OTP"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

def send_sms(phone_number: str, message: str) -> dict:
    """Send SMS using Amazon SNS"""
    try:
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes={
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        print(f"SMS sent to {phone_number}. MessageId: {response['MessageId']}")
        return {"success": True, "message_id": response['MessageId']}
    except ClientError as e:
        print(f"Failed to send SMS: {e}")
        return {"success": False, "error": str(e)}

def synthesize_speech(text: str, language: str) -> Optional[str]:
    """Synthesize speech - returns None if speech services not configured"""
    if not text:
        return None
    
    # Use Polly for Hindi and English
    if language in POLLY_LANGUAGES:
        try:
            voice_config = LANGUAGE_TO_POLLY_VOICE.get(language, ("Joanna", "en-US"))
            voice_id, language_code = voice_config
            
            print(f"Polly TTS: voice={voice_id}, language={language_code}")
            
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice_id,
                LanguageCode=language_code
            )
            audio_data = response["AudioStream"].read()
            return base64.b64encode(audio_data).decode("utf-8")
        except Exception as e:
            print(f"Polly synthesis error: {e}")
            return None
    
    # Use Azure Speech for other Indian languages (if configured)
    else:
        if not speechsdk:
            print("Azure Speech SDK not installed - skipping TTS")
            return None
            
        speech_key = os.getenv("AZURE_SPEECH_KEY")
        speech_region = os.getenv("AZURE_SPEECH_REGION")
        
        if not speech_key or not speech_region:
            print("Azure Speech credentials not configured - skipping TTS")
            return None
            
        try:
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
            voice_name = AZURE_SPEECH_VOICES.get(language, "en-US-JennyNeural")
            speech_config.speech_synthesis_voice_name = voice_name
            speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
            
            print(f"Azure Speech TTS: voice={voice_name}, region={speech_region}")
            
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return base64.b64encode(result.audio_data).decode("utf-8")
            else:
                print(f"Azure Speech synthesis failed: {result.reason}")
                return None
        except Exception as e:
            print(f"Azure Speech synthesis error: {e}")
            return None

# Models with Phone Number validation
class PhoneNumber(BaseModel):
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class UserSignup(BaseModel):
    phone: str
    password: str
    language: str
    location: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class UserLogin(BaseModel):
    phone: str
    password: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class OTPRequest(BaseModel):
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class OTPVerify(BaseModel):
    phone: str
    otp: str
    session_id: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class SignupWithOTP(BaseModel):
    phone: str
    password: str
    language: str
    location: str
    otp: str
    session_id: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class LoginWithOTP(BaseModel):
    phone: str
    password: str
    otp: str
    session_id: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(PHONE_PATTERN, v):
            raise ValueError('Phone number must start with +91 followed by 10 digits (e.g., +919876543210)')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class TextRequest(BaseModel):
    text: str
    language: str = "en"

class WeatherRequest(BaseModel):
    city: Optional[str] = None
    language: str = "en"

class CropPriceRequest(BaseModel):
    crop: str
    market: Optional[str] = None
    language: str = "en"

class SchemeRequest(BaseModel):
    topic: str
    language: str = "en"

class ReverseGeocodeRequest(BaseModel):
    latitude: float
    longitude: float

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        phone = payload.get("sub")
        
        # Get user from DynamoDB
        response = users_table.get_item(Key={'phone': phone})
        user = response.get('Item')
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# DynamoDB helper functions
def store_otp(phone: str, otp_code: str, purpose: str = "login") -> dict:
    """Store OTP in DynamoDB with 10 minute expiry"""
    session_id = str(uuid.uuid4())
    expiration_time = int((datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp())
    
    otp_record = {
        'phone': phone,
        'session_id': session_id,
        'otp_code': otp_code,
        'purpose': purpose,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'expires_at': expiration_time,
        'attempts': 0,
        'verified': False
    }
    
    otp_table.put_item(Item=otp_record)
    return {'session_id': session_id, 'expiry_minutes': 10}

def verify_otp(phone: str, session_id: str, submitted_otp: str) -> dict:
    """Verify OTP from DynamoDB"""
    try:
        response = otp_table.get_item(Key={'phone': phone})
        otp_record = response.get('Item')
        
        if not otp_record:
            return {'success': False, 'error': 'OTP not found. Please request a new OTP.'}
        
        if otp_record.get('session_id') != session_id:
            return {'success': False, 'error': 'Invalid session. Please request a new OTP.'}
        
        if otp_record.get('verified'):
            return {'success': False, 'error': 'OTP already used. Please request a new OTP.'}
        
        # Check expiration
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time > otp_record.get('expires_at', 0):
            return {'success': False, 'error': 'OTP expired. Please request a new OTP.'}
        
        # Check attempts
        attempts = otp_record.get('attempts', 0) + 1
        if attempts > 3:
            return {'success': False, 'error': 'Too many attempts. Please request a new OTP.'}
        
        # Update attempts
        otp_table.update_item(
            Key={'phone': phone},
            UpdateExpression='SET attempts = :attempts',
            ExpressionAttributeValues={':attempts': attempts}
        )
        
        # Verify OTP
        if otp_record['otp_code'] != submitted_otp:
            return {'success': False, 'error': f'Invalid OTP. {3 - attempts} attempts remaining.'}
        
        # Mark as verified
        otp_table.update_item(
            Key={'phone': phone},
            UpdateExpression='SET verified = :verified',
            ExpressionAttributeValues={':verified': True}
        )
        
        return {'success': True, 'message': 'OTP verified successfully'}
    except Exception as e:
        print(f"OTP verification error: {e}")
        return {'success': False, 'error': 'OTP verification failed'}

# Routes
@app.get("/")
async def root():
    return {"message": "Gram Vaani API with DynamoDB and SNS is running"}

@app.get("/health")
@app.get("/api/health")
async def health():
    try:
        # Test DynamoDB connection
        users_table.table_status
        return {
            "status": "healthy",
            "database": "DynamoDB connected",
            "sms_service": "SNS configured",
            "region": AWS_REGION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/api/location")
async def get_location():
    try:
        url = "http://ipapi.co/json/"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "location": f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}"
            }
        else:
            return {"location": "Location not available"}
    except Exception as e:
        print(f"Location API error: {e}")
        return {"location": "Delhi, India"}

@app.post("/api/reverse-geocode")
async def reverse_geocode(request: ReverseGeocodeRequest):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={request.latitude}&lon={request.longitude}&zoom=18&addressdetails=1"
        
        headers = {
            'User-Agent': 'GramVaani-App/1.0 (contact@gramvaani.com)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'address' in data:
                address_parts = data['address']
                
                village = address_parts.get('village', '')
                town = address_parts.get('town', '')
                city = address_parts.get('city', '')
                district = address_parts.get('state_district', '')
                state = address_parts.get('state', '')
                postcode = address_parts.get('postcode', '')
                
                address_components = []
                
                if village:
                    address_components.append(village)
                elif town:
                    address_components.append(town)
                elif city:
                    address_components.append(city)
                    
                if district and district not in address_components:
                    address_components.append(district)
                    
                if state:
                    address_components.append(state)
                    
                if postcode:
                    address_components.append(postcode)
                
                precise_address = ', '.join(filter(None, address_components))
                
                return {
                    "address": precise_address,
                    "coordinates": {
                        "latitude": request.latitude,
                        "longitude": request.longitude
                    }
                }
            else:
                return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}
        else:
            return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}
            
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return {"address": f"Coordinates: {request.latitude:.4f}, {request.longitude:.4f}"}

# OTP Request endpoint - for both signup and login
@app.post("/api/request-otp")
async def request_otp(request: OTPRequest):
    """Request OTP for signup or login"""
    try:
        phone = request.phone
        
        # Generate OTP
        otp_code = generate_otp()
        
        # Store OTP in DynamoDB
        otp_result = store_otp(phone, otp_code)
        
        # Send OTP via SMS
        message = f"Your OTP for GramVaani is {otp_code}. Valid for 10 minutes."
        sms_result = send_sms(phone, message)
        
        if not sms_result['success']:
            raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again.")
        
        return {
            "message": "OTP sent successfully",
            "session_id": otp_result['session_id'],
            "expiry_minutes": otp_result['expiry_minutes']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Request OTP error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Signup with OTP verification
@app.post("/api/signup", response_model=Token)
async def signup(user: SignupWithOTP):
    try:
        # Verify OTP first
        otp_result = verify_otp(user.phone, user.session_id, user.otp)
        if not otp_result['success']:
            raise HTTPException(status_code=400, detail=otp_result['error'])
        
        # Check if user already exists
        response = users_table.get_item(Key={'phone': user.phone})
        if response.get('Item'):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user in DynamoDB
        user_doc = {
            'phone': user.phone,
            'password': hashed_password.decode('utf-8'),
            'language': user.language,
            'location': user.location,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'verified': True
        }
        
        users_table.put_item(Item=user_doc)
        
        # Send success notification
        success_message = "You have successfully signed up for GramVaani. Welcome!"
        send_sms(user.phone, success_message)
        
        access_token = create_access_token(data={"sub": user.phone})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Login with OTP verification
@app.post("/api/login", response_model=Token)
async def login(user: LoginWithOTP):
    try:
        # Verify OTP first
        otp_result = verify_otp(user.phone, user.session_id, user.otp)
        if not otp_result['success']:
            raise HTTPException(status_code=400, detail=otp_result['error'])
        
        print(f"Login attempt for: {user.phone}")
        
        # Get user from DynamoDB
        response = users_table.get_item(Key={'phone': user.phone})
        db_user = response.get('Item')
        
        if not db_user:
            print(f"User not found: {user.phone}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = db_user["password"]
        
        # Check password
        import bcrypt
        if stored_password.startswith('$2b$'):
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                print(f"Invalid password for: {user.phone}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            if user.password != stored_password:
                print(f"Invalid password for: {user.phone}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Send login success notification
        success_message = "You have successfully logged into GramVaani."
        send_sms(user.phone, success_message)
        
        access_token = create_access_token(data={"sub": user.phone})
        print(f"Login successful for: {user.phone}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "phone": current_user["phone"],
        "language": current_user["language"],
        "location": current_user["location"]
    }

@app.post("/process-text")
async def process_text(request: TextRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_location = current_user.get("location", "India")
        print(f"Process text request: {request.text[:50]}...")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. User is in {user_location}."},
                {"role": "user", "content": request.text}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        print(f"AI response generated successfully")
        
        # Log query to DynamoDB
        query_id = str(uuid.uuid4())
        user_queries_table.put_item(Item={
            'user_phone': current_user["phone"],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'query_id': query_id,
            'query': request.text,
            'response': response_text
        })
        
        audio_data = synthesize_speech(response_text, request.language)

        return JSONResponse({
            "response_text": response_text,
            "audio_data": audio_data
        })
    except Exception as e:
        print(f"Process text error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@app.post("/api/weather")
async def get_weather(request: WeatherRequest, current_user: dict = Depends(get_current_user)):
    try:
        city = request.city
        if not city or city == 'current':
            location = current_user.get("location", "Delhi")
            city = location.split(",")[0].strip()
        
        print(f"Weather request for city: {city}, language: {request.language}")
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OpenWeather API key not configured."
            )
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 404:
            location_parts = current_user.get("location", "Delhi").split(",")
            if len(location_parts) > 1:
                fallback_city = location_parts[1].strip()
                res = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?q={fallback_city}&appid={api_key}&units=metric",
                    timeout=10
                )
                if res.status_code == 200:
                    city = fallback_city
        
        if res.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Weather data not found for {city}")
        
        data = res.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        # Use AI to generate response in selected language
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a weather assistant. Provide weather information in {language_name} language ONLY. Be concise and natural."},
                {"role": "user", "content": f"Tell me the weather in {city}: {weather_desc}, temperature {temp}°C, humidity {humidity}%"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Weather response in {language_name}: {response_text}")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Weather error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

@app.post("/api/crop-prices")
async def get_crop_prices(request: CropPriceRequest, current_user: dict = Depends(get_current_user)):
    try:
        market = request.market or current_user.get("location", "Delhi").split(",")[0]
        
        # Simulate crop prices
        base_prices = {
            'wheat': 2000, 'rice': 2400, 'corn': 1600, 'barley': 1800,
            'sugarcane': 5000, 'cotton': 6000, 'soybean': 4400, 'mustard': 5600,
            'onion': 3000, 'potato': 1400, 'tomato': 3600, 'chili': 8000
        }
        
        price = base_prices.get(request.crop.lower(), 2500)
        
        # Use AI to generate response in selected language
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a crop price assistant. Provide crop price information in {language_name} language ONLY. Be concise and natural."},
                {"role": "user", "content": f"Tell me the current price of {request.crop} in {market} market is ₹{price} per quintal"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Crop price response in {language_name}: {response_text}")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gov-schemes")
async def get_gov_schemes(request: SchemeRequest, current_user: dict = Depends(get_current_user)):
    try:
        print(f"Schemes request for topic: {request.topic}, language: {request.language}")
        
        language_name = LANGUAGE_NAMES.get(request.language, "English")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI assistant for rural India. Provide information about government schemes for farmers in {language_name} language ONLY. Be concise and helpful."},
                {"role": "user", "content": f"Tell me about government schemes related to {request.topic}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        print(f"Schemes response in {language_name} generated successfully")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        print(f"Schemes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching schemes: {str(e)}")

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    """
    Transcribe audio using Amazon Transcribe
    """
    if not transcribe_service:
        raise HTTPException(status_code=503, detail="Transcription service not available")
        
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3"]:
            raise HTTPException(status_code=400, detail="Only WAV and MP3 files supported")
        
        audio_bytes = await file.read()
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        
        return JSONResponse({"transcript": transcript})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Transcribe error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), language: str = "hi", current_user: dict = Depends(get_current_user)):
    """
    Process audio file: transcribe using Amazon Transcribe and generate AI response
    """
    if not transcribe_service:
        raise HTTPException(status_code=503, detail="Audio processing service not available")
        
    try:
        print(f"Processing audio file: {file.filename}, language: {language}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3", "webm", "ogg"]:
            file_extension = "wav"
        
        audio_bytes = await file.read()
        print(f"Audio bytes: {len(audio_bytes)}, Language selected: {language}")
        
        # Transcribe using Amazon Transcribe
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        print(f"Transcription successful (language: {language}): {transcript[:100]}...")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Generate AI response using Azure OpenAI
        user_location = current_user.get("location", "India")
        language_name = LANGUAGE_NAMES.get(language, "English")
        
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. User is in {user_location}. IMPORTANT: The user is speaking in {language_name}. You MUST respond ONLY in {language_name} language. Do not use any other language in your response."},
                {"role": "user", "content": transcript}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"AI response generated successfully")
        
        # Log query to DynamoDB
        query_id = str(uuid.uuid4())
        user_queries_table.put_item(Item={
            'user_phone': current_user["phone"],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'query_id': query_id,
            'query': transcript,
            'response': response_text,
            'query_type': 'audio'
        })
        
        audio_data = synthesize_speech(response_text, language)

        return JSONResponse({
            "transcript": transcript,
            "response_text": response_text,
            "audio_data": audio_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Process audio error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)
