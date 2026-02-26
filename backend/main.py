from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from openai import AzureOpenAI
import os
import base64
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio

load_dotenv()

app = FastAPI()

# MongoDB connection with working credentials
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://gramvani_user:GramVaani123!@firewall.jchsp.mongodb.net/gramvani?retryWrites=true&w=majority")
client_mongo = AsyncIOMotorClient(MONGO_URL)
db = client_mongo.gramvani
users_collection = db.user
user_queries_collection = db.user_queries

print("MongoDB connection initialized with gramvani_user")

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

LANGUAGE_TO_LOCALE = {
    "en": "en-US",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
}

def synthesize_speech(text: str, language: str) -> Optional[str]:
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    if not speech_key or not speech_region or not text:
        return None

    locale = LANGUAGE_TO_LOCALE.get(language, "en-US")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_language = locale

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return base64.b64encode(result.audio_data).decode("utf-8")

    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails.from_result(result)
        print(f"Speech synthesis canceled: {details.reason} - {details.error_details}")

    return None

def build_whisper_url(whisper_endpoint: str, deployment: str) -> str:
    base = whisper_endpoint.rstrip("/")
    if "/openai/" in base or "audio/transcriptions" in base:
        return base
    return f"{base}/openai/deployments/{deployment}/audio/transcriptions"

def get_whisper_api_versions() -> list[str]:
    primary_version = os.getenv("WHISPER_API_VERSION", "2024-06-01")
    fallback_versions = ["2024-02-15-preview", "2023-09-01-preview"]
    versions = [primary_version] + [v for v in fallback_versions if v != primary_version]
    return versions

def recognize_speech_with_azure(audio_bytes: bytes, language: str) -> str:
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    if not speech_key or not speech_region:
        raise HTTPException(status_code=500, detail="Azure Speech credentials not configured")

    locale = LANGUAGE_TO_LOCALE.get(language, "en-US")
    url = f"https://{speech_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
    }
    params = {
        "language": locale,
    }

    response = requests.post(url, headers=headers, params=params, data=audio_bytes, timeout=60)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {response.text}")

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Speech recognition failed: invalid response")

    transcript = data.get("DisplayText") or data.get("Text") or ""
    if not transcript:
        raise HTTPException(status_code=400, detail="Speech not recognized. Please try again.")

    return transcript

# Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    language: str
    location: str

class UserLogin(BaseModel):
    email: EmailStr
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

# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Database initialization
async def init_db():
    try:
        # Test connection
        await client_mongo.admin.command('ping')
        print("MongoDB connection successful")
        
        # Create indexes
        await users_collection.create_index("email", unique=True)
        await user_queries_collection.create_index("user_email")
        
        # Create test user if not exists
        test_user = await users_collection.find_one({"email": "test@example.com"})
        if not test_user:
            await users_collection.insert_one({
                "email": "test@example.com",
                "password": "password123",
                "language": "en",
                "location": "Delhi, India",
                "created_at": datetime.utcnow()
            })
            print("Test user created")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    await init_db()

# Routes
@app.get("/")
async def root():
    return {"message": "Gram Vaani API with MongoDB is running"}

@app.get("/health")
async def health():
    try:
        await client_mongo.admin.command('ping')
        user_count = await users_collection.count_documents({})
        test_user_exists = await users_collection.find_one({"email": "test@example.com"}) is not None
        
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "test_user_exists": test_user_exists
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
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

@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_doc = {
            "email": user.email,
            "password": user.password,
            "language": user.language,
            "location": user.location,
            "created_at": datetime.utcnow()
        }
        
        await users_collection.insert_one(user_doc)
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        print(f"Login attempt for: {user.email}")
        db_user = await users_collection.find_one({"email": user.email})
        if not db_user:
            print(f"User not found: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user.password != db_user["password"]:
            print(f"Invalid password for: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        print(f"Login successful for: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user["email"],
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
        
        # Log query to MongoDB
        await user_queries_collection.insert_one({
            "user_email": current_user["email"],
            "query": request.text,
            "response": response_text,
            "timestamp": datetime.utcnow()
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
        
        print(f"Weather request for city: {city}")
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="OpenWeather API key not configured. Get a free key from https://openweathermap.org/api"
            )
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        print(f"Calling OpenWeather API for city: {city}")
        
        res = requests.get(url, timeout=10)
        print(f"OpenWeather response status: {res.status_code}")
        
        if res.status_code == 401:
            raise HTTPException(
                status_code=500,
                detail="Invalid OpenWeather API key. Please add a valid key to OPENWEATHER_API_KEY in .env"
            )
        
        if res.status_code == 404:
            print(f"City not found: {city}. Trying with fallback city...")
            location_parts = current_user.get("location", "Delhi").split(",")
            if len(location_parts) > 1:
                fallback_city = location_parts[1].strip()
                print(f"Trying fallback city: {fallback_city}")
                res = requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather?q={fallback_city}&appid={api_key}&units=metric",
                    timeout=10
                )
                if res.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Weather data not found for {city}. Try a major city.")
                city = fallback_city
            else:
                raise HTTPException(status_code=400, detail=f"City '{city}' not found. Try entering a major city name.")
        
        if res.status_code != 200:
            print(f"OpenWeather error: {res.text}")
            raise HTTPException(status_code=500, detail=f"Weather API error: {res.text}")
        
        data = res.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        response_text = f"Weather in {city}: {weather_desc}, temperature {temp}°C, humidity {humidity}%"
        print(f"Weather response: {response_text}")
        
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
        response_text = f"Current price of {request.crop} in {market} market is ₹{price} per quintal"
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gov-schemes")
async def get_gov_schemes(request: SchemeRequest, current_user: dict = Depends(get_current_user)):
    try:
        print(f"Schemes request for topic: {request.topic}")
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are Gram Vaani, AI assistant for rural India. Provide information about government schemes for farmers in simple terms."},
                {"role": "user", "content": f"Tell me about government schemes related to {request.topic}"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        print(f"Schemes response generated successfully")
        
        audio_data = synthesize_speech(response_text, request.language)
        return JSONResponse({"text": response_text, "audio_data": audio_data})
    except Exception as e:
        print(f"Schemes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching schemes: {str(e)}")

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), language: str = "en", current_user: dict = Depends(get_current_user)):
    """
    Process audio file: transcribe using Whisper API and generate AI response
    """
    try:
        print(f"Processing audio file: {file.filename}, language: {language}")
        
        # Read audio file
        audio_bytes = await file.read()
        content_type = file.content_type or "application/octet-stream"
        print(f"Audio content-type: {content_type}, bytes: {len(audio_bytes)}")

        # Transcribe using Azure Speech Services
        transcript = recognize_speech_with_azure(audio_bytes, language)
        
        print(f"Transcription successful: {transcript[:100]}...")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Generate AI response using Azure OpenAI
        user_location = current_user.get("location", "India")
        
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. User is in {user_location}."},
                {"role": "user", "content": transcript}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = ai_response.choices[0].message.content
        print(f"AI response generated successfully")
        
        # Log query to MongoDB
        await user_queries_collection.insert_one({
            "user_email": current_user["email"],
            "query": transcript,
            "response": response_text,
            "query_type": "audio",
            "timestamp": datetime.utcnow()
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