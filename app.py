from flask import Flask, request, jsonify
import joblib
import pandas as pd
import logging
import traceback

# ✅ Import Firebase & Utility Functions
from firebase_db import store_crop_recommendation, store_sensor_data, store_pump_status
from sensor_simulation import generate_sensor_data
from weather_api import get_weather
from irrigation_control import control_pump
from chatbot import generate_chatbot_response  # ✅ Import AI Chatbot

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load ML Model & Data
try:
    model = joblib.load("crop_model.pkl")  # Ensure correct path
    scaler = joblib.load("scaler.pkl")
    reverse_crop_dict = joblib.load("reverse_crop_dict.pkl")
    logger.info("✅ Model and scaler loaded successfully.")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")
    raise

@app.route('/')
def home():
    return jsonify({"message": "✅ Smart Irrigation API is running! Use the correct endpoints."})

# ✅ Crop Recommendation API
@app.route('/recommend_crop', methods=['POST'])
def recommend_crop():
    try:
        data = request.get_json()
        logger.info(f"📥 Received JSON: {data}")

        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'user_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "❌ Missing required fields", "expected_fields": required_fields}), 400

        # 🌱 Get real-time sensor and weather data
        weather_data = get_weather(data['city'])

        features = pd.DataFrame([[data['N'], data['P'], data['K'], 
                          data["temperature"], data["humidity"], 
                          data['ph'], data["rainfall"]]], 
                        columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

        logger.info(f"🟢 Features for Prediction: {features}")

        scaled_features = scaler.transform(features)
        logger.info(f"📊 Scaled Features: {scaled_features}")

        prediction = model.predict(scaled_features)[0]
        crop = reverse_crop_dict.get(prediction, "Unknown Crop")

        if crop == "Unknown Crop":
            logger.error(f"⚠️ Prediction {prediction} not found in dictionary!")

        store_crop_recommendation(data['user_id'], crop, data)
        logger.info(f"✅ Recommendation stored for {crop}")

        return jsonify({"Recommended Crop": crop})
    
    except Exception as e:
        logger.error(f"❌ Error in /recommend_crop: {e}")
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# ✅ Sensor Data API
@app.route('/get_sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        sensor_data = generate_sensor_data()
        user_id = "test_user"
        store_sensor_data(user_id, sensor_data)
        return jsonify(sensor_data)
    except Exception as e:
        logger.error(f"❌ Error in /get_sensor_data: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# ✅ Weather API
@app.route('/get_weather', methods=['GET'])
def get_weather_data():
    try:
        city = request.args.get('city')
        weather = get_weather(city)
        return jsonify(weather)
    except Exception as e:
        logger.error(f"❌ Error in /get_weather: {e}")
        traceback.print_exc()
        return jsonify({"error": "An error occurred"}), 500

# ✅ Pump Status API
@app.route('/get_pump_status', methods=['POST'])
def get_pump_status():
    try:
        # ✅ Parse JSON request
        data = request.get_json()
        if not data or "selected_crop" not in data or "city" not in data:
            logger.error("❌ Invalid JSON format or missing required fields.")
            return jsonify({"error": "❌ Invalid JSON format or missing required fields"}), 400

        selected_crop = data["selected_crop"]
        city = data["city"]
        user_id = data.get("user_id", "unknown")  # Default to 'unknown' if not provided

        # ✅ Get Weather Data
        weather_data = get_weather(city)
        if not weather_data:
            logger.error("❌ Failed to fetch weather data.")
            return jsonify({"error": "❌ Failed to fetch weather data"}), 500
        logger.info(f"🟢 Weather Data: {weather_data}")

        # ✅ Get Soil Moisture Data
        sensor_data = generate_sensor_data()
        logger.info(f"🟢 Sensor Data: {sensor_data}")

        # ✅ Determine Pump Status
        pump_status = control_pump(selected_crop, sensor_data, weather_data)
        logger.info(f"🚰 Pump Status: {pump_status}")

        # ✅ Store Data in Firebase with user_id
        store_pump_status(user_id, selected_crop, pump_status, sensor_data, weather_data)

        # ✅ Send Response
        return jsonify({"selected_crop": selected_crop, "pump_status": pump_status})

    except Exception as e:
        logger.error(f"❌ Error in /get_pump_status: {str(e)}")
        return jsonify({"error": f"❌ Internal Server Error: {str(e)}"}), 500



# ✅ AI Chatbot API
@app.route('/get_chatbot_response', methods=['POST'])
def get_chatbot_response():
    try:
        data = request.get_json()
        logger.info(f"📥 Received chatbot request: {data}")

        if 'selected_crop' not in data or 'city' not in data:
            logger.error("❌ Missing required fields: 'selected_crop' or 'city'")
            return jsonify({"error": "❌ Missing required fields: 'selected_crop' or 'city'"}), 400

        # 🌱 Get soil & weather data
        sensor_data = generate_sensor_data()  # Soil moisture from sensor
        weather_data = get_weather(data['city'])  # Temp, humidity, rainfall from API
        logger.info(f"🟢 Sensor Data: {sensor_data}")
        logger.info(f"🟢 Weather Data: {weather_data}")

        # ✅ Generate chatbot response
        chatbot_response = generate_chatbot_response(data['selected_crop'], sensor_data, weather_data)
        logger.info(f"💬 Chatbot Response: {chatbot_response}")

        return jsonify({"Chatbot Response": chatbot_response})

    except Exception as e:
        logger.error(f"❌ Error in /get_chatbot_response: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
