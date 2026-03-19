# tools/news.py
# Gerçek API: NewsAPI (ücretsiz key)

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

def get_news(topic: str, limit: int = 5) -> dict:
    """
    Belirli bir konuda güncel haberleri getirir.
    """
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic,
            "apiKey": API_KEY,
            "pageSize": limit,
            "language": "tr",
            "sortBy": "publishedAt"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            return {
                "success": False,
                "error": data.get("message", "Haber getirilemedi.")
            }

        articles = data.get("articles", [])

        if not articles:
            return {
                "success": False,
                "error": f"'{topic}' konusunda haber bulunamadı."
            }

        news = []
        for article in articles:
            news.append({
                "headline": article.get("title", "Başlık yok"),
                "source": article.get("source", {}).get("name", "Bilinmiyor"),
                "published_at": article.get("publishedAt", "")[:16].replace("T", " "),
                "url": article.get("url", "")
            })

        return {
            "success": True,
            "topic": topic,
            "count": len(news),
            "news": news
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "NewsAPI zaman aşımına uğradı."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"API hatası: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}