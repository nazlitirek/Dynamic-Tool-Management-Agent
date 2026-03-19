# tools/currency.py
# Gerçek API: Frankfurter.app (ücretsiz, key yok, güncel kurlar)

import requests

def currency_converter(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    Döviz birimleri arasında güncel kurlarla dönüşüm yapar.
    """
    try:
        url = f"https://api.frankfurter.app/latest"
        params = {
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "amount": amount
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "rates" not in data:
            return {
                "success": False,
                "error": "Kur bilgisi alınamadı."
            }

        converted = data["rates"][to_currency.upper()]
        rate = round(converted / amount, 4)

        return {
            "success": True,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "original_amount": amount,
            "converted_amount": round(converted, 4),
            "exchange_rate": rate,
            "date": data.get("date", "")
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Frankfurter API zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}