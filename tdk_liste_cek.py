import requests

DOSYALAR = [
    "a.list", "b.list", "c.list", "ç.list", "d.list", "e.list",
    "f.list", "g.list",
    "h.list", "ı.list", "i.list",
    "j.list", "k.list", "l.list", "m.list", "n.list", "o.list",
    "ö.list", "p.list", "r.list", "s.list", "ş.list", "t.list",
    "u.list", "ü.list", "v.list", "y.list", "z.list"
]

BASE_URL = "https://raw.githubusercontent.com/CanNuhlar/Turkce-Kelime-Listesi/master/"

TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")


def turkce_buyuk_harf(kelime):
    ceviri = str.maketrans({
        "i": "İ",
        "ı": "I",
        "ş": "Ş",
        "ğ": "Ğ",
        "ü": "Ü",
        "ö": "Ö",
        "ç": "Ç",
    })
    return kelime.translate(ceviri).upper()


def temizle(kelime):
    kelime = kelime.strip()

    # Boşluklu kelimeleri ele.
    # Örn: "bacak kalemi" -> BACAKKALEMI yapılmayacak.
    if " " in kelime:
        return None

    # Tireli, noktalı, kesmeli kelimeleri ele.
    yasakli_karakterler = ["-", "'", "’", ".", ",", "/", "(", ")", "[", "]"]
    for karakter in yasakli_karakterler:
        if karakter in kelime:
            return None

    kelime = turkce_buyuk_harf(kelime)

    for karakter in kelime:
        if karakter not in TURKCE_HARFLER:
            return None

    if len(kelime) < 2 or len(kelime) > 15:
        return None

    return kelime


def main():
    tum_kelimeler = set()

    for dosya_adi in DOSYALAR:
        url = BASE_URL + dosya_adi
        print(f"İndiriliyor: {url}")

        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 404:
                print(f"  Dosya bulunamadı, atlandı: {dosya_adi}")
                continue

            response.raise_for_status()

        except Exception as hata:
            print(f"  Hata oldu, atlandı: {hata}")
            continue

        satirlar = response.text.splitlines()
        onceki = len(tum_kelimeler)

        for satir in satirlar:
            kelime = temizle(satir)
            if kelime:
                tum_kelimeler.add(kelime)

        print(f"  + {len(tum_kelimeler) - onceki} yeni kelime. Toplam: {len(tum_kelimeler)}")

    sirali = sorted(tum_kelimeler, key=lambda x: (len(x), x))

    with open("kelimeler.txt", "w", encoding="utf-8") as dosya:
        for kelime in sirali:
            dosya.write(kelime + "\n")

    print(f"\nBitti kanka. kelimeler.txt içine {len(sirali)} kelime yazıldı.")


main()