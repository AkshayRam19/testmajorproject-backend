import requests
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        # Fetch 6-hour rainfall prediction
        rainfall_forecast = data.get("rain", {}).get("6h", 0)

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": rainfall_forecast
        }
    except Exception as e:
        return {"error": str(e)}
