# disease routes
# backend/app/api/disease_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import base64
import uuid
from datetime import datetime
import hashlib
import os

router = APIRouter(tags=["Disease Detection"])

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Supported crops with additional info
SUPPORTED_CROPS = {
    "Tomato": {
        "common_diseases": ["Late Blight", "Early Blight", "Leaf Mold", "Septoria Leaf Spot"],
        "season": "Rabi/Kharif"
    },
    "Potato": {
        "common_diseases": ["Late Blight", "Early Blight", "Black Scurf", "Common Scab"],
        "season": "Rabi"
    },
    "Rice": {
        "common_diseases": ["Blast", "Bacterial Leaf Blight", "Sheath Blight", "Brown Spot"],
        "season": "Kharif"
    },
    "Wheat": {
        "common_diseases": ["Rust", "Powdery Mildew", "Leaf Blight", "Loose Smut"],
        "season": "Rabi"
    },
    "Corn": {
        "common_diseases": ["Northern Leaf Blight", "Southern Rust", "Gray Leaf Spot", "Common Rust"],
        "season": "Kharif"
    }
}

# Disease database with treatments (mock data)
DISEASE_DATABASE = {
    "Late Blight": {
        "scientific_name": "Phytophthora infestans",
        "treatment": "Apply copper-based fungicides (e.g., Mancozeb or Chlorothalonil) every 7-10 days",
        "prevention": "Ensure proper air circulation, avoid overhead watering, use resistant varieties",
        "organic_treatment": "Apply neem oil or copper oxychloride, remove infected leaves",
        "symptoms": ["Dark lesions on leaves", "White fungal growth", "Rotting fruits/tubers"]
    },
    "Early Blight": {
        "scientific_name": "Alternaria solani",
        "treatment": "Apply fungicides like Azoxystrobin or Chlorothalonil",
        "prevention": "Crop rotation, proper spacing, mulch to prevent soil splash",
        "organic_treatment": "Apply compost tea or Bacillus subtilis",
        "symptoms": ["Dark spots with concentric rings", "Yellowing around spots", "Leaf drop"]
    },
    "Powdery Mildew": {
        "scientific_name": "Erysiphales",
        "treatment": "Apply sulfur-based or potassium bicarbonate fungicides",
        "prevention": "Ensure good air circulation, avoid overcrowding",
        "organic_treatment": "Apply milk spray (1:10 ratio), neem oil",
        "symptoms": ["White powdery spots", "Distorted leaves", "Reduced growth"]
    },
    "Rust": {
        "scientific_name": "Puccinia",
        "treatment": "Apply fungicides like Propiconazole or Tebuconazole",
        "prevention": "Use resistant varieties, remove crop debris",
        "organic_treatment": "Apply sulfur or copper sprays",
        "symptoms": ["Rust-colored pustules", "Yellowing leaves", "Stunted growth"]
    },
    "Leaf Spot": {
        "scientific_name": "Various fungi",
        "treatment": "Apply fungicides containing Chlorothalonil or Mancozeb",
        "prevention": "Avoid overhead irrigation, rotate crops",
        "organic_treatment": "Apply copper spray or neem oil",
        "symptoms": ["Circular spots on leaves", "Yellow halos", "Premature leaf drop"]
    }
}

def get_file_extension(filename: str) -> str:
    """Extract file extension"""
    return os.path.splitext(filename)[1].lower()

def generate_image_id(filename: str) -> str:
    """Generate unique image ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"img_{timestamp}_{unique_id}"

def calculate_image_hash(contents: bytes) -> str:
    """Calculate image hash for duplicate detection"""
    return hashlib.md5(contents).hexdigest()

@router.get("/")
async def get_disease_info():
    """Get comprehensive information about plant diseases"""
    return {
        "message": "🌱 KrishiMitra AI Disease Detection API",
        "version": "1.0.0",
        "supported_crops": list(SUPPORTED_CROPS.keys()),
        "total_crops": len(SUPPORTED_CROPS),
        "crop_details": SUPPORTED_CROPS,
        "common_diseases": list(DISEASE_DATABASE.keys()),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "allowed_formats": [ext.replace('.', '').upper() for ext in ALLOWED_EXTENSIONS]
    }

@router.get("/crop/{crop_name}")
async def get_crop_diseases(crop_name: str):
    """Get diseases information for specific crop"""
    
    # Case-insensitive crop name
    crop_name = crop_name.title()
    
    if crop_name not in SUPPORTED_CROPS:
        similar = [c for c in SUPPORTED_CROPS.keys() if crop_name.lower() in c.lower()]
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Crop '{crop_name}' not supported",
                "supported_crops": list(SUPPORTED_CROPS.keys()),
                "suggestions": similar[:3]
            }
        )
    
    crop_info = SUPPORTED_CROPS[crop_name]
    diseases = []
    
    for disease_name in crop_info["common_diseases"]:
        if disease_name in DISEASE_DATABASE:
            diseases.append({
                "name": disease_name,
                **DISEASE_DATABASE[disease_name]
            })
    
    return {
        "crop": crop_name,
        "season": crop_info["season"],
        "total_diseases": len(diseases),
        "diseases": diseases
    }

@router.get("/disease/{disease_name}")
async def get_disease_details(disease_name: str):
    """Get detailed information about specific disease"""
    
    # Case-insensitive disease name
    disease_key = next((d for d in DISEASE_DATABASE.keys() if d.lower() == disease_name.lower()), None)
    
    if not disease_key:
        similar = [d for d in DISEASE_DATABASE.keys() if disease_name.lower() in d.lower()]
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Disease '{disease_name}' not found",
                "available_diseases": list(DISEASE_DATABASE.keys()),
                "suggestions": similar[:3]
            }
        )
    
    return {
        "name": disease_key,
        **DISEASE_DATABASE[disease_key]
    }

@router.post("/detect")
async def detect_disease(
    file: UploadFile = File(..., description="Plant leaf image (max 5MB)"),
    crop_type: str = Form("unknown", description="Type of crop (optional)")
):
    """
    Upload plant image for AI-powered disease detection
    
    - **file**: Image of plant leaf (JPEG, PNG, etc.)
    - **crop_type**: Optional crop name for better accuracy
    """
    
    # 👈 FIX 1: Validate crop type
    if crop_type != "unknown":
        crop_type = crop_type.title()
        if crop_type not in SUPPORTED_CROPS:
            crop_type = "unknown"
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image. Please upload a valid image file."
        )
    
    # Validate file extension
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {[e.replace('.', '') for e in ALLOWED_EXTENSIONS]}"
        )
    
    try:
        # 👈 FIX 2: Check file size
        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            size_mb = len(contents) / (1024 * 1024)
            raise HTTPException(
                status_code=400, 
                detail=f"Image too large: {size_mb:.1f}MB. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
            )
        
        # 👈 FIX 3: Generate image ID
        image_id = generate_image_id(file.filename)
        image_hash = calculate_image_hash(contents)
        
        # Mock disease detection (replace with actual ML model)
        import random
        detected_disease = random.choice(list(DISEASE_DATABASE.keys()))
        confidence = round(random.uniform(0.75, 0.98), 2)
        
        # Get disease details
        disease_info = DISEASE_DATABASE[detected_disease]
        
        # Determine severity based on confidence (mock logic)
        if confidence > 0.9:
            severity = "High"
        elif confidence > 0.7:
            severity = "Moderate"
        else:
            severity = "Low"
        
        # Generate recommendations
        recommendations = [
            f"Apply {disease_info['treatment'].split('(')[0].strip()}",
            "Remove and destroy infected plant parts",
            f"Monitor nearby plants for {detected_disease.lower()} symptoms"
        ]
        
        return {
            "success": True,
            "image_id": image_id,  # 👈 FIX 3: Added image ID
            "filename": file.filename,
            "file_size_kb": round(len(contents) / 1024, 2),
            "image_hash": image_hash[:8],  # First 8 chars for reference
            "crop_type": crop_type if crop_type != "unknown" else "Not specified",
            "detection": {
                "disease": detected_disease,
                "scientific_name": disease_info["scientific_name"],
                "confidence": confidence,
                "severity": severity,
                "symptoms": disease_info["symptoms"][:3]  # Top 3 symptoms
            },
            "treatment": {
                "chemical": disease_info["treatment"],
                "organic": disease_info["organic_treatment"],
                "prevention": disease_info["prevention"]
            },
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "This is an AI-powered analysis. Please consult with local agricultural expert for confirmation."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@router.post("/detect/batch")
async def detect_diseases_batch(
    files: list[UploadFile] = File(..., description="Multiple plant images (max 5 files)")
):
    """
    Upload multiple images for batch disease detection
    Maximum 5 images per request
    """
    
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed per batch")
    
    results = []
    for file in files:
        try:
            # Reuse single detection logic
            result = await detect_disease(file, "unknown")
            results.append({
                "filename": file.filename,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "batch_id": str(uuid.uuid4())[:8],
        "total_processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }