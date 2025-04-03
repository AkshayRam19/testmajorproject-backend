import json
import logging
import traceback
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("irrigation_control")

# ✅ Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(r'C:\Users\DELL\Desktop\testmajorproject\backend\firebase-key.json')
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        logger.info("✅ Firebase initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Error initializing Firebase: {e}")
        db = None
else:
    db = firestore.client()
    logger.info("✅ Firebase already initialized.")

# ✅ Load crop requirements from JSON
try:
    with open("crop_requirements.json", "r") as f:
        crop_requirements = json.load(f)
    logger.info("✅ Crop requirements loaded successfully.")
except Exception as e:
    logger.error(f"❌ Error loading crop requirements: {e}")
    crop_requirements = {}

def control_pump(selected_crop, sensor_data, weather_data):
    """
    Determines if the pump should be ON or OFF based on:
    - Crop-specific ideal conditions.
    - Soil moisture levels.
    - Forecasted rainfall (if rain is expected in 6 hours, pump stays OFF).
    """
    crop_conditions = crop_requirements.get(selected_crop, {})

    temp_range = crop_conditions.get("temperature", [10, 40])
    humidity_range = crop_conditions.get("humidity", [30, 80])
    rainfall_range = crop_conditions.get("rainfall", [0, 500])
    moisture_range = crop_conditions.get("soil_moisture", [20, 80])

    temp = weather_data.get("temperature", 25)
    humidity = weather_data.get("humidity", 50)
    rainfall = weather_data.get("rainfall", 0)
    soil_moisture = sensor_data.get("soil_moisture", 30)

    logger.info(f"📊 Checking irrigation needs for {selected_crop}...")
    logger.info(f"🌡️ Temp: {temp}°C | 💧 Humidity: {humidity}% | ☔ Rainfall: {rainfall}mm | 🌱 Soil Moisture: {soil_moisture}%")

    if soil_moisture < moisture_range[0] and rainfall < 5:
        logger.info("✅ Soil moisture too low & no rain expected. Turning PUMP ON.")
        return "ON"

    if temp < temp_range[0] or temp > temp_range[1]:
        logger.info("⚠️ Temperature out of crop's ideal range. Turning PUMP ON.")
        return "ON"

    if humidity < humidity_range[0] or humidity > humidity_range[1]:
        logger.info("⚠️ Humidity out of crop's ideal range. Turning PUMP ON.")
        return "ON"

    if rainfall < rainfall_range[0] or rainfall > rainfall_range[1]:
        logger.info("⚠️ Rainfall outside ideal range. Turning PUMP ON.")
        return "ON"

    if rainfall >= 5:
        logger.info("✅ Rain expected soon. Keeping PUMP OFF.")
        return "OFF"

    logger.info("✅ All conditions met. Keeping PUMP OFF.")
    return "OFF"

def store_pump_status(selected_crop, pump_status, sensor_data, weather_data):
    """
    Store the pump status in Firebase along with the selected crop and other relevant data.
    """
    if db is None:
        logger.error("❌ Firebase is not initialized.")
        return

    firebase_data = {
        'selected_crop': selected_crop,
        'pump_status': pump_status,
        'sensor_data': sensor_data,
        'weather_data': weather_data
    }

    save_to_firebase(firebase_data)
    logger.info("✅ Pump status stored successfully in Firebase.")

def save_to_firebase(data):
    """
    Save data to Firebase Firestore.
    """
    try:
        db.collection('pump_status_data').add(data)
        logger.info("✅ Pump status saved to Firebase Firestore.")
    except Exception as e:
        logger.error(f"❌ Error saving data to Firebase: {e}")
