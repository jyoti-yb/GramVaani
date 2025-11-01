from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from openai import AzureOpenAI
import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://gramvani_user:GramVaani123!@firewall.jchsp.mongodb.net/gramvani?retryWrites=true&w=majority")
client_mongo = AsyncIOMotorClient(MONGO_URL)
db = client_mongo.gramvani
users_collection = db.user

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Auth functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return {"message": "Gram Vaani API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        user_doc = {
            "email": user.email,
            "password": hashed_password,
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
        db_user = await users_collection.find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
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
        
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
            messages=[
                {"role": "system", "content": f"You are Gram Vaani, AI Voice Assistant for Rural India. Help with farming, weather, crops, and government schemes. User is in {user_location}."},
                {"role": "user", "content": request.text}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        return JSONResponse({
            "response_text": response_text,
            "audio_data": None
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weather")
async def get_weather(city: str = "Delhi"):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY", "99f42bfabc8ad962157251343277ea08")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url)
        data = res.json()

        if res.status_code != 200:
            return JSONResponse({"error": "Weather data not found"}, status_code=400)

        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        response_text = f"Weather in {city}: {weather_desc}, {temp}°C, {humidity}% humidity"
        
        return JSONResponse({"text": response_text, "audio_data": None})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))