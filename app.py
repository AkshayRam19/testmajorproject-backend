from flask import Flask, request, jsonify
import joblib
import pandas as pd
import logging
import traceback
from flask_cors import CORS
import os


# ✅ Import Firebase & Utility Functions
from firebase_db import store_crop_recommendation, store_sensor_data, store_pump_status
from sensor_simulation import generate_sensor_data
from weather_api import get_weather
from irrigation_control import control_pump
from chatbot import generate_chatbot_response  # ✅ AI Chatbot Integration

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)

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
        required_fields = ['N', 'P', 'K', 'ph', 'city']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "❌ Missing required fields", "expected_fields": required_fields}), 400

        # 🌱 Fetch weather data dynamically
        weather_data = get_weather(data['city'])
        if not weather_data:
            return jsonify({"error": "❌ Unable to fetch weather data"}), 500
        
        temperature = weather_data['temperature']
        humidity = weather_data['humidity']
        rainfall = weather_data['rainfall']

        # ✅ Generate Sensor Data (simulated)
        sensor_data = generate_sensor_data()

        features = pd.DataFrame([[data['N'], data['P'], data['K'], 
                                  temperature, humidity, 
                                  data['ph'], rainfall]],
                                columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

        scaled_features = scaler.transform(features)
        prediction = model.predict(scaled_features)[0]
        crop = reverse_crop_dict.get(prediction, "Unknown Crop")

        # ✅ Store in Firestore (Crop recommendation, sensor data, weather data)
        store_crop_recommendation(crop, data, weather_data)  # Store crop, soil (data), and weather data
        store_sensor_data(sensor_data)  # Store simulated sensor data

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
        store_sensor_data(sensor_data)
        return jsonify(sensor_data)
    except Exception as e:
        logger.error(f"❌ Error in /get_sensor_data: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# ✅ Pump Status API
@app.route('/get_pump_status', methods=['POST'])
def get_pump_status():
    try:
        data = request.get_json()
        if not data or "selected_crop" not in data or "city" not in data:
            return jsonify({"error": "❌ Invalid JSON format or missing required fields"}), 400

        selected_crop = data["selected_crop"]
        city = data["city"]

        # ✅ Get Weather & Sensor Data
        weather_data = get_weather(city)
        sensor_data = generate_sensor_data()
        pump_status = control_pump(selected_crop, sensor_data, weather_data)

        # ✅ Store Data in Firestore (Pump status, selected crop, sensor data, weather data)
        store_pump_status(selected_crop, pump_status, sensor_data, weather_data)

        return jsonify({"selected_crop": selected_crop, "pump_status": pump_status})

    except Exception as e:
        logger.error(f"❌ Error in /get_pump_status: {str(e)}")
        return jsonify({"error": f"❌ Internal Server Error: {str(e)}"}), 500
# ✅ AI Chatbot API
@app.route('/get_chatbot_response', methods=['POST'])
def get_chatbot_response():
    try:
        data = request.get_json()
        if 'selected_crop' not in data or 'city' not in data:
            return jsonify({"error": "❌ Missing required fields: 'selected_crop' or 'city'"}), 400

        sensor_data = generate_sensor_data()
        weather_data = get_weather(data['city'])
        chatbot_response = generate_chatbot_response(data['selected_crop'], sensor_data, weather_data)

        return jsonify({"Chatbot Response": chatbot_response})

    except Exception as e:
        logger.error(f"❌ Error in /get_chatbot_response: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500

# ✅ Weather Data API (New Route)
@app.route('/get_weather', methods=['GET'])
def get_weather_data():
    try:
        city = request.args.get('city')
        if not city:
            return jsonify({"error": "❌ City parameter is required"}), 400
        
        # Call the weather API to fetch weather data
        weather_data = get_weather(city)
        if weather_data:
            return jsonify(weather_data)
        else:
            return jsonify({"error": "❌ Unable to fetch weather data"}), 500
    except Exception as e:
        logger.error(f"❌ Error in /get_weather: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host='0.0.0.0', port=port, debug=False)
