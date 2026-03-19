# tools/world_clock.py

from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

geolocator = Nominatim(user_agent="DynamicToolAgent/1.0")
tf = TimezoneFinder()

def get_world_time(city: str) -> dict:
    """
    Dünyanın herhangi bir şehrinin yerel saatini döndürür.
    Gerçek API: Nominatim (OpenStreetMap) + TimezoneFinder
    """
    try:
        # Şehri koordinata çevir
        location: Location | None = geolocator.geocode(city, timeout=10)  # type: ignore

        if not location:
            return {
                "success": False,
                "error": f"'{city}' şehri bulunamadı."
            }

        # Koordinattan timezone bul
        raw = dict(location.raw)
        lat = raw.get("lat")
        lon = raw.get("lon")

        if not lat or not lon:
            return {
                "success": False,
                "error": f"'{city}' için koordinat bulunamadı."
            }

        tz_name = tf.timezone_at(lat=float(lat), lng=float(lon))

        if not tz_name:
            return {
                "success": False,
                "error": f"'{city}' için timezone bulunamadı."
            }

        tz = pytz.timezone(tz_name)
        local_time = datetime.now(tz)

        return {
            "success": True,
            "city": city,
            "timezone": tz_name,
            "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": local_time.strftime("%A"),
            "utc_offset": local_time.strftime("%z")
        }

    except Exception as e:
        return {"success": False, "error": str(e)}