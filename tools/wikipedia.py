# tools/wikipedia.py
import requests
from urllib.parse import quote

def search_wikipedia(query: str) -> dict:
    """
    Wikipedia'da konu arar ve özet bilgi döndürür.
    """
    try:
        headers = {
            "User-Agent": "DynamicToolAgent/1.0 (educational project; contact@example.com)"
        }

        # Önce arama yap
        search_url = "https://tr.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1
        }

        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()

        results = search_data.get("query", {}).get("search", [])
        if not results:
            return {
                "success": False,
                "error": f"'{query}' için Wikipedia'da sonuç bulunamadı."
            }

        page_title = results[0]["title"]

        # Sayfanın özetini getir
        summary_url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{quote(page_title)}"
        summary_response = requests.get(summary_url, headers=headers, timeout=10)
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        return {
            "success": True,
            "query": query,
            "title": summary_data.get("title", page_title),
            "summary": summary_data.get("extract", "Özet bulunamadı."),
            "url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "last_updated": summary_data.get("timestamp", "")[:10]
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Wikipedia API zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}