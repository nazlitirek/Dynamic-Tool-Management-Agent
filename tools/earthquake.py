# tools/earthquake.py
# Gerçek API: USGS Earthquake Hazards Program (ücretsiz, key yok)

import requests
from datetime import datetime, timedelta

def get_earthquakes(min_magnitude: float = 3.0, limit: int = 5) -> dict:
    """
    Son depremleri USGS API'dan getirir.
    """
    try:
        # Son 7 günün depremlerini getir
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)

        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "starttime": start_time.strftime("%Y-%m-%d"),
            "endtime": end_time.strftime("%Y-%m-%d"),
            "minmagnitude": min_magnitude,
            "limit": limit,
            "orderby": "magnitude"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        earthquakes = []
        for feature in data["features"]:
            props = feature["properties"]
            coords = feature["geometry"]["coordinates"]
            magnitude = props["mag"]
            place = props["place"]
            time_ms = props["time"]
            time_str = datetime.utcfromtimestamp(time_ms / 1000).strftime("%Y-%m-%d %H:%M")

            earthquakes.append({
                "magnitude": magnitude,
                "location": place,
                "depth_km": round(coords[2], 1),
                "time": time_str,
                "severity": "Hafif" if magnitude < 4 else "Orta" if magnitude < 5 else "Güçlü"
            })

        return {
            "success": True,
            "count": len(earthquakes),
            "min_magnitude": min_magnitude,
            "earthquakes": earthquakes
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "USGS API zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}