"""
MongoDB Seed Script for Smart Farm Advisor Data
Run this script to populate the database with initial data
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://gramvani_user:GramVaani123!@firewall.jchsp.mongodb.net/gramvani?retryWrites=true&w=majority")
client = MongoClient(MONGO_URL)
db = client.gramvani

def seed_crop_recommendations():
    """Seed crop recommendations data"""
    crops = [
        {
            "crop_name": "Mango",
            "climate_match": "Climate Match",
            "soil_compatibility": 24,
            "water_requirement": "Moderate",
            "water_level": "Water: Moderate",
            "yield_potential": "High",
            "optimal_conditions": {
                "temperature_min": 10,
                "temperature_max": 15,
                "humidity_min": 30,
                "humidity_max": 45,
                "rainfall_min": 80,
                "rainfall_max": 120,
                "nitrogen_min": 40,
                "nitrogen_max": 60,
                "phosphorus_min": 40,
                "phosphorus_max": 60,
                "potassium_min": 40,
                "potassium_max": 60,
                "ph_min": 8.0,
                "ph_max": 9.0
            },
            "growing_season": "Summer",
            "market_demand": "High",
            "created_at": datetime.now()
        },
        {
            "crop_name": "Mothbeans",
            "climate_match": "Climate Match",
            "soil_compatibility": 17,
            "water_requirement": "Moderate",
            "water_level": "Water: Moderate",
            "yield_potential": "Moderate",
            "optimal_conditions": {
                "temperature_min": 10,
                "temperature_max": 15,
                "humidity_min": 30,
                "humidity_max": 45,
                "rainfall_min": 80,
                "rainfall_max": 120,
                "nitrogen_min": 45,
                "nitrogen_max": 55,
                "phosphorus_min": 45,
                "phosphorus_max": 55,
                "potassium_min": 45,
                "potassium_max": 55,
                "ph_min": 8.0,
                "ph_max": 9.0
            },
            "growing_season": "Kharif",
            "market_demand": "Moderate",
            "created_at": datetime.now()
        },
        {
            "crop_name": "Papaya",
            "climate_match": "Climate Match",
            "soil_compatibility": 15,
            "water_requirement": "High",
            "water_level": "Water: High",
            "yield_potential": "High",
            "optimal_conditions": {
                "temperature_min": 10,
                "temperature_max": 15,
                "humidity_min": 30,
                "humidity_max": 45,
                "rainfall_min": 80,
                "rainfall_max": 120,
                "nitrogen_min": 48,
                "nitrogen_max": 52,
                "phosphorus_min": 48,
                "phosphorus_max": 52,
                "potassium_min": 48,
                "potassium_max": 52,
                "ph_min": 8.0,
                "ph_max": 9.0
            },
            "growing_season": "Year-round",
            "market_demand": "High",
            "created_at": datetime.now()
        }
    ]
    
    db.crop_recommendations.delete_many({})
    db.crop_recommendations.insert_many(crops)
    print(f"✅ Seeded {len(crops)} crop recommendations")


def seed_optimization_strategies():
    """Seed optimization strategies data"""
    strategies = [
        {
            "strategy_name": "Drip Irrigation",
            "category": "Irrigation",
            "impact_level": "High",
            "difficulty": "Medium",
            "cost_effectiveness": "75%",
            "description": "Efficient water delivery system that saves 40% water",
            "benefits": [
                "Reduces water consumption by 40%",
                "Improves crop yield",
                "Reduces weed growth"
            ],
            "implementation_steps": [
                "Install drip lines along crop rows",
                "Connect to water source with filter",
                "Set timer for automated watering"
            ],
            "suitable_for_crops": ["Mango", "Papaya", "Cotton"],
            "resource_links": ["https://agricoop.gov.in/drip-irrigation"],
            "badge": "Minimal",
            "created_at": datetime.now()
        },
        {
            "strategy_name": "Precision Fertigation",
            "category": "Fertilization",
            "impact_level": "High",
            "difficulty": "Low",
            "cost_effectiveness": "75%",
            "description": "Combine fertilizer with irrigation for optimal nutrient delivery",
            "benefits": [
                "Reduces fertilizer waste",
                "Improves nutrient uptake",
                "Saves labor costs"
            ],
            "implementation_steps": [
                "Mix water-soluble fertilizers",
                "Inject into irrigation system",
                "Monitor soil nutrient levels"
            ],
            "suitable_for_crops": ["All crops"],
            "resource_links": ["https://agricoop.gov.in/fertigation"],
            "badge": "Moderate",
            "created_at": datetime.now()
        },
        {
            "strategy_name": "Mulching System",
            "category": "Soil Management",
            "impact_level": "Medium",
            "difficulty": "Low",
            "cost_effectiveness": "80%",
            "description": "Cover soil with organic material to retain moisture",
            "benefits": [
                "Retains soil moisture",
                "Reduces weed growth by 70%",
                "Improves soil health"
            ],
            "implementation_steps": [
                "Spread organic mulch around plants",
                "Maintain 2-3 inch thickness",
                "Keep mulch away from plant stems"
            ],
            "suitable_for_crops": ["Vegetables", "Fruits"],
            "resource_links": ["https://agricoop.gov.in/mulching"],
            "badge": "Peak",
            "created_at": datetime.now()
        },
        {
            "strategy_name": "Smart Monitoring",
            "category": "Monitoring",
            "impact_level": "High",
            "difficulty": "Medium",
            "cost_effectiveness": "50%",
            "description": "Use sensors and IoT devices to monitor crop health",
            "benefits": [
                "Early disease detection",
                "Optimized resource usage",
                "Data-driven decisions"
            ],
            "implementation_steps": [
                "Install soil moisture sensors",
                "Set up weather monitoring",
                "Connect to mobile app"
            ],
            "suitable_for_crops": ["All crops"],
            "resource_links": ["https://agricoop.gov.in/smart-farming"],
            "badge": "Peak",
            "created_at": datetime.now()
        }
    ]
    
    db.optimization_strategies.delete_many({})
    db.optimization_strategies.insert_many(strategies)
    print(f"✅ Seeded {len(strategies)} optimization strategies")


def seed_farm_intelligence():
    """Seed farm intelligence analytics data"""
    analytics = {
        "location": "Kunchanapalli",
        "load_predictions": 3,
        "top_crop": "mango",
        "soil_stability": 86,
        "climate_risk": "Low",
        "feature_importance": {
            "nitrogen": 20,
            "phosphorus": 15,
            "potassium": 15,
            "temperature": 18,
            "humidity": 12,
            "ph": 10,
            "rainfall": 10
        },
        "ai_insights": {
            "soil_ph_optimal": True,
            "nitrogen_level": "Optimal",
            "rainfall_suitability": "Suitable for mango cultivation",
            "temperature_range": "Ideal for tropical crops"
        },
        "last_updated": datetime.now(),
        "created_at": datetime.now()
    }
    
    # This will be user-specific, so we'll create a template
    print("✅ Farm intelligence template ready (will be created per user)")
    return analytics


def seed_environmental_profiles():
    """Seed environmental profile template"""
    profile = {
        "location": {
            "city": "Kunchanapalli",
            "state": "Andhra Pradesh",
            "coordinates": {"lat": 14.4426, "lng": 79.9865}
        },
        "temperature": 12,
        "humidity": 37,
        "rainfall": 100,
        "nitrogen": 50,
        "phosphorus": 50,
        "potassium": 50,
        "soil_ph": 8.5,
        "soil_temperature": 12,
        "soil_humidity": 37,
        "rainfall_annual": 100,
        "last_updated": datetime.now(),
        "created_at": datetime.now()
    }
    
    print("✅ Environmental profile template ready (will be created per user)")
    return profile


def main():
    """Run all seed functions"""
    print("🌱 Starting database seeding...")
    print("-" * 50)
    
    seed_crop_recommendations()
    seed_optimization_strategies()
    seed_farm_intelligence()
    seed_environmental_profiles()
    
    print("-" * 50)
    print("✅ Database seeding completed successfully!")
    print("\nCollections populated:")
    print(f"  - crop_recommendations: {db.crop_recommendations.count_documents({})}")
    print(f"  - optimization_strategies: {db.optimization_strategies.count_documents({})}")


if __name__ == "__main__":
    main()
