# tool_registry.py

TOOLS = [
    {
        "name": "get_weather",
        "description": "Belirli bir şehrin güncel hava durumunu getirir. Sıcaklık, nem, rüzgar bilgisi döndürür.",
        "category": ["weather", "location"],
        "tags": ["hava", "sıcaklık", "nem", "rüzgar", "hava durumu", "weather"],
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Şehir adı, örnek: İstanbul"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_earthquakes",
        "description": "Son depremleri büyüklük ve konum bilgisiyle listeler.",
        "category": ["disaster", "location", "news"],
        "tags": ["deprem", "sarsıntı", "afet", "büyüklük", "richter", "earthquake"],
        "parameters": {
            "type": "object",
            "properties": {
                "min_magnitude": {
                    "type": "number",
                    "description": "Minimum deprem büyüklüğü, örnek: 3.0"
                },
                "limit": {
                    "type": "integer",
                    "description": "Kaç deprem listeleneceği, örnek: 5"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_stock_price",
        "description": "Hisse senedi veya kripto para fiyatını getirir. Borsa verileri döndürür.",
        "category": ["finance", "stock"],
        "tags": ["hisse", "borsa", "fiyat", "yatırım", "kripto", "bitcoin", "stock", "bist"],
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Hisse senedi sembolü, örnek: THYAO, AAPL, BTC"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_movie_info",
        "description": "Film veya dizi hakkında bilgi getirir. Yönetmen, puan, tür, süre bilgisi döndürür.",
        "category": ["entertainment", "media"],
        "tags": ["film", "dizi", "sinema", "yönetmen", "imdb", "movie", "puan"],
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Film veya dizi adı, örnek: Inception"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "ip_lookup",
        "description": "Bir IP adresinin hangi ülke, şehir ve internet sağlayıcısına ait olduğunu gösterir.",
        "category": ["network", "location"],
        "tags": ["ip", "konum", "ülke", "şehir", "isp", "vpn", "network", "adres", "192", "lookup"],
        "parameters": {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "Sorgulanacak IP adresi, örnek: 192.168.1.1"
                }
            },
            "required": ["ip_address"]
        }
    },
    {
        "name": "get_news",
        "description": "Belirli bir konuda güncel haberleri listeler.",
        "category": ["news", "search"],
        "tags": ["haber", "güncel", "gazete", "manşet", "news", "medya"],
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Haber konusu, örnek: teknoloji, spor, ekonomi"
                },
                "limit": {
                    "type": "integer",
                    "description": "Kaç haber getirileceği, örnek: 5"
                }
            },
        "limit": {
        "type": "integer",
        "description": "Kaç haber getirileceği, örnek: 5",
        "default": 5
        },
            "required": ["topic"]
        }
    },
    {
        "name": "get_joke",
        "description": "Rastgele komik şaka veya bilmece getirir.",
        "category": ["entertainment", "fun"],
        "tags": ["şaka", "komedi", "eğlence", "bilmece", "joke", "gülmece", "fıkra", "espri"],
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Şaka kategorisi: 'general' veya 'science'",
                    "enum": ["general", "science"]
                }
            },
            "required": []
        }
    },
    {
        "name": "get_world_time",
        "description": "Dünyanın herhangi bir şehrinin yerel saatini ve tarihini döndürür.",
        "category": ["utility", "time", "location"],
        "tags": ["saat", "zaman", "tarih", "saat dilimi", "timezone", "world clock"],
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Şehir adı, örnek: Istanbul, London, Tokyo"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "search_wikipedia",
        "description": "Wikipedia'da konu arar ve özet bilgi döndürür.",
        "category": ["search", "knowledge"],
        "tags": ["wikipedia", "ansiklopedi", "bilgi", "araştırma", "özet", "wiki", 
         "dağ", "tarih", "coğrafya", "bilim", "kim", "ne", "nedir", "hangi"],        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak konu, örnek: Albert Einstein"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "currency_converter",
        "description": "Döviz ve kripto para birimleri arasında güncel kurlarla dönüşüm yapar.",
        "category": ["finance", "currency"],
        "tags": ["döviz", "kur", "para", "dolar", "euro", "lira", "kripto", "currency"],
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Dönüştürülecek miktar"
                },
                "from_currency": {
                    "type": "string",
                    "description": "Kaynak para birimi, örnek: USD"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Hedef para birimi, örnek: TRY"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    },
    {
        "name": "execute_code",
        "description": "Python kodu yazarak karmaşık matematiksel hesaplamalar yapar.",
        "category": ["compute", "math"],
        "tags": ["hesap", "matematik", "python", "kod", "hesaplama", "compute"],
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Çalıştırılacak Python kodu. Sonucu 'result' değişkenine ata."
                }
            },
            "required": ["code"]
        }
    }
]

def get_all_tools():
    """Tüm araçları döndürür."""
    return TOOLS

def get_tool_by_name(name: str):
    """İsme göre araç getirir."""
    for tool in TOOLS:
        if tool["name"] == name:
            return tool
    return None

def add_tool(tool: dict):
    """
    Yeni araç ekler.
    Sistemi yeniden başlatmaya gerek yok — dinamik yapı.
    """
    TOOLS.append(tool)
    print(f"✓ Yeni araç eklendi: {tool['name']}")