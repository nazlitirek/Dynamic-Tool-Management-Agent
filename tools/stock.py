# tools/stock.py
# Gerçek API: Yahoo Finance (ücretsiz, key yok)

import requests

def get_stock_price(symbol: str) -> dict:
    """
    Hisse senedi veya kripto para fiyatını getirir.
    """
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()

        result = data["chart"]["result"]
        if not result:
            return {"success": False, "error": f"'{symbol}' sembolü bulunamadı."}

        meta = result[0]["meta"]
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("previousClose") or meta.get("chartPreviousClose")

        if price is None or prev_close is None:
            return {"success": False, "error": f"'{symbol}' için fiyat verisi alınamadı."}

        change = round(price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2)

        return {
            "success": True,
            "symbol": symbol.upper(),
            "price": round(price, 2),
            "change": change,
            "change_percent": change_pct,
            "direction": "▲" if change >= 0 else "▼",
            "currency": meta.get("currency", "USD")
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Yahoo Finance zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}