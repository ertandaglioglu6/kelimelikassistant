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
        raise ValueError("Kesilmiş tahta görüntüsü okunamadı.")

    return gorsel


def _sari_turuncu_piksel_mi(hsv_piksel):
    h, s, v = [int(deger) for deger in hsv_piksel]

    # Gerçek taşların sarı/krem/turuncu arka plan aralığı.
    renk_uygun = 4 <= h <= 40
    doygunluk_uygun = 45 <= s <= 255
    parlaklik_uygun = v >= 105

    return renk_uygun and doygunluk_uygun and parlaklik_uygun


def _tas_rengi_var_mi(hucre):
    """
    Hücrenin farklı bölgelerinde taşın sarı/turuncu zeminini arar.

    Tek başına yeterli değildir. K3 gibi renkli bonus kareleri de benzer
    renkte olabileceği için ayrıca büyük harf kontrolü yapılır.
    """
    h, w = hucre.shape[:2]

    if h < 10 or w < 10:
        return False

    hsv = cv2.cvtColor(hucre, cv2.COLOR_BGR2HSV)

    noktalar = [
        (0.20, 0.20),
        (0.40, 0.18),
        (0.60, 0.18),
        (0.80, 0.20),

        (0.18, 0.40),
        (0.82, 0.42),

        (0.18, 0.62),
        (0.82, 0.64),

        (0.20, 0.80),
        (0.40, 0.82),
        (0.60, 0.82),
        (0.80, 0.80),
    ]

    uygun_nokta = 0

    for x_oran, y_oran in noktalar:
        x = min(max(int(w * x_oran), 0), w - 1)
        y = min(max(int(h * y_oran), 0), h - 1)

        yaricap = max(int(min(h, w) * 0.035), 1)

        x1 = max(x - yaricap, 0)
        x2 = min(x + yaricap + 1, w)
        y1 = max(y - yaricap, 0)
        y2 = min(y + yaricap + 1, h)

        yama = hsv[y1:y2, x1:x2]

        if yama.size == 0:
            continue

        medyan = np.median(
            yama.reshape(-1, 3),
            axis=0
        )

        if _sari_turuncu_piksel_mi(medyan):
            uygun_nokta += 1

    # On iki noktanın en az yedisi taş renginde olmalı.
    return uygun_nokta >= 7


def _buyuk_harf_sekli_var_mi(hucre):
    """
    Hücrenin ortasında gerçek oyun taşı üzerindeki harf kadar büyük,
    koyu renkli bir şekil olup olmadığını kontrol eder.

    H2/K2/H3/K3 yazıları daha küçük olduğu için büyük ölçüde elenir.
    """
    h, w = hucre.shape[:2]

    if h < 10 or w < 10:
        return False

    # Izgara çizgilerini, taş kenarlarını ve sağ üstteki puan rakamını çıkar.
    y1 = int(h * 0.14)
    y2 = int(h * 0.86)
    x1 = int(w * 0.13)
    x2 = int(w * 0.78)

    merkez = hucre[y1:y2, x1:x2]

    if merkez.size == 0:
        return False

    merkez = cv2.resize(
        merkez,
        (260, 300),
        interpolation=cv2.INTER_CUBIC
    )

    gri = cv2.cvtColor(merkez, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    # Koyu harfi açık taş zemininden ayır.
    _, ikili = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Küçük yazı ve görüntü gürültülerini azalt.
    cekirdek = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    ikili = cv2.morphologyEx(
        ikili,
        cv2.MORPH_OPEN,
        cekirdek,
        iterations=1
    )

    konturlar, _ = cv2.findContours(
        ikili,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    goruntu_h, goruntu_w = ikili.shape
    goruntu_alani = goruntu_h * goruntu_w

    for kontur in konturlar:
        alan = cv2.contourArea(kontur)
        x, y, genislik, yukseklik = cv2.boundingRect(kontur)

        alan_orani = alan / float(goruntu_alani)
        yukseklik_orani = yukseklik / float(goruntu_h)
        genislik_orani = genislik / float(goruntu_w)

        merkez_x = x + genislik / 2
        merkez_y = y + yukseklik / 2

        yatay_merkezde = (
            goruntu_w * 0.15
            <= merkez_x
            <= goruntu_w * 0.85
        )

        dikey_merkezde = (
            goruntu_h * 0.18
            <= merkez_y
            <= goruntu_h * 0.82
        )

        # I, İ ve J gibi ince harfler için genişlik sınırı düşük tutuldu.
        yeterince_buyuk = (
            yukseklik_orani >= 0.37
            and genislik_orani >= 0.035
            and alan_orani >= 0.006
        )

        if yeterince_buyuk and yatay_merkezde and dikey_merkezde:
            return True

    return False


def _tas_var_mi(hucre):
    """
    Taş kabul etmek için iki şartın da sağlanması gerekir:

    1. Hücrenin büyük bölümü taş renginde olmalı.
    2. Ortada büyük bir oyun harfi bulunmalı.

    Böylece bonus karelerinin küçük H2/K2/H3/K3 yazıları elenir.
    """
    if not _tas_rengi_var_mi(hucre):
        return False

    if not _buyuk_harf_sekli_var_mi(hucre):
        return False

    return True


def _hucre_hazirla(hucre):
    h, w = hucre.shape[:2]

    # Izgara çizgileri ve sağ üstteki küçük puan rakamı dışarıda kalır.
    y1 = int(h * 0.12)
    y2 = int(h * 0.88)
    x1 = int(w * 0.10)
    x2 = int(w * 0.78)

    kirpilmis = hucre[y1:y2, x1:x2]

    kirpilmis = cv2.resize(
        kirpilmis,
        None,
        fx=6.0,
        fy=6.0,
        interpolation=cv2.INTER_CUBIC
    )

    gri = cv2.cvtColor(kirpilmis, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    _, ikili = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    konturlar, _ = cv2.findContours(
        ikili,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    temiz = np.zeros_like(ikili)
    toplam_alan = ikili.shape[0] * ikili.shape[1]

    for kontur in konturlar:
        alan = cv2.contourArea(kontur)
        _, _, kontur_genisligi, kontur_yuksekligi = cv2.boundingRect(kontur)

        alan_yeterli = alan >= toplam_alan * 0.0015
        yukseklik_yeterli = (
            kontur_yuksekligi >= ikili.shape[0] * 0.14
        )

        if alan_yeterli and yukseklik_yeterli:
            cv2.drawContours(
                temiz,
                [kontur],
                -1,
                255,
                thickness=cv2.FILLED
            )

    # EasyOCR siyah harfi beyaz zeminde daha istikrarlı okuyabilir.
    temiz = cv2.bitwise_not(temiz)

    # Görüntünün çevresine boşluk ekle.
    temiz = cv2.copyMakeBorder(
        temiz,
        45,
        45,
        45,
        45,
        cv2.BORDER_CONSTANT,
        value=255
    )

    return cv2.cvtColor(temiz, cv2.COLOR_GRAY2BGR)


def _metni_temizle(metin):
    """
    OCR sonucunun içinden ilk uygun harfi seçmez.

    Sonuç temizlendikten sonra tam olarak tek bir Türkçe harf değilse
    reddedilir. Böylece H2 gibi sonuçlardan H seçilmez.
    """
    metin = str(metin).strip().upper()

    metin = unicodedata.normalize("NFC", metin)

    donusumler = {
        "İ": "İ",
        "|": "I",
        "1": "I",
        "0": "O",
        "5": "S",
    }

    for eski, yeni in donusumler.items():
        metin = metin.replace(eski, yeni)

    # Boşluk ve noktalama işaretlerini temizle.
    temiz_karakterler = []

    for karakter in metin:
        if karakter.isalnum() or karakter in TURKCE_HARF_KUMESI:
            temiz_karakterler.append(karakter)

    metin = "".join(temiz_karakterler)

    # Rakam veya birden fazla karakter bulunuyorsa reddet.
    if len(metin) != 1:
        return ""

    if metin not in TURKCE_HARF_KUMESI:
        return ""

    return metin


def hucreyi_oku(hucre, tas_kontrol_edildi=False):
    if not tas_kontrol_edildi and not _tas_var_mi(hucre):
        return ".", 1.0

    hazir = _hucre_hazirla(hucre)
    reader = _reader()

    sonuc = reader.recognize(
        hazir,
        horizontal_list=None,
        free_list=None,
        decoder="greedy",
        beamWidth=5,
        batch_size=1,
        workers=0,
        allowlist=TURKCE_HARFLER,
        detail=1,
        paragraph=False,
        contrast_ths=0.05,
        adjust_contrast=0.7
    )

    if not sonuc:
        return ".", 0.0

    en_iyi = max(
        sonuc,
        key=lambda item: float(item[2])
    )

    harf = _metni_temizle(en_iyi[1])
    guven = float(en_iyi[2])

    # 0.05 çok düşüktü; rastgele yanlış okumaları kolayca kabul ediyordu.
    if not harf or guven < 0.18:
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

            tas_var = _tas_var_mi(hucre)

            if not tas_var:
                tahta_satiri.append(".")
                continue

            tespit_edilen_tas_sayisi += 1

            harf, guven = hucreyi_oku(
                hucre,
                tas_kontrol_edildi=True
            )

            tahta_satiri.append(harf)

            if harf != ".":
                okunan_harf_sayisi += 1
                okunan_guvenler.append(guven)

        tahta.append(tahta_satiri)

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