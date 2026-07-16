from functools import lru_cache
from pathlib import Path
import math
import unicodedata

import cv2
import easyocr
import numpy as np

from vision_engine import harf_adaylari


TURKCE_HARFLER = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
TURKCE_HARF_KUMESI = set(TURKCE_HARFLER)


@lru_cache(maxsize=1)
def _reader():
    return easyocr.Reader(
        ["tr", "en"],
        gpu=False,
        detector=False,
        recognizer=True,
        verbose=False,
    )


@lru_cache(maxsize=1)
def _sozluk():
    yol = Path(__file__).with_name("kelimeler.txt")

    if not yol.exists():
        return set(), {}

    kelimeler = set()
    uzunluga_gore = {}

    with yol.open("r", encoding="utf-8") as dosya:
        for satir in dosya:
            kelime = unicodedata.normalize(
                "NFC",
                satir.strip().upper(),
            )

            if len(kelime) < 2:
                continue

            if not all(harf in TURKCE_HARF_KUMESI for harf in kelime):
                continue

            kelimeler.add(kelime)
            uzunluga_gore.setdefault(len(kelime), []).append(kelime)

    return kelimeler, uzunluga_gore


def _png_bytes_to_bgr(gorsel_bytes):
    veri = np.frombuffer(gorsel_bytes, dtype=np.uint8)
    gorsel = cv2.imdecode(veri, cv2.IMREAD_COLOR)

    if gorsel is None:
        raise ValueError("Tahta görüntüsü okunamadı.")

    return gorsel


def _tas_var_mi(hucre):
    h, w = hucre.shape[:2]

    if h < 10 or w < 10:
        return False

    hsv = cv2.cvtColor(hucre, cv2.COLOR_BGR2HSV)

    yamalar = [
        hsv[int(h * 0.15):int(h * 0.32), int(w * 0.15):int(w * 0.32)],
        hsv[int(h * 0.15):int(h * 0.32), int(w * 0.68):int(w * 0.85)],
        hsv[int(h * 0.68):int(h * 0.85), int(w * 0.15):int(w * 0.32)],
        hsv[int(h * 0.68):int(h * 0.85), int(w * 0.68):int(w * 0.85)],
    ]

    uygun_kose = 0

    for yama in yamalar:
        if yama.size == 0:
            continue

        renk, doygunluk, parlaklik = np.median(
            yama.reshape(-1, 3),
            axis=0,
        )

        yildiz_rengi = (
            16 <= renk <= 21
            and doygunluk >= 145
            and parlaklik >= 240
        )

        sari_tas = (
            19 <= renk <= 30
            and 80 <= doygunluk <= 140
            and parlaklik >= 220
        )

        turuncu_tas = (
            8 <= renk <= 16
            and doygunluk >= 190
            and parlaklik >= 180
        )

        if not yildiz_rengi and (sari_tas or turuncu_tas):
            uygun_kose += 1

    return uygun_kose >= 3


def _metni_temizle(metin):
    metin = unicodedata.normalize(
        "NFC",
        str(metin).strip().upper(),
    )

    donusumler = {
        "İ": "İ",
        "|": "I",
        "1": "I",
        "0": "O",
        "5": "S",
    }

    for eski, yeni in donusumler.items():
        metin = metin.replace(eski, yeni)

    temiz = "".join(
        karakter
        for karakter in metin
        if karakter in TURKCE_HARF_KUMESI
    )

    if len(temiz) == 2 and temiz[0] == temiz[1]:
        temiz = temiz[0]

    return temiz if len(temiz) == 1 else ""


def _ocr_adaylari_olustur(hucre):
    h, w = hucre.shape[:2]

    kirp = hucre[
        int(h * 0.08):int(h * 0.91),
        int(w * 0.06):int(w * 0.80),
    ]

    kirp = cv2.resize(
        kirp,
        (360, 420),
        interpolation=cv2.INTER_CUBIC,
    )

    gri = cv2.cvtColor(kirp, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    _, normal_esik = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    _, ters_esik = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    adaylar = [
        kirp,
        cv2.cvtColor(normal_esik, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(ters_esik, cv2.COLOR_GRAY2BGR),
    ]

    return [
        cv2.copyMakeBorder(
            aday,
            60,
            60,
            60,
            60,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255),
        )
        for aday in adaylar
    ]


def _adaylari_birlestir(model_adaylari, ocr_harfi, ocr_guveni):
    puanlar = {}

    for harf, guven in model_adaylari:
        puanlar[harf] = max(
            puanlar.get(harf, 0.0),
            float(guven),
        )

    if ocr_harfi:
        ocr_puani = min(0.98, 0.25 + (ocr_guveni * 0.75))
        puanlar[ocr_harfi] = max(
            puanlar.get(ocr_harfi, 0.0),
            ocr_puani,
        )

    sirali = sorted(
        puanlar.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    toplam = sum(puan for _, puan in sirali) + 1e-8

    return [
        (harf, float(puan / toplam))
        for harf, puan in sirali[:5]
    ]


def hucreyi_oku(hucre):
    if not _tas_var_mi(hucre):
        return ".", 1.0, []

    try:
        model_adaylari = harf_adaylari(
            hucre,
            komsu_sayisi=15,
            aday_sayisi=5,
        )
    except Exception:
        model_adaylari = []

    ocr_harfi = ""
    ocr_guveni = 0.0
    bulunanlar = []

    reader = _reader()

    for aday in _ocr_adaylari_olustur(hucre):
        try:
            sonuc = reader.recognize(
                aday,
                horizontal_list=None,
                free_list=None,
                decoder="greedy",
                beamWidth=5,
                batch_size=1,
                workers=0,
                allowlist=TURKCE_HARFLER,
                detail=1,
                paragraph=False,
                contrast_ths=0.01,
                adjust_contrast=0.7,
            )
        except Exception:
            sonuc = []

        for item in sonuc:
            harf = _metni_temizle(item[1])
            guven = float(item[2])

            if harf:
                bulunanlar.append((harf, guven))

    if bulunanlar:
        ocr_harfi, ocr_guveni = max(
            bulunanlar,
            key=lambda item: item[1],
        )

    adaylar = _adaylari_birlestir(
        model_adaylari,
        ocr_harfi,
        ocr_guveni,
    )

    if not adaylar:
        return ".", 0.0, []

    harf, guven = adaylar[0]
    return harf, float(guven), adaylar


def _kelime_parcalarini_bul(tahta):
    boyut = len(tahta)
    parcalar = []

    for satir in range(boyut):
        sutun = 0

        while sutun < boyut:
            if tahta[satir][sutun] == ".":
                sutun += 1
                continue

            baslangic = sutun

            while sutun < boyut and tahta[satir][sutun] != ".":
                sutun += 1

            if sutun - baslangic >= 2:
                parcalar.append([
                    (satir, indeks)
                    for indeks in range(baslangic, sutun)
                ])

    for sutun in range(boyut):
        satir = 0

        while satir < boyut:
            if tahta[satir][sutun] == ".":
                satir += 1
                continue

            baslangic = satir

            while satir < boyut and tahta[satir][sutun] != ".":
                satir += 1

            if satir - baslangic >= 2:
                parcalar.append([
                    (indeks, sutun)
                    for indeks in range(baslangic, satir)
                ])

    return parcalar


def _kelimeyi_sozlukle_duzelt(
    tahta,
    aday_matrisi,
    koordinatlar,
    kelime_kumesi,
    uzunluga_gore,
):
    mevcut = "".join(
        tahta[satir][sutun]
        for satir, sutun in koordinatlar
    )

    if mevcut in kelime_kumesi:
        return 0

    uzunluk = len(koordinatlar)
    uygun_kelimeler = uzunluga_gore.get(uzunluk, [])

    aday_harf_kumeleri = []

    for satir, sutun in koordinatlar:
        adaylar = aday_matrisi[satir][sutun]

        if not adaylar:
            adaylar = [(tahta[satir][sutun], 1.0)]

        aday_harf_kumeleri.append({
            harf
            for harf, _ in adaylar[:4]
        })

    en_iyi_kelime = None
    en_iyi_puan = -math.inf
    en_iyi_degisim = 99
    ikinci_puan = -math.inf

    for kelime in uygun_kelimeler:
        if any(
            kelime[index] not in aday_harf_kumeleri[index]
            for index in range(uzunluk)
        ):
            continue

        degisim_sayisi = sum(
            kelime[index] != mevcut[index]
            for index in range(uzunluk)
        )

        if degisim_sayisi == 0 or degisim_sayisi > 2:
            continue

        puan = 0.0

        for index, (satir, sutun) in enumerate(koordinatlar):
            adaylar = dict(aday_matrisi[satir][sutun])
            olasilik = adaylar.get(kelime[index], 0.01)
            puan += math.log(max(olasilik, 1e-5))

            if kelime[index] == mevcut[index]:
                puan += 0.18

        if puan > en_iyi_puan:
            ikinci_puan = en_iyi_puan
            en_iyi_puan = puan
            en_iyi_kelime = kelime
            en_iyi_degisim = degisim_sayisi
        elif puan > ikinci_puan:
            ikinci_puan = puan

    if en_iyi_kelime is None:
        return 0

    # Birden fazla yakın sözlük adayı varsa rastgele düzeltme yapma.
    if ikinci_puan > -math.inf and en_iyi_puan - ikinci_puan < 0.30:
        return 0

    # İki harf değişiyorsa daha yüksek fark iste.
    if en_iyi_degisim == 2 and (
        ikinci_puan > -math.inf
        and en_iyi_puan - ikinci_puan < 0.60
    ):
        return 0

    degisim = 0

    for index, (satir, sutun) in enumerate(koordinatlar):
        yeni_harf = en_iyi_kelime[index]

        if tahta[satir][sutun] != yeni_harf:
            tahta[satir][sutun] = yeni_harf
            degisim += 1

    return degisim


def _tahtayi_sozlukle_duzelt(tahta, aday_matrisi):
    kelime_kumesi, uzunluga_gore = _sozluk()

    if not kelime_kumesi:
        return 0

    toplam_degisim = 0

    # Yatay ve dikey kesişmelerden yararlanmak için iki tur çalıştır.
    for _ in range(2):
        tur_degisim = 0

        for koordinatlar in _kelime_parcalarini_bul(tahta):
            tur_degisim += _kelimeyi_sozlukle_duzelt(
                tahta,
                aday_matrisi,
                koordinatlar,
                kelime_kumesi,
                uzunluga_gore,
            )

        toplam_degisim += tur_degisim

        if tur_degisim == 0:
            break

    return toplam_degisim


def tahtayi_oku(kesilmis_tahta_bytes, boyut=15):
    gorsel = _png_bytes_to_bgr(kesilmis_tahta_bytes)

    hedef_boyut = boyut * 100
    gorsel = cv2.resize(
        gorsel,
        (hedef_boyut, hedef_boyut),
        interpolation=cv2.INTER_AREA,
    )

    hucre_boyutu = hedef_boyut // boyut

    tahta = []
    aday_matrisi = []
    okunan_guvenler = []
    okunan_harf_sayisi = 0
    tespit_edilen_tas_sayisi = 0

    for satir in range(boyut):
        tahta_satiri = []
        aday_satiri = []

        for sutun in range(boyut):
            y1 = satir * hucre_boyutu
            y2 = (satir + 1) * hucre_boyutu
            x1 = sutun * hucre_boyutu
            x2 = (sutun + 1) * hucre_boyutu

            hucre = gorsel[y1:y2, x1:x2]

            if not _tas_var_mi(hucre):
                tahta_satiri.append(".")
                aday_satiri.append([])
                continue

            tespit_edilen_tas_sayisi += 1

            harf, guven, adaylar = hucreyi_oku(hucre)

            tahta_satiri.append(harf)
            aday_satiri.append(adaylar)

            if harf != ".":
                okunan_harf_sayisi += 1
                okunan_guvenler.append(guven)

        tahta.append(tahta_satiri)
        aday_matrisi.append(aday_satiri)

    if tespit_edilen_tas_sayisi == 0:
        raise ValueError("Taş rengi algılanamadı.")

    if tespit_edilen_tas_sayisi > 110:
        raise ValueError(
            f"{tespit_edilen_tas_sayisi} taş tespit edildi. "
            "Bonus kareleri taş sanılmış olabilir."
        )

    if okunan_harf_sayisi == 0:
        raise ValueError(
            f"{tespit_edilen_tas_sayisi} taş tespit edildi "
            "fakat harfler okunamadı."
        )

    sozluk_duzeltme_sayisi = _tahtayi_sozlukle_duzelt(
        tahta,
        aday_matrisi,
    )

    ortalama_guven = (
        sum(okunan_guvenler) / len(okunan_guvenler)
        if okunan_guvenler
        else 0.0
    )

    return {
        "tahta": tahta,
        "tespit_edilen_tas_sayisi": tespit_edilen_tas_sayisi,
        "okunan_harf_sayisi": okunan_harf_sayisi,
        "ortalama_guven": ortalama_guven,
        "sozluk_duzeltme_sayisi": sozluk_duzeltme_sayisi,
    }