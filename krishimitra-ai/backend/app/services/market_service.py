# market service
import requests
import os
import logging
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache settings
CACHE_DURATION = 15 * 60  # 15 minutes in seconds
_cache = {}

# Mock data sources (replace with real APIs)
MANDI_API_URL = os.getenv("MANDI_API_URL", "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070")
API_KEY = os.getenv("MANDI_API_KEY", "YOUR_API_KEY")

# Major agricultural markets in India
MAJOR_MANDIS = [
    {"name": "Azadpur Mandi", "city": "Delhi", "state": "Delhi", "grade": "National"},
    {"name": "APMC Vashi", "city": "Mumbai", "state": "Maharashtra", "grade": "National"},
    {"name": "Gultekdi Mandi", "city": "Pune", "state": "Maharashtra", "grade": "Regional"},
    {"name": "Koyambedu Market", "city": "Chennai", "state": "Tamil Nadu", "grade": "Regional"},
    {"name": "Yesvantpur Market", "city": "Bangalore", "state": "Karnataka", "grade": "Regional"},
    {"name": "Amaravati Market", "city": "Amaravati", "state": "Andhra Pradesh", "grade": "Regional"},
    {"name": "Gandhi Market", "city": "Hyderabad", "state": "Telangana", "grade": "Regional"},
    {"name": "Krishnagiri Market", "city": "Krishnagiri", "state": "Tamil Nadu", "grade": "Local"},
    {"name": "Ludhiana Mandi", "city": "Ludhiana", "state": "Punjab", "grade": "Regional"},
    {"name": "Kanpur Mandi", "city": "Kanpur", "state": "Uttar Pradesh", "grade": "Regional"},
    {"name": "Patna Market", "city": "Patna", "state": "Bihar", "grade": "Regional"},
    {"name": "Kolkata Market", "city": "Kolkata", "state": "West Bengal", "grade": "National"}
]

# Crop categories
CROP_CATEGORIES = {
    "Wheat": "Grains",
    "Rice": "Grains", 
    "Maize": "Grains",
    "Bajra": "Grains",
    "Jowar": "Grains",
    "Barley": "Grains",
    
    "Tur": "Pulses",
    "Moong": "Pulses",
    "Urad": "Pulses",
    "Masoor": "Pulses",
    "Chana": "Pulses",
    
    "Groundnut": "Oilseeds",
    "Mustard": "Oilseeds",
    "Soybean": "Oilseeds",
    "Sunflower": "Oilseeds",
    
    "Potato": "Vegetables",
    "Onion": "Vegetables",
    "Tomato": "Vegetables",
    "Brinjal": "Vegetables",
    "Cabbage": "Vegetables",
    "Cauliflower": "Vegetables",
    "Ladyfinger": "Vegetables",
    "Green Peas": "Vegetables",
    
    "Banana": "Fruits",
    "Mango": "Fruits",
    "Orange": "Fruits",
    "Apple": "Fruits",
    "Grapes": "Fruits",
    "Pomegranate": "Fruits",
    
    "Cotton": "Cash Crops",
    "Sugarcane": "Cash Crops",
    "Jute": "Cash Crops",
    "Tea": "Cash Crops",
    "Coffee": "Cash Crops"
}

# MSP (Minimum Support Price) data 2024-25 (₹/quintal)
MSP_RATES = {
    "Wheat": 2275,
    "Rice": 2200,
    "Maize": 2090,
    "Bajra": 2350,
    "Jowar": 3180,
    "Barley": 1730,
    "Tur": 7000,
    "Moong": 7550,
    "Urad": 7350,
    "Masoor": 6425,
    "Chana": 5440,
    "Groundnut": 5670,
    "Mustard": 5650,
    "Soybean": 4600,
    "Sunflower": 6760,
    "Cotton": 7020,
    "Sugarcane": 340
}


class MarketService:
    """
    Market price service for agricultural commodities
    """
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
    
    def get_market_prices(self, 
                          crop: Optional[str] = None, 
                          state: Optional[str] = None,
                          mandi: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current market prices
        
        Args:
            crop: Optional crop name filter
            state: Optional state filter
            mandi: Optional mandi name filter
        
        Returns:
            Dictionary with market prices data
        """
        try:
            # Check cache
            cache_key = f"market_prices_{crop}_{state}_{mandi}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.info("Returning cached market data")
                return cached_data
            
            # Get data from source
            if self.use_mock:
                prices = self._get_mock_market_data()
            else:
                prices = self._fetch_from_api()
            
            # Apply filters
            if crop:
                prices = [p for p in prices if p["crop"].lower() == crop.lower()]
            if state:
                prices = [p for p in prices if p.get("state", "").lower() == state.lower()]
            if mandi:
                prices = [p for p in prices if mandi.lower() in p["market"].lower()]
            
            # Enhance with additional data
            prices = [self._enhance_price_data(p) for p in prices]
            
            # Calculate statistics
            stats = self._calculate_statistics(prices)
            
            result = {
                "date": datetime.now().date().isoformat(),
                "total_records": len(prices),
                "filters": {
                    "crop": crop or "all",
                    "state": state or "all",
                    "mandi": mandi or "all"
                },
                "prices": prices,
                "summary": stats,
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache the result
            self._add_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching market prices: {str(e)}")
            return self._get_fallback_market_data(crop, state, mandi)
    
    def get_crop_price(self, crop: str, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Get price for specific crop across mandis
        """
        data = self.get_market_prices(crop=crop, state=state)
        
        if not data["prices"]:
            return {
                "status": "error",
                "message": f"No data found for crop: {crop}",
                "crop": crop
            }
        
        prices = data["prices"]
        
        # Find best price
        best_price = max(prices, key=lambda x: x["price"])
        best_mandi = best_price["market"]
        
        # Calculate average
        avg_price = sum(p["price"] for p in prices) / len(prices)
        
        # Get MSP for comparison
        msp = MSP_RATES.get(crop.title(), None)
        
        return {
            "crop": crop,
            "date": data["date"],
            "total_mandis": len(prices),
            "average_price": round(avg_price, 2),
            "min_price": min(p["price"] for p in prices),
            "max_price": max(p["price"] for p in prices),
            "msp": msp,
            "price_vs_msp": round(((avg_price / msp) - 1) * 100, 2) if msp else None,
            "best_mandi": {
                "name": best_mandi,
                "price": best_price["price"],
                "state": best_price.get("state", "Unknown")
            },
            "prices": sorted(prices, key=lambda x: x["price"], reverse=True)
        }
    
    def get_price_trends(self, crop: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical price trends for a crop
        """
        try:
            # In production, this would fetch from a database
            # For now, generate mock trends
            
            trends = []
            current_date = datetime.now()
            
            for i in range(days):
                date = current_date - timedelta(days=i)
                
                # Generate realistic price variation
                base_price = MSP_RATES.get(crop.title(), 2000)
                variation = random.uniform(-200, 200)
                seasonal_factor = 1 + 0.1 * (date.month / 12)
                
                price = base_price * seasonal_factor + variation
                
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(price, 2)
                })
            
            # Sort by date
            trends.sort(key=lambda x: x["date"])
            
            # Calculate statistics
            prices = [t["price"] for t in trends]
            
            return {
                "crop": crop,
                "period": f"Last {days} days",
                "start_date": trends[0]["date"] if trends else None,
                "end_date": trends[-1]["date"] if trends else None,
                "average_price": round(sum(prices) / len(prices), 2),
                "min_price": round(min(prices), 2),
                "max_price": round(max(prices), 2),
                "volatility": round((max(prices) - min(prices)) / (sum(prices) / len(prices)) * 100, 2),
                "trend": self._calculate_trend(prices),
                "prices": trends
            }
            
        except Exception as e:
            logger.error(f"Error generating trends: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "crop": crop
            }
    
    def compare_crops(self, crops: List[str]) -> Dict[str, Any]:
        """
        Compare prices of multiple crops
        """
        comparison = []
        
        for crop in crops:
            try:
                data = self.get_crop_price(crop)
                if "error" not in data:
                    comparison.append({
                        "crop": crop,
                        "average_price": data.get("average_price", 0),
                        "max_price": data.get("max_price", 0),
                        "min_price": data.get("min_price", 0),
                        "total_mandis": data.get("total_mandis", 0),
                        "best_mandi": data.get("best_mandi", {})
                    })
            except Exception as e:
                logger.error(f"Error comparing crop {crop}: {str(e)}")
        
        # Sort by average price
        comparison.sort(key=lambda x: x["average_price"], reverse=True)
        
        return {
            "date": datetime.now().date().isoformat(),
            "crops_compared": len(comparison),
            "most_profitable": comparison[0]["crop"] if comparison else None,
            "comparison": comparison
        }
    
    def get_mandi_list(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of mandis, optionally filtered by state
        """
        mandis = MAJOR_MANDIS
        
        if state:
            mandis = [m for m in mandis if m["state"].lower() == state.lower()]
        
        return mandis
    
    def get_nearby_mandis(self, lat: float, lon: float, radius_km: int = 100) -> List[Dict[str, Any]]:
        """
        Get mandis near given coordinates
        """
        # In production, use geospatial query
        # For now, return nearby based on state
        
        # Mock implementation - in reality, use proper geocoding
        nearby = []
        for mandi in MAJOR_MANDIS:
            # Simulate distance calculation
            distance = random.randint(10, 200)
            if distance <= radius_km:
                mandi_copy = mandi.copy()
                mandi_copy["distance_km"] = distance
                mandi_copy["estimated_travel_time"] = f"{distance // 40} hours"
                nearby.append(mandi_copy)
        
        return sorted(nearby, key=lambda x: x["distance_km"])
    
    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch real data from API (to be implemented)
        """
        # This is where you'd integrate with:
        # - AGMARKNET API
        # - Government data portal
        # - Commodity exchange APIs
        
        # For now, return enhanced mock data
        return self._get_mock_market_data()
    
    def _get_mock_market_data(self) -> List[Dict[str, Any]]:
        """
        Generate realistic mock market data
        """
        prices = []
        
        crops = list(CROP_CATEGORIES.keys())
        
        for mandi in MAJOR_MANDIS:
            # Each mandi trades 10-15 crops
            num_crops = random.randint(10, 15)
            mandi_crops = random.sample(crops, num_crops)
            
            for crop in mandi_crops:
                # Base price from MSP or random
                base_price = MSP_RATES.get(crop, random.randint(1500, 5000))
                
                # Price variation by mandi
                variation = random.uniform(-300, 300)
                price = base_price + variation
                
                # Price change trend
                change = round(random.uniform(-5, 5), 1)
                
                prices.append({
                    "crop": crop,
                    "category": CROP_CATEGORIES.get(crop, "Other"),
                    "market": mandi["name"],
                    "city": mandi["city"],
                    "state": mandi["state"],
                    "grade": mandi["grade"],
                    "price": round(price, 2),
                    "unit": "per quintal",
                    "change": change,
                    "change_percent": round((change / price) * 100, 2),
                    "trend": "up" if change > 0 else "down" if change < 0 else "stable",
                    "arrival": random.randint(100, 1000),  # Quantity in quintals
                    "demand": random.choice(["High", "Medium", "Low"])
                })
        
        return prices
    
    def _enhance_price_data(self, price_data: Dict) -> Dict:
        """
        Add additional calculated fields
        """
        # Add selling advice
        if price_data["trend"] == "up":
            advice = "📈 Prices rising - Good time to sell"
        elif price_data["trend"] == "down":
            advice = "📉 Prices falling - Consider waiting"
        else:
            advice = "📊 Stable market - Can sell now"
        
        # Add price vs MSP comparison
        msp = MSP_RATES.get(price_data["crop"])
        if msp:
            vs_msp = round(((price_data["price"] / msp) - 1) * 100, 2)
            msp_message = f"{vs_msp:+.1f}% vs MSP"
        else:
            vs_msp = None
            msp_message = "MSP not available"
        
        # Add farmer-friendly message
        if price_data["demand"] == "High" and price_data["trend"] == "up":
            farmer_message = "🔥 Hot market! High demand and rising prices."
        elif price_data["demand"] == "Low" and price_data["trend"] == "down":
            farmer_message = "⚠️ Slow market. Consider storing if possible."
        else:
            farmer_message = "✓ Normal market conditions."
        
        price_data["selling_advice"] = advice
        price_data["vs_msp"] = vs_msp
        price_data["msp_message"] = msp_message
        price_data["farmer_message"] = farmer_message
        
        return price_data
    
    def _calculate_statistics(self, prices: List[Dict]) -> Dict:
        """
        Calculate market statistics
        """
        if not prices:
            return {}
        
        prices_list = [p["price"] for p in prices]
        
        return {
            "average_price": round(sum(prices_list) / len(prices_list), 2),
            "median_price": round(sorted(prices_list)[len(prices_list)//2], 2),
            "min_price": round(min(prices_list), 2),
            "max_price": round(max(prices_list), 2),
            "total_mandis": len(set(p["market"] for p in prices)),
            "total_crops": len(set(p["crop"] for p in prices)),
            "states_covered": len(set(p["state"] for p in prices))
        }
    
    def _calculate_trend(self, prices: List[float]) -> str:
        """
        Calculate overall trend direction
        """
        if len(prices) < 2:
            return "stable"
        
        first_half = prices[:len(prices)//2]
        second_half = prices[len(prices)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        change = ((avg_second - avg_first) / avg_first) * 100
        
        if change > 5:
            return "strong_up"
        elif change > 2:
            return "up"
        elif change < -5:
            return "strong_down"
        elif change < -2:
            return "down"
        else:
            return "stable"
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
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
    
    def _add_to_cache(self, key: str, data: Dict):
        """
        Add data to cache with timestamp
        """
        _cache[key] = (data, time.time())
    
    def _get_fallback_market_data(self, crop=None, state=None, mandi=None) -> Dict[str, Any]:
        """
        Get fallback data when service fails
        """
        logger.warning("Using fallback market data")
        
        # Basic mock data
        mock_prices = [
            {"crop": "Wheat", "price": 2400, "market": "Azadpur Mandi", "state": "Delhi"},
            {"crop": "Rice", "price": 2200, "market": "APMC Vashi", "state": "Maharashtra"},
            {"crop": "Tomato", "price": 1800, "market": "Koyambedu", "state": "Tamil Nadu"},
            {"crop": "Onion", "price": 1500, "market": "Gultekdi", "state": "Maharashtra"},
            {"crop": "Potato", "price": 1600, "market": "Amaravati", "state": "Andhra Pradesh"},
            {"crop": "Cotton", "price": 7000, "market": "Gandhi Market", "state": "Telangana"}
        ]
        
        # Apply filters
        if crop:
            mock_prices = [p for p in mock_prices if p["crop"].lower() == crop.lower()]
        if state:
            mock_prices = [p for p in mock_prices if p["state"].lower() == state.lower()]
        
        return {
            "date": datetime.now().date().isoformat(),
            "prices": mock_prices,
            "is_fallback": True,
            "message": "Using approximate data. Please try again later.",
            "generated_at": datetime.now().isoformat()
        }


# Singleton instance
_market_service_instance = None

def get_market_service(use_mock: bool = False) -> MarketService:
    """
    Get or create market service singleton
    """
    global _market_service_instance
    if _market_service_instance is None:
        _market_service_instance = MarketService(use_mock=use_mock)
    return _market_service_instance


# Simple function versions for backward compatibility
def get_market_prices(crop: Optional[str] = None, state: Optional[str] = None) -> List[Dict]:
    """
    Simple function to get market prices
    """
    service = get_market_service(use_mock=True)
    result = service.get_market_prices(crop=crop, state=state)
    return result.get("prices", [])


def get_crop_price(crop: str) -> Dict:
    """
    Simple function to get crop price details
    """
    service = get_market_service(use_mock=True)
    return service.get_crop_price(crop)


def get_msp_rate(crop: str) -> Optional[float]:
    """
    Get MSP rate for a crop
    """
    return MSP_RATES.get(crop.title())


def get_price_advice(price: float, msp: float) -> str:
    """
    Get selling advice based on price vs MSP
    """
    if not msp:
        return "Check local mandi rates"
    
    ratio = price / msp
    
    if ratio >= 1.2:
        return "✅ Excellent price! Good time to sell."
    elif ratio >= 1.1:
        return "👍 Good price above MSP."
    elif ratio >= 1.0:
        return "👌 Fair price at MSP level."
    else:
        return "⚠️ Price below MSP. Consider holding or check other mandis."