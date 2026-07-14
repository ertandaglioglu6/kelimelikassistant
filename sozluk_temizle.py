from shutil import copyfile


DOSYA_ADI = "kelimeler.txt"
YEDEK_DOSYA_ADI = "kelimeler_yedek.txt"

TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")

# Şimdilik izin verdiğimiz güvenli 2 harfli kelimeler
IZINLI_2_HARFLI_KELIMELER = {
    "AB", "AD", "AH", "AK", "AL", "AM", "AN", "AR", "AS", "AT", "AV", "AY", "AZ",
    "BU", "Çİ",
    "ED", "EH", "EK", "EL", "EM", "EN", "ER", "ES", "ET", "EV", "EY",
    "FA",
    "HA", "HE", "HU",
    "IR", "IS",
    "İÇ", "İL", "İN", "İP", "İR", "İS", "İŞ", "İT", "İZ",
    "KA", "KE", "Kİ",
    "LA", "LE",
    "MI", "Mİ", "MU", "MÜ",
    "NE",
    "OD", "OF", "OH", "OK", "OL", "OM", "ON", "OR", "OT", "OV", "OY", "OZ",
    "ÖÇ", "ÖF", "ÖN", "ÖZ",
    "PA", "PE",
    "RA",
    "SA", "SE", "SI", "Sİ", "SU",
    "TA", "TE", "TI", "Tİ", "TU",
    "UN",
    "ÜÇ", "ÜF", "ÜN",
    "YA", "YE", "YI",
}


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


def kelime_gecerli_mi(kelime):
    kelime = kelime.strip()

    if not kelime:
        return False

    # Boşluklu kelimeler kalmasın
    if " " in kelime:
        return False

    # Tireli, noktalı, kesmeli şeyler kalmasın
    yasakli_karakterler = ["-", "'", "’", ".", ",", "/", "(", ")", "[", "]", ":", ";"]
    for karakter in yasakli_karakterler:
        if karakter in kelime:
            return False

    kelime = turkce_buyuk_harf(kelime)

    # Sadece Türkçe harflerden oluşsun
    for karakter in kelime:
        if karakter not in TURKCE_HARFLER:
            return False

    # Kelimelik tahtası 15x15
    if len(kelime) < 2 or len(kelime) > 15:
        return False

    # En kritik temizlik:
    # 2 harfli kelimelerde sadece izin verdiklerimiz kalsın
    if len(kelime) == 2 and kelime not in IZINLI_2_HARFLI_KELIMELER:
        return False

    return True


def main():
    print("Sözlük temizleniyor...")

    copyfile(DOSYA_ADI, YEDEK_DOSYA_ADI)
    print(f"Yedek oluşturuldu: {YEDEK_DOSYA_ADI}")

    temiz_kelimeler = set()
    silinen_sayi = 0

    with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
        for satir in dosya:
            kelime = turkce_buyuk_harf(satir.strip())

            if kelime_gecerli_mi(kelime):
                temiz_kelimeler.add(kelime)
            else:
                silinen_sayi += 1

    sirali = sorted(temiz_kelimeler, key=lambda x: (len(x), x))

    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        for kelime in sirali:
            dosya.write(kelime + "\n")

    print(f"Temiz kelime sayısı: {len(sirali)}")
    print(f"Silinen satır sayısı: {silinen_sayi}")
    print("Bitti kanka. kelimeler.txt temizlendi.")


main()