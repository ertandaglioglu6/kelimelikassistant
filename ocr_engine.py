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


def _tas_rengi_var_mi(hucre):
    h, w = hucre.shape[:2]

    if h < 10 or w < 10:
        return False

    # Yazıdan etkilenmemek için hücrenin iç kısmının tamamını kullan.
    ic = hucre[
        int(h * 0.16):int(h * 0.84),
        int(w * 0.16):int(w * 0.84)
    ]

    if ic.size == 0:
        return False

    hsv = cv2.cvtColor(ic, cv2.COLOR_BGR2HSV)
    pikseller = hsv.reshape(-1, 3)

    h_degerleri = pikseller[:, 0]
    s_degerleri = pikseller[:, 1]
    v_degerleri = pikseller[:, 2]

    # Normal sarı taşlar.
    sari_maske = (
        (h_degerleri >= 18)
        & (h_degerleri <= 30)
        & (s_degerleri >= 75)
        & (s_degerleri <= 165)
        & (v_degerleri >= 205)
    )

    # Son oynanan turuncu taşlar.
    turuncu_maske = (
        (h_degerleri >= 7)
        & (h_degerleri <= 19)
        & (s_degerleri >= 160)
        & (v_degerleri >= 170)
    )

    tas_orani = float(np.mean(sari_maske | turuncu_maske))

    # Hücrenin önemli kısmı taş rengindeyse taş kabul et.
    return tas_orani >= 0.42
def _buyuk_harf_var_mi(hucre):
    """
    Taşın ortasında büyük ve koyu bir harf bulunmasını şart koşar.
    Bonus karelerindeki küçük H2/K2/H3/K3 yazılarını eler.
    """
    h, w = hucre.shape[:2]

    bolge = hucre[
        int(h * 0.12):int(h * 0.88),
        int(w * 0.10):int(w * 0.79)
    ]

    if bolge.size == 0:
        return False

    bolge = cv2.resize(
        bolge,
        (280, 320),
        interpolation=cv2.INTER_CUBIC
    )

    gri = cv2.cvtColor(bolge, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    _, ikili = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    ikili = cv2.morphologyEx(
        ikili,
        cv2.MORPH_OPEN,
        np.ones((3, 3), np.uint8),
        iterations=1
    )

    konturlar, _ = cv2.findContours(
        ikili,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    goruntu_h, goruntu_w = ikili.shape
    toplam_alan = goruntu_h * goruntu_w

    for kontur in konturlar:
        alan = cv2.contourArea(kontur)
        x, y, genislik, yukseklik = cv2.boundingRect(kontur)

        # Çerçeve veya hücre kenarı olabilecek şekilleri alma.
        kenara_deger = (
            x <= 3
            or y <= 3
            or x + genislik >= goruntu_w - 3
            or y + yukseklik >= goruntu_h - 3
        )

        if kenara_deger:
            continue

        yukseklik_orani = yukseklik / float(goruntu_h)
        genislik_orani = genislik / float(goruntu_w)
        alan_orani = alan / float(toplam_alan)

        merkez_x = x + genislik / 2
        merkez_y = y + yukseklik / 2

        merkezde = (
            goruntu_w * 0.10 <= merkez_x <= goruntu_w * 0.82
            and goruntu_h * 0.15 <= merkez_y <= goruntu_h * 0.82
        )

        buyuk_harf = (
            yukseklik_orani >= 0.34
            and genislik_orani >= 0.035
            and alan_orani >= 0.004
        )

        if merkezde and buyuk_harf:
            return True

    return False


def _tas_var_mi(hucre):
    return _tas_rengi_var_mi(hucre)


def _hucre_hazirla(hucre):
    h, w = hucre.shape[:2]

    # Sağ üstteki küçük puan rakamını dışarıda bırak.
    bolge = hucre[
        int(h * 0.10):int(h * 0.90),
        int(w * 0.08):int(w * 0.78)
    ]

    bolge = cv2.resize(
        bolge,
        None,
        fx=7.0,
        fy=7.0,
        interpolation=cv2.INTER_CUBIC
    )

    gri = cv2.cvtColor(bolge, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (3, 3), 0)

    _, ikili = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    ikili = cv2.copyMakeBorder(
        ikili,
        45,
        45,
        45,
        45,
        cv2.BORDER_CONSTANT,
        value=255
    )

    return cv2.cvtColor(ikili, cv2.COLOR_GRAY2BGR)


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

    # Tam olarak tek karakter değilse reddet.
    if len(metin) != 1:
        return ""

    if metin not in TURKCE_HARF_KUMESI:
        return ""

    return metin


def hucreyi_oku(hucre, tas_kontrol_edildi=False):
    if not tas_kontrol_edildi and not _tas_var_mi(hucre):
        return ".", 1.0

    hazir = _hucre_hazirla(hucre)

    sonuc = _reader().recognize(
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

    if not harf or guven < 0.20:
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

            harf, guven = hucreyi_oku(
                hucre,
                tas_kontrol_edildi=True
            )

            tahta_satiri.append(harf)

            if harf != ".":
                okunan_harf_sayisi += 1
                okunan_guvenler.append(guven)

        tahta.append(tahta_satiri)

    # Çok fazla taş tespit edilirse yanlış tabloyu uygulama.
    if tespit_edilen_tas_sayisi > 60:
        raise ValueError(
            "Bonus kareleri taş sanıldı. "
            "Tahtanın tamamının net göründüğü başka bir ekran görüntüsü yükle."
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