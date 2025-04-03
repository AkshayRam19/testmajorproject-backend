import firebase_admin
from firebase_admin import credentials, firestore
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
            "weather_data": weather_data,  # ✅ Include weather data
            "timestamp": datetime.utcnow()
        }
        db.collection("crop_recommendations").add(data)  # ✅ Using .add() instead of user_id
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
