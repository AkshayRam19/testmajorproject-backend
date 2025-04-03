import google.generativeai as genai
import logging

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot")

# ✅ Google Gemini API Key
genai.configure(api_key="AIzaSyAihMtyjV1MA9mI2JOBOz4RxbGaBF3gnS4")
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_chatbot_response(user_crop, soil_data, weather_data):
    """
    Generates AI farming advice for user-selected crops based on soil & weather conditions.
    """
    try:
        prompt = f"""
        A farmer wants to grow {user_crop}.
        Given the current conditions:
        - Soil Data: {soil_data}
        - Weather Forecast: {weather_data}
        
        Provide expert farming advice on how to improve the yield.
        """
        
        response = model.generate_content(prompt)
        
        # ✅ Extract AI response
        advice = response.text if response and hasattr(response, "text") else "No response received."
        return advice
    
    except Exception as e:
        logger.error(f"❌ Chatbot Error: {e}")
        return "⚠️ Sorry, I couldn't generate advice. Try again later."