# 🌾 Hyperlocal Context Implementation

## Overview
Enhanced location-based agricultural intelligence with:
- **Soil type data** by district
- **Seasonal crop calendars** (Kharif/Rabi/Summer)
- **Pest outbreak clustering** and alerts
- **Nearby farmer success stories**

## Database: MongoDB Atlas
Using your existing MongoDB connection for:
- Flexible querying (location clustering)
- Hierarchical data (State → District → Village)
- Fast geospatial queries

## Setup

### 1. Install Dependencies
```bash
cd backend
pip install pymongo
```

### 2. Seed Hyperlocal Data
```bash
python setup_hyperlocal.py
```

This creates 3 MongoDB collections:
- `hyperlocal_context` - Soil types, crops, rainfall by district
- `success_stories` - Verified farmer success stories
- `pest_outbreaks` - Real-time pest/disease reports

## API Endpoints

### Get Hyperlocal Context
```
GET /api/hyperlocal-context
Authorization: Bearer <token>
```

**Response:**
```json
{
  "has_data": true,
  "location": "Bangalore, Karnataka",
  "soil_type": "Red Sandy Loam",
  "rainfall": "900mm",
  "current_season": "kharif",
  "recommended_crops": ["Ragi", "Maize", "Groundnut"],
  "pest_alerts": ["Fall Armyworm in Maize"]
}
```

### Get Success Stories
```
GET /api/success-stories?limit=10
Authorization: Bearer <token>
```

**Response:**
```json
{
  "stories": [
    {
      "farmer": "Ramesh Kumar",
      "location": "Bangalore, Karnataka",
      "crop": "Tomato",
      "achievement": "Increased yield by 40% using drip irrigation",
      "method": "Drip irrigation + organic fertilizers"
    }
  ],
  "count": 1
}
```

### Report Pest Outbreak
```
POST /api/report-pest-outbreak
Authorization: Bearer <token>
Content-Type: application/json

{
  "pest_name": "Fall Armyworm",
  "crop": "Maize",
  "severity": "high"
}
```

**Response:**
```json
{
  "status": "success",
  "outbreak_alert": true,
  "nearby_reports": 5,
  "message": "Outbreak alert! 5 reports in your area"
}
```

## Data Structure

### Hyperlocal Context
```python
{
  "state": "Karnataka",
  "district": "Bangalore",
  "soil_type": "Red Sandy Loam",
  "rainfall": "900mm",
  "crops": {
    "kharif": ["Ragi", "Maize", "Groundnut"],
    "rabi": ["Tomato", "Beans", "Cabbage"],
    "summer": ["Cucumber", "Ridge Gourd"]
  },
  "pest_alerts": ["Fall Armyworm in Maize"]
}
```

### Pest Outbreak Clustering
- Tracks reports by location + pest + timestamp
- Alerts when 3+ reports in same area within 7 days
- Enables early warning system

## Expanding the Dataset

### Add More Districts
Edit `hyperlocal_data.py`:
```python
"Telangana": {
    "districts": {
        "Hyderabad": {
            "soil_type": "Red Soil",
            "rainfall": "800mm",
            "crops": {
                "kharif": ["Paddy", "Cotton"],
                "rabi": ["Maize", "Sunflower"],
                "summer": ["Vegetables"]
            }
        }
    }
}
```

Then run: `python setup_hyperlocal.py`

### Add Success Stories
```python
SUCCESS_STORIES.append({
    "farmer": "Lakshmi Devi",
    "location": "Mysore, Karnataka",
    "crop": "Paddy",
    "achievement": "Doubled income using SRI method",
    "method": "System of Rice Intensification"
})
```

## Integration with Chat

The AI assistant automatically uses hyperlocal context when:
1. User asks about crops: "What should I plant now?"
2. User asks about soil: "What's my soil type?"
3. User reports pests: "I see worms in my maize"

Example:
```
User: "What crops should I grow now?"
AI: "Based on your location (Bangalore, Karnataka) with Red Sandy Loam soil 
     and current Kharif season, I recommend: Ragi, Maize, or Groundnut."
```

## Why MongoDB over DynamoDB?

✅ **Better for this use case:**
- Complex queries (location clustering)
- Flexible schema (varying district data)
- Geospatial indexing
- Already configured in your project

❌ **DynamoDB would require:**
- Additional AWS setup
- More complex query patterns
- Higher cost for location-based queries

## Next Steps

1. **Run setup:** `python setup_hyperlocal.py`
2. **Test API:** Use Postman or frontend
3. **Add more data:** Expand `hyperlocal_data.py`
4. **Integrate frontend:** Display soil type, seasonal crops, success stories

## Data Sources (for expansion)

- **Soil Data:** ICAR, State Agriculture Departments
- **Crop Calendars:** Ministry of Agriculture
- **Success Stories:** Farmer testimonials, NGO reports
- **Pest Alerts:** ICAR-NBAIR, State Plant Protection Offices
