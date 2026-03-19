# tools/ip_lookup.py
# Gerçek API: ip-api.com (ücretsiz, key yok)

import requests

def ip_lookup(ip_address: str) -> dict:
    """
    IP adresinin konum ve detay bilgilerini getirir.
    """
    try:
        url = f"http://ip-api.com/json/{ip_address}?lang=tr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "fail":
            return {
                "success": False,
                "error": f"'{ip_address}' geçersiz veya özel bir IP adresi."
            }

        return {
            "success": True,
            "ip": ip_address,
            "country": data.get("country", "Bilinmiyor"),
            "city": data.get("city", "Bilinmiyor"),
            "region": data.get("regionName", "Bilinmiyor"),
            "isp": data.get("isp", "Bilinmiyor"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
            "timezone": data.get("timezone", "Bilinmiyor"),
            "is_vpn": False
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "ip-api.com zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}