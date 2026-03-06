"""
Data Aggregator - Fetch ALL data first, then pass to LLM
This ensures LLM responses are based on actual data, not hallucinations
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os

def fetch_all_context_data(user_location: str, query: str) -> dict:
    """
    Fetch ALL relevant data before LLM processing
    Returns comprehensive context for accurate responses
    """
    
    context = {
        "hyperlocal": None,
        "weather": None,
        "pest_outbreaks": [],
        "disease_reports": [],
        "success_stories": [],
        "nearby_reports": [],
        "seasonal_info": None
    }
    
    # 1. Fetch Hyperlocal Agricultural Data
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URL"))
        db = mongo_client.gramvani
        
        location_parts = [p.strip() for p in user_location.split(",")]
        query_filter = {}
        
        if len(location_parts) >= 2:
            query_filter = {
                "$or": [
                    {"district": {"$regex": location_parts[0], "$options": "i"}},
                    {"state": {"$regex": location_parts[1], "$options": "i"}}
                ]
            }
        elif len(location_parts) == 1:
            query_filter = {
                "$or": [
                    {"district": {"$regex": location_parts[0], "$options": "i"}},
                    {"state": {"$regex": location_parts[0], "$options": "i"}}
                ]
            }
        
        hyperlocal_data = db.hyperlocal_context.find_one(query_filter)
        
        if hyperlocal_data:
            # Get current season
            month = datetime.utcnow().month
            if month in [6, 7, 8, 9, 10]:
                season = "kharif"
            elif month in [11, 12, 1, 2, 3]:
                season = "rabi"
            else:
                season = "summer"
            
            context["hyperlocal"] = {
                "district": hyperlocal_data.get("district"),
                "state": hyperlocal_data.get("state"),
                "soil_type": hyperlocal_data.get("soil_type"),
                "rainfall": hyperlocal_data.get("rainfall"),
                "current_season": season,
                "recommended_crops": hyperlocal_data.get("crops", {}).get(season, []),
                "all_crops": hyperlocal_data.get("crops", {}),
                "pest_alerts": hyperlocal_data.get("pest_alerts", [])
            }
            
            context["seasonal_info"] = {
                "season": season,
                "months": get_season_months(season),
                "activities": get_seasonal_activities(season)
            }
    except Exception as e:
        print(f"Hyperlocal data fetch error: {e}")
    
    # 2. Fetch Weather Data (if query mentions weather)
    if any(word in query.lower() for word in ['weather', 'temperature', 'rain', 'climate']):
        try:
            city = user_location.split(",")[0].strip()
            api_key = os.getenv("OPENWEATHER_API_KEY")
            
            if api_key:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=10)
                
                if res.status_code == 200:
                    data = res.json()
                    context["weather"] = {
                        "city": city,
                        "description": data["weather"][0]["description"],
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "feels_like": data["main"]["feels_like"]
                    }
        except Exception as e:
            print(f"Weather fetch error: {e}")
    
    # 3. Fetch Pest Outbreaks (last 7 days) + Government Pest Data
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # User-reported pests
        pest_reports = list(db.pest_outbreaks.find({
            "location": {"$regex": location_parts[0], "$options": "i"},
            "timestamp": {"$gte": week_ago}
        }).limit(10))
        
        # Government pest data
        govt_pest_reports = list(db.pest_reports.find({
            "state": {"$regex": location_parts[0] if len(location_parts) > 0 else "", "$options": "i"}
        }).limit(5))
        
        context["pest_outbreaks"] = [
            {
                "pest_name": r.get("pest_name"),
                "crop": r.get("crop"),
                "severity": r.get("severity"),
                "days_ago": (datetime.utcnow() - r.get("timestamp")).days if isinstance(r.get("timestamp"), datetime) else 0,
                "source": "Community Report"
            }
            for r in pest_reports
        ]
        
        # Add government pest data
        for r in govt_pest_reports:
            context["pest_outbreaks"].append({
                "pest_name": r.get("pest_name"),
                "crop": r.get("crop"),
                "severity": r.get("severity"),
                "description": r.get("description"),
                "source": r.get("source", "Government Data")
            })
    except Exception as e:
        print(f"Pest outbreak fetch error: {e}")
    
    # 4. Fetch Disease Reports from Government Data
    try:
        govt_disease_reports = list(db.disease_reports.find({
            "state": {"$regex": location_parts[0] if len(location_parts) > 0 else "", "$options": "i"}
        }).limit(5))
        
        context["disease_reports"] = [
            {
                "disease_name": r.get("disease_name"),
                "crop": r.get("crop"),
                "severity": r.get("severity"),
                "description": r.get("description"),
                "source": r.get("source", "Government Data")
            }
            for r in govt_disease_reports
        ]
    except Exception as e:
        print(f"Disease reports fetch error: {e}")
    
    # 5. Fetch Success Stories (nearby farmers)
    try:
        stories = list(db.success_stories.find({
            "location": {"$regex": location_parts[0], "$options": "i"}
        }).limit(5))
        
        context["success_stories"] = [
            {
                "farmer": s.get("farmer"),
                "crop": s.get("crop"),
                "achievement": s.get("achievement"),
                "method": s.get("method")
            }
            for s in stories
        ]
    except Exception as e:
        print(f"Success stories fetch error: {e}")
    
    # 6. Fetch Crop Prices (if query mentions prices)
    if any(word in query.lower() for word in ['price', 'cost', 'rate', 'market', 'mandi']):
        context["crop_prices"] = {
            "market": location_parts[0],
            "prices": {
                "wheat": 2000,
                "rice": 2400,
                "cotton": 6000,
                "soybean": 4400,
                "onion": 3000,
                "potato": 1400,
                "tomato": 3600
            },
            "unit": "₹ per quintal",
            "last_updated": "Today"
        }
    
    return context

def get_season_months(season: str) -> str:
    """Get month range for season"""
    seasons = {
        "kharif": "June to October (Monsoon season)",
        "rabi": "November to March (Winter season)",
        "summer": "April to May (Summer season)"
    }
    return seasons.get(season, "")

def get_seasonal_activities(season: str) -> list:
    """Get farming activities for season"""
    activities = {
        "kharif": [
            "Sowing of monsoon crops",
            "Prepare fields before monsoon",
            "Check irrigation systems",
            "Monitor pest activity (high during monsoon)"
        ],
        "rabi": [
            "Sowing of winter crops",
            "Harvest kharif crops",
            "Prepare for winter",
            "Apply fertilizers"
        ],
        "summer": [
            "Harvest rabi crops",
            "Prepare for next kharif season",
            "Maintain irrigation",
            "Grow short-duration vegetables"
        ]
    }
    return activities.get(season, [])

def format_context_for_llm(context: dict) -> str:
    """
    Format fetched data into structured prompt for LLM
    """
    
    prompt_parts = []
    
    # Hyperlocal context
    if context.get("hyperlocal"):
        h = context["hyperlocal"]
        prompt_parts.append(f"""
LOCATION DATA:
- District: {h['district']}, {h['state']}
- Soil Type: {h['soil_type']}
- Average Rainfall: {h['rainfall']}
- Current Season: {h['current_season']} ({context['seasonal_info']['months']})
- Recommended Crops for {h['current_season']}: {', '.join(h['recommended_crops'])}
- All Crops by Season:
  * Kharif: {', '.join(h['all_crops'].get('kharif', []))}
  * Rabi: {', '.join(h['all_crops'].get('rabi', []))}
  * Summer: {', '.join(h['all_crops'].get('summer', []))}
- Pest Alerts: {', '.join(h['pest_alerts']) if h['pest_alerts'] else 'None'}
""")
    
    # Weather data
    if context.get("weather"):
        w = context["weather"]
        prompt_parts.append(f"""
CURRENT WEATHER ({w['city']}):
- Condition: {w['description']}
- Temperature: {w['temperature']}°C (Feels like {w['feels_like']}°C)
- Humidity: {w['humidity']}%
- Wind Speed: {w['wind_speed']} m/s
""")
    
    # Pest outbreaks
    if context.get("pest_outbreaks"):
        prompt_parts.append("\nRECENT PEST OUTBREAKS:")
        for pest in context["pest_outbreaks"]:
            source = pest.get('source', 'Unknown')
            if 'days_ago' in pest:
                prompt_parts.append(f"- {pest['pest_name']} in {pest['crop']} ({pest['severity']} severity, {pest['days_ago']} days ago) [{source}]")
            else:
                prompt_parts.append(f"- {pest['pest_name']} in {pest['crop']} ({pest['severity']} severity) - {pest.get('description', '')} [{source}]")
    
    # Disease reports
    if context.get("disease_reports"):
        prompt_parts.append("\nCROP DISEASE ALERTS:")
        for disease in context["disease_reports"]:
            prompt_parts.append(f"- {disease['disease_name']} in {disease['crop']} ({disease['severity']} severity) - {disease.get('description', '')} [{disease.get('source', 'Unknown')}]")
    
    # Success stories
    if context.get("success_stories"):
        prompt_parts.append("\nNEARBY FARMER SUCCESS STORIES:")
        for story in context["success_stories"]:
            prompt_parts.append(f"- {story['farmer']}: {story['achievement']} ({story['method']})")
    
    # Crop prices
    if context.get("crop_prices"):
        p = context["crop_prices"]
        prompt_parts.append(f"\nCURRENT MARKET PRICES ({p['market']} Market):")
        for crop, price in p["prices"].items():
            prompt_parts.append(f"- {crop.capitalize()}: ₹{price} per quintal")
    
    # Seasonal activities
    if context.get("seasonal_info"):
        prompt_parts.append(f"\nSEASONAL ACTIVITIES ({context['seasonal_info']['season'].upper()}):")
        for activity in context['seasonal_info']['activities']:
            prompt_parts.append(f"- {activity}")
    
    return "\n".join(prompt_parts)
