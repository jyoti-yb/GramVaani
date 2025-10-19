# 🏆 Gram Vaani - OpenAI X NXT Buildathon Submission

## 🎯 Project Overview

**Gram Vaani** is a revolutionary AI-powered voice assistant designed specifically for rural Indian farmers. It bridges the "digital dialect divide" by understanding local languages and dialects, providing critical information about weather, crop prices, and government schemes.

## 🌟 Key Features

### 🗣️ Multi-Dialect Voice Recognition
- Supports Hindi, Telugu, Punjabi, Bhojpuri, Maithili, and other regional languages
- Uses OpenAI Whisper for robust speech-to-text conversion
- Handles regional accents and pronunciation variations

### 🤖 Intelligent Understanding
- GPT-4 powered intent recognition
- Context-aware responses for rural users
- Natural language processing for imperfect transcriptions

### 📊 Real-Time Information
- **Weather Data**: Live weather updates with farming advice
- **Crop Prices**: Current market prices from government sources
- **Government Schemes**: Information about PM-KISAN, Fasal Bima Yojana, etc.

### 🔊 Voice-First Design
- Text-to-speech responses in local languages
- Mobile-optimized interface
- Works on low-bandwidth networks

## 🏗️ Technical Architecture

```
User Voice Input → React Frontend → FastAPI Backend → OpenAI Services
                                    ↓
                            External APIs (Weather, Markets)
                                    ↓
                            Local Database (Govt Schemes)
```

## 🛠️ Tech Stack

- **Frontend**: React + Vite (Modern, fast development)
- **Backend**: Python + FastAPI (High-performance API)
- **AI Services**: OpenAI Whisper, GPT-4, TTS
- **Data Sources**: OpenWeatherMap, Government APIs
- **Database**: CSV-based local storage for offline capability

## 🚀 Quick Start

### Option 1: One-Click Start
```bash
# Windows
start_all.bat

# Manual start
start_backend.bat  # Terminal 1
start_frontend.bat # Terminal 2
```

### Option 2: Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 🎤 Demo Scenarios

### Weather Query
**User**: "Delhi mein mausam kaisa hai?"
**Response**: "Delhi mein aaj temperature 25 degree Celsius hai. Hawa ki speed 10 km/h hai. Ye weather farming ke liye accha hai."

### Crop Price Query
**User**: "Wheat ka price kya hai?"
**Response**: "Wheat ka current price ₹2500 per quintal hai Delhi Mandi mein. Ye price stable hai aur selling ke liye accha time hai."

### Government Scheme Query
**User**: "PM Kisan scheme ke bare mein batao"
**Response**: "PM-KISAN scheme mein aapko ₹6000 per year milta hai 3 installments mein. Ye scheme sabhi landholding farmers ke liye hai."

## 🌾 Impact on Rural India

### Problem Solved
- **Digital Divide**: Language barriers preventing access to information
- **Information Gap**: Lack of real-time weather and market data
- **Government Services**: Difficulty accessing scheme information

### Solution Benefits
- **Inclusive Technology**: Works in local languages
- **Real-Time Information**: Live weather and market updates
- **Government Outreach**: Easy access to scheme information
- **Cost-Effective**: Works on basic smartphones

## 🏆 Buildathon Highlights

### Innovation
- First AI assistant designed specifically for rural Indian dialects
- Voice-first approach for low-literacy users
- Offline-capable design for poor connectivity

### Technical Excellence
- Modern React + FastAPI architecture
- OpenAI integration for state-of-the-art AI
- Mobile-first responsive design

### Social Impact
- Bridges digital divide in rural India
- Empowers farmers with information
- Supports government digital initiatives

## 📱 User Experience

1. **Simple Interface**: Large microphone button, clear instructions
2. **Voice Interaction**: Speak naturally in your dialect
3. **Instant Response**: Get information in voice and text
4. **Mobile Optimized**: Works on any smartphone

## 🔮 Future Enhancements

- **Offline Mode**: Complete offline functionality
- **More Languages**: Support for 50+ Indian languages
- **Advanced Features**: Crop disease detection, market predictions
- **Integration**: WhatsApp, SMS integration

## 🎯 Buildathon Success Factors

✅ **Problem-Solution Fit**: Addresses real rural challenges
✅ **Technical Innovation**: Advanced AI with simple interface  
✅ **Social Impact**: Empowers millions of farmers
✅ **Scalability**: Can be deployed across India
✅ **Sustainability**: Uses existing government data sources

---

**Gram Vaani** - Bridging the digital dialect divide, one voice at a time! 🌾🤖
