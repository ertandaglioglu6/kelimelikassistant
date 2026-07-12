import time
from collections import Counter
from tahta import tahta_yazdir
from solver import hamleleri_bul, hamleyi_tahtada_goster


HARF_PUANLARI = {
    "A": 1, "E": 1, "İ": 1, "K": 1, "L": 1, "R": 1, "N": 1, "T": 1,
    "I": 2, "M": 2, "O": 2, "S": 2, "U": 2,
    "B": 3, "D": 3, "Ü": 3, "Y": 3,
    "C": 4, "Ç": 4, "Ş": 4, "Z": 4,
    "G": 5, "H": 5, "P": 5,
    "F": 7, "Ö": 7, "V": 7,
    "Ğ": 8,
    "J": 10,
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


def sozluk_yukle(dosya_yolu):
    kelimeler = set()

    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        for satir in dosya:
            kelime = turkce_buyuk_harf(satir.strip())

            if kelime and len(kelime) <= 15:
                kelimeler.add(kelime)

    return kelimeler


def kelime_yapilabilir_mi(kelime, harfler):
    kelime_sayac = Counter(kelime)
    harf_sayac = Counter(harfler)

    for harf, adet in kelime_sayac.items():
        if harf_sayac[harf] < adet:
            return False

    return True


def puan_hesapla(kelime):
    toplam = 0

    for harf in kelime:
        toplam += HARF_PUANLARI.get(harf, 0)

    return toplam


def tahta_girisi_al():
    print("\nGüncel tahtayı 15 satır halinde gir.")
    print("Boş kareler için . kullan.")
    print("Örnek satır: .......KALE....")
    print()

    tahta = []

    for satir_no in range(15):
        while True:
            satir = input(f"{satir_no}. satır: ")
            satir = turkce_buyuk_harf(satir.strip().replace(" ", ""))

            if len(satir) != 15:
                print("Hata: Her satır tam 15 karakter olmalı kanka.")
                continue

            tahta_satiri = []
            hatali_karakter_var = False

            for karakter in satir:
                if karakter == ".":
                    tahta_satiri.append(".")
                elif karakter in HARF_PUANLARI:
                    tahta_satiri.append(karakter)
                else:
                    print(f"Hata: Geçersiz karakter var: {karakter}")
                    hatali_karakter_var = True
                    break

            if hatali_karakter_var:
                continue

            tahta.append(tahta_satiri)
            break

    return tahta


def main():
    sozluk = sozluk_yukle("kelimeler.txt")
    print(f"{len(sozluk)} kelime yüklendi.")

    tahta = tahta_girisi_al()

    print("\nGirdiğin tahta:")
    tahta_yazdir(tahta)

    eldeki_harfler = input("\nElindeki harfleri yaz: ")
    eldeki_harfler = turkce_buyuk_harf(eldeki_harfler.replace(" ", ""))

    print("\nHamleler aranıyor...")

    baslangic = time.time()

    hamleler = hamleleri_bul(tahta, sozluk, eldeki_harfler, puan_hesapla)

    bitis = time.time()
    gecen_sure = bitis - baslangic

    print(f"\n{len(hamleler)} hamle bulundu.")
    print(f"Arama süresi: {gecen_sure:.2f} saniye\n")

    for index, hamle in enumerate(hamleler[:10], start=1):
        kullanilan_harfler = hamle.get("kullanilan_harfler", "")

        print(
            f"{index}. {hamle['kelime']} - "
            f"Satır: {hamle['satir']}, "
            f"Sütun: {hamle['sutun']}, "
            f"Yön: {hamle['yon']}, "
            f"Puan: {hamle['puan']}, "
            f"Kullanılan: {kullanilan_harfler}"
        )

    if hamleler:
        en_iyi_hamle = hamleler[0]

        print("\nEn iyi hamlenin tahtadaki görünümü:")
        yeni_tahta = hamleyi_tahtada_goster(tahta, en_iyi_hamle)
        tahta_yazdir(yeni_tahta)
    else:
        print("Uygun hamle bulunamadı.")


    if __name__ == "__main__":

     main()