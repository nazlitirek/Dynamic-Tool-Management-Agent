# tools/weather.py
# Gerçek API: OpenWeatherMap (ücretsiz key)

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(location: str) -> dict:
    """
    Belirli bir şehrin güncel hava durumunu getirir.
    """
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": API_KEY,
            "units": "metric",
            "lang": "tr"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "location": data["name"],
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6),
            "condition": data["weather"][0]["description"].capitalize(),
            "description": f"{data['name']} için güncel hava durumu"
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"'{location}' şehri bulunamadı."}
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "OpenWeatherMap zaman aşımına uğradı."}
    except Exception as e:
        return {"success": False, "error": str(e)}