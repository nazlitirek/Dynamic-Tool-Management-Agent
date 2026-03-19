# test_false_positive.py
# False positive oranını ölçen test scripti — 10 pozitif, 10 negatif

from tool_manager import build_index, search_tools

TEST_CASES = [
    # ✅ POZİTİF SENARYOLAR — araç bulunması bekleniyor
    ("İstanbul'da hava nasıl",           ["get_weather"]),
    ("100 euro kaç dolar eder",          ["currency_converter"]),
    ("Son depremleri göster",            ["get_earthquakes"]),
    ("Teknoloji haberleri getir",        ["get_news"]),
    ("Inception filminin puanı kaç",     ["get_movie_info"]),
    ("Tokyo'da şu an saat kaç",          ["get_world_time"]),
    ("Bana programcı şakası anlat",      ["get_joke"]),
    ("8.8.8.8 IP adresi nerede",         ["ip_lookup"]),
    ("Fibonacci sayılarını hesapla",     ["execute_code"]),
    ("Atatürk hakkında bilgi ver",       ["search_wikipedia"]),

    # ❌ NEGATİF SENARYOLAR — hiçbir araç bulunmamalı
    ("Bana uçak bileti bul",             []),
    ("Pizza tarifi ver",                 []),
    ("Otel rezervasyonu yap",            []),
    ("Şarkı söyle",                      []),
    ("Bana masal anlat",                 []),
    ("Instagram hesabımı aç",            []),
    ("E-posta hesabıma giriş yap",       []),
    ("Araba kiralama fiyatı",            []),
    ("Doktor randevusu al",              []),
    ("Vergi beyannamemi doldur",         []),
]

def run_tests():
    print("🧪 False Positive Testi Başlıyor...\n")
    build_index()
    print()

    true_positive = 0   # Doğru araç bulunan sorgu sayısı
    false_positive = 0  # Yanlış araç önerilen sorgu sayısı
    false_negative = 0  # Araç bulunması gerekirken bulunmayan sorgu sayısı
    true_negative = 0   # Hiç araç önerilmemesi gereken ve önerilmeyen sorgu sayısı

    results = []

    for query, expected_tools in TEST_CASES:
        found_tools = [t["name"] for t in search_tools(query)]

        if not expected_tools:
            # Negatif senaryo — hiçbir araç bulunmamalı
            if not found_tools:
                true_negative += 1
                status = "✅ TN"
            else:
                false_positive += 1  # Kaç araç önerildiğine değil, bu sorgu yanlış sonuç verdi mi
                status = f"❌ FP — bulunan: {found_tools}"
        else:
            # Pozitif senaryo — belirli araçlar bulunmalı
            correct = [t for t in found_tools if t in expected_tools]
            wrong   = [t for t in found_tools if t not in expected_tools]
            missed  = [t for t in expected_tools if t not in found_tools]

            if correct and not wrong and not missed:
                true_positive += 1
                status = "✅ TP"
            elif correct and wrong:
                # Doğru araç bulundu ama yanında yanlış araç da var
                false_positive += 1
                status = f"⚠️  TP+FP — doğru: {correct}, yanlış: {wrong}"
            elif missed and not found_tools:
                false_negative += 1
                status = f"❌ FN — beklenen: {expected_tools}, bulunan: []"
            elif missed:
                false_negative += 1
                status = f"❌ FN — beklenen: {expected_tools}, bulunan: {found_tools}"
            else:
                false_positive += 1
                status = f"❌ FP — bulunan: {found_tools}"

        results.append((query, status))

    # Sonuçları yazdır
    print("\n" + "="*65)
    print("📊 TEST SONUÇLARI")
    print("="*65)
    print(f"{'DURUM':<55} | SORGU")
    print("-"*65)
    for query, status in results:
        print(f"{status:<55} | '{query}'")

    total = len(TEST_CASES)
    precision = true_positive / (true_positive + false_positive) * 100 if (true_positive + false_positive) > 0 else 100
    recall    = true_positive / (true_positive + false_negative) * 100 if (true_positive + false_negative) > 0 else 100
    fp_rate   = false_positive / (false_positive + true_negative) * 100 if (false_positive + true_negative) > 0 else 0

    print("\n" + "="*65)
    print("📈 METRİKLER")
    print("="*65)
    print(f"Toplam test        : {total} ({total//2} pozitif, {total//2} negatif)")
    print(f"True Positive      : {true_positive}   (doğru sonuç veren sorgu)")
    print(f"False Positive     : {false_positive}   (yanlış araç öneren sorgu)")
    print(f"False Negative     : {false_negative}   (araç bulması gerekirken bulmayan sorgu)")
    print(f"True Negative      : {true_negative}   (doğru şekilde araç önermeen sorgu)")
    print(f"Precision          : %{precision:.1f}  (bulunanların ne kadarı doğru)")
    print(f"Recall             : %{recall:.1f}  (doğruların ne kadarı bulundu)")
    print(f"False Positive Rate: %{fp_rate:.1f}  (negatif sorularda yanlış öneri oranı)")
    print("🧪 False Positive Testi Başlıyor...\n")
    build_index()
    print()

    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0

    results = []

    for query, expected_tools in TEST_CASES:
        found_tools = [t["name"] for t in search_tools(query)]

        if not expected_tools:
            # Negatif senaryo — hiçbir araç bulunmamalı
            if not found_tools:
                true_negative += 1
                status = "✅ TN"
            else:
                false_positive += len(found_tools)
                status = f"❌ FP — bulunan: {found_tools}"
        else:
            # Pozitif senaryo — belirli araçlar bulunmalı
            correct = [t for t in found_tools if t in expected_tools]
            wrong   = [t for t in found_tools if t not in expected_tools]
            missed  = [t for t in expected_tools if t not in found_tools]

            true_positive  += len(correct)
            false_positive += len(wrong)
            false_negative += len(missed)

            if correct and not wrong and not missed:
                status = "✅ TP"
            elif correct and wrong:
                status = f"⚠️  TP+FP — doğru: {correct}, yanlış: {wrong}"
            elif missed:
                status = f"❌ FN — beklenen: {expected_tools}, bulunan: {found_tools}"
            else:
                status = f"❌ FP — bulunan: {found_tools}"

        results.append((query, status))

    # Sonuçları yazdır
    print("\n" + "="*65)
    print("📊 TEST SONUÇLARI")
    print("="*65)
    print(f"{'DURUM':<55} | SORGU")
    print("-"*65)
    for query, status in results:
        print(f"{status:<55} | '{query}'")

    total = len(TEST_CASES)
    precision = true_positive / (true_positive + false_positive) * 100 if (true_positive + false_positive) > 0 else 100
    recall    = true_positive / (true_positive + false_negative) * 100 if (true_positive + false_negative) > 0 else 100
    fp_rate   = false_positive / (false_positive + true_negative) * 100 if (false_positive + true_negative) > 0 else 0

    print("\n" + "="*65)
    print("📈 METRİKLER")
    print("="*65)
    print(f"Toplam test        : {total} ({total//2} pozitif, {total//2} negatif)")
    print(f"True Positive      : {true_positive}   (doğru araç bulundu)")
    print(f"False Positive     : {false_positive}   (yanlış araç önerildi)")
    print(f"False Negative     : {false_negative}   (araç bulunması gerekirken bulunmadı)")
    print(f"True Negative      : {true_negative}   (gereksiz araç önerilmedi)")
    print(f"Precision          : %{precision:.1f}  (bulunanların ne kadarı doğru)")
    print(f"Recall             : %{recall:.1f}  (doğruların ne kadarı bulundu)")
    print(f"False Positive Rate: %{fp_rate:.1f}  (negatif sorularda yanlış öneri oranı)")

if __name__ == "__main__":
    run_tests()