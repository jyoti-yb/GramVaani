from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

load_dotenv()

app = FastAPI()

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
users_table = dynamodb.Table('gramvaani_users')
queries_table = dynamodb.Table('gramvaani_user_querie')
sessions_table = dynamodb.Table('gramvaani_sessions')
village_trust_table = dynamodb.Table('gramvaani_village_trust')

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
        
        # Translate query to English for RAG
        query_english = translate_to_english(request.text, request.language)
        
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        # Log query to DynamoDB
        queries_table.put_item(Item={
            "query_id": query_id,
            "user_phone": current_user["phone_number"],
            "query": request.text,
            "query_english": query_english,
            "response": response_text,
            "language": request.language,
            "timestamp": datetime.utcnow().isoformat(),
            "helpful": None,  # Will be updated by feedback
            "feedback_text": None
        })
        
        audio_data = synthesize_speech(response_text, request.language)

        return JSONResponse({
            "query_id": query_id,
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
        print(f"Processing audio file: {file.filename}, language: {language}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["wav", "mp3", "webm", "ogg"]:
            file_extension = "wav"
        
        audio_bytes = await file.read()
        print(f"Audio bytes: {len(audio_bytes)}, Language selected: {language}")
        
        transcript = await transcribe_service.transcribe_audio(audio_bytes, file_extension, language)
        print(f"Transcription successful (language: {language}): {transcript[:100]}...")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
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
        
        # Translate query to English for RAG
        query_english = translate_to_english(transcript, language)
        
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        # Log query to DynamoDB
        queries_table.put_item(Item={
            "query_id": query_id,
            "user_phone": current_user["phone_number"],
            "query": transcript,
            "query_english": query_english,
            "response": response_text,
            "query_type": "audio",
            "language": language,
            "timestamp": datetime.utcnow().isoformat(),
            "helpful": None,
            "feedback_text": None
        })
        
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
        print(f"Process audio error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
