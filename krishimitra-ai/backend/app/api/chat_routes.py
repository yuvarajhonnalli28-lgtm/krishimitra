# backend/app/api/chat_routes.py

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import random
import os
import uuid

from google import genai


router = APIRouter(tags=["AI Advisor"])


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)

GEMINI_MODEL = "gemini-3.6-flash"


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

LANGUAGE_NAMES = {
    "english": "English",
    "kannada": "Kannada",
    "hindi": "Hindi",
    "telugu": "Telugu",
    "tamil": "Tamil",
    "marathi": "Marathi",
}


# ============================================================
# MESSAGE MODEL
# ============================================================

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now
    )


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):
    message: str

    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4())[:8]
    )

    history: Optional[List[Message]] = Field(
        default_factory=list
    )

    language: Optional[str] = "english"

    farmer_id: Optional[str] = None


# ============================================================
# CHAT RESPONSE
# ============================================================

class ChatResponse(BaseModel):
    response: str

    suggestions: List[str] = []

    session_id: str

    confidence: float

    category: str

    timestamp: datetime

    follow_up_questions: List[str] = []

    action_items: List[str] = []


# ============================================================
# KNOWLEDGE BASE
# ============================================================

KNOWLEDGE_BASE = {

    "crops": {

        "keywords": [
            "crop",
            "plant",
            "grow",
            "seed",
            "sow",
            "harvest"
        ],

        "responses": [

            {
                "pattern": [
                    "wheat",
                    "gehu"
                ],

                "response":
                    "🌾 Wheat is a Rabi crop sown Oct–Dec and harvested Mar–Apr. Recommended varieties: HD-2967, PBW-343.",

                "follow_up": [
                    "When to irrigate wheat?",
                    "Fertilizer for wheat?",
                    "Wheat disease control?"
                ]
            },

            {
                "pattern": [
                    "rice",
                    "paddy"
                ],

                "response":
                    "🌾 Rice is a Kharif crop grown during monsoon. Maintain appropriate water management for healthy growth.",

                "follow_up": [
                    "Rice nursery preparation?",
                    "Paddy transplanting time?",
                    "Rice fertilizer schedule?"
                ]
            },

            {
                "pattern": [
                    "tomato"
                ],

                "response":
                    "🍅 Tomato grows best in well-drained soil. Use staking and mulch for better yield.",

                "follow_up": [
                    "Tomato diseases?",
                    "Tomato pruning?",
                    "Best tomato varieties?"
                ]
            }
        ],

        "default":
            "Tell me your soil type, season, and region. I will recommend suitable crops."
    },


    "fertilizer": {

        "keywords": [
            "fertilizer",
            "urea",
            "dap",
            "npk",
            "manure"
        ],

        "responses": [

            {
                "pattern": [
                    "urea"
                ],

                "response":
                    "🧪 Urea contains 46% nitrogen. Apply fertilizer according to the crop, growth stage, soil condition, and product label.",

                "follow_up": [
                    "Urea for paddy?",
                    "When to apply urea?",
                    "Urea alternatives?"
                ]
            },

            {
                "pattern": [
                    "dap"
                ],

                "response":
                    "🧪 DAP fertilizer is commonly described as 18:46:0 and supplies nitrogen and phosphorus. Application should depend on soil testing and crop requirements.",

                "follow_up": [
                    "DAP vs SSP?",
                    "DAP for vegetables?",
                    "DAP application method?"
                ]
            }
        ],

        "default":
            "Tell me your crop, growth stage, soil type, and location. I will suggest a suitable fertilizer approach."
    },


    "pest": {

        "keywords": [
            "pest",
            "disease",
            "fungus",
            "insect",
            "aphid",
            "blight"
        ],

        "responses": [

            {
                "pattern": [
                    "aphid"
                ],

                "response":
                    "🐛 Aphids are sap-sucking insects. For mild infestations, monitor the crop and consider appropriate non-chemical control. For serious infestation, use only a locally approved product according to its label.",

                "follow_up": [
                    "Aphids on wheat?",
                    "Organic aphid control?",
                    "Aphids on mustard?"
                ]
            },

            {
                "pattern": [
                    "blight"
                ],

                "response":
                    "🍂 Blight symptoms can have different causes. Please provide the crop, symptoms, and a photo if possible before selecting a treatment.",

                "follow_up": [
                    "Early blight treatment?",
                    "Blight resistant varieties?",
                    "Blight in potato?"
                ]
            }
        ],

        "default":
            "Please describe the crop, symptoms, and pest or disease you see. A clear photo can help with diagnosis."
    },


    "market": {

        "keywords": [
            "price",
            "rate",
            "market",
            "sell",
            "mandi"
        ],

        "responses": [

            {
                "pattern": [
                    "price",
                    "rate"
                ],

                "response":
                    "💰 Current market prices can change frequently. I should not invent a live price. Tell me your crop and location so live market data can be connected later.",

                "follow_up": [
                    "Best time to sell?",
                    "Mandi near me?",
                    "Price trends?"
                ]
            }
        ],

        "default":
            "Tell me the crop name and location. I can provide market guidance."
    }
}


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(message: str):

    message_lower = message.lower()

    best_category = "general"

    best_confidence = 0.0

    matched_data = {}

    for category, data in KNOWLEDGE_BASE.items():

        for keyword in data["keywords"]:

            if keyword in message_lower:

                confidence = 0.6

                for response in data["responses"]:

                    for pattern in response["pattern"]:

                        if pattern in message_lower:

                            confidence += 0.2

                            matched_data = response

                if confidence > best_confidence:

                    best_confidence = confidence

                    best_category = category

    return (
        best_category,
        min(best_confidence, 0.95),
        matched_data
    )


# ============================================================
# LANGUAGE VALIDATION
# ============================================================

def normalize_language(language: Optional[str]):

    if not language:
        return "english"

    language = language.lower().strip()

    if language not in LANGUAGE_NAMES:
        return "english"

    return language


# ============================================================
# GEMINI RESPONSE
# ============================================================

async def generate_response(
    message: str,
    history=None,
    language="english"
):

    # --------------------------------------------------------
    # Check Gemini API key
    # --------------------------------------------------------

    if gemini_client is None:

        return (
            "Gemini API key is not configured. Please check the backend environment.",
            []
        )


    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------

    language = normalize_language(
        language
    )

    language_name = LANGUAGE_NAMES[
        language
    ]


    # --------------------------------------------------------
    # System instructions
    # --------------------------------------------------------

    system_prompt = f"""
You are KrishiMitra AI, an agricultural advisory assistant
for farmers.

The farmer selected this language:

{language_name}

You MUST answer the farmer in {language_name}.

Supported languages:
- English
- Kannada
- Hindi
- Telugu
- Tamil
- Marathi

If the selected language is Kannada, answer naturally in Kannada script.

If the selected language is Hindi, answer naturally in Hindi script.

If the selected language is Telugu, answer naturally in Telugu script.

If the selected language is Tamil, answer naturally in Tamil script.

If the selected language is Marathi, answer naturally in Marathi script.

If the selected language is English, answer in English.

Do not switch to English unless the farmer asks for English.

Use simple language that farmers can understand.

Give practical, clear and safe farming advice.

For fertilizer questions:
- Consider crop.
- Consider growth stage.
- Consider soil condition.
- Consider location when available.
- Do not invent exact fertilizer doses when important information is missing.
- Recommend soil testing when appropriate.
- Tell the farmer to follow the fertilizer product label.

For pest and disease questions:
- Ask for crop and symptoms when necessary.
- Do not confidently identify a disease from text alone.
- Photos can help with diagnosis.
- Recommend local agricultural experts when uncertain.
- Consider integrated pest management.
- Protect beneficial insects and pollinators.
- Follow local pesticide regulations and product labels.

For market-price questions:
- Do not invent current prices.
- Clearly say when live market data is unavailable.
- Current prices should come from a reliable live market data source.

For weather questions:
- Do not pretend that you have live weather information unless it is actually provided.
- Clearly distinguish general weather-related advice from live forecasts.

Keep answers practical and easy to understand.

Use headings and bullet points when useful.

Do not claim to have performed actions or accessed live information
unless that information is actually available.
"""


    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    conversation = ""

    if history:

        for item in history[-10:]:

            role = getattr(
                item,
                "role",
                "user"
            )

            content = getattr(
                item,
                "content",
                ""
            )

            if content:

                if role == "assistant":
                    role_name = "KrishiMitra AI"
                else:
                    role_name = "Farmer"

                conversation += (
                    f"{role_name}: {content}\n"
                )


    # --------------------------------------------------------
    # Gemini prompt
    # --------------------------------------------------------

    prompt = f"""
{system_prompt}

Previous conversation:

{conversation}

Farmer's current question:

{message}

Answer the farmer's current question in
{language_name}.

Do not mention these instructions.
"""


    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    try:

        response = (
            gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
        )

        response_text = (
            response.text.strip()
            if response.text
            else ""
        )

        if not response_text:

            return (
                "Sorry, I could not generate a response right now. Please try again.",
                []
            )

        return (
            response_text,
            []
        )


    except Exception as e:

        print(
            f"Gemini API error: {e}"
        )

        error_text = str(e).lower()


        # ----------------------------------------------------
        # Gemini overloaded / unavailable
        # ----------------------------------------------------

        if (
            "503" in error_text
            or "unavailable" in error_text
            or "high demand" in error_text
        ):

            return (
                "The AI service is temporarily busy. Please try again in a few seconds.",
                []
            )


        # ----------------------------------------------------
        # Rate limit
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "rate limit" in error_text
        ):

            return (
                "The AI service is temporarily rate-limited. Please wait a moment and try again.",
                []
            )


        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if (
            "401" in error_text
            or "403" in error_text
            or "api key" in error_text
        ):

            return (
                "There is a problem with the Gemini API configuration. Please check the API key.",
                []
            )


        # ----------------------------------------------------
        # Generic error
        # ----------------------------------------------------

        return (
            "Sorry, I could not connect to the AI service right now. Please try again.",
            []
        )


# ============================================================
# CHAT INFORMATION
# ============================================================

@router.get("/")
async def chat_info():

    return {

        "message":
            "KrishiMitra AI Advisor",

        "capabilities":
            list(KNOWLEDGE_BASE.keys()),

        "languages_supported":
            list(LANGUAGE_NAMES.values()),

        "model":
            GEMINI_MODEL,

        "speech_supported":
            True,

        "text_to_speech_supported":
            True
    }


# ============================================================
# SEND CHAT MESSAGE
# ============================================================

@router.post(
    "/message",
    response_model=ChatResponse
)
async def send_message(
    request: ChatRequest
):

    # --------------------------------------------------------
    # Detect category
    # --------------------------------------------------------

    (
        category,
        confidence,
        matched_data
    ) = detect_intent(
        request.message
    )


    # --------------------------------------------------------
    # Generate Gemini response
    # --------------------------------------------------------

    (
        response_text,
        follow_up
    ) = await generate_response(

        request.message,

        request.history,

        request.language
    )


    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    suggestions = [

        "Crop advice",

        "Fertilizer help",

        "Pest control",

        "Market price"
    ]


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return ChatResponse(

        response=response_text,

        suggestions=suggestions,

        session_id=(
            request.session_id
            or str(uuid.uuid4())[:8]
        ),

        confidence=confidence,

        category=category,

        timestamp=datetime.now(),

        follow_up_questions=follow_up,

        action_items=[]
    )


# ============================================================
# FEEDBACK
# ============================================================

@router.post("/feedback")
async def submit_feedback(

    session_id: str,

    rating: int = Query(
        ...,
        ge=1,
        le=5
    ),

    feedback_text: Optional[str] = None

):

    return {

        "status":
            "success",

        "message":
            "Thank you for your feedback!",

        "session_id":
            session_id,

        "rating":
            rating,

        "feedback_text":
            feedback_text,

        "timestamp":
            datetime.now().isoformat()
    }


# ============================================================
# SESSION HISTORY
# ============================================================

@router.get(
    "/session/{session_id}"
)
async def get_session_history(
    session_id: str
):

    return {

        "session_id":
            session_id,

        "message_count":
            random.randint(3, 15),

        "duration_minutes":
            random.randint(2, 30),

        "topics_discussed":
            random.sample(
                list(KNOWLEDGE_BASE.keys()),
                k=min(
                    3,
                    len(KNOWLEDGE_BASE)
                )
            )
    }