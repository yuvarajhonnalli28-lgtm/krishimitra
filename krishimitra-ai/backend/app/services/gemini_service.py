# gemini service
import google.generativeai as genai
import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# System prompts for different farming contexts
SYSTEM_PROMPTS = {
    "general": """You are KrishiMitra AI, a helpful farming assistant for Indian farmers. 
    Provide practical, easy-to-understand advice about crops, farming practices, pest management, 
    and agriculture in India. Use simple language and include local terms when helpful.
    Keep responses concise and actionable.""",
    
    "crops": """You are an expert in Indian agriculture specializing in crop management.
    Provide advice on crop selection, sowing times, irrigation, and harvesting for different seasons (Rabi/Kharif).
    Include regional variations for different states.""",
    
    "pests": """You are a plant protection expert specializing in pest and disease management.
    Provide identification tips, organic and chemical control methods, and prevention strategies.
    Include symptoms and treatment options for common crop diseases.""",
    
    "market": """You are an agricultural market analyst specializing in Indian mandi prices.
    Provide insights on market trends, best times to sell, and price forecasts.
    Include MSP (Minimum Support Price) information when relevant.""",
    
    "weather": """You are a weather specialist for agriculture.
    Provide farming advice based on weather conditions, seasonal forecasts,
    and climate impact on different crops."""
}

# Conversation history storage (in production, use a database)
conversation_history = {}

class GeminiService:
    """
    Service for interacting with Google's Gemini AI
    """
    
    def __init__(self, model_name: str = "gemini-pro"):
        """
        Initialize Gemini service
        
        Args:
            model_name: Gemini model to use
        """
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini model '{self.model_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            self.model = None
    
    def ask(self, 
            question: str, 
            context: str = "general",
            session_id: Optional[str] = None,
            language: str = "english",
            include_history: bool = True) -> Dict[str, Any]:
        """
        Ask a question to Gemini
        
        Args:
            question: User's question
            context: Context type (general, crops, pests, market, weather)
            session_id: Optional session ID for conversation history
            language: Preferred language (english/hindi)
            include_history: Whether to include conversation history
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Check if model is available
            if not self.model:
                return self._get_fallback_response(question, "Model not initialized")
            
            # Prepare prompt with system context
            prompt = self._prepare_prompt(question, context, language)
            
            # Add conversation history if available
            if session_id and include_history:
                history = self._get_conversation_history(session_id)
                if history:
                    prompt = self._add_history_to_prompt(prompt, history)
            
            logger.info(f"Sending question to Gemini: {question[:50]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract response text
            if hasattr(response, 'text'):
                answer = response.text
            else:
                answer = str(response)
            
            # Clean up response
            answer = self._clean_response(answer)
            
            # Store in history
            if session_id:
                self._store_conversation(session_id, question, answer)
            
            # Generate follow-up suggestions
            suggestions = self._generate_suggestions(answer, context)
            
            return {
                "success": True,
                "response": answer,
                "context": context,
                "language": language,
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini API call: {str(e)}")
            return {
                "success": False,
                "response": self._get_error_message(e),
                "error": str(e),
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
    
    def ask_farming_question(self, 
                             question: str, 
                             crop: Optional[str] = None,
                             region: Optional[str] = None,
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a farming-specific question with crop and region context
        
        Args:
            question: User's question
            crop: Optional crop name for context
            region: Optional region/state for localized advice
            session_id: Optional session ID
        """
        # Build context
        context_parts = []
        if crop:
            context_parts.append(f"regarding {crop} crop")
        if region:
            context_parts.append(f"in {region} region")
        
        context_str = " ".join(context_parts)
        enhanced_question = f"Farming question {context_str}: {question}"
        
        return self.ask(enhanced_question, context="general", session_id=session_id)
    
    def get_crop_advice(self, 
                        crop: str, 
                        stage: str = "general",
                        region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get specific crop advice
        
        Args:
            crop: Crop name
            stage: Growth stage (sowing, growing, harvesting, general)
            region: Region for localized advice
        """
        stage_prompts = {
            "sowing": f"When is the best time to sow {crop}? What is the seed rate and method?",
            "growing": f"What are the best practices for growing {crop}? Irrigation, fertilizer, and care?",
            "harvesting": f"When and how to harvest {crop} for best yield?",
            "general": f"Complete guide for cultivating {crop}"
        }
        
        question = stage_prompts.get(stage, stage_prompts["general"])
        
        if region:
            question += f" in {region}"
        
        return self.ask_farming_question(question, crop=crop, region=region)
    
    def diagnose_pest(self, 
                      crop: str, 
                      symptoms: str,
                      region: Optional[str] = None) -> Dict[str, Any]:
        """
        Diagnose pest or disease based on symptoms
        
        Args:
            crop: Crop name
            symptoms: Description of symptoms
            region: Region for localized advice
        """
        question = f"My {crop} crop has these symptoms: {symptoms}. What disease or pest is this and how do I treat it?"
        
        if region:
            question += f" I'm farming in {region}."
        
        return self.ask(question, context="pests")
    
    def get_market_insights(self, 
                            crop: str, 
                            mandi: Optional[str] = None) -> Dict[str, Any]:
        """
        Get market insights for a crop
        
        Args:
            crop: Crop name
            mandi: Optional mandi name
        """
        if mandi:
            question = f"What is the current market situation for {crop} in {mandi} mandi? Should farmers sell now or wait?"
        else:
            question = f"What is the market outlook for {crop}? Best time to sell and price trends?"
        
        return self.ask(question, context="market")
    
    def _prepare_prompt(self, question: str, context: str, language: str) -> str:
        """Prepare prompt with system context"""
        system_prompt = SYSTEM_PROMPTS.get(context, SYSTEM_PROMPTS["general"])
        
        language_instruction = ""
        if language.lower() == "hindi":
            language_instruction = "Respond in Hindi with Hinglish (Hindi+English) for better understanding."
        elif language.lower() == "simple":
            language_instruction = "Use very simple language, as if explaining to a farmer with basic education."
        
        prompt = f"""{system_prompt}

{language_instruction}

Important guidelines:
- Be practical and actionable
- Use local terms when helpful
- Keep responses concise (under 300 words unless detailed explanation needed)
- If unsure, suggest consulting local agricultural expert
- Include safety precautions when recommending pesticides/chemicals

Farmer's question: {question}

Answer:"""
        
        return prompt
    
    def _add_history_to_prompt(self, prompt: str, history: List[Dict]) -> str:
        """Add conversation history to prompt"""
        if not history:
            return prompt
        
        history_text = "\n\nPrevious conversation:\n"
        for i, msg in enumerate(history[-3:]):  # Last 3 messages
            role = "Farmer" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
        
        return history_text + "\n" + prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean up response text"""
        # Remove excessive whitespace
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        response = '\n'.join(lines)
        
        # Ensure response ends with proper punctuation
        if response and response[-1] not in '.!?':
            response += '.'
        
        return response
    
    def _generate_suggestions(self, response: str, context: str) -> List[str]:
        """Generate follow-up question suggestions"""
        # This could be enhanced with AI, but for now use rule-based
        suggestions = {
            "general": [
                "Tell me about crop rotation",
                "Best fertilizers for vegetables",
                "Organic pest control methods",
                "Government schemes for farmers"
            ],
            "crops": [
                "When to sow wheat?",
                "Rice farming tips",
                "Best vegetables for summer",
                "Crop insurance information"
            ],
            "pests": [
                "Natural pest control",
                "Common tomato diseases",
                "Aphid control methods",
                "Organic pesticides recipe"
            ],
            "market": [
                "Current mandi prices",
                "Best time to sell wheat",
                "MSP rates 2024",
                "Export opportunities"
            ],
            "weather": [
                "Rain forecast for my area",
                "How to protect crops from heat",
                "Frost protection methods",
                "Climate resilient farming"
            ]
        }
        
        return suggestions.get(context, suggestions["general"])
    
    def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return conversation_history.get(session_id, [])
    
    def _store_conversation(self, session_id: str, question: str, answer: str):
        """Store conversation in history"""
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Store user question
        conversation_history[session_id].append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store assistant answer
        conversation_history[session_id].append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 messages
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
    
    def _get_error_message(self, error: Exception) -> str:
        """Get user-friendly error message"""
        error_str = str(error).lower()
        
        if "api key" in error_str:
            return "I'm having trouble connecting. Please check your API configuration."
        elif "quota" in error_str or "limit" in error_str:
            return "I've reached my limit. Please try again later."
        elif "safety" in error_str:
            return "I can't answer that question. Please ask about farming topics."
        else:
            return "I'm having trouble right now. Please try again in a moment."
    
    def _get_fallback_response(self, question: str, reason: str) -> Dict[str, Any]:
        """Get fallback response when Gemini is unavailable"""
        logger.warning(f"Using fallback response. Reason: {reason}")
        
        fallback_responses = {
            "greeting": "Namaste! I'm your KrishiMitra AI assistant. How can I help with your farming questions today?",
            "crops": "For crop-specific advice, please tell me which crop you're interested in and your region.",
            "pests": "To diagnose plant problems, please describe the symptoms you're seeing on your crops.",
            "weather": "For weather-based farming advice, please check our weather forecast section.",
            "market": "For current market prices, please visit our Market Prices page.",
            "default": "I'm currently in offline mode. Please try again later or check our other features."
        }
        
        # Simple keyword matching
        if "hello" in question.lower() or "hi" in question.lower():
            response = fallback_responses["greeting"]
        elif any(word in question.lower() for word in ["crop", "plant", "grow", "sow"]):
            response = fallback_responses["crops"]
        elif any(word in question.lower() for word in ["pest", "disease", "insect", "problem"]):
            response = fallback_responses["pests"]
        elif any(word in question.lower() for word in ["weather", "rain", "temperature"]):
            response = fallback_responses["weather"]
        elif any(word in question.lower() for word in ["price", "market", "sell", "rate"]):
            response = fallback_responses["market"]
        else:
            response = fallback_responses["default"]
        
        return {
            "success": True,
            "response": response,
            "is_fallback": True,
            "message": "Using offline mode. Gemini AI connection unavailable.",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_gemini_service_instance = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance


# Simple function for backward compatibility
def ask_gemini(question: str) -> str:
    """
    Simple function to ask Gemini a question
    """
    service = get_gemini_service()
    result = service.ask(question)
    return result.get("response", "I'm having trouble answering right now.")


# Enhanced functions
def ask_farming_advisor(question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Ask the farming advisor with session tracking
    """
    service = get_gemini_service()
    return service.ask(question, context="general", session_id=session_id)


def get_crop_recommendation(soil_type: str, season: str, region: str) -> Dict[str, Any]:
    """
    Get crop recommendations based on soil, season, and region
    """
    service = get_gemini_service()
    question = f"What crops should I grow in {soil_type} soil during {season} season in {region}?"
    return service.ask(question, context="crops")


def diagnose_plant_disease(symptoms: str, crop: str) -> Dict[str, Any]:
    """
    Diagnose plant disease from symptoms
    """
    service = get_gemini_service()
    return service.diagnose_pest(crop, symptoms)


def get_fertilizer_recommendation(crop: str, soil_test: Optional[str] = None) -> Dict[str, Any]:
    """
    Get fertilizer recommendations for a crop
    """
    service = get_gemini_service()
    if soil_test:
        question = f"What fertilizer should I use for {crop} based on soil test: {soil_test}?"
    else:
        question = f"What is the general fertilizer schedule for {crop}?"
    return service.ask(question, context="crops")


# Health check
def check_gemini_health() -> Dict[str, Any]:
    """
    Check if Gemini service is healthy
    """
    try:
        service = get_gemini_service()
        if service.model:
            # Quick test
            test_result = service.ask("Say 'OK' if you're working", include_history=False)
            return {
                "status": "healthy" if test_result["success"] else "unhealthy",
                "model": service.model_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "reason": "Model not initialized",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "reason": str(e),
            "timestamp": datetime.now().isoformat()
        }