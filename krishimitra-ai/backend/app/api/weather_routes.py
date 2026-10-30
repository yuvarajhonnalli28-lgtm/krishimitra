# weather routes
# backend/app/api/weather_routes.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import random
from typing import Optional

router = APIRouter(tags=["Weather"])  # 👈 Added tags here

# Weather advice based on conditions
def get_farming_advice(temp: int, humidity: int, condition: str, rain_chance: int = 0) -> str:
    """Generate farming advice based on weather conditions"""
    
    if condition.lower() == "rainy" or rain_chance > 70:
        return "🌧️ Avoid irrigation. Good for planting if heavy rain not expected."
    elif temp > 35:
        return "☀️ High temperature. Ensure adequate irrigation and mulch to retain moisture."
    elif temp < 15:
        return "❄️ Low temperature. Protect sensitive crops with cover."
    elif humidity > 80:
        return "💧 High humidity. Monitor for fungal diseases. Ensure good air circulation."
    elif humidity < 30:
        return "🌵 Low humidity. Increase irrigation frequency."
    elif condition.lower() == "sunny":
        return "☀️ Good for harvesting and pesticide application."
    else:
        return "🌱 Normal conditions. Continue regular farm operations."

@router.get("/")
async def get_weather(
    location: Optional[str] = Query("Sample Farm, India", description="City or location name")
):
    """Get current weather for specified location"""
    
    temp = random.randint(20, 35)
    humidity = random.randint(40, 90)
    condition = random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"])
    rain_chance = random.randint(0, 100) if condition == "Rainy" else random.randint(0, 30)
    
    return {
        "location": location,
        "temperature": temp,
        "humidity": humidity,
        "rainfall": random.randint(0, 20),
        "wind_speed": random.randint(5, 25),
        "condition": condition,
        "rain_chance": rain_chance,
        "timestamp": datetime.now().isoformat(),
        "advice": get_farming_advice(temp, humidity, condition, rain_chance)  # 👈 Added advice
    }

@router.get("/forecast")
async def get_forecast(
    days: int = Query(5, ge=1, le=7, description="Number of forecast days (1-7)"),
    location: Optional[str] = Query("Sample Farm, India", description="City or location name")
):
    """Get weather forecast for next N days"""
    
    if days > 7:
        raise HTTPException(status_code=400, detail="Maximum 7 days forecast")
    
    forecast = []
    current_date = datetime.now().date()
    
    for i in range(days):
        temp_max = random.randint(28, 38)
        temp_min = random.randint(18, 25)
        humidity = random.randint(40, 90)
        condition = random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"])
        rain_chance = random.randint(0, 100) if condition == "Rainy" else random.randint(0, 30)
        
        forecast.append({
            "day": i + 1,
            "date": (current_date + timedelta(days=i)).isoformat(),  # 👈 Fixed: now shows future dates
            "max_temp": temp_max,
            "min_temp": temp_min,
            "humidity": humidity,
            "condition": condition,
            "rain_chance": rain_chance,
            "wind_speed": random.randint(5, 25),
            "advice": get_farming_advice(
                (temp_max + temp_min) // 2,  # Average temperature
                humidity, 
                condition, 
                rain_chance
            )  # 👈 Added advice for each day
        })
    
    return {
        "location": location,
        "forecast": forecast,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/location/{city}")
async def get_weather_by_location(city: str):
    """Get weather for specific location"""
    
    temp = random.randint(20, 35)
    humidity = random.randint(40, 90)
    condition = random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"])
    rain_chance = random.randint(0, 100) if condition == "Rainy" else random.randint(0, 30)
    
    return {
        "location": city.title(),  # 👈 Format city name nicely
        "temperature": temp,
        "humidity": humidity,
        "condition": condition,
        "rain_chance": rain_chance,
        "wind_speed": random.randint(5, 25),
        "timestamp": datetime.now().isoformat(),
        "advice": get_farming_advice(temp, humidity, condition, rain_chance),  # 👈 Added advice
        "message": f"🌾 Weather data for {city.title()}"
    }

@router.get("/advisory/daily")
async def get_daily_advisory():
    """Get daily farming advisory based on weather"""
    
    temp = random.randint(20, 35)
    humidity = random.randint(40, 90)
    condition = random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"])
    
    advisory = {
        "date": datetime.now().date().isoformat(),
        "weather_summary": f"{condition}, {temp}°C, {humidity}% humidity",
        "farming_tasks": [],
        "cautions": []
    }
    
    # Generate farming tasks based on weather
    if condition == "Sunny":
        advisory["farming_tasks"] = [
            "✅ Good day for harvesting",
            "✅ Apply fertilizers",
            "✅ Check irrigation systems"
        ]
        advisory["cautions"] = [
            "⚠️ Protect young plants from strong sun",
            "⚠️ Monitor soil moisture"
        ]
    elif condition == "Rainy":
        advisory["farming_tasks"] = [
            "✅ Check drainage systems",
            "✅ Harvest ripe produce before rain"
        ]
        advisory["cautions"] = [
            "⚠️ Avoid walking in wet fields",
            "⚠️ Watch for fungal diseases",
            "⚠️ Delay pesticide application"
        ]
    elif condition == "Cloudy":
        advisory["farming_tasks"] = [
            "✅ Good for transplanting",
            "✅ Apply organic mulch",
            "✅ Inspect crops for pests"
        ]
        advisory["cautions"] = [
            "⚠️ Prepare for possible rain"
        ]
    
    # Temperature-based advice
    if temp > 35:
        advisory["cautions"].append("⚠️ Heat stress possible - ensure adequate irrigation")
    elif temp < 15:
        advisory["cautions"].append("⚠️ Cold conditions - protect sensitive crops")
    
    # Humidity-based advice
    if humidity > 80:
        advisory["cautions"].append("⚠️ High humidity - monitor for fungal diseases")
    
    return advisory