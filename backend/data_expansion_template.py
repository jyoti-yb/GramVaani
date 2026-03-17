# Template for Expanding Hyperlocal Data
# Copy this structure to add more states/districts

EXPANDED_DATA_TEMPLATE = {
    "State_Name": {
        "districts": {
            "District_Name": {
                "soil_type": "Soil classification (Red/Black/Alluvial/Sandy/Laterite)",
                "rainfall": "Annual rainfall in mm",
                "crops": {
                    "kharif": ["Crop1", "Crop2", "Crop3"],  # June-October
                    "rabi": ["Crop1", "Crop2", "Crop3"],    # November-March
                    "summer": ["Crop1", "Crop2"]            # April-May
                },
                "pest_alerts": ["Common pest/disease issues"],
                "irrigation": "Primary irrigation method",
                "avg_farm_size": "Average farm size in acres"
            }
        }
    }
}

# Example: Adding more comprehensive data
COMPREHENSIVE_DATA = {
    "Andhra Pradesh": {
        "districts": {
            "Guntur": {
                "soil_type": "Black Cotton Soil",
                "rainfall": "900mm",
                "crops": {
                    "kharif": ["Paddy", "Cotton", "Chili"],
                    "rabi": ["Tobacco", "Sunflower", "Maize"],
                    "summer": ["Watermelon", "Muskmelon"]
                },
                "pest_alerts": ["Thrips in Chili", "Bollworm in Cotton"],
                "irrigation": "Canal + Borewell",
                "avg_farm_size": "3 acres"
            },
            "Krishna": {
                "soil_type": "Alluvial Soil",
                "rainfall": "1000mm",
                "crops": {
                    "kharif": ["Paddy", "Sugarcane"],
                    "rabi": ["Paddy", "Pulses"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Stem Borer in Paddy"],
                "irrigation": "Canal",
                "avg_farm_size": "2.5 acres"
            }
        }
    },
    "Gujarat": {
        "districts": {
            "Ahmedabad": {
                "soil_type": "Sandy Loam",
                "rainfall": "800mm",
                "crops": {
                    "kharif": ["Cotton", "Groundnut", "Bajra"],
                    "rabi": ["Wheat", "Cumin", "Fennel"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Pink Bollworm in Cotton"],
                "irrigation": "Drip + Sprinkler",
                "avg_farm_size": "4 acres"
            },
            "Surat": {
                "soil_type": "Black Soil",
                "rainfall": "1200mm",
                "crops": {
                    "kharif": ["Sugarcane", "Paddy"],
                    "rabi": ["Wheat", "Vegetables"],
                    "summer": ["Mango", "Chikoo"]
                },
                "pest_alerts": ["Fruit Fly in Mango"],
                "irrigation": "Canal",
                "avg_farm_size": "3 acres"
            }
        }
    },
    "Rajasthan": {
        "districts": {
            "Jaipur": {
                "soil_type": "Sandy Soil",
                "rainfall": "600mm",
                "crops": {
                    "kharif": ["Bajra", "Jowar", "Groundnut"],
                    "rabi": ["Wheat", "Mustard", "Gram"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Locust attacks possible"],
                "irrigation": "Drip irrigation",
                "avg_farm_size": "5 acres"
            }
        }
    },
    "West Bengal": {
        "districts": {
            "Kolkata": {
                "soil_type": "Alluvial Soil",
                "rainfall": "1600mm",
                "crops": {
                    "kharif": ["Paddy", "Jute"],
                    "rabi": ["Wheat", "Potato", "Mustard"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Blast in Paddy", "Late Blight in Potato"],
                "irrigation": "Canal + Pond",
                "avg_farm_size": "1.5 acres"
            }
        }
    },
    "Madhya Pradesh": {
        "districts": {
            "Indore": {
                "soil_type": "Black Soil",
                "rainfall": "900mm",
                "crops": {
                    "kharif": ["Soybean", "Cotton", "Maize"],
                    "rabi": ["Wheat", "Gram", "Mustard"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Yellow Mosaic in Soybean"],
                "irrigation": "Borewell",
                "avg_farm_size": "4 acres"
            }
        }
    }
}

# More Success Stories Template
MORE_SUCCESS_STORIES = [
    {
        "farmer": "Suresh Patil",
        "location": "Pune, Maharashtra",
        "crop": "Soybean",
        "achievement": "Reduced pest damage by 60% using IPM",
        "method": "Integrated Pest Management with pheromone traps"
    },
    {
        "farmer": "Lakshmi Devi",
        "location": "Guntur, Andhra Pradesh",
        "crop": "Chili",
        "achievement": "Increased income by 80% with organic farming",
        "method": "Organic certification + direct market linkage"
    },
    {
        "farmer": "Rajesh Singh",
        "location": "Jaipur, Rajasthan",
        "crop": "Bajra",
        "achievement": "Survived drought with 70% yield using mulching",
        "method": "Plastic mulching + drip irrigation"
    },
    {
        "farmer": "Priya Sharma",
        "location": "Ahmedabad, Gujarat",
        "crop": "Cotton",
        "achievement": "Doubled profit with Bt Cotton + IPM",
        "method": "Bt Cotton seeds + biological pest control"
    },
    {
        "farmer": "Mohan Kumar",
        "location": "Mysore, Karnataka",
        "crop": "Paddy",
        "achievement": "Saved 40% water using SRI method",
        "method": "System of Rice Intensification"
    }
]

# How to use this template:
# 1. Copy the structure above
# 2. Add to hyperlocal_data.py
# 3. Run: python setup_hyperlocal.py
# 4. Data will be available via API

# Data Sources for Expansion:
"""
1. Soil Data:
   - ICAR (Indian Council of Agricultural Research)
   - State Agriculture Departments
   - Soil Health Card data

2. Crop Calendars:
   - Ministry of Agriculture & Farmers Welfare
   - State Agricultural Universities
   - ICAR-CRIDA (Central Research Institute for Dryland Agriculture)

3. Pest Alerts:
   - ICAR-NBAIR (National Bureau of Agricultural Insect Resources)
   - State Plant Protection Offices
   - Directorate of Plant Protection, Quarantine & Storage

4. Success Stories:
   - Farmer testimonials
   - NGO reports (PRADAN, Digital Green, etc.)
   - Krishi Vigyan Kendras (KVKs)
   - State Agriculture Department case studies

5. Market Data:
   - Agmarknet (agmarknet.gov.in)
   - eNAM (National Agriculture Market)
   - State Mandi Boards
"""
