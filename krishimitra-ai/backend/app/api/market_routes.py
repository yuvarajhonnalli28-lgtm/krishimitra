# market routes
# backend/app/api/market_routes.py
from fastapi import APIRouter, Query, HTTPException
from datetime import date, timedelta
import random
from typing import Optional, List

router = APIRouter(tags=["Crop Market"])  # 👈 Added tags for better docs

# Mock crop data with categories
crops_data = {
    "Grains": ["Wheat", "Rice", "Corn", "Barley", "Millet"],
    "Pulses": ["Soybean", "Lentil", "Chickpea", "Peas"],
    "Vegetables": ["Potato", "Tomato", "Onion", "Carrot", "Cabbage", "Cauliflower"],
    "Fruits": ["Mango", "Banana", "Apple", "Orange", "Grapes"],
    "Cash Crops": ["Cotton", "Sugarcane", "Tea", "Coffee"]
}

# Flatten the list for easy searching
all_crops = [crop for category in crops_data.values() for crop in category]

# Market locations with states
markets = [
    {"name": "APMC Mumbai", "state": "Maharashtra", "grade": "National"},
    {"name": "Azadpur Mandi", "state": "Delhi", "grade": "National"},
    {"name": "Koyambedu Market", "state": "Tamil Nadu", "grade": "Regional"},
    {"name": "Gultekdi Mandi", "state": "Maharashtra", "grade": "Regional"},
    {"name": "Vashi APMC", "state": "Maharashtra", "grade": "National"},
    {"name": "Yesvantpur Market", "state": "Karnataka", "grade": "Regional"}
]

def get_price_range(crop: str) -> tuple:
    """Get realistic price range based on crop type"""
    price_ranges = {
        "Grains": (1800, 2500),
        "Pulses": (4000, 7000),
        "Vegetables": (1500, 3500),
        "Fruits": (2000, 5000),
        "Cash Crops": (3500, 8000)
    }
    
    for category, crops in crops_data.items():
        if crop in crops:
            return price_ranges[category]
    return (1500, 4000)  # Default range

def get_market_news(crop: str, price: float, trend: str) -> str:
    """Generate market news based on price trends"""
    if trend == "up":
        return f"📈 {crop} prices are rising due to high demand and low supply."
    elif trend == "down":
        return f"📉 {crop} prices are dropping due to increased arrivals."
    else:
        return f"📊 {crop} market is stable with steady demand."

@router.get("/")
async def get_market_prices(
    category: Optional[str] = Query(None, description="Filter by crop category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort_by: Optional[str] = Query(None, regex="^(price|change|crop)$", description="Sort by field")
):
    """Get current market prices for all crops with filters"""
    
    prices = []
    
    # Determine which crops to show
    if category and category in crops_data:
        crop_list = crops_data[category]
    else:
        crop_list = all_crops
    
    for crop in crop_list:
        price_range = get_price_range(crop)
        price = round(random.uniform(price_range[0], price_range[1]), 2)
        change = round(random.uniform(-8, 8), 1)
        market = random.choice(markets)
        
        # Apply filters
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue
            
        prices.append({
            "crop": crop,
            "price": price,
            "unit": "per quintal",
            "change": change,
            "change_percent": round((change / price) * 100, 2) if price > 0 else 0,
            "market": market["name"],
            "state": market["state"],
            "trend": "up" if change > 0 else "down" if change < 0 else "stable",
            "news": get_market_news(crop, price, "up" if change > 0 else "down")
        })
    
    # Sorting
    if sort_by == "price":
        prices.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "change":
        prices.sort(key=lambda x: x["change"], reverse=True)
    elif sort_by == "crop":
        prices.sort(key=lambda x: x["crop"])
    
    return {
        "date": date.today().isoformat(),
        "total_crops": len(prices),
        "category": category or "All",
        "prices": prices,
        "summary": {
            "average_price": round(sum(p["price"] for p in prices) / len(prices), 2) if prices else 0,
            "highest_price": max(p["price"] for p in prices) if prices else 0,
            "lowest_price": min(p["price"] for p in prices) if prices else 0
        }
    }

@router.get("/{crop_name}")
async def get_crop_price(
    crop_name: str,
    market_grade: Optional[str] = Query(None, regex="^(National|Regional|Local)$", description="Filter by market grade")
):
    """Get detailed price information for specific crop"""
    
    # 👈 FIX: Case-insensitive crop name
    crop_name = crop_name.title()
    
    # Check if crop exists
    if crop_name not in all_crops:
        # Find similar crops (typo correction)
        similar = [c for c in all_crops if crop_name.lower() in c.lower()][:3]
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Crop not found",
                "available_crops": all_crops[:10],  # Show first 10
                "suggestions": similar
            }
        )
    
    price_range = get_price_range(crop_name)
    base_price = round(random.uniform(price_range[0], price_range[1]), 2)
    trend = random.choice(["up", "down", "stable"])
    
    # Filter markets
    available_markets = markets
    if market_grade:
        available_markets = [m for m in markets if m["grade"] == market_grade]
    
    market_prices = []
    for market in available_markets[:3]:  # Limit to 3 markets
        # Vary price by market
        variation = random.uniform(-200, 200)
        market_prices.append({
            "name": market["name"],
            "state": market["state"],
            "price": round(base_price + variation, 2),
            "demand": random.choice(["High", "Medium", "Low"])
        })
    
    return {
        "crop": crop_name,
        "category": next((cat for cat, crops in crops_data.items() if crop_name in crops), "Other"),
        "base_price": base_price,
        "unit": "per quintal",
        "trend": trend,
        "trend_strength": random.choice(["Strong", "Moderate", "Weak"]),
        "price_range": {
            "min": price_range[0],
            "max": price_range[1]
        },
        "markets": market_prices,
        "historical_comparison": {
            "last_week": round(base_price * random.uniform(0.9, 1.1), 2),
            "last_month": round(base_price * random.uniform(0.8, 1.2), 2),
            "last_year": round(base_price * random.uniform(0.7, 1.3), 2)
        },
        "best_time_to_sell": random.choice(["Now", "Next week", "Wait for 2 weeks"]),
        "farming_advice": f"🌾 Based on market trends, {trend} demand expected. Consider {'selling soon' if trend == 'up' else 'waiting for better prices' if trend == 'down' else 'regular marketing'}."
    }

@router.get("/trends/{crop_name}")
async def get_price_trends(
    crop_name: str,
    days: int = Query(7, ge=1, le=90, description="Number of days for trend (1-90)"),
    interval: str = Query("daily", regex="^(daily|weekly|monthly)$", description="Trend interval")
):
    """Get historical price trends for specific crop"""
    
    # 👈 FIX: Case-insensitive crop name
    crop_name = crop_name.title()
    
    if crop_name not in all_crops:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    price_range = get_price_range(crop_name)
    trends = []
    current_date = date.today()
    
    # Adjust step based on interval
    if interval == "daily":
        step = 1
    elif interval == "weekly":
        step = 7
    else:  # monthly
        step = 30
    
    for i in range(0, days, step):
        # 👈 FIX: Historical dates (going backwards)
        trend_date = current_date - timedelta(days=i)
        
        # Add some realistic price variation
        base_price = random.uniform(price_range[0], price_range[1])
        seasonal_factor = 1 + 0.1 * (trend_date.month / 12)  # Simple seasonal adjustment
        
        trends.append({
            "date": trend_date.isoformat(),
            "price": round(base_price * seasonal_factor, 2),
            "volume": random.randint(100, 1000),  # Trading volume in quintals
            "market_sentiment": random.choice(["Bullish", "Neutral", "Bearish"])
        })
    
    # Sort by date (oldest first)
    trends.sort(key=lambda x: x["date"])
    
    # Calculate statistics
    prices = [t["price"] for t in trends]
    
    return {
        "crop": crop_name,
        "interval": interval,
        "period": f"Last {days} days",
        "trends": trends,
        "statistics": {
            "average_price": round(sum(prices) / len(prices), 2),
            "highest_price": round(max(prices), 2),
            "highest_date": trends[prices.index(max(prices))]["date"],
            "lowest_price": round(min(prices), 2),
            "lowest_date": trends[prices.index(min(prices))]["date"],
            "volatility": round((max(prices) - min(prices)) / (sum(prices) / len(prices)) * 100, 2)
        },
        "prediction": {
            "next_week": round(prices[-1] * random.uniform(0.95, 1.05), 2),
            "next_month": round(prices[-1] * random.uniform(0.9, 1.1), 2),
            "confidence": random.choice(["High", "Medium", "Low"])
        }
    }

@router.get("/compare/")
async def compare_crops(
    crops: str = Query(..., description="Comma-separated crop names (e.g., Wheat,Rice,Tomato)"),
    days: int = Query(30, ge=7, le=365, description="Comparison period")
):
    """Compare prices of multiple crops"""
    
    crop_list = [c.strip().title() for c in crops.split(",")]
    valid_crops = [c for c in crop_list if c in all_crops]
    
    if not valid_crops:
        raise HTTPException(status_code=404, detail="No valid crops found")
    
    comparison = []
    for crop in valid_crops:
        price_range = get_price_range(crop)
        comparison.append({
            "crop": crop,
            "current_price": round(random.uniform(price_range[0], price_range[1]), 2),
            "price_change_30d": round(random.uniform(-15, 15), 1),
            "profitability": random.choice(["High", "Medium", "Low"]),
            "demand": random.choice(["Growing", "Stable", "Declining"]),
            "recommendation": random.choice(["Plant now", "Wait", "Good for current season"])
        })
    
    return {
        "date": date.today().isoformat(),
        "comparison_period": f"Last {days} days",
        "crops": comparison,
        "best_crop": max(comparison, key=lambda x: x["current_price"])["crop"],
        "most_profitable": max(comparison, key=lambda x: x.get("profitability") == "High")["crop"]
    }