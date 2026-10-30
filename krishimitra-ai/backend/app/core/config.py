# config
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, print_config
from app.api import disease_routes, weather_routes, market_routes, chat_routes
import logging

# Print configuration on startup
print_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Root route
@app.get("/")
def home():
    return {
        "message": f"Welcome to {settings.APP_NAME} Backend 🌾",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "Running"
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "features": {
            "disease_detection": settings.ENABLE_DISEASE_DETECTION,
            "weather": settings.ENABLE_WEATHER,
            "market": settings.ENABLE_MARKET,
            "chat": settings.ENABLE_CHAT
        }
    }

# Include routers
app.include_router(disease_routes.router, prefix="/api/disease", tags=["Disease Detection"])
app.include_router(weather_routes.router, prefix="/api/weather", tags=["Weather"])
app.include_router(market_routes.router, prefix="/api/market", tags=["Crop Market"])
app.include_router(chat_routes.router, prefix="/api/chat", tags=["AI Advisor"])

logger.info(f"✅ {settings.APP_NAME} started successfully")