# tools/movie.py

import random

def get_movie_info(title: str) -> dict:
    """
    Film veya dizi bilgisi getirir.
    Şu an mock veri döndürüyor.
    Gerçek API: OMDB API (ücretsiz key)
    """
    genres = ["Aksiyon", "Drama", "Komedi", "Korku", "Bilim Kurgu", "Animasyon"]
    directors = ["Christopher Nolan", "Steven Spielberg", "Quentin Tarantino", "Martin Scorsese"]
    
    return {
        "success": True,
        "title": title,
        "year": random.randint(1990, 2024),
        "genre": random.choice(genres),
        "director": random.choice(directors),
        "rating": round(random.uniform(5.0, 9.5), 1),
        "duration_min": random.randint(85, 180),
        "description": f"'{title}' filmi hakkında detaylı bilgi.",
        "awards": random.choice(["Oscar Adayı", "Altın Küre Kazananı", "Ödül yok", "BAFTA Adayı"])
    }