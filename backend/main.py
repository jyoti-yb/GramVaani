from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import openai
import os
import json
import requests
from typing import Optional
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Gram Vaani API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def root():
    return {"message": "Gram Vaani API is running!"}

@app.post("/process-audio")
async def process_audio(audio_file: UploadFile = File(...)):
    """
    Process audio input and return voice response
    """
    try:
        # Check if OpenAI API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or not api_key.startswith("sk-"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key is not configured properly. Please check your .env file and ensure OPENAI_API_KEY is set with a valid key from https://platform.openai.com/api-keys"
            )
        
        # Save uploaded audio file
        audio_content = await audio_file.read()
        
        # Step 1: Speech-to-Text using Whisper
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_content)
        
        with open("temp_audio.wav", "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        
        user_text = transcript.text
        os.remove("temp_audio.wav")
        
        # Step 2: Intent Recognition and Entity Extraction
        intent_response = await recognize_intent(user_text)
        
        # Step 3: Information Retrieval
        information = await retrieve_information(intent_response)
        
        # Step 4: Response Generation
        response_text = await generate_response(user_text, intent_response, information)
        
        # Step 5: Text-to-Speech
        audio_response = await text_to_speech(response_text)
        
        return JSONResponse({
            "transcript": user_text,
            "intent": intent_response,
            "response_text": response_text,
            "audio_url": audio_response
        })
        
    except Exception as e:
        print(f"Error in process_audio: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def recognize_intent(user_text: str):
    """
    Use GPT-4 to recognize user intent and extract entities
    """
    prompt = f"""
    Analyze this user query from a rural Indian context: "{user_text}"
    
    Identify:
    1. Intent: weather, crop_price, government_scheme, general_help, or other
    2. Entities: location, crop_name, scheme_name, etc.
    3. Language: detected dialect/language
    
    Return JSON format:
    {{
        "intent": "weather",
        "entities": {{"location": "Delhi", "crop": "wheat"}},
        "language": "Hindi",
        "confidence": 0.9
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)

async def retrieve_information(intent_data):
    """
    Retrieve relevant information based on intent
    """
    intent = intent_data.get("intent")
    entities = intent_data.get("entities", {})
    
    if intent == "weather":
        return await get_weather_info(entities.get("location", "Delhi"))
    elif intent == "crop_price":
        return await get_crop_price_info(entities.get("crop", "wheat"))
    elif intent == "government_scheme":
        return await get_government_scheme_info(entities.get("scheme", ""))
    else:
        return {"type": "general", "message": "I can help you with weather, crop prices, and government schemes."}

async def get_weather_info(location: str):
    """
    Get weather information from OpenWeatherMap API
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "Weather API key not configured"}
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
            return {
                "type": "weather",
                "location": data["name"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
    except Exception as e:
        return {"error": f"Weather data unavailable: {str(e)}"}

async def get_crop_price_info(crop: str):
    """
    Get crop price information from government APIs
    """
    try:
        # Using Agmarknet API or similar government source
        # For demo, we'll use a mock API response
        api_key = os.getenv("AGMARKNET_API_KEY")
        
        if api_key:
            # Real API call to government crop price database
            url = f"https://api.agmarknet.gov.in/api/price/{crop}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "type": "crop_price",
                        "crop": crop,
                        "price": data.get("price", "N/A"),
                        "unit": data.get("unit", "quintal"),
                        "market": data.get("market", "Local Mandi"),
                        "date": data.get("date", "Today")
                    }
        
        # Fallback response for demo
        return {
            "type": "crop_price",
            "crop": crop,
            "message": f"Price information for {crop} is being fetched from government sources. Please check with your local mandi for current rates."
        }
    except Exception as e:
        return {"error": f"Crop price data unavailable: {str(e)}"}

async def get_government_scheme_info(scheme: str):
    """
    Get government scheme information from government APIs
    """
    try:
        # Using government portal APIs
        api_key = os.getenv("GOVT_PORTAL_API_KEY")
        
        if api_key:
            # Real API call to government schemes database
            url = f"https://api.india.gov.in/api/schemes"
            params = {"search": scheme} if scheme else {}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers={"Authorization": f"Bearer {api_key}"})
                if response.status_code == 200:
                    data = response.json()
                    schemes = data.get("schemes", [])
                    return {
                        "type": "government_scheme",
                        "schemes": schemes[:3]  # Limit to 3 schemes
                    }
        
        # Fallback with hardcoded popular schemes for demo
        popular_schemes = [
            {
                "name": "PM-KISAN",
                "description": "Direct income support to farmers",
                "benefits": "₹6000 per year in 3 installments",
                "eligibility": "All landholding farmer families"
            },
            {
                "name": "Fasal Bima Yojana",
                "description": "Crop insurance scheme",
                "benefits": "Financial support for crop loss",
                "eligibility": "All farmers including sharecroppers"
            },
            {
                "name": "Pradhan Mantri Kisan Maan Dhan Yojana",
                "description": "Pension scheme for farmers",
                "benefits": "₹3000 monthly pension after 60 years",
                "eligibility": "Farmers aged 18-40 years"
            }
        ]
        
        return {
            "type": "government_scheme",
            "schemes": popular_schemes
        }
    except Exception as e:
        return {"error": f"Government scheme data unavailable: {str(e)}"}

async def generate_response(user_text: str, intent_data: dict, information: dict):
    """
    Generate natural language response using GPT-4
    """
    prompt = f"""
    You are Gram Vaani, a helpful AI assistant for rural Indian farmers. 
    
    User asked: "{user_text}"
    Intent: {intent_data.get('intent')}
    Information retrieved: {json.dumps(information, indent=2)}
    
    Generate a helpful, simple response in Hindi/English mix that rural users can understand.
    Keep it conversational, friendly, and practical.
    If the information is about weather, mention how it affects farming.
    If it's about crop prices, give practical advice.
    If it's about government schemes, explain benefits simply.
    
    Response should be 2-3 sentences maximum.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

async def text_to_speech(text: str):
    """
    Convert text to speech using OpenAI TTS
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save audio file
        audio_filename = f"response_{hash(text)}.mp3"
        audio_path = f"static/{audio_filename}"
        
        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)
        
        with open(audio_path, "wb") as f:
            f.write(response.content)
        
        return f"/static/{audio_filename}"
        
    except Exception as e:
        return None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Gram Vaani API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
