from pathlib import Path

import cv2
import numpy as np


_MODEL = None
_HOG = cv2.HOGDescriptor((48, 48), (16, 16), (8, 8), (8, 8), 9)


def _model_yukle():
    global _MODEL

    if _MODEL is None:
        yol = Path(__file__).with_name("harf_modeli.npz")
        veri = np.load(yol, allow_pickle=False)
        _MODEL = (
            veri["X"].astype(np.float32),
            veri["y"].astype(str),
        )

    return _MODEL


def _ozellik(hucre):
    h, w = hucre.shape[:2]

    kirp = hucre[
        int(h * 0.10):int(h * 0.90),
        int(w * 0.08):int(w * 0.78),
    ]

    gri = cv2.cvtColor(kirp, cv2.COLOR_BGR2GRAY)
    gri = cv2.resize(gri, (48, 48), interpolation=cv2.INTER_CUBIC)

    _, ikili = cv2.threshold(
        gri,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    adet, etiket, istatistik, _ = cv2.connectedComponentsWithStats(
        ikili,
        8,
    )

    temiz = np.zeros_like(ikili)

    for i in range(1, adet):
        x, y, genislik, yukseklik, alan = istatistik[i]

        if (
            alan > 20
            and x > 1
            and y > 1
            and x + genislik < 47
            and y + yukseklik < 47
        ):
            temiz[etiket == i] = 255

    return _HOG.compute(temiz).reshape(-1).astype(np.float32)


def harf_adaylari(hucre, komsu_sayisi=15, aday_sayisi=5):
    """
    Hücre için en olası harfleri:
    [("R", 0.52), ("K", 0.27), ("P", 0.11)] biçiminde döndürür.
    """
    X, y = _model_yukle()
    sorgu = _ozellik(hucre)

    x_norm = np.linalg.norm(X, axis=1) + 1e-8
    sorgu_norm = np.linalg.norm(sorgu) + 1e-8
    benzerlik = (X @ sorgu) / (x_norm * sorgu_norm)

    komsu_sayisi = min(komsu_sayisi, len(benzerlik))
    indeksler = np.argsort(benzerlik)[-komsu_sayisi:][::-1]

    oylar = {}

    for indeks in indeksler:
        harf = str(y[indeks])
        agirlik = float(max(benzerlik[indeks], 0.0)) ** 4
        oylar[harf] = oylar.get(harf, 0.0) + agirlik

    sirali = sorted(
        oylar.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    toplam = sum(puan for _, puan in sirali) + 1e-8

    return [
        (harf, float(puan / toplam))
        for harf, puan in sirali[:aday_sayisi]
    ]


def harfi_tani(hucre, k=15):
    adaylar = harf_adaylari(
        hucre,
        komsu_sayisi=k,
        aday_sayisi=5,
    )

    en_iyi_harf, en_iyi_guven = adaylar[0]
    ikinci_guven = adaylar[1][1] if len(adaylar) > 1 else 0.0

    return (
        en_iyi_harf,
        float(en_iyi_guven),
        float(en_iyi_guven - ikinci_guven),
    )