import firebase_admin
from firebase_admin import credentials, firestore, messaging
import logging
from datetime import datetime

# ✅ Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize Firebase (Avoid Re-initialization)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        logger.info("✅ Firebase initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Firebase Init Error: {e}")
        raise

# ✅ Function to Store Crop Recommendation
def store_crop_recommendation(crop, soil_data, weather_data):
    """
    Stores the recommended crop along with soil and weather data in Firestore.
    """
    try:
        data = {
            "recommended_crop": crop,
            "soil_data": soil_data,
            "weather_data": weather_data,
            "timestamp": datetime.utcnow()
        }
        db.collection("crop_recommendations").add(data)
        logger.info(f"✅ Crop recommendation saved successfully.")
    except Exception as e:
        logger.error(f"❌ Firebase Error (Crop Recommendation): {e}")

# ✅ Function to Store Sensor Data
def store_sensor_data(sensor_data):
    """
    Stores sensor data (temperature, humidity, soil moisture, etc.) in Firestore.
    """
    try:
        sensor_data["timestamp"] = datetime.utcnow()
        db.collection("sensor_data").add(sensor_data)
        logger.info("✅ Sensor data saved.")
    except Exception as e:
        logger.error(f"❌ Firebase Error (Sensor Data): {e}")

# ✅ Function to Store Pump Status
def store_pump_status(selected_crop, pump_status, sensor_data, weather_data):
    """
    Stores pump status along with sensor & weather data in Firestore.
    """
    try:
        data = {
            "selected_crop": selected_crop,
            "pump_status": pump_status,
            "sensor_data": sensor_data,
            "weather_data": weather_data,
            "timestamp": datetime.utcnow()
        }
        db.collection("pump_status").add(data)
        logger.info("✅ Pump status saved.")
    except Exception as e:
        logger.error(f"❌ Firebase Error (Pump Status): {e}")

# ✅ Function to Get Unique User Cities (For Weather Notifications)
def get_user_cities():
    """
    Retrieves unique cities where users have entered crop data.
    """
    try:
        recommendations = db.collection("crop_recommendations").stream()
        cities = {doc.to_dict().get("soil_data", {}).get("city") for doc in recommendations}
        cities = {city for city in cities if city}  # Remove None values
        logger.info(f"✅ Retrieved cities: {cities}")
        return list(cities)
    except Exception as e:
        logger.error(f"❌ Firebase Error (Get Cities): {e}")
        return []

# ✅ Function to Send Weather Notification
def send_weather_notification(city, weather_data):
    """
    Sends a push notification if rain is detected in the user's city.
    """
    try:
        if weather_data.get("rainfall", 0) > 0:  # ✅ Check for rain
            message = messaging.Message(
                notification=messaging.Notification(
                    title="🌧️ Rain Alert!",
                    body=f"Rain detected in {city}. Adjust irrigation accordingly!"
                ),
                topic="weather_alerts"  # ✅ Broadcast to all users subscribed
            )
            response = messaging.send(message)
            logger.info(f"✅ Weather notification sent: {response}")
    except Exception as e:
        logger.error(f"❌ Firebase Error (Weather Notification): {e}")
