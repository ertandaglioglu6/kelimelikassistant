from functools import lru_cache
import unicodedata

import cv2
import easyocr
import numpy as np


TURKCE_HARFLER = "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
TURKCE_HARF_KUMESI = set(TURKCE_HARFLER)


@lru_cache(maxsize=1)
def _reader():
    return easyocr.Reader(
        ["tr", "en"],
        gpu=False,
        detector=False,
        recognizer=True,
        verbose=False
    )


def _png_bytes_to_bgr(gorsel_bytes):
    veri = np.frombuffer(gorsel_bytes, dtype=np.uint8)
    gorsel = cv2.imdecode(veri, cv2.IMREAD_COLOR)

    if gorsel is None:
        raise ValueError("Tahta görüntüsü okunamadı.")

    return gorsel


def _tas_var_mi(hucre):
    """
    Sarı ve turuncu taşları RGB farkıyla algılar.
    Gri, mavi, yeşil ve pembe bonus karelerini reddeder.
    """
    h, w = hucre.shape[:2]

    if h < 10 or w < 10:
        return False

    ic = hucre[
        int(h * 0.18):int(h * 0.82),
        int(w * 0.18):int(w * 0.82)
    ]

    if ic.size == 0:
        return False

    # OpenCV BGR kullanır.
    b, g, r = cv2.split(ic.astype(np.int16))

    # Açık sarı taş.
    sari = (
        (r >= 185)
        & (g >= 155)
        & ((r - b) >= 28)
        & ((g - b) >= 18)
        & (np.abs(r - g) <= 95)
    )

    # Turuncu taş.
    turuncu = (
        (r >= 190)
        & (g >= 70)
        & (g <= 190)
        & ((r - g) >= 35)
        & ((g - b) >= 25)
    )

    tas_orani = float(np.mean(sari | turuncu))
    return tas_orani >= 0.28


def _metni_temizle(metin):
    metin = unicodedata.normalize(
        "NFC",
        str(metin).strip().upper()
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

    # EasyOCR bazen aynı harfi iki kez döndürebilir.
    if len(temiz) == 2 and temiz[0] == temiz[1]:
        temiz = temiz[0]

    if len(temiz) != 1:
        return ""

    return temiz


def _ocr_adaylari_olustur(hucre):
    h, w = hucre.shape[:2]

    # Sağ üstteki puan rakamını mümkün olduğunca dışarıda bırak.
    kirp = hucre[
        int(h * 0.08):int(h * 0.91),
        int(w * 0.06):int(w * 0.80)
    ]

    kirp = cv2.resize(
        kirp,
        (360, 420),
        interpolation=cv2.INTER_CUBIC
    )

    gri = cv2.cvtColor(kirp, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    _, normal_esik = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    _, ters_esik = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    adaylar = [
        kirp,
        cv2.cvtColor(normal_esik, cv2.COLOR_GRAY2BGR),
        cv2.cvtColor(ters_esik, cv2.COLOR_GRAY2BGR),
    ]

    sonuc = []

    for aday in adaylar:
        aday = cv2.copyMakeBorder(
            aday,
            60,
            60,
            60,
            60,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255)
        )
        sonuc.append(aday)

    return sonuc


def hucreyi_oku(hucre):
    if not _tas_var_mi(hucre):
        return ".", 1.0

    reader = _reader()
    bulunanlar = []

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
                adjust_contrast=0.7
            )
        except Exception:
            sonuc = []

        for item in sonuc:
            harf = _metni_temizle(item[1])
            guven = float(item[2])

            if harf:
                bulunanlar.append((harf, guven))

    if not bulunanlar:
        return ".", 0.0

    harf, guven = max(
        bulunanlar,
        key=lambda item: item[1]
    )

    # Şimdilik düşük tutuyoruz; yanlışları sonradan tek tek sıkılaştırırız.
    if guven < 0.05:
        return ".", guven

    return harf, guven


def tahtayi_oku(kesilmis_tahta_bytes, boyut=15):
    gorsel = _png_bytes_to_bgr(kesilmis_tahta_bytes)

    hedef_boyut = boyut * 100
    gorsel = cv2.resize(
        gorsel,
        (hedef_boyut, hedef_boyut),
        interpolation=cv2.INTER_AREA
    )

    hucre_boyutu = hedef_boyut // boyut

    tahta = []
    okunan_guvenler = []
    okunan_harf_sayisi = 0
    tespit_edilen_tas_sayisi = 0

    for satir in range(boyut):
        tahta_satiri = []

        for sutun in range(boyut):
            y1 = satir * hucre_boyutu
            y2 = (satir + 1) * hucre_boyutu
            x1 = sutun * hucre_boyutu
            x2 = (sutun + 1) * hucre_boyutu

            hucre = gorsel[y1:y2, x1:x2]

            if not _tas_var_mi(hucre):
                tahta_satiri.append(".")
                continue

            tespit_edilen_tas_sayisi += 1
            harf, guven = hucreyi_oku(hucre)
            tahta_satiri.append(harf)

            if harf != ".":
                okunan_harf_sayisi += 1
                okunan_guvenler.append(guven)

        tahta.append(tahta_satiri)

    if tespit_edilen_tas_sayisi == 0:
        raise ValueError(
            "Taş rengi algılanamadı. Yüklediğin ekran görüntüsünü kırpmadan tekrar dene."
        )

    if okunan_harf_sayisi == 0:
        raise ValueError(
            f"{tespit_edilen_tas_sayisi} taş tespit edildi fakat harfler okunamadı."
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
    }