# Gram Vaani - Local Setup Guide

## Prerequisites
- Python 3.11+ 
- Node.js 18+
- OpenAI API Key
- OpenWeatherMap API Key (optional)

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env file with your API keys
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Required APIs
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional APIs (for real government data)
AGMARKNET_API_KEY=your_agmarknet_api_key_here
GOVT_PORTAL_API_KEY=your_govt_portal_api_key_here
```

## API Keys Setup

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file

### OpenWeatherMap API Key (Optional)
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key
4. Add it to your `.env` file

### Government APIs (Optional - for real data)
- **Agmarknet API**: For real crop prices from government sources
- **Government Portal API**: For real government scheme information
- Without these, the app uses fallback data for demonstration

## Testing the Application

1. Open http://localhost:3000 in your browser
2. Click the microphone button
3. Speak in your local dialect (Hindi, Telugu, Punjabi, etc.)
4. Ask about:
   - Weather: "Delhi mein mausam kaisa hai?"
   - Crop prices: "Wheat ka price kya hai?"
   - Government schemes: "PM Kisan scheme ke bare mein batao"

## Troubleshooting

### Microphone Issues
- Ensure browser has microphone permissions
- Use HTTPS in production (required for microphone access)

### API Issues
- Check your OpenAI API key is valid
- Ensure you have sufficient API credits
- Check console for error messages

### Network Issues
- Ensure backend is running on port 8000
- Check CORS settings if running on different ports
