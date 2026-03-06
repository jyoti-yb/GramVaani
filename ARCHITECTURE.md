# Hyperlocal Context - System Architecture

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  • User location: "Bangalore, Karnataka"                         │
│  • Query: "What crops should I plant now?"                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                         │
│                                                                   │
│  1. Receive user query + location                                │
│  2. Fetch hyperlocal context from MongoDB                        │
│  3. Enrich AI prompt with context                                │
│  4. Generate response with Azure OpenAI                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
        ┌───────────────────┐  ┌──────────────────┐
        │  MongoDB Atlas    │  │  Azure OpenAI    │
        │                   │  │                  │
        │  Collections:     │  │  GPT-4o-mini     │
        │  • hyperlocal     │  │  with enhanced   │
        │  • success_stories│  │  context         │
        │  • pest_outbreaks │  │                  │
        └───────────────────┘  └──────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │   Hyperlocal Context Data     │
        │                               │
        │  • Soil: Red Sandy Loam       │
        │  • Season: Kharif             │
        │  • Crops: Ragi, Maize         │
        │  • Pest Alerts: Fall Armyworm │
        └───────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │      AI Response              │
        │                               │
        │  "Based on your Red Sandy     │
        │   Loam soil in Bangalore      │
        │   and current Kharif season,  │
        │   I recommend planting Ragi   │
        │   or Maize. Watch out for     │
        │   Fall Armyworm in Maize."    │
        └───────────────────────────────┘
```

## 🔄 Pest Outbreak Clustering Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Farmer A reports: "Fall Armyworm in Maize" (Day 1)         │
│  Location: Bangalore Rural                                    │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Farmer B reports: "Fall Armyworm in Maize" (Day 3)         │
│  Location: Bangalore Rural                                    │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Farmer C reports: "Fall Armyworm in Maize" (Day 5)         │
│  Location: Bangalore Rural                                    │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  CLUSTERING ALGORITHM          │
        │                                │
        │  Query: Count reports where:   │
        │  • Location matches            │
        │  • Pest name matches           │
        │  • Within last 7 days          │
        │                                │
        │  Result: 3 reports found       │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  ⚠️ OUTBREAK ALERT TRIGGERED   │
        │                                │
        │  Notify all farmers in area:   │
        │  "Fall Armyworm outbreak       │
        │   detected in Bangalore Rural" │
        └────────────────────────────────┘
```

## 🗄️ Database Schema

### Collection: hyperlocal_context
```json
{
  "_id": ObjectId("..."),
  "state": "Karnataka",
  "district": "Bangalore",
  "soil_type": "Red Sandy Loam",
  "rainfall": "900mm",
  "crops": {
    "kharif": ["Ragi", "Maize", "Groundnut"],
    "rabi": ["Tomato", "Beans", "Cabbage"],
    "summer": ["Cucumber", "Ridge Gourd"]
  },
  "pest_alerts": ["Fall Armyworm in Maize", "Aphids in Vegetables"],
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Collection: success_stories
```json
{
  "_id": ObjectId("..."),
  "farmer": "Ramesh Kumar",
  "location": "Bangalore, Karnataka",
  "crop": "Tomato",
  "achievement": "Increased yield by 40% using drip irrigation",
  "method": "Drip irrigation + organic fertilizers",
  "verified": true,
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Collection: pest_outbreaks
```json
{
  "_id": ObjectId("..."),
  "user_phone": "9999999999",
  "location": "Bangalore, Karnataka",
  "pest_name": "Fall Armyworm",
  "crop": "Maize",
  "severity": "high",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "verified": false
}
```

## 🎯 API Integration Points

### 1. Chat Integration
```python
# In process_text() and process_audio()
hyperlocal_context = fetch_from_mongodb(user_location)
ai_prompt = f"User context: {hyperlocal_context}"
response = azure_openai.chat(prompt=ai_prompt)
```

### 2. Weather Integration
```python
# In get_weather()
hyperlocal_data = fetch_from_mongodb(user_location)
weather_response += f"Soil type: {hyperlocal_data['soil_type']}"
weather_response += f"Recommended crops: {hyperlocal_data['crops']}"
```

### 3. Pest Alert Integration
```python
# In report_pest_outbreak()
nearby_reports = count_reports(location, pest_name, last_7_days)
if nearby_reports >= 3:
    trigger_outbreak_alert()
```

## 📈 Scalability Considerations

### Current Setup (MVP)
- **Data:** 5 states, 5 districts
- **Storage:** MongoDB Atlas (Free tier: 512MB)
- **Queries:** ~100 requests/day
- **Cost:** $0 (using free tier)

### Scale to 100 Districts
- **Data:** ~20 states, 100 districts
- **Storage:** ~50MB (text data)
- **Queries:** ~10,000 requests/day
- **Cost:** Still free tier

### Scale to All India (700+ Districts)
- **Data:** 28 states, 700+ districts
- **Storage:** ~300MB
- **Queries:** ~100,000 requests/day
- **Cost:** MongoDB Atlas M10 (~$57/month)
- **Optimization:** Add caching layer (Redis)

## 🔐 Data Quality & Verification

### Tier 1: Official Data (High Trust)
- Soil types from ICAR
- Crop calendars from Ministry of Agriculture
- Verified by agricultural experts

### Tier 2: Community Data (Medium Trust)
- Farmer reports (pest outbreaks)
- Success stories
- Requires 3+ validations to mark as verified

### Tier 3: Crowdsourced (Low Trust)
- Individual farmer observations
- Displayed with disclaimer
- Used for trend analysis only

## 🚀 Performance Optimization

### 1. Indexing
```python
# MongoDB indexes for fast queries
hyperlocal_collection.create_index([("state", 1), ("district", 1)])
success_stories_collection.create_index([("location", 1)])
pest_outbreaks_collection.create_index([("location", 1), ("timestamp", -1)])
```

### 2. Caching (Future)
```python
# Cache hyperlocal context for 24 hours
@cache(ttl=86400)
def get_hyperlocal_context(location):
    return hyperlocal_collection.find_one({"district": location})
```

### 3. Query Optimization
```python
# Use projection to fetch only needed fields
hyperlocal_collection.find_one(
    {"district": "Bangalore"},
    {"soil_type": 1, "crops": 1, "pest_alerts": 1}
)
```

## 🔮 Future Enhancements

### Phase 2: Advanced Features
1. **Geospatial Queries**
   - Use lat/long for precise location
   - Find farmers within 10km radius
   - Heatmap of pest outbreaks

2. **Predictive Analytics**
   - ML model: Soil + Weather → Yield prediction
   - Pest outbreak forecasting
   - Optimal planting time recommendations

3. **Market Integration**
   - Link hyperlocal data with mandi prices
   - Suggest crops based on demand + soil
   - Price trend analysis by region

4. **Community Features**
   - Farmer-to-farmer messaging
   - Local expert network
   - Video success stories

### Phase 3: Scale
1. **Multi-language Support**
   - Translate hyperlocal data to 9 Indian languages
   - Voice-based data entry for farmers

2. **Offline Mode**
   - Cache hyperlocal data on device
   - Sync when internet available

3. **Government Integration**
   - Direct link to PM-KISAN
   - Scheme eligibility based on location + crop
   - Digital land records integration

---

**Current Status:** ✅ Phase 1 Complete (MVP)  
**Next Step:** Run `python setup_hyperlocal.py` to deploy
