# tools/joke.py

import random

def get_joke(category: str = "general") -> dict:
    """
    Rastgele Türkçe şaka getirir.
    """
    jokes = {
        "general": [
            {"setup": "Programcı neden güneşe bakmaz?", "punchline": "Çünkü Windows açık!"},
            {"setup": "Python neden terapiste gitti?", "punchline": "Çünkü çok fazla indentation sorunu vardı."},
            {"setup": "Veritabanı neden üzgündü?", "punchline": "Çünkü bütün ilişkileri JOIN'di."},
            {"setup": "Yazılımcı neden evlenmez?", "punchline": "Çünkü her ilişkide bug çıkıyor."},
            {"setup": "Git kullanıcısı neden sakin?", "punchline": "Çünkü her şeyi commit'ledi."},
            {"setup": "Yazılımcı neden mutfağa girmez?", "punchline": "Çünkü çorba yaparken stack overflow oluyor."},
            {"setup": "Neden yazılımcılar gözlüklü olur?", "punchline": "Çünkü C# ile çalışıyorlar."},
            {"setup": "Bir yazılımcı markete gider, eşi der ki: '1 ekmek al, yumurta varsa 6 tane al.'", "punchline": "Yazılımcı 6 ekmek alır. Çünkü yumurta vardı."},
        ],
        "science": [
            {"setup": "Atom neden güvenilmez?", "punchline": "Çünkü her şeyi onlar oluşturur!"},
            {"setup": "Schrödinger'in kedisi bara girdi.", "punchline": "Ve girmedi."},
            {"setup": "Işık hızında giden arabanın farlarını açsak ne olur?", "punchline": "Hiçbir şey. Çünkü ışık zaten orada."},
            {"setup": "Newton elma ağacının altında uyurken ne düşündü?", "punchline": "Hiçbir şey, elma kafasına düştü."},
            {"setup": "Kimyacı neden iyi aşçıdır?", "punchline": "Çünkü her şeyin formülünü biliyor."},
            {"setup": "Fizikçi neden üzgündü?", "punchline": "Çünkü potansiyel enerjisi vardı ama kinetik enerjisi yoktu."},
            {"setup": "Matematikçi neden ormanda kayboldu?", "punchline": "Çünkü pi'nin sonu yoktu."},
            {"setup": "Einstein neden kötü öğrenciydi?", "punchline": "Çünkü her şeyi göreceli buluyordu."},
        ],
        "programming": [
            {"setup": "Java geliştiricisi kafeterya'ya gider ne der?", "punchline": "'Bir büyük, yavaş, ağır kahve lütfen.'"},
            {"setup": "Recursive fonksiyon neden terapiste gitti?", "punchline": "Çünkü kendini çağırmaktan bıktı."},
            {"setup": "Frontend developer neden üzgün?", "punchline": "Çünkü hayatı CSS gibi — her şey görünüşe göre."},
            {"setup": "Backend developer neden mutlu?", "punchline": "Çünkü kimse ne yaptığını görmüyor."},
            {"setup": "Neden programcılar karanlıktan korkmaz?", "punchline": "Çünkü dark mode'da çalışıyorlar."},
            {"setup": "Bir programcı eşine 'Seni sonsuz döngü kadar seviyorum' dedi.", "punchline": "Eşi: 'Bu hiç bitmeyecek mi?'"},
            {"setup": "Neden yazılımcılar her zaman soğuk alır?", "punchline": "Çünkü Windows açık bırakıyorlar."},
            {"setup": "Stack Overflow neden evlendi?", "punchline": "Çünkü her sorusuna cevap buldu."},
        ]
    }

    selected = jokes.get(category, jokes["general"])
    joke = random.choice(selected)

    return {
        "success": True,
        "category": category,
        "setup": joke["setup"],
        "punchline": joke["punchline"]
    }