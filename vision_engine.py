from pathlib import Path
import cv2
import numpy as np

_MODEL = None
_HOG = cv2.HOGDescriptor((48,48),(16,16),(8,8),(8,8),9)

def _model_yukle():
    global _MODEL
    if _MODEL is None:
        yol = Path(__file__).with_name("harf_modeli.npz")
        veri = np.load(yol, allow_pickle=False)
        _MODEL = (veri["X"].astype(np.float32), veri["y"].astype(str))
    return _MODEL

def _ozellik(hucre):
    h,w = hucre.shape[:2]
    kirp = hucre[int(h*.10):int(h*.90), int(w*.08):int(w*.78)]
    gri = cv2.cvtColor(kirp, cv2.COLOR_BGR2GRAY)
    gri = cv2.resize(gri,(48,48),interpolation=cv2.INTER_CUBIC)
    _, ikili = cv2.threshold(gri,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    adet, etiket, istatistik, _ = cv2.connectedComponentsWithStats(ikili,8)
    temiz = np.zeros_like(ikili)
    for i in range(1,adet):
        x,y,wk,hk,alan = istatistik[i]
        if alan > 20 and x > 1 and y > 1 and x+wk < 47 and y+hk < 47:
            temiz[etiket == i] = 255

    return _HOG.compute(temiz).reshape(-1).astype(np.float32)

def harfi_tani(hucre, k=7):
    X, y = _model_yukle()
    q = _ozellik(hucre)

    # cosine distance
    xn = np.linalg.norm(X,axis=1) + 1e-8
    qn = np.linalg.norm(q) + 1e-8
    benzerlik = (X @ q) / (xn * qn)

    idx = np.argsort(benzerlik)[-k:][::-1]
    oylar = {}
    for i in idx:
        harf = str(y[i])
        agirlik = float(max(benzerlik[i],0.0)) ** 3
        oylar[harf] = oylar.get(harf,0.0) + agirlik

    sirali = sorted(oylar.items(), key=lambda z:z[1], reverse=True)
    en_iyi = sirali[0]
    ikinci = sirali[1][1] if len(sirali)>1 else 0.0
    toplam = sum(oylar.values()) + 1e-8
    guven = en_iyi[1] / toplam
    fark = en_iyi[1] - ikinci
    return en_iyi[0], float(guven), float(fark)