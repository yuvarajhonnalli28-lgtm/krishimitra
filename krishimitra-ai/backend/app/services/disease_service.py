from app.services.leaf_ai_service import analyze_leaf_image
# backend/app/services/disease_service.py
import sys
import os
from pathlib import Path
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Fix imports for both direct and module execution
try:
    # When run as module
    from app.ml.predictor import predict_disease, get_predictor, get_model_status
    from app.ml.preprocessing import validate_image, get_image_info
    from app.utils.helpers import generate_image_id
except ImportError:
    # When run directly, add path and try again
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from app.ml.predictor import predict_disease, get_predictor, get_model_status
    from app.ml.preprocessing import validate_image, get_image_info
    from app.utils.helpers import generate_image_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Treatment database (mock data)
TREATMENT_DATABASE = {
    "Tomato Late Blight": {
        "chemical": "Apply copper-based fungicides (Mancozeb or Chlorothalonil) every 7-10 days",
        "organic": "Apply neem oil spray or copper oxychloride",
        "prevention": "Ensure proper air circulation, avoid overhead watering, use resistant varieties",
        "symptoms": ["Dark lesions on leaves", "White fungal growth", "Rotting fruits"],
        "confidence_threshold": 0.7
    },
    "default": {
        "chemical": "Consult local agricultural expert for specific treatment",
        "organic": "Try neem oil or organic compost as general remedy",
        "prevention": "Maintain good farm hygiene, proper spacing, and regular monitoring",
        "symptoms": ["Observed symptoms on plant"],
        "confidence_threshold": 0.5
    }
}

# Severity descriptions
SEVERITY_DESCRIPTIONS = {
    "high": "Immediate action required. Disease is severe and spreading rapidly.",
    "moderate": "Take action soon. Disease is present but not yet severe.",
    "low": "Monitor regularly. Early stage disease detected.",
    "uncertain": "Low confidence detection. Please consult local expert for verification."
}

def detect_disease(image, crop_type: Optional[str] = None, use_mock: bool = False) -> Dict[str, Any]:
    """
    Detect disease from image with enhanced processing
    
    Args:
        image: Uploaded image file
        crop_type: Optional crop type for better accuracy
        use_mock: Use mock predictions (for development)
    
    Returns:
        Dictionary with detection results and treatment recommendations
    """
    try:
        logger.info(f"Starting disease detection for image. Crop type: {crop_type}")
        
        # Step 1: Validate image
        validate_image(image)
        
        # Step 2: Get image info
        image_info = get_image_info(image)
        logger.info(f"Image info: {image_info}")
        
        # Step 3: Generate unique image ID
        image_id = generate_image_id()
        
        # Step 4: Get prediction from ML model
        logger.info("Calling prediction model...")
        prediction_result = predict_disease(image, use_mock=use_mock)
        
        if not prediction_result.get("success", False):
            error_msg = prediction_result.get("error", "Unknown error")
            logger.error(f"Prediction failed: {error_msg}")
            return {
                "status": "error",
                "message": f"Disease detection failed: {error_msg}",
                "image_id": image_id
            }
        
        # Step 5: Get disease name
        disease_name = prediction_result.get("disease", "Unknown")
        confidence = prediction_result.get("confidence", 0.0)
        severity = prediction_result.get("severity", "unknown")
        
        logger.info(f"Prediction: {disease_name} with confidence {confidence}")
        
        # Step 6: Get treatment recommendations
        treatment_info = get_treatment_recommendations(disease_name, confidence)
        
        # Step 7: Check if confidence is above threshold
        confidence_threshold = treatment_info.get("confidence_threshold", 0.5)
        is_reliable = confidence >= confidence_threshold
        
        # Step 8: Prepare response
        response = {
            "status": "success",
            "image_id": image_id,
            "image_info": {
                "format": image_info.get("format", "unknown"),
                "size": image_info.get("size", [0, 0]),
                "width": image_info.get("width", 0),
                "height": image_info.get("height", 0)
            },
            "detection": {
                "disease": disease_name,
                "scientific_name": treatment_info.get("scientific_name", "Not available"),
                "confidence": round(confidence, 3),
                "severity": severity,
                "severity_description": SEVERITY_DESCRIPTIONS.get(severity, ""),
                "is_reliable": is_reliable,
                "reliability_message": get_reliability_message(confidence, confidence_threshold),
                "alternatives": prediction_result.get("alternatives", [])
            },
            "treatment": {
                "chemical": treatment_info.get("chemical", "Consult local expert"),
                "organic": treatment_info.get("organic", "Monitor plants regularly"),
                "prevention": treatment_info.get("prevention", "Maintain good farm hygiene")
            },
            "symptoms": treatment_info.get("symptoms", ["Observe plant carefully"]),
            "crop_type": crop_type if crop_type else "Not specified",
            "model_used": prediction_result.get("model_used", "unknown"),
            "disclaimer": "This is an AI-powered analysis. Please consult with local agricultural expert for confirmation.",
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 9: Add warnings if needed
        if not is_reliable:
            response["warning"] = f"Low confidence detection. Confidence ({confidence:.2f}) is below threshold ({confidence_threshold}). Please verify with expert."
        
        logger.info(f"Disease detection completed successfully. Image ID: {image_id}")
        return response
        
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return {
            "status": "error",
            "message": str(ve),
            "error_type": "validation_error"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in disease detection: {str(e)}")
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "error_type": "internal_error"
        }


def get_treatment_recommendations(disease_name: str, confidence: float) -> Dict[str, Any]:
    """
    Get treatment recommendations based on disease name
    """
    # Clean disease name for lookup
    disease_key = disease_name.strip()
    
    # Look up in database
    treatment = TREATMENT_DATABASE.get(disease_key)
    
    if not treatment:
        # Try partial match
        for key in TREATMENT_DATABASE:
            if key.lower() in disease_name.lower() or disease_name.lower() in key.lower():
                treatment = TREATMENT_DATABASE[key]
                break
        
        # If still not found, use default
        if not treatment:
            treatment = TREATMENT_DATABASE["default"]
            treatment["disease_name"] = disease_name
    
    # Add confidence-based adjustments
    if confidence < treatment.get("confidence_threshold", 0.5):
        treatment["recommendation_priority"] = "Verify before acting"
    else:
        treatment["recommendation_priority"] = "Can proceed with treatment"
    
    return treatment


def get_reliability_message(confidence: float, threshold: float) -> str:
    """
    Get reliability message based on confidence
    """
    if confidence >= 0.9:
        return "Highly reliable detection"
    elif confidence >= 0.8:
        return "Reliable detection"
    elif confidence >= threshold:
        return "Moderately reliable - take precautions"
    else:
        return "Low reliability - verify with expert"


def generate_image_id() -> str:
    """
    Generate a unique image ID
    """
    import uuid
    return f"img_{uuid.uuid4().hex[:8]}"


# Test the module when run directly
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧪 Testing Disease Service Module")
    print("="*50)
    
    print(f"\n✅ Module loaded successfully!")
    print(f"📁 Current file: {__file__}")
    print(f"📂 Python path: {sys.path[0]}")
    
    # Test the functions
    print("\n📊 Available functions:")
    print(f"  - detect_disease()")
    print(f"  - get_treatment_recommendations()")
    print(f"  - get_reliability_message()")
    print(f"  - generate_image_id()")
    
    # Test generate_image_id
    test_id = generate_image_id()
    print(f"\n🆔 Test image ID: {test_id}")
    
    print("\n✨ Service is ready to use!\n")