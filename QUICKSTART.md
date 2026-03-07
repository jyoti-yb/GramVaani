# Gram Vaani - Quick Start Guide

## ✅ Configuration Status

Your Azure OpenAI configuration has been successfully set up:

- **Endpoint**: https://panda-openai-api.openai.azure.com/
- **Deployment**: gpt-4o-mini
- **API Version**: 2024-12-01-preview
- **API Key**: Configured ✓

## ✅ Verification Complete

All systems tested and working:
- ✓ Python syntax valid
- ✓ Dependencies installed
- ✓ Environment variables loaded
- ✓ Azure OpenAI connection successful
- ✓ MongoDB connection successful
- ✓ FastAPI server starts correctly

## 🚀 How to Run

### Option 1: Using the startup script
```bash
./start_server.sh
```

### Option 2: Manual start
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📍 API Endpoints

Once running, access:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 Test Credentials

- Email: test@example.com
- Password: password123

## 📝 Available Endpoints

- `POST /api/signup` - User registration
- `POST /api/login` - User login
- `GET /api/me` - Get current user
- `POST /process-text` - AI text processing
- `POST /api/weather` - Weather information
- `POST /api/crop-prices` - Crop price information
- `POST /api/gov-schemes` - Government schemes info
- `GET /api/location` - Get user location
- `POST /api/reverse-geocode` - Reverse geocoding

## 🛠️ Testing

Test Azure OpenAI connection:
```bash
cd backend
python test_azure_openai.py
```

## 📦 Dependencies

All required packages are installed:
- fastapi 0.109.0
- openai 2.24.0 (upgraded)
- motor 3.6.0
- pymongo 4.9

## ⚠️ Important Notes

1. The `.env` file contains your Azure OpenAI credentials
2. MongoDB is configured and connected
3. CORS is enabled for local development
4. The server runs on port 8000 by default
