# backend/app/services/leaf_ai_service.py

import os
import io
import json
import logging

from PIL import Image, ImageOps
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

client = genai.Client(api_key=API_KEY) if API_KEY else None


def analyze_leaf_image(image_file, crop_type=None):
    """
    Analyze an uploaded leaf image with Gemini.

    Returns a structured disease assessment and
    treatment recommendations.
    """

    if client is None:
        return {
            "success": False,
            "error": (
                "Gemini API key is missing. "
                "Configure GEMINI_API_KEY in backend/.env."
            )
        }

    try:
        # Read uploaded image safely.
        if hasattr(image_file, "seek"):
            image_file.seek(0)

        if isinstance(image_file, bytes):
            image_bytes = image_file
        else:
            image_bytes = image_file.read()

        if not image_bytes:
            return {
                "success": False,
                "error": "The uploaded image is empty."
            }

        # Validate and convert the image.
        with Image.open(io.BytesIO(image_bytes)) as source:
            source.verify()

        with Image.open(io.BytesIO(image_bytes)) as source:
            image = ImageOps.exif_transpose(source)
            image = image.convert("RGB")

            # Keep the request manageable.
            image.thumbnail((1024, 1024))

            image_buffer = io.BytesIO()
            image.save(image_buffer, format="JPEG", quality=85)
            jpeg_bytes = image_buffer.getvalue()

        crop_instruction = (
            f"The user-selected crop is: {crop_type}."
            if crop_type
            else "The crop species has not been specified."
        )

        prompt = f"""
You are an agricultural plant-health assistant.

Analyze the attached plant leaf image.

{crop_instruction}

Tasks:
1. Identify the likely plant species if possible.
2. Assess whether the leaf appears healthy or diseased.
3. If disease is suspected, provide the most likely disease.
4. Describe visible symptoms that support your assessment.
5. Provide cautious, crop-specific management recommendations.
6. Mention when an agricultural expert should verify the result.

Important rules:
- Base your assessment on the image, not on a predetermined disease.
- Do not invent symptoms that are not visible.
- If the image is unclear or insufficient, say so.
- Do not claim certainty when the image cannot establish a diagnosis.
- Do not recommend a pesticide unless it is appropriate to the
  identified crop and disease. Advise following local registration,
  product labels, and agricultural guidance.
- Do not treat an AI confidence estimate as a calibrated probability.
- If the image is not a plant leaf, report that clearly.

Return ONLY valid JSON with this structure:

{{
  "is_plant_leaf": true,
  "crop": "crop name or unknown",
  "health_status": "healthy, diseased, or uncertain",
  "disease": "likely disease name or unknown",
  "confidence": "high, medium, or low",
  "visible_symptoms": [
    "visible symptom"
  ],
  "possible_causes": [
    "possible cause"
  ],
  "treatment": {{
    "chemical": "cautious, locally appropriate guidance",
    "organic": "appropriate management advice",
    "prevention": "prevention advice"
  }},
  "recommendation": "short practical summary",
  "needs_expert_confirmation": true
}}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(
                    data=jpeg_bytes,
                    mime_type="image/jpeg"
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )

        response_text = response.text

        if not response_text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        result = json.loads(response_text)

        if not isinstance(result, dict):
            raise ValueError(
                "Gemini returned an unexpected response format."
            )

        if not result.get("is_plant_leaf", False):
            return {
                "success": False,
                "error": (
                    "The uploaded image could not be "
                    "identified as a plant leaf."
                ),
                "analysis": result,
                "model_used": MODEL_NAME
            }

        result["success"] = True
        result["model_used"] = MODEL_NAME

        logger.info(
            "Gemini leaf analysis completed: crop=%s, disease=%s",
            result.get("crop"),
            result.get("disease")
        )

        return result

    except json.JSONDecodeError:
        logger.exception(
            "Gemini returned invalid JSON."
        )

        return {
            "success": False,
            "error": "The AI response could not be parsed."
        }

    except Exception as exc:
        logger.exception(
            "Leaf image analysis failed."
        )

        return {
            "success": False,
            "error": str(exc)
        }