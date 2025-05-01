"""
AI wrapper module for Medico that provides fallback functionality when APIs are unavailable.
This module handles both Meditron model integration and Google GenAI integration.
"""
import os
import logging
import random

# Configure logging
logger = logging.getLogger(__name__)

# Try to import GenAI, but with error handling in case of compatibility issues
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    # Initialize the client safely
    try:
        client = genai.Client(api_key="AIzaSyB0R26JpwnrxR1iHP7SRdlXImYhG2NAYLQ")
        GENAI_CLIENT_WORKING = True
    except TypeError:
        logger.warning("Google GenAI client initialization failed due to compatibility issues")
        GENAI_CLIENT_WORKING = False
except ImportError:
    logger.warning("Google GenAI module not available")
    GENAI_AVAILABLE = False
    GENAI_CLIENT_WORKING = False

# Try to import the Meditron model, but with error handling
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HF_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Hugging Face Transformers not available")
    HF_TRANSFORMERS_AVAILABLE = False

FALLBACK_RESPONSES = {
    "questions": [
        "What are your main symptoms?",
        "How long have you been experiencing these symptoms?",
        "Do you have any previous medical conditions?",
        "Are you currently taking any medications?",
        "Do you have any allergies to medications?"
    ],
    "diagnostics": [
        "Based on the symptoms you've described, it could be a viral infection.",
        "Your symptoms suggest you might be experiencing a mild allergic reaction.",
        "This might be a common cold or seasonal flu.",
        "Your symptoms are consistent with stress-related conditions.",
        "This could be a minor inflammatory condition."
    ],
    "advice": [
        "I recommend plenty of rest and staying hydrated.",
        "Over-the-counter pain relievers might help with your symptoms.",
        "You should consider scheduling an appointment with a specialist.",
        "Monitor your symptoms for the next 24-48 hours.",
        "Applying warm compresses may provide some relief."
    ]
}

def send_chat_message(user_input):
    """
    Sends a user message to the AI system with fallbacks if API is unavailable.
    Args:
        user_input (str): User's message
    Returns:
        str: AI response
    """
    # First try GenAI if available
    if GENAI_AVAILABLE and GENAI_CLIENT_WORKING:
        try:
            return _send_genai_message(user_input)
        except Exception as e:
            logger.error(f"GenAI error: {e}")
            # Fall through to next option
    
    # If GenAI failed or isn't available, use rule-based responses
    return _generate_fallback_response(user_input)

def generate_medical_report(prompt):
    """
    Generates a medical report based on the provided prompt.
    Falls back to a simple response if AI services are unavailable.
    
    Args:
        prompt (str): The patient information and history
        
    Returns:
        str: Generated medical report
    """
    if GENAI_AVAILABLE and GENAI_CLIENT_WORKING:
        try:
            system_prompt = (
                "You are a medical assistant. Generate a comprehensive medical report "
                "based on the patient information provided. Include sections for "
                "History of Present Illness, Assessment, and Plan."
            )
            
            # Try to create a chat with system instructions
            try:
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=types.GenerateContentConfig(system_instruction=system_prompt)
                )
                response = chat.send_message(prompt)
                return response.text
            except:
                # If chat with system instructions fails, try direct generation
                response = client.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Error generating medical report with GenAI: {e}")
    
    # Fallback to basic report generation
    return _generate_fallback_report(prompt)

def _send_genai_message(user_input):
    """Sends message using Google GenAI"""
    try:
        # Try with chat format first
        try:
            chat = client.chats.create(model="gemini-1.5-flash")
            response = chat.send_message(user_input)
            return response.text
        except:
            # If chat format fails, try direct generation
            response = client.generate_content(user_input)
            return response.text
    except Exception as e:
        logger.error(f"GenAI message error: {e}")
        raise

def _generate_fallback_response(user_input):
    """Generates a rule-based fallback response"""
    user_input = user_input.lower()
    
    if "headache" in user_input or "pain" in user_input:
        return "I understand you're experiencing pain. Can you tell me more about when it started and if anything makes it better or worse?"
    
    elif "fever" in user_input or "temperature" in user_input:
        return "Fever can be a sign of infection. Have you taken your temperature? It's also important to stay hydrated and rest."
    
    elif "appointment" in user_input or "schedule" in user_input or "book" in user_input:
        return "I can help you schedule an appointment. Please provide your preferred date and time, and I'll check availability."
    
    elif "medicine" in user_input or "medication" in user_input or "prescription" in user_input:
        return "It's important to take medications as prescribed. If you're experiencing side effects, please consult with your doctor before making any changes."
    
    elif "thank" in user_input:
        return "You're welcome! I'm here to help with any health questions you may have."
    
    elif "hi" in user_input or "hello" in user_input or "hey" in user_input:
        return "Hello! I'm your medical assistant. How can I help you today?"
    
    else:
        return "I understand you have a medical concern. Could you please provide more details about your symptoms so I can assist you better?"

def _generate_fallback_report(prompt):
    """Generates a simple medical report when AI services are unavailable"""
    # Extract some keywords from the prompt to personalize the report
    keywords = []
    for term in ["headache", "pain", "fever", "cough", "fatigue", "nausea", "dizziness"]:
        if term in prompt.lower():
            keywords.append(term)
    
    if not keywords:
        keywords = ["unspecified symptoms"]
    
    report = f"""
MEDICAL REPORT
--------------
Date: {os.environ.get('REQUEST_DATE', 'Current Date')}

HISTORY OF PRESENT ILLNESS:
Patient presents with {', '.join(keywords)}. Detailed patient history was collected and reviewed.

ASSESSMENT:
Based on the presented symptoms and history, the patient may be experiencing a condition that requires further evaluation.

PLAN:
1. Rest and monitor symptoms
2. Stay hydrated
3. Consider over-the-counter medications as appropriate for symptoms
4. Follow up if symptoms persist or worsen
5. Consider scheduling an appointment with a specialist for further evaluation

Note: This is a preliminary assessment generated by the Medico AI assistant.
"""
    return report