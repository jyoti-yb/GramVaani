from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import AzureOpenAI
import os
import base64
import azure.cognitiveservices.speech as speechsdk
import boto3
from dotenv import load_dotenv
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional
from transcribe_service import TranscribeService
import bcrypt
import uuid
import asyncio
from pymongo import MongoClient
from data_aggregator import fetch_all_context_data, format_context_for_llm, fetch_context_sync

load_dotenv()

# MongoDB connection for hyperlocal data (with connection pooling)
mongo_client = MongoClient(
    os.getenv("MONGO_URL"),
    maxPoolSize=10,  # Connection pool
    minPoolSize=2,
    maxIdleTimeMS=30000,  # 30 seconds
    serverSelectionTimeoutMS=5000  # 5 seconds timeout
)
mongo_db = mongo_client.gramvani
hyperlocal_collection = mongo_db.hyperlocal_context
success_stories_collection = mongo_db.success_stories
pest_outbreaks_collection = mongo_db.pest_outbreaks

app = FastAPI()

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
users_table = dynamodb.Table('gramvaani_users')
queries_table = dynamodb.Table('gramvaani_user_querie')
sessions_table = dynamodb.Table('gramvaani_sessions')
village_trust_table = dynamodb.Table('gramvaani_village_trust')
community_reports_table = dynamodb.Table('gramvaani_community_reports')

print("DynamoDB connection initialized")

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

# Azure OpenAI
azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
)

# Amazon Polly
polly_client = boto3.client("polly", region_name="ap-south-1")

# Amazon Transcribe
transcribe_service = TranscribeService()

# WhatsApp credentials
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

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

def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text to English using Azure OpenAI GPT"""
    if source_lang == "en":
        return text
    try:
        language_name = LANGUAGE_NAMES.get(source_lang, "Unknown")
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following {language_name} text to English. Only return the translated text, nothing else."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def synthesize_speech(text: str, language: str) -> Optional[str]:
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
    
    # Use Azure Speech for other Indian languages
    else:
        try:
            speech_key = os.getenv("AZURE_SPEECH_KEY")
            speech_region = os.getenv("AZURE_SPEECH_REGION")
            
            if not speech_key or not speech_region:
                print("Azure Speech credentials not configured")
                return None
            
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

# Models
class UserSignup(BaseModel):
    phone_number: str
    password: str
    language: str
    location: str

class UserLogin(BaseModel):
    phone_number: str
    password: str

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

class FeedbackRequest(BaseModel):
    query_id: str
    helpful: bool
    feedback_text: Optional[str] = None

class CommunityReportRequest(BaseModel):
    report_type: str  # pest, disease, weather, success
    crop: Optional[str] = None
    description: str
    severity: Optional[str] = "medium"  # low, medium, high
    language: str = "en"

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number = payload.get("sub")
        response = users_table.get_item(Key={'phone_number': phone_number})
        user = response.get('Item')
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.on_event("startup")
async def startup_event():
    print("DynamoDB tables ready")

# Routes
@app.get("/")
async def root():
    return {"message": "Gram Vaani API with DynamoDB is running"}

@app.get("/health")
async def health():
    try:
        users_table.table_status
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# WhatsApp Webhook Verification
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Verify WhatsApp webhook subscription"""
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        print("Webhook verified successfully")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        print("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

# WhatsApp Webhook Handler
@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    try:
        body = await request.json()
        print(f"WhatsApp webhook received: {body}")
        
        # Quick response to avoid Meta retries
        asyncio.create_task(process_whatsapp_message(body))
        
        return JSONResponse({"status": "received"}, status_code=200)
    except Exception as e:
        print(f"Webhook error: {e}")
        return JSONResponse({"status": "error"}, status_code=200)

async def process_whatsapp_message(body: dict):
    """Process WhatsApp message asynchronously"""
    try:
        entry = body.get("entry", [])
        if not entry:
            return
        
        changes = entry[0].get("changes", [])
        if not changes:
            return
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return
        
        message = messages[0]
        sender = message.get("from")
        message_type = message.get("type")
        
        # Only process text messages
        if message_type != "text":
            await send_whatsapp_message(sender, "Sorry, I can only process text messages at the moment.")
            return
        
        message_text = message.get("text", {}).get("body", "")
        
        if not message_text:
            return
        
        print(f"Processing message from {sender}: {message_text}")
        
        # Get or create user (use phone number as identifier)
        user = await get_or_create_whatsapp_user(sender)
        
        # Process with AI
        ai_response = await process_ai_query(message_text, user)
        
        # Send response back to WhatsApp
        await send_whatsapp_message(sender, ai_response)
        
    except Exception as e:
        print(f"Process WhatsApp message error: {e}")
        import traceback
        traceback.print_exc()

def normalize_phone_number(phone: str) -> str:
    """Remove country code from WhatsApp phone number"""
    # WhatsApp sends: 919032611376, DB has: 9032611376
    if phone.startswith('91') and len(phone) > 10:
        return phone[2:]  # Remove '91' country code
    return phone

async def get_or_create_whatsapp_user(phone_number: str) -> dict:
    """Get existing user or create new one for WhatsApp"""
    try:
        # Try with normalized phone (without country code)
        normalized_phone = normalize_phone_number(phone_number)
        
        response = users_table.get_item(Key={'phone_number': normalized_phone})
        user = response.get('Item')
        
        if user:
            print(f"Found existing user: {normalized_phone}")
            return user
        
        # Try with original phone number
        response = users_table.get_item(Key={'phone_number': phone_number})
        user = response.get('Item')
        
        if user:
            print(f"Found existing user: {phone_number}")
            return user
        
        # Create new user with default settings
        new_user = {
            "phone_number": normalized_phone,
            "password": "",
            "language": "en",
            "location": "India",
            "created_at": datetime.utcnow().isoformat(),
            "source": "whatsapp"
        }
        
        users_table.put_item(Item=new_user)
        print(f"Created new WhatsApp user: {normalized_phone}")
        
        return new_user
    except Exception as e:
        print(f"Get/create user error: {e}")
        return {
            "phone_number": normalize_phone_number(phone_number),
            "language": "en",
            "location": "India"
        }

async def process_ai_query(text: str, user: dict) -> str:
    """Process user query with AI - routes to specialized endpoints like GUI"""
    try:
        user_location = user.get("location", "India")
        language = user.get("language", "en")
        user_phone = user.get("phone_number", "Unknown")
        text_lower = text.lower()
        
        # Build user context for AI
        user_context = f"User phone: {user_phone}, Location: {user_location}, Language: {language}"
        
        # Detect intent and route to specialized endpoints
        # Weather queries
        if any(word in text_lower for word in ['weather', 'temperature', 'rain', 'climate', 'मौसम', 'बारिश', 'तापमान']):
            return await handle_weather_query(text, user, language)
        
        # Crop price queries
        elif any(word in text_lower for word in ['price', 'cost', 'rate', 'market', 'mandi', 'कीमत', 'दाम', 'भाव', 'मंडी']):
            return await handle_crop_price_query(text, user, language)
        
        # Government scheme queries
        elif any(word in text_lower for word in ['scheme', 'subsidy', 'loan', 'government', 'योजना', 'सब्सिडी', 'ऋण', 'सरकार']):
            return await handle_scheme_query(text, user, language)
        
        # Personal info queries (who am i, my profile, etc.)
        elif any(word in text_lower for word in ['who am i', 'my profile', 'my details', 'my info', 'about me', 'मैं कौन', 'मेरी जानकारी']):
            language_name = LANGUAGE_NAMES.get(language, "English")
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are Gram Vaani assistant. Tell the user about their profile in {language_name} language. Be friendly and concise."},
                    {"role": "user", "content": f"Tell me about my profile. My details: Phone: {user_phone}, Location: {user_location}, Preferred Language: {language_name}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        # General farming query
        else:
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are Gram Vaani, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. {user_context}. Keep responses concise for WhatsApp (under 300 words)."},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            # Log query to DynamoDB
            query_id = str(uuid.uuid4())
            query_english = translate_to_english(text, language)
            
            query_item = {
                "query_id": query_id,
                "user_phone": user["phone_number"],
                "query": text,
                "query_english": query_english,
                "response": response_text,
                "query_type": "whatsapp",
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "helpful": None,
                "feedback_text": None
            }
            queries_table.put_item(Item=query_item)
            
            return response_text
    except Exception as e:
        print(f"AI query error: {e}")
        return "Sorry, I'm having trouble processing your request. Please try again."

async def handle_weather_query(text: str, user: dict, language: str) -> str:
    """Handle weather queries using the same logic as /api/weather"""
    try:
        location = user.get("location", "Delhi")
        city = location.split(",")[0].strip()
        
        print(f"Weather query - User location: {location}, City: {city}")
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            print("ERROR: OpenWeather API key not found")
            return "Sorry, weather service is not configured. Please try again later."
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        print(f"Weather API URL: {url}")
        
        res = requests.get(url, timeout=10)
        print(f"Weather API response status: {res.status_code}")
        
        if res.status_code == 404:
            # Try with fallback city if location has multiple parts
            location_parts = location.split(",")
            if len(location_parts) > 1:
                fallback_city = location_parts[1].strip()
                print(f"Trying fallback city: {fallback_city}")
                url = f"https://api.openweathermap.org/data/2.5/weather?q={fallback_city}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    city = fallback_city
        
        if res.status_code != 200:
            print(f"Weather API error: {res.status_code} - {res.text}")
            return f"Sorry, I couldn't find weather information for {city}. Please update your location in settings."
        
        data = res.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        print(f"Weather data: {weather_desc}, {temp}°C, {humidity}% humidity")
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a weather assistant. Provide weather information in {language_name} language ONLY. Be concise and natural for WhatsApp."},
                {"role": "user", "content": f"Tell me the weather in {city}: {weather_desc}, temperature {temp}°C, humidity {humidity}%"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Weather response generated: {response_text[:100]}...")
        return response_text
    except Exception as e:
        print(f"Weather query error: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, I couldn't fetch weather information right now."

async def handle_crop_price_query(text: str, user: dict, language: str) -> str:
    """Handle crop price queries using the same logic as /api/crop-prices"""
    try:
        print(f"Crop price query: {text}")
        
        # Extract crop name from query using AI
        crop_extraction = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Extract the crop name from the user's query. Return only the crop name in English (e.g., wheat, rice, tomato, onion). If no crop is mentioned, return 'wheat'."},
                {"role": "user", "content": text}
            ],
            max_tokens=20,
            temperature=0.3
        )
        
        crop = crop_extraction.choices[0].message.content.strip().lower()
        location = user.get("location", "Delhi")
        market = location.split(",")[0]
        
        print(f"Extracted crop: {crop}, Market: {market}")
        
        base_prices = {
            'wheat': 2000, 'rice': 2400, 'corn': 1600, 'barley': 1800,
            'sugarcane': 5000, 'cotton': 6000, 'soybean': 4400, 'mustard': 5600,
            'onion': 3000, 'potato': 1400, 'tomato': 3600, 'chili': 8000
        }
        
        price = base_prices.get(crop, 2500)
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are a crop price assistant. Provide crop price information in {language_name} language ONLY. Be concise for WhatsApp."},
                {"role": "user", "content": f"Tell me the current price of {crop} in {market} market is ₹{price} per quintal"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"Crop price response: {response_text[:100]}...")
        return response_text
    except Exception as e:
        print(f"Crop price query error: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry, I couldn't fetch crop price information right now."

async def handle_scheme_query(text: str, user: dict, language: str) -> str:
    """Handle government scheme queries using the same logic as /api/gov-schemes"""
    try:
        language_name = LANGUAGE_NAMES.get(language, "English")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI assistant for rural India. Provide information about government schemes for farmers in {language_name} language ONLY. Be concise and helpful for WhatsApp (under 300 words)."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Scheme query error: {e}")
        return "Sorry, I couldn't fetch scheme information right now."

async def send_whatsapp_message(to: str, message: str):
    """Send message to WhatsApp user via Graph API"""
    try:
        url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"Message sent successfully to {to}")
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Send WhatsApp message error: {e}")

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

@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        response = users_table.get_item(Key={'phone_number': user.phone_number})
        if response.get('Item'):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        users_table.put_item(Item={
            "phone_number": user.phone_number,
            "password": hashed_password.decode('utf-8'),
            "language": user.language,
            "location": user.location,
            "created_at": datetime.utcnow().isoformat()
        })
        
        access_token = create_access_token(data={"sub": user.phone_number})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        print(f"Login attempt for: {user.phone_number}")
        response = users_table.get_item(Key={'phone_number': user.phone_number})
        db_user = response.get('Item')
        if not db_user:
            print(f"User not found: {user.phone_number}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        stored_password = db_user["password"]
        
        if stored_password.startswith('$2b$'):
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                print(f"Invalid password for: {user.phone_number}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            if user.password != stored_password:
                print(f"Invalid password for: {user.phone_number}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.phone_number})
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions_table.put_item(Item={
            "session_id": session_id,
            "user_phone": user.phone_number,
            "login_time": datetime.utcnow().isoformat(),
            "query_ids": []  # Will store query IDs
        })
        
        print(f"Login successful for: {user.phone_number}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "phone_number": current_user["phone_number"],
        "language": current_user["language"],
        "location": current_user["location"]
    }

@app.get("/api/query-history")
async def get_query_history(current_user: dict = Depends(get_current_user)):
    """Fetch user's query history from DynamoDB"""
    try:
        from boto3.dynamodb.conditions import Key
        
        response = queries_table.query(
            IndexName='user_phone-index',
            KeyConditionExpression=Key('user_phone').eq(current_user["phone_number"]),
            ScanIndexForward=False,  # Sort by timestamp descending
            Limit=50  # Last 50 queries
        )
        
        queries = response.get('Items', [])
        return {"queries": queries, "count": len(queries)}
    except Exception as e:
        print(f"Query history error: {e}")
        return {"queries": [], "count": 0}

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    """Submit feedback for a query response"""
    try:
        # Update query with feedback
        queries_table.update_item(
            Key={'query_id': feedback.query_id},
            UpdateExpression='SET helpful = :h, feedback_text = :f, feedback_time = :t',
            ExpressionAttributeValues={
                ':h': feedback.helpful,
                ':f': feedback.feedback_text or '',
                ':t': datetime.utcnow().isoformat()
            }
        )
        
        # Update village trust score
        village_id = current_user.get('location', 'Unknown').split(',')[0].strip()
        update_village_trust(village_id, feedback.helpful)
        
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        print(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def update_village_trust(village_id: str, helpful: bool):
    """Update village trust score based on feedback"""
    try:
        from boto3.dynamodb.conditions import Key
        
        # Get or create village trust record
        response = village_trust_table.get_item(Key={'village_id': village_id})
        
        if response.get('Item'):
            item = response['Item']
            total = item.get('total_responses', 0) + 1
            helpful_count = item.get('helpful_count', 0) + (1 if helpful else 0)
        else:
            total = 1
            helpful_count = 1 if helpful else 0
        
        trust_score = (helpful_count / total) * 100 if total > 0 else 0
        
        village_trust_table.put_item(Item={
            'village_id': village_id,
            'total_responses': total,
            'helpful_count': helpful_count,
            'trust_score': round(trust_score, 2),
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Village trust update error: {e}")

@app.get("/api/village-trust/{village_id}")
async def get_village_trust(village_id: str):
    """Get village trust score"""
    try:
        response = village_trust_table.get_item(Key={'village_id': village_id})
        if response.get('Item'):
            return response['Item']
        return {
            'village_id': village_id,
            'total_responses': 0,
            'helpful_count': 0,
            'trust_score': 0
        }
    except Exception as e:
        print(f"Village trust fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/community-report")
async def submit_community_report(report: CommunityReportRequest, current_user: dict = Depends(get_current_user)):
    """Submit a community report (pest, disease, weather observation, success story)"""
    try:
        report_id = str(uuid.uuid4())
        village_id = current_user.get('location', 'Unknown').split(',')[0].strip()
        
        # Translate description to English
        description_english = translate_to_english(report.description, report.language)
        
        report_item = {
            'report_id': report_id,
            'user_phone': current_user['phone_number'],
            'village_id': village_id,
            'report_type': report.report_type,
            'crop': report.crop or 'general',
            'description': report.description,
            'description_english': description_english,
            'severity': report.severity,
            'language': report.language,
            'timestamp': datetime.utcnow().isoformat(),
            'verified': False,
            'validation_count': 0,
            'validators': []
        }
        
        community_reports_table.put_item(Item=report_item)
        
        # Check for outbreak pattern (5+ reports in same village within 7 days)
        from boto3.dynamodb.conditions import Key
        from datetime import timedelta
        
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_reports = community_reports_table.query(
            IndexName='village_id-timestamp-index',
            KeyConditionExpression=Key('village_id').eq(village_id) & Key('timestamp').gt(week_ago),
            FilterExpression='report_type = :rt',
            ExpressionAttributeValues={':rt': report.report_type}
        )
        
        outbreak_detected = len(recent_reports.get('Items', [])) >= 5
        
        return {
            'status': 'success',
            'report_id': report_id,
            'message': 'Report submitted successfully',
            'outbreak_alert': outbreak_detected,
            'similar_reports': len(recent_reports.get('Items', []))
        }
    except Exception as e:
        print(f"Community report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/community-reports")
async def get_community_reports(current_user: dict = Depends(get_current_user), limit: int = 20):
    """Get recent community reports - show all reports if no village-specific index"""
    try:
        # Try to get all reports (fallback if index doesn't exist)
        response = community_reports_table.scan(Limit=limit)
        reports = response.get('Items', [])
        
        # Sort by timestamp (most recent first)
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {'reports': reports[:limit], 'count': len(reports)}
    except Exception as e:
        print(f"Fetch reports error: {e}")
        return {'reports': [], 'count': 0}

@app.post("/api/validate-report/{report_id}")
async def validate_report(report_id: str, helpful: bool, current_user: dict = Depends(get_current_user)):
    """Peer validation: farmers validate other farmers' reports"""
    try:
        response = community_reports_table.get_item(Key={'report_id': report_id})
        report = response.get('Item')
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        validators = report.get('validators', [])
        user_phone = current_user['phone_number']
        
        # Prevent duplicate validation
        if user_phone in validators:
            return {'status': 'already_validated', 'message': 'You have already validated this report'}
        
        validators.append(user_phone)
        validation_count = report.get('validation_count', 0) + (1 if helpful else 0)
        
        # Mark as verified if 3+ farmers validate
        verified = len(validators) >= 3 and validation_count >= 2
        
        community_reports_table.update_item(
            Key={'report_id': report_id},
            UpdateExpression='SET validators = :v, validation_count = :vc, verified = :vf',
            ExpressionAttributeValues={
                ':v': validators,
                ':vc': validation_count,
                ':vf': verified
            }
        )
        
        return {
            'status': 'success',
            'verified': verified,
            'validation_count': validation_count,
            'total_validators': len(validators)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/village-leaderboard")
async def get_village_leaderboard(limit: int = 10):
    """Get top villages by trust score (Gold/Silver/Bronze)"""
    try:
        response = village_trust_table.scan()
        villages = response.get('Items', [])
        
        # Sort by trust score
        villages.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
        
        # Assign tiers
        for i, village in enumerate(villages[:limit]):
            score = village.get('trust_score', 0)
            if score >= 80:
                village['tier'] = 'Gold'
                village['tier_icon'] = '🥇'
            elif score >= 60:
                village['tier'] = 'Silver'
                village['tier_icon'] = '🥈'
            else:
                village['tier'] = 'Bronze'
                village['tier_icon'] = '🥉'
            village['rank'] = i + 1
        
        return {'leaderboard': villages[:limit], 'total_villages': len(villages)}
    except Exception as e:
        print(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hyperlocal-context")
async def get_hyperlocal_context(current_user: dict = Depends(get_current_user)):
    """Get hyperlocal agricultural context based on user location"""
    try:
        location = current_user.get("location", "")
        parts = [p.strip() for p in location.split(",")]
        
        # Try to match district or state
        query = {}
        if len(parts) >= 2:
            query = {"$or": [{"district": {"$regex": parts[0], "$options": "i"}}, {"state": {"$regex": parts[1], "$options": "i"}}]}
        elif len(parts) == 1:
            query = {"$or": [{"district": {"$regex": parts[0], "$options": "i"}}, {"state": {"$regex": parts[0], "$options": "i"}}]}
        
        context = hyperlocal_collection.find_one(query)
        
        if not context:
            return {"message": "No hyperlocal data available for your location", "has_data": False}
        
        # Get current season
        month = datetime.utcnow().month
        if month in [6, 7, 8, 9, 10]:  # June-Oct
            season = "kharif"
        elif month in [11, 12, 1, 2, 3]:  # Nov-Mar
            season = "rabi"
        else:
            season = "summer"
        
        return {
            "has_data": True,
            "location": f"{context['district']}, {context['state']}",
            "soil_type": context["soil_type"],
            "rainfall": context["rainfall"],
            "current_season": season,
            "recommended_crops": context["crops"].get(season, []),
            "all_crops": context["crops"],
            "pest_alerts": context.get("pest_alerts", [])
        }
    except Exception as e:
        print(f"Hyperlocal context error: {e}")
        return {"has_data": False, "message": "Error fetching hyperlocal data"}

@app.get("/api/success-stories")
async def get_success_stories(current_user: dict = Depends(get_current_user), limit: int = 10):
    """Get nearby farmer success stories"""
    try:
        location = current_user.get("location", "")
        
        # Find stories from same region
        stories = list(success_stories_collection.find(
            {"location": {"$regex": location.split(",")[0], "$options": "i"}}
        ).limit(limit))
        
        # If no local stories, get any stories
        if not stories:
            stories = list(success_stories_collection.find().limit(limit))
        
        for story in stories:
            story["_id"] = str(story["_id"])
        
        return {"stories": stories, "count": len(stories)}
    except Exception as e:
        print(f"Success stories error: {e}")
        return {"stories": [], "count": 0}

@app.post("/api/report-pest-outbreak")
async def report_pest_outbreak(current_user: dict = Depends(get_current_user), pest_name: str = "", crop: str = "", severity: str = "medium"):
    """Report pest outbreak for location clustering"""
    try:
        location = current_user.get("location", "Unknown")
        
        outbreak = {
            "user_phone": current_user["phone_number"],
            "location": location,
            "pest_name": pest_name,
            "crop": crop,
            "severity": severity,
            "timestamp": datetime.utcnow(),
            "verified": False
        }
        
        pest_outbreaks_collection.insert_one(outbreak)
        
        # Check for clustering (3+ reports in same area within 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        nearby_reports = pest_outbreaks_collection.count_documents({
            "location": {"$regex": location.split(",")[0], "$options": "i"},
            "pest_name": pest_name,
            "timestamp": {"$gte": week_ago}
        })
        
        alert = nearby_reports >= 3
        
        return {
            "status": "success",
            "outbreak_alert": alert,
            "nearby_reports": nearby_reports,
            "message": f"Outbreak alert! {nearby_reports} reports in your area" if alert else "Report submitted"
        }
    except Exception as e:
        print(f"Pest outbreak report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/outbreak-map")
async def get_outbreak_map():
    """Get pest/disease outbreak patterns across villages"""
    try:
        from boto3.dynamodb.conditions import Key
        from datetime import timedelta
        from collections import defaultdict
        
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        # Get all recent reports
        response = community_reports_table.scan(
            FilterExpression='#ts > :week_ago AND (report_type = :pest OR report_type = :disease)',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':week_ago': week_ago,
                ':pest': 'pest',
                ':disease': 'disease'
            }
        )
        
        reports = response.get('Items', [])
        
        # Group by village and type
        outbreak_data = defaultdict(lambda: {'pest': 0, 'disease': 0, 'reports': []})
        
        for report in reports:
            village = report.get('village_id', 'Unknown')
            report_type = report.get('report_type')
            outbreak_data[village][report_type] += 1
            outbreak_data[village]['reports'].append({
                'type': report_type,
                'crop': report.get('crop'),
                'description': report.get('description_english', report.get('description')),
                'severity': report.get('severity'),
                'timestamp': report.get('timestamp')
            })
        
        # Identify outbreaks (5+ reports)
        outbreaks = []
        for village, data in outbreak_data.items():
            total = data['pest'] + data['disease']
            if total >= 5:
                outbreaks.append({
                    'village': village,
                    'pest_count': data['pest'],
                    'disease_count': data['disease'],
                    'total_reports': total,
                    'alert_level': 'high' if total >= 10 else 'medium',
                    'recent_reports': data['reports'][:5]
                })
        
        return {
            'outbreaks': outbreaks,
            'total_reports': len(reports),
            'affected_villages': len(outbreak_data)
        }
    except Exception as e:
        print(f"Outbreak map error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-text")
async def process_text(request: TextRequest, current_user: dict = Depends(get_current_user)):
    try:
        user_location = current_user.get("location", "India")
        print(f"Process text: {request.text[:50]}...")
        
        # OPTIMIZED: Fetch minimal context data (use sync version in async context)
        context_data = fetch_context_sync(user_location, request.text)
        formatted_context = format_context_for_llm(context_data)
        
        print(f"Context: {len(formatted_context)} chars")
        
        # Shorter system prompt
        system_prompt = f"""You are Gram Vaani, AI assistant for rural India. Use the data below to answer.

{formatted_context}

Be concise and practical."""
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.text}
            ],
            max_tokens=500,  # Reduced from 1000
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Async TTS generation
        audio_data = synthesize_speech(response_text, request.language)
        
        # Log query async (don't wait)
        query_id = str(uuid.uuid4())
        asyncio.create_task(log_query_async(query_id, current_user, request.text, response_text, request.language))

        return JSONResponse({
            "query_id": query_id,
            "response_text": response_text,
            "audio_data": audio_data
        })
    except Exception as e:
        print(f"Process text error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def log_query_async(query_id: str, user: dict, query: str, response: str, language: str):
    """Log query asynchronously without blocking response"""
    try:
        query_item = {
            "query_id": query_id,
            "user_phone": user["phone_number"],
            "query": query,
            "response": response,
            "language": language,
            "timestamp": datetime.utcnow().isoformat(),
            "helpful": None
        }
        queries_table.put_item(Item=query_item)
    except Exception as e:
        print(f"Log error: {e}")

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
        
        base_prices = {
            'wheat': 2000, 'rice': 2400, 'corn': 1600, 'barley': 1800,
            'sugarcane': 5000, 'cotton': 6000, 'soybean': 4400, 'mustard': 5600,
            'onion': 3000, 'potato': 1400, 'tomato': 3600, 'chili': 8000
        }
        
        price = base_prices.get(request.crop.lower(), 2500)
        
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
    try:
        print(f"Audio: {file.filename}, lang: {language}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3", "webm", "ogg"]:
            file_extension = "wav"
        
        audio_bytes = await file.read()
        
        # Transcribe
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        print(f"Transcript: {transcript[:50]}...")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed")
        
        user_location = current_user.get("location", "India")
        
        # OPTIMIZED: Minimal context (use sync version)
        context_data = fetch_context_sync(user_location, transcript)
        formatted_context = format_context_for_llm(context_data)
        
        language_name = LANGUAGE_NAMES.get(language, "English")
        system_prompt = f"""You are Gram Vaani. Help with farming. User in {user_location}. Respond in {language_name} ONLY.

{formatted_context}

Be concise."""
        
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript}
            ],
            max_tokens=500,  # Reduced
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        
        # Async logging
        query_id = str(uuid.uuid4())
        asyncio.create_task(log_query_async(query_id, current_user, transcript, response_text, language))
        
        audio_data = synthesize_speech(response_text, language)

        return JSONResponse({
            "query_id": query_id,
            "transcript": transcript,
            "response_text": response_text,
            "audio_data": audio_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Audio error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
