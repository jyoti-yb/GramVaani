from click import prompt
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

import os
import base64
import azure.cognitiveservices.speech as speechsdk
import boto3
from dotenv import load_dotenv
import requests
import jwt
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio
from transcribe_service import TranscribeService
import bcrypt
from rag.generator import FarmerAssistant

bedrock_agent = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.getenv("AWS_REGION", "ap-south-1")
)

import os
load_dotenv()

AGENT_ID = os.getenv("BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.getenv("BEDROCK_AGENT_ALIAS_ID")


def ask_gramvaani(query: str):

    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=str(uuid.uuid4()),
        inputText=query
    )

    completion = ""

    for event in response["completion"]:
        chunk = event["chunk"]["bytes"].decode()
        completion += chunk

    return completion

app = FastAPI()
rag_assistant = FarmerAssistant()

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



# Amazon Polly
polly_client = boto3.client("polly", region_name="ap-south-1")

# Amazon Transcribe
transcribe_service = TranscribeService()

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
        prompt = f"Translate the following {language_name} text to English:\n\n{text}"

        translated = ask_gramvaani(prompt)

        return translated.strip()
        ##
        # return response.choices[0].message.content.strip()
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
            hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
            await users_collection.insert_one({
                "email": "test@example.com",
                "password": hashed_password.decode('utf-8'),
                "language": "en",
                "location": "Delhi, India",
                "created_at": datetime.utcnow()
            })
            print("Test user created with hashed password")
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
        
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "email": user.email,
            "password": hashed_password.decode('utf-8'),
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
        
        stored_password = db_user["password"]
        
        # Check if password is hashed (starts with $2b$) or plain text
        if stored_password.startswith('$2b$'):
            # Hashed password - use bcrypt
            if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
                print(f"Invalid password for: {user.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            # Plain text password (legacy) - direct comparison
            if user.password != stored_password:
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
        
        response_text = ask_gramvaani(request.text)
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
        prompt = f"""
        Explain the weather to a farmer.

        City: {city}
        Weather: {weather_desc}
        Temperature: {temp}
        Humidity: {humidity}
        """

        response_text = ask_gramvaani(prompt)
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
        prompt = f"""
        Provide crop price information for farmers.

        Crop: {request.crop}
        Market: {market}
        Price: {price} rupees per quintal
        """

        response_text = ask_gramvaani(prompt)
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
        
        prompt = f"""
        Explain government schemes for farmers.

        Topic: {request.topic}
        Language: {language_name}
        """

        response_text = ask_gramvaani(prompt)
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
        
        
        response_text = ask_gramvaani(transcript)
        print(f"AI response generated successfully")
        
        # Translate query to English for RAG
        query_english = translate_to_english(transcript, language)
        
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        # Log query to DynamoDB
        queries_table.put_item(Item={
            "query_id": query_id,
            "user_phone": current_user["phone_number"],
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
<<<<<<< Updated upstream
        print(f"Process audio error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
=======
        print(f"Audio error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Advisor Page Endpoints
@app.get("/api/advisor/weather")
async def get_advisor_weather(current_user: dict = Depends(get_current_user)):
    try:
        location = current_user.get("location", "Delhi")
        city = location.split(",")[0].strip()
        
        api_key = os.getenv("OPENWEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=10)
        
        if res.status_code != 200:
            return {"location": city, "temperature": 25, "humidity": 60, "description": "Clear sky", "alerts": []}
        
        data = res.json()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]
        
        alerts = []
        if humidity > 80:
            alerts.append("High humidity may increase fungal infection risk")
        if temp > 35:
            alerts.append("High temperature - ensure adequate irrigation")
        
        return {
            "location": city,
            "temperature": temp,
            "humidity": humidity,
            "description": desc,
            "rainfall": None,
            "alerts": alerts
        }
    except Exception as e:
        print(f"Advisor weather error: {e}")
        return {"location": "Unknown", "temperature": 25, "humidity": 60, "description": "Clear", "alerts": []}

@app.get("/api/advisor/crops")
async def get_crop_recommendations(current_user: dict = Depends(get_current_user)):
    try:
        location = current_user.get("location", "India")
        
        # Get user query history for interest analysis
        from boto3.dynamodb.conditions import Key
        response = queries_table.query(
            IndexName='user_phone-index',
            KeyConditionExpression=Key('user_phone').eq(current_user["phone_number"]),
            Limit=20
        )
        queries = response.get('Items', [])
        
        # Simple ML simulation (Random Forest would go here)
        base_crops = [
            {"name": "Rice", "ml_score": 85, "regional_score": 90, "interest_score": 70},
            {"name": "Wheat", "ml_score": 80, "regional_score": 85, "interest_score": 60},
            {"name": "Cotton", "ml_score": 75, "regional_score": 70, "interest_score": 50},
            {"name": "Sugarcane", "ml_score": 70, "regional_score": 75, "interest_score": 40},
            {"name": "Maize", "ml_score": 78, "regional_score": 65, "interest_score": 55},
            {"name": "Soybean", "ml_score": 72, "regional_score": 60, "interest_score": 45}
        ]
        
        # Calculate final scores
        for crop in base_crops:
            crop["score"] = int(0.5 * crop["ml_score"] + 0.3 * crop["regional_score"] + 0.2 * crop["interest_score"])
        
        # Sort by score
        base_crops.sort(key=lambda x: x["score"], reverse=True)
        
        # Generate explanations using Azure OpenAI
        crops_with_details = []
        for crop in base_crops[:6]:
            explanation_response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a crop advisor. Provide a brief 1-sentence explanation for why this crop is suitable."},
                    {"role": "user", "content": f"Why is {crop['name']} suitable for {location}?"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            crops_with_details.append({
                "name": crop["name"],
                "score": crop["score"],
                "explanation": explanation_response.choices[0].message.content,
                "water_requirement": "Medium" if crop["score"] > 75 else "Low",
                "yield_potential": "High" if crop["score"] > 80 else "Medium",
                "market_price": 2000 + (crop["score"] * 20)
            })
        
        return {"crops": crops_with_details}
    except Exception as e:
        print(f"Crop recommendations error: {e}")
        return {"crops": []}

@app.get("/api/advisor/strategies")
async def get_farming_strategies(current_user: dict = Depends(get_current_user)):
    try:
        strategies = [
            {
                "name": "Drip Irrigation",
                "explanation": "Save up to 60% water with drip irrigation. Delivers water directly to plant roots, reducing evaporation and improving crop yield.",
                "link": "https://agricoop.gov.in"
            },
            {
                "name": "Mulching",
                "explanation": "Cover soil with organic material to retain moisture, suppress weeds, and improve soil health naturally.",
                "link": "https://icar.org.in"
            },
            {
                "name": "Precision Fertigation",
                "explanation": "Combine fertilizer with irrigation for optimal nutrient delivery. Reduces fertilizer waste and improves crop nutrition.",
                "link": "https://agricoop.gov.in"
            },
            {
                "name": "Organic Pest Control",
                "explanation": "Use neem oil, beneficial insects, and crop rotation to control pests naturally without harmful chemicals.",
                "link": "https://icar.org.in"
            },
            {
                "name": "Crop Rotation",
                "explanation": "Alternate different crops each season to improve soil fertility, break pest cycles, and increase yields.",
                "link": "https://agricoop.gov.in"
            },
            {
                "name": "Soil Testing",
                "explanation": "Regular soil testing helps determine nutrient deficiencies and pH levels for better fertilizer management.",
                "link": "https://icar.org.in"
            }
        ]
        
        return {"strategies": strategies}
    except Exception as e:
        print(f"Strategies error: {e}")
        return {"strategies": []}


# Voice Assistant Endpoint
@app.post("/api/advisor/assistant")
async def advisor_assistant(file: Optional[UploadFile] = File(None), text: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    try:
        query_text = text
        
        # Handle voice input
        if file:
            audio_bytes = await file.read()
            file_extension = file.filename.split(".")[-1].lower() if file.filename else "wav"
            query_text = await transcribe_service.transcribe_audio(audio_bytes, file_extension, current_user.get("language", "en"))
        
        if not query_text:
            raise HTTPException(status_code=400, detail="No query provided")
        
        query_lower = query_text.lower()
        location = current_user.get("location", "India")
        
        # Intent detection
        if any(word in query_lower for word in ['crop', 'grow', 'plant', 'cultivate', 'recommend', 'फसल', 'खेती']):
            # Crop recommendation query
            from boto3.dynamodb.conditions import Key
            response = queries_table.query(
                IndexName='user_phone-index',
                KeyConditionExpression=Key('user_phone').eq(current_user["phone_number"]),
                Limit=10
            )
            queries = response.get('Items', [])
            
            crops = ["Rice", "Wheat", "Cotton", "Sugarcane", "Maize"]
            ai_response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are GramVaani crop advisor. User location: {location}. Recommend suitable crops based on their query. Be concise."},
                    {"role": "user", "content": query_text}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return {"transcript": query_text, "response": ai_response.choices[0].message.content}
        
        elif any(word in query_lower for word in ['strategy', 'technique', 'method', 'irrigation', 'drip', 'mulch', 'तकनीक', 'सिंचाई']):
            # Farming strategy query
            strategies = [
                "Drip Irrigation: Save 60% water by delivering water directly to roots",
                "Mulching: Cover soil to retain moisture and suppress weeds",
                "Crop Rotation: Alternate crops to improve soil fertility"
            ]
            ai_response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": f"You are GramVaani farming advisor. Explain farming strategies. Available: {', '.join(strategies)}. Be practical."},
                    {"role": "user", "content": query_text}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return {"transcript": query_text, "response": ai_response.choices[0].message.content}
        
        elif any(word in query_lower for word in ['weather', 'rain', 'temperature', 'climate', 'मौसम', 'बारिश']):
            # Weather impact query
            api_key = os.getenv("OPENWEATHER_API_KEY")
            city = location.split(",")[0].strip()
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            res = requests.get(url, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                desc = data["weather"][0]["description"]
                
                ai_response = azure_client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": f"You are GramVaani weather advisor. Current weather in {city}: {desc}, {temp}°C, {humidity}% humidity. Explain impact on crops."},
                        {"role": "user", "content": query_text}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                return {"transcript": query_text, "response": ai_response.choices[0].message.content}
        
        elif any(word in query_lower for word in ['soil', 'ph', 'nitrogen', 'fertilizer', 'nutrient', 'मिट्टी', 'खाद']):
            # Soil health query
            ai_response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are GramVaani soil health advisor. Provide practical advice on soil testing, pH management, and fertilizer use."},
                    {"role": "user", "content": query_text}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return {"transcript": query_text, "response": ai_response.choices[0].message.content}
        
        # General farming guidance
        ai_response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": f"You are GramVaani, AI assistant for farmers in {location}. Provide practical farming guidance. Be concise and helpful."},
                {"role": "user", "content": query_text}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return {"transcript": query_text, "response": ai_response.choices[0].message.content}
        
    except Exception as e:
        print(f"Assistant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agriculture News Endpoint with Images
@app.get("/api/advisor/news")
async def get_agriculture_news(current_user: dict = Depends(get_current_user)):
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        fallback_image = "https://images.unsplash.com/photo-1592982537447-6f2a6a0a5f17?w=400"
        
        if not news_api_key:
            return {
                "articles": [
                    {"title": "Cotton prices expected to rise this month", "summary": "Export demand has increased cotton prices by 12%.", "source": "AgriMarket News", "url": "https://agricoop.gov.in", "image": fallback_image},
                    {"title": "New irrigation subsidy scheme announced", "summary": "Government announces 50% subsidy on drip irrigation systems.", "source": "Ministry of Agriculture", "url": "https://agricoop.gov.in", "image": "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400"},
                    {"title": "Weather alert: Heavy rainfall expected", "summary": "IMD predicts heavy rainfall. Farmers advised to postpone fertilizer application.", "source": "India Meteorological Department", "url": "https://icar.org.in", "image": "https://images.unsplash.com/photo-1601597111158-2fceff292cdc?w=400"}
                ]
            }
        
        query = "(agriculture OR farming OR crop OR fertilizer OR irrigation OR farmer OR pest OR disease) AND NOT (politics OR entertainment OR sports)"
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize=12&apiKey={news_api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return {"articles": [{"title": "Cotton prices expected to rise", "summary": "Export demand increased.", "source": "AgriMarket News", "url": "https://agricoop.gov.in", "image": fallback_image}]}
        
        data = response.json()
        articles = []
        
        for article in data.get("articles", [])[:12]:
            image_url = article.get("urlToImage") or fallback_image
            description = article.get("description", "")
            if description and len(description) > 150:
                try:
                    summary_response = azure_client.chat.completions.create(
                        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                        messages=[{"role": "system", "content": "Summarize in 1-2 sentences (max 100 words)."}, {"role": "user", "content": description}],
                        max_tokens=80, temperature=0.5
                    )
                    description = summary_response.choices[0].message.content
                except:
                    description = description[:150] + "..."
            
            articles.append({"title": article.get("title", "Agriculture News"), "summary": description or "Read more for details.", "source": article.get("source", {}).get("name", "News Source"), "url": article.get("url", "https://agricoop.gov.in"), "image": image_url})
        
        return {"articles": articles}
    except Exception as e:
        print(f"News API error: {e}")
        fallback_image = "https://images.unsplash.com/photo-1592982537447-6f2a6a0a5f17?w=400"
        return {"articles": [{"title": "Cotton prices expected to rise", "summary": "Export demand increased.", "source": "AgriMarket News", "url": "https://agricoop.gov.in", "image": fallback_image}]}


>>>>>>> Stashed changes
