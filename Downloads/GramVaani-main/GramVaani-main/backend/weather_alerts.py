"""
Weather Alert Service for GramVaani
Monitors weather conditions and sends SMS alerts to farmers
"""

import os
import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

class AlertType(Enum):
    HEATWAVE = "heatwave"
    HEAVY_RAIN = "heavy_rain"
    HIGH_HUMIDITY = "high_humidity"
    HIGH_WIND = "high_wind"
    LOW_TEMPERATURE = "low_temperature"
    THUNDERSTORM = "thunderstorm"
    DRY_SPELL = "dry_spell"

@dataclass
class WeatherData:
    temp: float  # Celsius
    humidity: float  # Percentage
    wind_speed: float  # km/h
    rain_mm: float  # mm expected
    description: str
    city: str

@dataclass
class WeatherAlert:
    alert_type: AlertType
    title: str
    message: str
    crop_advice: Optional[str] = None
    severity: str = "medium"  # low, medium, high

# Alert thresholds
THRESHOLDS = {
    "heatwave_temp": 38,  # °C
    "heavy_rain_mm": 20,  # mm
    "high_humidity": 80,  # %
    "humidity_fungal_temp_min": 20,  # °C
    "humidity_fungal_temp_max": 30,  # °C
    "high_wind_speed": 20,  # km/h
    "frost_temp": 8,  # °C
    "dry_spell_days": 7  # days without rain
}

# Crop-specific advice templates
CROP_ADVICE = {
    "heatwave": {
        "chilli": "High temperature today may cause flower drop in chilli crop. Ensure proper irrigation and avoid spraying during afternoon.",
        "tomato": "Heat stress may affect tomato fruit setting. Provide shade if possible and water in early morning.",
        "wheat": "High temperature can affect wheat grain filling. Ensure adequate irrigation.",
        "rice": "Paddy can tolerate heat but ensure standing water in fields.",
        "cotton": "Cotton is heat tolerant but ensure regular irrigation during flowering.",
        "default": "Irrigate in early morning or evening. Avoid fertilizer application during peak afternoon heat."
    },
    "heavy_rain": {
        "paddy": "Rainfall expected. Paddy fields may benefit, but check bunds and drainage channels.",
        "tomato": "Heavy rain can cause fruit cracking in tomato. Ensure proper drainage.",
        "onion": "Excess water can cause bulb rot in onion. Ensure field drainage.",
        "cotton": "Heavy rain during boll opening can damage cotton. Monitor fields closely.",
        "default": "Ensure proper drainage in fields to prevent waterlogging."
    },
    "high_humidity": {
        "tomato": "High humidity can cause leaf spot in tomato crop. Monitor leaves and remove infected plants if seen.",
        "chilli": "Humidity increases anthracnose risk in chilli. Apply preventive fungicide spray.",
        "grape": "High humidity increases downy mildew risk in grapes. Scout for symptoms.",
        "potato": "Late blight risk high in potato. Monitor and apply protective spray if needed.",
        "default": "Inspect leaves regularly for fungal spots. Avoid spraying before rain."
    },
    "high_wind": {
        "banana": "Secure banana plants. Strong winds can cause pseudostem breakage.",
        "sugarcane": "Tall sugarcane may lodge in high winds. Consider harvesting mature crop.",
        "maize": "Wind can cause lodging in maize. Avoid if crop is at tasseling stage.",
        "default": "Avoid spraying pesticides today as spray may drift and become ineffective."
    },
    "low_temperature": {
        "tomato": "Tomato is sensitive to frost. Cover plants with plastic sheets at night.",
        "chilli": "Chilli plants may show cold injury. Avoid irrigation in evening.",
        "papaya": "Papaya is frost sensitive. Protect young plants.",
        "wheat": "Wheat can tolerate cold but watch for frost injury on young tillers.",
        "default": "Consider covering young plants during night to protect from frost."
    },
    "thunderstorm": {
        "default": "Avoid field work during storm hours. Secure loose farm materials and equipment."
    },
    "dry_spell": {
        "rice": "Plan alternate wetting and drying if water is limited for paddy.",
        "sugarcane": "Sugarcane is drought tolerant but irrigation improves yield.",
        "cotton": "Cotton can tolerate short dry spells but irrigate during flowering.",
        "default": "Plan irrigation accordingly to avoid crop stress."
    }
}

class WeatherAlertService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str) -> Optional[WeatherData]:
        """Fetch current weather data for a city"""
        try:
            url = f"{self.base_url}/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Weather API error for {city}: {response.status_code}")
                return None
            
            data = response.json()
            
            # Get rain data (if available)
            rain_mm = 0
            if 'rain' in data:
                rain_mm = data['rain'].get('1h', 0) or data['rain'].get('3h', 0)
            
            return WeatherData(
                temp=data['main']['temp'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed'] * 3.6,  # Convert m/s to km/h
                rain_mm=rain_mm,
                description=data['weather'][0]['description'],
                city=city
            )
        except Exception as e:
            print(f"Error fetching weather for {city}: {e}")
            return None
    
    def get_forecast(self, city: str) -> Optional[Dict]:
        """Fetch 5-day weather forecast"""
        try:
            url = f"{self.base_url}/forecast?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            return response.json()
        except Exception as e:
            print(f"Error fetching forecast for {city}: {e}")
            return None
    
    def check_for_alerts(self, weather: WeatherData, user_crops: List[str] = None) -> List[WeatherAlert]:
        """Check weather conditions and generate alerts"""
        alerts = []
        crops = user_crops or ["default"]
        
        # 1. Heatwave Alert (Temp > 38°C)
        if weather.temp > THRESHOLDS["heatwave_temp"]:
            crop_advice = self._get_crop_advice("heatwave", crops)
            alerts.append(WeatherAlert(
                alert_type=AlertType.HEATWAVE,
                title="🔥 Heatwave Alert",
                message=f"Heatwave alert in {weather.city}! Temperature is {weather.temp:.1f}°C. High temperature may stress crops.",
                crop_advice=crop_advice,
                severity="high"
            ))
        
        # 2. Heavy Rain Alert (Rain > 20mm)
        if weather.rain_mm > THRESHOLDS["heavy_rain_mm"] or "rain" in weather.description.lower():
            crop_advice = self._get_crop_advice("heavy_rain", crops)
            # Check description for heavy rain indicators
            is_heavy = weather.rain_mm > THRESHOLDS["heavy_rain_mm"] or any(
                word in weather.description.lower() 
                for word in ["heavy", "shower", "storm"]
            )
            if is_heavy:
                alerts.append(WeatherAlert(
                    alert_type=AlertType.HEAVY_RAIN,
                    title="🌧️ Heavy Rain Alert",
                    message=f"Heavy rain expected in {weather.city}. Avoid pesticide spraying today.",
                    crop_advice=crop_advice,
                    severity="medium"
                ))
        
        # 3. High Humidity - Fungal Risk (Humidity > 80% and Temp 20-30°C)
        if (weather.humidity > THRESHOLDS["high_humidity"] and 
            THRESHOLDS["humidity_fungal_temp_min"] <= weather.temp <= THRESHOLDS["humidity_fungal_temp_max"]):
            crop_advice = self._get_crop_advice("high_humidity", crops)
            alerts.append(WeatherAlert(
                alert_type=AlertType.HIGH_HUMIDITY,
                title="🌫️ High Humidity Alert",
                message=f"High humidity ({weather.humidity}%) in {weather.city} may increase fungal disease risk.",
                crop_advice=crop_advice,
                severity="medium"
            ))
        
        # 4. High Wind Speed (> 20 km/h)
        if weather.wind_speed > THRESHOLDS["high_wind_speed"]:
            crop_advice = self._get_crop_advice("high_wind", crops)
            alerts.append(WeatherAlert(
                alert_type=AlertType.HIGH_WIND,
                title="🌬️ High Wind Alert",
                message=f"Strong winds ({weather.wind_speed:.1f} km/h) expected in {weather.city}.",
                crop_advice=crop_advice,
                severity="medium"
            ))
        
        # 5. Low Temperature / Frost Warning (< 8°C)
        if weather.temp < THRESHOLDS["frost_temp"]:
            crop_advice = self._get_crop_advice("low_temperature", crops)
            alerts.append(WeatherAlert(
                alert_type=AlertType.LOW_TEMPERATURE,
                title="❄️ Frost Warning",
                message=f"Low temperature alert in {weather.city}! Temperature is {weather.temp:.1f}°C. Sensitive crops may face frost damage.",
                crop_advice=crop_advice,
                severity="high"
            ))
        
        # 6. Thunderstorm Alert
        if any(word in weather.description.lower() for word in ["thunder", "storm", "lightning"]):
            crop_advice = self._get_crop_advice("thunderstorm", crops)
            alerts.append(WeatherAlert(
                alert_type=AlertType.THUNDERSTORM,
                title="🌩️ Thunderstorm Alert",
                message=f"Thunderstorm expected in {weather.city}.",
                crop_advice=crop_advice,
                severity="high"
            ))
        
        return alerts
    
    def _get_crop_advice(self, alert_type: str, crops: List[str]) -> str:
        """Get crop-specific advice for an alert type"""
        advice_dict = CROP_ADVICE.get(alert_type, {})
        
        # Try to find advice for user's crops
        for crop in crops:
            crop_lower = crop.lower()
            if crop_lower in advice_dict:
                return advice_dict[crop_lower]
        
        # Return default advice
        return advice_dict.get("default", "Take appropriate precautions.")
    
    def format_sms_message(self, alert: WeatherAlert) -> str:
        """Format alert as SMS message"""
        message = f"{alert.title}\n\n{alert.message}"
        
        if alert.crop_advice:
            message += f"\n\n🌾 Advice: {alert.crop_advice}"
        
        return message
    
    def check_dry_spell(self, city: str, days_without_rain: int) -> Optional[WeatherAlert]:
        """Check for dry spell condition"""
        if days_without_rain >= THRESHOLDS["dry_spell_days"]:
            return WeatherAlert(
                alert_type=AlertType.DRY_SPELL,
                title="☀️ Dry Spell Alert",
                message=f"No rainfall in {city} for {days_without_rain} days. Plan irrigation accordingly to avoid crop stress.",
                crop_advice=CROP_ADVICE["dry_spell"]["default"],
                severity="medium"
            )
        return None


# Singleton instance
weather_alert_service = WeatherAlertService()
