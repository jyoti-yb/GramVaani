# Smart Farm Advisor Setup Guide

## Step 1: Seed the Database

Run the seed script to populate MongoDB with initial data:

```bash
cd backend
python seed_database.py
```

This will create:
- 3 crop recommendations (Mango 24%, Mothbeans 17%, Papaya 15%)
- 4 optimization strategies (Drip Irrigation, Precision Fertigation, Mulching, Smart Monitoring)
- Templates for environmental profiles and farm intelligence

## Step 2: Verify Backend Endpoints

The following endpoints have been added to `main.py`:

- `GET /api/environmental-profile` - Get user's soil parameters
- `GET /api/crop-recommendations` - Get AI crop recommendations
- `GET /api/optimization-strategies` - Get farming strategies
- `GET /api/farm-intelligence` - Get analytics data
- `POST /api/get-crop-recommendation` - Calculate recommendations with custom parameters

## Step 3: Test the Advisor Page

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to the Advisor page (Smart Farm icon in navigation)

## Features

### ✅ Dynamic Data from MongoDB
- Environmental profile (Temperature, Humidity, Rainfall, N, P, K, pH)
- Crop recommendations with compatibility scores
- Optimization strategies with badges
- Farm intelligence analytics

### ✅ Interactive Sliders
- Adjust soil parameters in real-time
- Click "Get Crop Recommendation" to recalculate
- Compatibility scores update dynamically

### ✅ AI Insight Banner
- Shows real-time analysis based on current parameters
- Updates when sliders change

### ✅ Professional Design
- Two-column grid layout
- Green theme matching reference image
- Progress bars and badges
- Fully responsive

## Data Flow

1. **User opens Advisor page** → Frontend fetches data from 4 endpoints
2. **User adjusts sliders** → State updates in React
3. **User clicks "Get Recommendation"** → POST request with new parameters
4. **Backend calculates compatibility** → Returns sorted crop list
5. **Frontend updates UI** → Shows new recommendations

## MongoDB Collections Used

1. `environmental_profiles` - User soil parameters
2. `crop_recommendations` - Crop data with optimal conditions
3. `optimization_strategies` - Farming techniques
4. `farm_intelligence_analytics` - Analytics and insights

## Customization

### Add More Crops
Edit `seed_database.py` and add to the `crops` array:
```python
{
    "crop_name": "Cotton",
    "soil_compatibility": 20,
    "water_requirement": "High",
    ...
}
```

### Add More Strategies
Edit `seed_database.py` and add to the `strategies` array:
```python
{
    "strategy_name": "Organic Farming",
    "badge": "Peak",
    ...
}
```

### Adjust Compatibility Algorithm
Edit the `calculate_compatibility()` function in `main.py` to change scoring logic.

## Troubleshooting

### No data showing?
- Run `python seed_database.py` to populate database
- Check MongoDB connection in `.env`
- Verify backend is running on port 8000

### Sliders not working?
- Check browser console for errors
- Verify React state is updating
- Check network tab for API calls

### Recommendations not updating?
- Verify POST endpoint is being called
- Check backend logs for errors
- Ensure MongoDB write permissions

## Next Steps

1. ✅ Seed database with real crop data
2. ✅ Test all API endpoints
3. ✅ Verify UI matches reference image
4. 🔄 Add ML model for better recommendations
5. 🔄 Integrate weather API for real-time data
6. 🔄 Add more crops and strategies
