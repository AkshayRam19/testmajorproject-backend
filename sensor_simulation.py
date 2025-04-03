import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sensor_data():
    """
    Simulates soil moisture sensor data.
    """
    try:
        data = {
            "soil_moisture": random.randint(10, 100)  # Simulated soil moisture value
        }
        logger.info(f"🌱 Simulated Soil Moisture Data: {data}")
        return data
    except Exception as e:
        logger.error(f"❌ Error generating sensor data: {e}")
        return {"error": "Sensor simulation failed"}
