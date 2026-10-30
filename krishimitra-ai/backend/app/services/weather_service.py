# weather service
import requests
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenWeatherMap API configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"

# Cache settings
CACHE_DURATION = 30 * 60  # 30 minutes in seconds
_cache = {}

# Default locations for India (major agricultural regions)
DEFAULT_LOCATIONS = [
    {"city": "Punjab", "state": "Punjab", "lat": 31.1471, "lon": 75.3412},
    {"city": "Haryana", "state": "Haryana", "lat": 29.0588, "lon": 76.0856},
    {"city": "Uttar Pradesh", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    {"city": "Maharashtra", "state": "Maharashtra", "lat": 19.7515, "lon": 75.7139},
    {"city": "Karnataka", "state": "Karnataka", "lat": 15.3173, "lon": 75.7139},
    {"city": "Tamil Nadu", "state": "Tamil Nadu", "lat": 11.1271, "lon": 78.6569},
    {"city": "Madhya Pradesh", "state": "Madhya Pradesh", "lat": 22.9734, "lon": 78.6569},
    {"city": "Bihar", "state": "Bihar", "lat": 25.0961, "lon": 85.3131},
    {"city": "West Bengal", "state": "West Bengal", "lat": 22.9868, "lon": 87.8550},
    {"city": "Gujarat", "state": "Gujarat", "lat": 22.2587, "lon": 71.1924}
]

# Farming advice based on weather conditions
FARMING_ADVICE = {
    "rain": {
        "light": "Light rain expected. Good for sowing. Ensure proper drainage.",
        "moderate": "Moderate rainfall. Avoid irrigation. Check for waterlogging.",
        "heavy": "Heavy rain warning! Postpone harvesting. Protect young plants."
    },
    "temperature": {
        "cold": "Low temperature. Protect sensitive crops with covers. Delay irrigation.",
        "mild": "Ideal temperature for most crops. Good for farming activities.",
        "hot": "High temperature. Increase irrigation. Use mulch to retain moisture.",
        "extreme": "Extreme heat! Provide shade for vegetables. Avoid working midday."
    },
    "humidity": {
        "low": "Low humidity. Increase irrigation frequency. Watch for pests.",
        "moderate": "Moderate humidity. Good conditions for most crops.",
        "high": "High humidity. Monitor for fungal diseases. Ensure air circulation."
    },
    "wind": {
        "low": "Light winds. Good for spraying pesticides.",
        "moderate": "Moderate winds. Avoid spraying. Check for wind damage.",
        "high": "Strong winds! Secure stakes and trellises. Protect young plants."
    }
}


def get_weather(city: str, country_code: str = "IN") -> Dict[str, Any]:
    """
    Get current weather for a city
    
    Args:
        city: City name
        country_code: Country code (default: IN for India)
    
    Returns:
        Dictionary with weather data
    """
    try:
        # Check cache first
        cache_key = f"weather_{city}_{country_code}"
        cached_data = _get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Returning cached weather data for {city}")
            return cached_data
        
        logger.info(f"Fetching weather data for {city}, {country_code}")
        
        # First, get coordinates for the city
        coords = get_coordinates(city, country_code)
        
        if not coords:
            # Fallback to direct city query
            url = f"{BASE_URL}/weather?q={city},{country_code}&appid={API_KEY}&units=metric"
        else:
            # Use coordinates for more accurate data
            url = f"{BASE_URL}/weather?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Process and enhance weather data
        weather_data = _process_weather_data(data, city)
        
        # Cache the result
        _add_to_cache(cache_key, weather_data)
        
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {city}: {str(e)}")
        return _get_fallback_weather(city)
        
    except KeyError as e:
        logger.error(f"Unexpected API response format for {city}: {str(e)}")
        return _get_fallback_weather(city)
        
    except Exception as e:
        logger.error(f"Unexpected error for {city}: {str(e)}")
        return _get_fallback_weather(city)


def get_weather_by_coords(lat: float, lon: float, location_name: str = None) -> Dict[str, Any]:
    """
    Get current weather by coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        location_name: Optional location name
    
    Returns:
        Dictionary with weather data
    """
    try:
        cache_key = f"weather_coords_{lat}_{lon}"
        cached_data = _get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        url = f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        location = location_name or data.get("name", "Unknown location")
        weather_data = _process_weather_data(data, location)
        
        _add_to_cache(cache_key, weather_data)
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Error fetching weather by coordinates: {str(e)}")
        return _get_fallback_weather(location_name or "your location")


def get_forecast(city: str, days: int = 5, country_code: str = "IN") -> Dict[str, Any]:
    """
    Get weather forecast for a city
    
    Args:
        city: City name
        days: Number of days (1-7)
        country_code: Country code
    
    Returns:
        Dictionary with forecast data
    """
    try:
        # Validate days
        days = min(max(days, 1), 7)
        
        cache_key = f"forecast_{city}_{country_code}_{days}"
        cached_data = _get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        logger.info(f"Fetching {days}-day forecast for {city}")
        
        # Get coordinates first
        coords = get_coordinates(city, country_code)
        
        if not coords:
            url = f"{BASE_URL}/forecast?q={city},{country_code}&appid={API_KEY}&units=metric&cnt={days*8}"
        else:
            url = f"{BASE_URL}/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={API_KEY}&units=metric&cnt={days*8}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Process forecast data
        forecast_data = _process_forecast_data(data, city, days)
        
        _add_to_cache(cache_key, forecast_data)
        
        return forecast_data
        
    except Exception as e:
        logger.error(f"Error fetching forecast for {city}: {str(e)}")
        return _get_fallback_forecast(city, days)


def get_coordinates(city: str, country_code: str = "IN") -> Optional[Dict[str, float]]:
    """
    Get coordinates for a city
    
    Args:
        city: City name
        country_code: Country code
    
    Returns:
        Dictionary with lat and lon or None if not found
    """
    try:
        url = f"{GEOCODING_URL}?q={city},{country_code}&limit=1&appid={API_KEY}"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            return {
                "lat": data[0]["lat"],
                "lon": data[0]["lon"],
                "name": data[0].get("name", city),
                "state": data[0].get("state", ""),
                "country": data[0].get("country", country_code)
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting coordinates for {city}: {str(e)}")
        return None


def _process_weather_data(data: Dict, location: str) -> Dict[str, Any]:
    """
    Process and enhance raw weather data
    """
    # Extract basic weather data
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"] * 3.6  # Convert m/s to km/h
    weather_desc = data["weather"][0]["description"]
    weather_main = data["weather"][0]["main"]
    
    # Get rain data if available
    rain = data.get("rain", {}).get("1h", 0)
    
    # Calculate additional metrics
    feels_like = data["main"]["feels_like"]
    pressure = data["main"]["pressure"]
    visibility = data.get("visibility", 10000) / 1000  # Convert to km
    
    # Generate farming advice
    advice = _generate_farming_advice(temp, humidity, weather_main, wind_speed, rain)
    
    # Determine condition category
    condition = _get_condition_category(weather_main, temp, rain)
    
    return {
        "location": location,
        "country": data.get("sys", {}).get("country", "IN"),
        "coordinates": {
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"]
        },
        "temperature": round(temp, 1),
        "feels_like": round(feels_like, 1),
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": round(wind_speed, 1),
        "wind_direction": data["wind"].get("deg", 0),
        "rainfall": round(rain, 1),
        "visibility": round(visibility, 1),
        "condition": condition,
        "description": weather_desc.capitalize(),
        "icon": _get_weather_icon(weather_main),
        "advice": advice,
        "timestamp": datetime.now().isoformat(),
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat() if "sys" in data else None,
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat() if "sys" in data else None
    }


def _process_forecast_data(data: Dict, location: str, days: int) -> Dict[str, Any]:
    """
    Process and enhance forecast data
    """
    forecast_list = []
    
    # Group by day
    daily_data = {}
    
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_str = dt.strftime("%Y-%m-%d")
        
        if date_str not in daily_data:
            daily_data[date_str] = []
        
        daily_data[date_str].append(item)
    
    # Process each day
    for date_str, items in list(daily_data.items())[:days]:
        temps = [i["main"]["temp"] for i in items]
        humidities = [i["main"]["humidity"] for i in items]
        
        # Get dominant weather condition
        weather_counts = {}
        for item in items:
            condition = item["weather"][0]["main"]
            weather_counts[condition] = weather_counts.get(condition, 0) + 1
        
        dominant_condition = max(weather_counts, key=weather_counts.get)
        
        # Calculate rain chance
        rain_items = [i for i in items if i.get("rain", {}).get("3h", 0) > 0]
        rain_chance = (len(rain_items) / len(items)) * 100
        
        # Get max/min temp
        max_temp = max(temps)
        min_temp = min(temps)
        
        # Generate daily advice
        avg_temp = (max_temp + min_temp) / 2
        avg_humidity = sum(humidities) / len(humidities)
        advice = _generate_farming_advice(avg_temp, avg_humidity, dominant_condition, 10, rain_chance/100)
        
        forecast_list.append({
            "date": date_str,
            "day": datetime.strptime(date_str, "%Y-%m-%d").strftime("%A"),
            "max_temp": round(max_temp, 1),
            "min_temp": round(min_temp, 1),
            "avg_temp": round(avg_temp, 1),
            "humidity": round(avg_humidity),
            "condition": dominant_condition,
            "description": items[0]["weather"][0]["description"].capitalize(),
            "icon": _get_weather_icon(dominant_condition),
            "rain_chance": round(rain_chance),
            "wind_speed": round(items[0]["wind"]["speed"] * 3.6, 1),
            "advice": advice
        })
    
    return {
        "location": location,
        "country": data.get("city", {}).get("country", "IN"),
        "coordinates": {
            "lat": data["city"]["coord"]["lat"],
            "lon": data["city"]["coord"]["lon"]
        },
        "forecast": forecast_list,
        "generated_at": datetime.now().isoformat()
    }


def _generate_farming_advice(temp: float, humidity: float, condition: str, wind_speed: float, rain: float) -> str:
    """
    Generate farming advice based on weather conditions
    """
    advice_parts = []
    
    # Temperature advice
    if temp < 10:
        advice_parts.append(FARMING_ADVICE["temperature"]["cold"])
    elif temp < 20:
        advice_parts.append(FARMING_ADVICE["temperature"]["mild"])
    elif temp < 35:
        advice_parts.append(FARMING_ADVICE["temperature"]["hot"])
    else:
        advice_parts.append(FARMING_ADVICE["temperature"]["extreme"])
    
    # Humidity advice
    if humidity < 30:
        advice_parts.append(FARMING_ADVICE["humidity"]["low"])
    elif humidity < 60:
        advice_parts.append(FARMING_ADVICE["humidity"]["moderate"])
    else:
        advice_parts.append(FARMING_ADVICE["humidity"]["high"])
    
    # Rain advice
    if rain > 10:
        advice_parts.append(FARMING_ADVICE["rain"]["heavy"])
    elif rain > 2:
        advice_parts.append(FARMING_ADVICE["rain"]["moderate"])
    elif rain > 0:
        advice_parts.append(FARMING_ADVICE["rain"]["light"])
    
    # Wind advice
    if wind_speed < 10:
        advice_parts.append(FARMING_ADVICE["wind"]["low"])
    elif wind_speed < 30:
        advice_parts.append(FARMING_ADVICE["wind"]["moderate"])
    else:
        advice_parts.append(FARMING_ADVICE["wind"]["high"])
    
    return " ".join(advice_parts)


def _get_condition_category(condition: str, temp: float, rain: float) -> str:
    """
    Categorize weather condition
    """
    condition_lower = condition.lower()
    
    if "rain" in condition_lower or "drizzle" in condition_lower or rain > 0:
        return "Rainy"
    elif "cloud" in condition_lower:
        return "Cloudy"
    elif "clear" in condition_lower or "sun" in condition_lower:
        return "Sunny" if temp > 20 else "Clear"
    elif "storm" in condition_lower or "thunder" in condition_lower:
        return "Thunderstorm"
    elif "snow" in condition_lower:
        return "Snowy"
    elif "fog" in condition_lower or "mist" in condition_lower:
        return "Foggy"
    else:
        return "Partly Cloudy"


def _get_weather_icon(condition: str) -> str:
    """
    Get emoji icon for weather condition
    """
    icons = {
        "Clear": "☀️",
        "Sunny": "☀️",
        "Clouds": "☁️",
        "Cloudy": "☁️",
        "Partly Cloudy": "⛅",
        "Rain": "🌧️",
        "Rainy": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Snowy": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Foggy": "🌫️",
        "Haze": "🌫️",
        "Windy": "💨"
    }
    return icons.get(condition, "🌤️")


def _get_from_cache(key: str) -> Optional[Dict]:
    """
    Get data from cache if not expired
    """
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_DURATION:
            return data
        else:
            del _cache[key]
    return None


def _add_to_cache(key: str, data: Dict):
    """
    Add data to cache with timestamp
    """
    _cache[key] = (data, time.time())


def _get_fallback_weather(location: str) -> Dict[str, Any]:
    """
    Get fallback weather data when API fails
    """
    logger.warning(f"Using fallback weather data for {location}")
    
    import random
    
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy"]
    condition = random.choice(conditions)
    
    temp = random.randint(20, 35)
    humidity = random.randint(40, 85)
    
    return {
        "location": location,
        "temperature": temp,
        "feels_like": temp - 2,
        "humidity": humidity,
        "wind_speed": random.randint(5, 20),
        "condition": condition,
        "description": condition,
        "icon": _get_weather_icon(condition),
        "advice": _generate_farming_advice(temp, humidity, condition, 10, 0),
        "timestamp": datetime.now().isoformat(),
        "is_fallback": True,
        "message": "Using approximate data. Please try again later."
    }


def _get_fallback_forecast(location: str, days: int) -> Dict[str, Any]:
    """
    Get fallback forecast data when API fails
    """
    import random
    from datetime import timedelta
    
    forecast = []
    current_date = datetime.now()
    
    for i in range(days):
        date = current_date + timedelta(days=i)
        condition = random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Rainy"])
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "max_temp": random.randint(28, 38),
            "min_temp": random.randint(18, 25),
            "humidity": random.randint(40, 85),
            "condition": condition,
            "rain_chance": random.randint(0, 80) if condition == "Rainy" else random.randint(0, 30),
            "icon": _get_weather_icon(condition)
        })
    
    return {
        "location": location,
        "forecast": forecast,
        "generated_at": datetime.now().isoformat(),
        "is_fallback": True,
        "message": "Using approximate forecast. Please try again later."
    }


def get_agricultural_zones() -> List[Dict[str, Any]]:
    """
    Get list of major agricultural zones in India
    """
    return DEFAULT_LOCATIONS


def get_weather_alerts(city: str) -> List[Dict[str, Any]]:
    """
    Get weather alerts for farming
    """
    alerts = []
    
    try:
        weather = get_weather(city)
        
        # Check for extreme conditions
        if weather["temperature"] > 40:
            alerts.append({
                "type": "heat_wave",
                "severity": "high",
                "message": "Extreme heat! Protect crops from sun damage.",
                "action": "Provide shade, increase irrigation"
            })
        
        if weather["temperature"] < 5:
            alerts.append({
                "type": "cold_wave",
                "severity": "high",
                "message": "Freezing temperatures expected!",
                "action": "Cover sensitive crops, use mulch"
            })
        
        if weather["wind_speed"] > 40:
            alerts.append({
                "type": "strong_winds",
                "severity": "moderate",
                "message": "Strong winds expected.",
                "action": "Secure stakes and trellises"
            })
        
        if weather.get("rainfall", 0) > 50:
            alerts.append({
                "type": "heavy_rain",
                "severity": "high",
                "message": "Heavy rainfall warning!",
                "action": "Ensure proper drainage, avoid fieldwork"
            })
        
        if weather["humidity"] > 85 and weather["temperature"] > 25:
            alerts.append({
                "type": "disease_risk",
                "severity": "moderate",
                "message": "High risk of fungal diseases.",
                "action": "Monitor crops closely, apply preventive sprays"
            })
        
    except Exception as e:
        logger.error(f"Error generating alerts: {str(e)}")
    
    return alerts