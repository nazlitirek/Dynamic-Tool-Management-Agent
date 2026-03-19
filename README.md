# Dynamic Tool Management Agent

Büyük ölçekli sistemlerde araç yönetimi sorununu çözen, dinamik araç keşfi yapan bir AI agent prototipi.

## Sistem Mimarisi

### Temel Fikir
Geleneksel LLM sistemlerinde tüm araçlar baştan system prompt'a yazılır. 100+ araç olunca context window dolar, model yavaşlar ve her yeni araç eklenince kod değiştirmek gerekir.

Bu sistemde **Main Agent başlangıçta hiçbir aracı bilmez.** İhtiyaç duyunca Tool Manager'a sorar, araçları öğrenir ve kullanır.

### Bileşenler

**1. Tool Registry (`tool_registry.py`)**
Tüm araçların meta verisini tutan merkezi kayıt sistemi. Her araç şu bilgileri içerir:
- `name` — araç adı
- `description` — ne yaptığının açıklaması
- `category` — araç kategorisi (keyword filter için)
- `tags` — anahtar kelimeler (keyword filter için)
- `parameters` — JSON Schema formatında parametre tanımı

Yeni araç eklemek için sadece `add_tool()` çağrılır. Sistemin geri kalanında hiçbir değişiklik gerekmez.

Sistemde şu an 11 araç kayıtlıdır:

1. **`get_weather`**: Belirtilen şehrin sıcaklık, nem, rüzgar hızı ve hava durumu bilgisini getirir. OpenWeatherMap API kullanılmıştır. ✅ Gerçek

2. **`get_earthquakes`**: Son depremleri büyüklük, konum, derinlik ve zaman bilgisiyle listeler. USGS Earthquake Hazards API kullanılmıştır. ✅ Gerçek

3. **`get_stock_price`**: Hisse senedi ve kripto para birimlerinin anlık fiyat, değişim ve yüzde bilgisini getirir. Yahoo Finance API kullanılmıştır. ✅ Gerçek

4. **`currency_converter`**: Döviz birimleri arasında güncel kurlarla dönüşüm yapar. Frankfurter API kullanılmıştır. ✅ Gerçek

5. **`get_news`**: Belirtilen konuda güncel haber başlıklarını ve kaynaklarını listeler. NewsAPI kullanılmıştır. ✅ Gerçek

6. **`get_world_time`**: Dünyanın herhangi bir şehrinin yerel saatini ve saat dilimini döndürür. Nominatim (OpenStreetMap) ve TimezoneFinder kütüphanesi kullanılmıştır. ✅ Gerçek

7. **`search_wikipedia`**: Verilen konu için Wikipedia'dan özet bilgi ve sayfa bağlantısı getirir. Wikipedia REST API kullanılmıştır. ✅ Gerçek

8. **`ip_lookup`**: Bir IP adresinin ülke, şehir, bölge ve internet servis sağlayıcı bilgilerini getirir. ip-api.com kullanılmıştır. ✅ Gerçek

9. **`execute_code`**: Python kodu çalıştırarak matematiksel hesaplamalar ve algoritmalar uygular. Python'un yerleşik `exec()` fonksiyonu kullanılmıştır. ✅ Gerçek

10. **`get_movie_info`**: Film ve dizi hakkında yönetmen, tür, puan ve süre bilgisi döndürür. Mock veri kullanılmaktadır. 🟡 Mock

11. **`get_joke`**: Türkçe programlama, bilim ve genel kategorilerde şaka getirir. Mock veri kullanılmaktadır. 🟡 Mock

**2. Tool Manager (`tool_manager.py`)**
3 katmanlı araç arama servisi. Her katman bir öncekinin çıktısını alır ve filtreler.

### Katman 1 — Keyword Filter
Sorgu kelimelerini araçların `tags` ve `category` alanlarıyla karşılaştırır. Basit string eşleştirmesi yaparak 100 araçtan ilgili ~5-10 aracı seçer. Hızlı ve API çağrısı gerektirmez.

Katman 1 boş liste döndürürse sistem durmaz — Katman 2 devreye girer. Bunun nedeni şudur: kullanıcı "coğrafi konum sorgula" gibi tag'larda olmayan bir ifade kullanmış olabilir ama semantik olarak `ip_lookup` aracıyla eşleşebilir.

### Katman 2 — Semantic Search
ChromaDB ve `sentence-transformers` kullanarak embedding benzerliği yapar.

- Katman 1'den aday geldiyse **sadece o adaylar arasında** arama yapar
- Katman 1'den hiç aday gelmadiyse **tüm araç koleksiyonunda** arama yapar

Bu sayede Katman 1'in kaçırdığı araçlar semantik benzerlikle yakalanabilir.

Katman 2'den boş liste gelirse Katman 3'e boş liste iletilir.

### Katman 3 — LLM Reranker
Groq API üzerinden Llama 3.3 70B modelini kullanarak nihai kararı verir.

- Katman 2'den **boş liste** gelirse direkt `[]` döndürür — **API çağrısı yapılmaz**
- Katman 2'den aday geldiyse Claude'a sorar: "Bu görev için hangisi gerçekten gerekli?"
- False positive'leri eler, alakasız araçları çıkarır

**3. Main Agent (`main_agent.py`)**
Zero-knowledge başlayan ana ajan. System prompt'unda hiçbir araç tanımı yoktur. Görevi alır, tool_search ile araçları keşfeder ve kullanır.

### False Positive Yönetimi

Sadece semantic search kullanan sistemlerde "uçak bileti ara" sorgusuna `get_weather` gibi alakasız araçlar gelebilir. Bunu engellemek için 3 katmanlı filtre:

1. Keyword filter önce büyük havuzu küçültür
2. Semantic search anlamsal benzerliği kullanır
3. LLM Reranker nihai kararı verir ve alakasız araçları eler

📈 METRİKLER
=================================================================
Toplam test        : 20 (10 pozitif, 10 negatif)
True Positive      : 10   (doğru araç bulundu)
False Positive     : 0   (yanlış araç önerildi)
False Negative     : 0   (araç bulunması gerekirken bulunmadı)
True Negative      : 10   (gereksiz araç önerilmedi)
Precision          : %100.0  (bulunanların ne kadarı doğru)
Recall             : %100.0  (doğruların ne kadarı bulundu)
False Positive Rate: %0.0  (negatif sorularda yanlış öneri oranı)

## Kurulum

### Gereksinimler
- Python 3.12+
- Groq API key (ücretsiz — console.groq.com)

### Adımlar
```bash
# 1. Repoyu klonla
git clone https://github.com/kullanici/dynamic-tool-agent
cd dynamic-tool-agent

# 2. Virtual environment oluştur
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Bağımlılıkları kur
pip install -r requirements.txt

# 4. .env dosyası oluştur
echo GROQ_API_KEY=buraya_keyini_yaz > .env
echo NEWS_API_KEY=buraya_keyini_yaz > .env
echo OPENWEATHER_API_KEY=buraya_keyini_yaz > .env

# 5. Çalıştır
python main.py
```

### Gerekli Paketler
```
chromadb
sentence-transformers
python-dotenv
pytz
groq
requests

```

## Kullanım

### Temel Kullanım
```python
from tool_manager import build_index
from main_agent import run_agent

build_index()  # Araçları index'e ekle (bir kez çalışır)
result = run_agent("İstanbul'un hava durumu nasıl?")
```

### Yeni Araç Ekleme
```python
from tool_registry import add_tool

add_tool({
    "name": "translate_text",
    "description": "Metni istenen dile çevirir.",
    "category": ["language", "translation"],
    "tags": ["çeviri", "dil", "translate"],
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Çevrilecek metin"},
            "target_language": {"type": "string", "description": "Hedef dil"}
        },
        "required": ["text", "target_language"]
    }
})
```

Sistemin geri kalanında hiçbir değişiklik yapmana gerek yok.

## Örnek Çıktılar

### Senaryo 1 
```
👤 Kullanıcı: Teknoloji haberleri neler?
============================================================

🔧 Araç çağrısı: tool_search({'query': 'teknoloji haberleri'})        

🔍 Araç aranıyor: 'teknoloji haberleri'
  [Katman 1] 'teknoloji haberleri' → 1 araç kaldı: ['get_news']       
  [Katman 2] Semantic search → ['get_news']
  [Katman 3] LLM Reranker → ['get_news']
  ✓ Sonuç: ['get_news']

  ✓ tool_search sonucu: ['get_news']
  ⚠️ API hatası, tekrar deneniyor (1/3)...

🔧 Araç çağrısı: get_news({'limit': 5, 'topic': 'teknoloji'})
  ✓ get_news sonucu alındı

🤖 Agent: Son dakika teknoloji haberleri için bazı güncel haberler şunlardır:
- Elon Musk'ın annesi İstanbul'da.
- İran'ın kilit ismi Ali Laricani kimdir? İsrail'in saldırısında öldürüldü.
- Şarj istasyonu ayağınıza geliyor: Çin’den mobil robot çözümü.       
- Güçlü ama şaşkın.
- İstanbul Spor Etkinlikleri Ve İşletmeciliği Ticaret Anonim Şirketi Genel Müdürlüğü.
```

### Senaryo 2 
```
👤 Kullanıcı: 100 dolar kaç türk lirası eder?
============================================================
  ⚠️ API hatası, tekrar deneniyor (1/3)...

🔧 Araç çağrısı: tool_search({'query': 'döviz kuru öğrenme'})

🔍 Araç aranıyor: 'döviz kuru öğrenme'
  [Katman 1] 'döviz kuru öğrenme' → 1 araç kaldı: ['currency_converter']
  [Katman 2] Semantic search → ['currency_converter']
  [Katman 3] LLM Reranker → ['currency_converter']
  ✓ Sonuç: ['currency_converter']

  ✓ tool_search sonucu: ['currency_converter']

🔧 Araç çağrısı: currency_converter({'amount': 100, 'from_currency': 'USD', 'to_currency': 'TRY'})
  ✓ currency_converter sonucu alındı

🤖 Agent: 100 dolar approximately 4421.74 türk lirasına eşittir. 
```

### Senaryo 3 — Başarısız
```
👤 Kullanıcı: Bana uçak bileti bul
============================================================

🔧 Araç çağrısı: tool_search({'query': 'uçak bileti bulma'})

🔍 Araç aranıyor: 'uçak bileti bulma'
  [Katman 1] 'uçak bileti bulma' → 0 araç kaldı: []
  [Katman 2] Semantic search → ['search_wikipedia', 'get_joke', 'get_movie_info', 'get_news', 'get_world_time']
  [Katman 3] LLM Reranker → []
  ✓ Sonuç: []


🤖 Agent: Bu görev için uygun araç bulunamadığından, uçak bileti bulma işlemi gerçekleştirilemiyor.


### Senaryo 4 — Başarısız
```
============================================================
  ⚠️ API hatası, tekrar deneniyor (1/3)...

🔧 Araç çağrısı: tool_search({'query': "Spotify'da şarkı açma"})      

🔍 Araç aranıyor: 'Spotify'da şarkı açma'
  [Katman 1] 'Spotify'da şarkı açma' → 0 araç kaldı: []
  [Katman 2] Semantic search → ['search_wikipedia', 'get_movie_info', 'get_joke', 'get_weather', 'get_stock_price']
  [Katman 3] LLM Reranker → []
  ✓ Sonuç: []


🔧 Araç çağrısı: tool_search({'query': "Spotify'da şarkı açma"})      

🔍 Araç aranıyor: 'Spotify'da şarkı açma'
  [Katman 1] 'Spotify'da şarkı açma' → 0 araç kaldı: []
  [Katman 2] Semantic search → ['search_wikipedia', 'get_movie_info', 'get_joke', 'get_weather', 'get_stock_price']
  [Katman 3] LLM Reranker → []
  ✓ Sonuç: []


🤖 Agent: Bu görev için uygun araç bulunamadı. Spotify'da şarkı açmak için gereken araçları keşfedemeyince bunu yapamıyorum.
```


## Proje Yapısı
```
dynamic-tool-agent/
├── tools/
│   ├── __init__.py
│   ├── weather.py
│   ├── earthquake.py
│   ├── stock.py
│   ├── movie.py
│   ├── ip_lookup.py
│   ├── news.py
│   ├── joke.py
│   ├── world_clock.py
│   ├── wikipedia.py
│   ├── currency.py
│   └── calculator.py
├── tool_registry.py
├── tool_manager.py
├── main_agent.py
├── main.py
├── test_false_positive.py
├── requirements.txt
└── .env
```

## Genişletilebilirlik

105. aracı eklemek için sadece `tool_registry.py`'ye yeni bir entry eklemek yeterli. Sistem otomatik olarak:
- Yeni aracı embedding'e çevirir
- ChromaDB'ye ekler
- Keyword filter'a dahil eder
- Main Agent'ın keşfedebileceği hale getirir

Hiçbir prompt değişikliği, hiçbir kod düzenlemesi gerekmez.