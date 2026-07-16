import cv2
import numpy as np


def _noktalar_sirala(noktalar):
    noktalar = np.asarray(noktalar, dtype=np.float32).reshape(4, 2)

    toplam = noktalar.sum(axis=1)
    fark = np.diff(noktalar, axis=1).reshape(-1)

    sol_ust = noktalar[np.argmin(toplam)]
    sag_alt = noktalar[np.argmax(toplam)]
    sag_ust = noktalar[np.argmin(fark)]
    sol_alt = noktalar[np.argmax(fark)]

    return np.array(
        [sol_ust, sag_ust, sag_alt, sol_alt],
        dtype=np.float32
    )


def _perspektif_duzelt(gorsel, dortgen):
    dortgen = _noktalar_sirala(dortgen)
    sol_ust, sag_ust, sag_alt, sol_alt = dortgen

    ust_genislik = np.linalg.norm(sag_ust - sol_ust)
    alt_genislik = np.linalg.norm(sag_alt - sol_alt)
    sol_yukseklik = np.linalg.norm(sol_alt - sol_ust)
    sag_yukseklik = np.linalg.norm(sag_alt - sag_ust)

    boyut = int(
        max(
            ust_genislik,
            alt_genislik,
            sol_yukseklik,
            sag_yukseklik
        )
    )

    boyut = max(boyut, 600)

    hedef = np.array(
        [
            [0, 0],
            [boyut - 1, 0],
            [boyut - 1, boyut - 1],
            [0, boyut - 1],
        ],
        dtype=np.float32
    )

    donusum = cv2.getPerspectiveTransform(dortgen, hedef)
    return cv2.warpPerspective(gorsel, donusum, (boyut, boyut))


def _en_buyuk_kareyi_bul(gorsel):
    gri = cv2.cvtColor(gorsel, cv2.COLOR_BGR2GRAY)
    gri = cv2.GaussianBlur(gri, (5, 5), 0)

    kenarlar = cv2.Canny(gri, 35, 110)
    kenarlar = cv2.dilate(
        kenarlar,
        np.ones((5, 5), np.uint8),
        iterations=2
    )

    konturlar, _ = cv2.findContours(
        kenarlar,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    goruntu_alani = gorsel.shape[0] * gorsel.shape[1]
    adaylar = []

    for kontur in konturlar:
        alan = cv2.contourArea(kontur)

        if alan < goruntu_alani * 0.20:
            continue

        cevre = cv2.arcLength(kontur, True)
        yaklasik = cv2.approxPolyDP(kontur, 0.02 * cevre, True)

        if len(yaklasik) != 4:
            continue

        x, y, w, h = cv2.boundingRect(yaklasik)
        oran = w / float(h)

        if not 0.78 <= oran <= 1.22:
            continue

        adaylar.append((alan, yaklasik))

    if not adaylar:
        return None

    adaylar.sort(key=lambda item: item[0], reverse=True)
    return adaylar[0][1]


def _oyun_ekrani_icin_yedek_kesim(gorsel):
    yukseklik, genislik = gorsel.shape[:2]

    if yukseklik >= genislik:
        tahta = gorsel[:genislik, :genislik]
    else:
        kenar = min(yukseklik, genislik)
        x = max((genislik - kenar) // 2, 0)
        tahta = gorsel[:kenar, x:x + kenar]

    return cv2.resize(tahta, (900, 900), interpolation=cv2.INTER_AREA)


def tahtayi_bul_ve_duzelt(gorsel_bytes):
    veri = np.frombuffer(gorsel_bytes, dtype=np.uint8)
    gorsel = cv2.imdecode(veri, cv2.IMREAD_COLOR)

    if gorsel is None:
        raise ValueError("Görsel okunamadı.")

    dortgen = _en_buyuk_kareyi_bul(gorsel)

    if dortgen is not None:
        tahta = _perspektif_duzelt(gorsel, dortgen)
    else:
        tahta = _oyun_ekrani_icin_yedek_kesim(gorsel)

    basarili, tampon = cv2.imencode(".png", tahta)

    if not basarili:
        raise ValueError("Kesilmiş tahta PNG formatına çevrilemedi.")

    return tampon.tobytes()


def grid_overlay_olustur(gorsel_bytes, boyut=15):
    veri = np.frombuffer(gorsel_bytes, dtype=np.uint8)
    gorsel = cv2.imdecode(veri, cv2.IMREAD_COLOR)

    if gorsel is None:
        raise ValueError("Grid için görüntü okunamadı.")

    gorsel = cv2.resize(gorsel, (900, 900), interpolation=cv2.INTER_AREA)

    hucre = 900 / boyut

    for i in range(boyut + 1):
        konum = int(round(i * hucre))

        cv2.line(
            gorsel,
            (konum, 0),
            (konum, 899),
            (0, 0, 255),
            2
        )

        cv2.line(
            gorsel,
            (0, konum),
            (899, konum),
            (0, 0, 255),
            2
        )

    for satir in range(boyut):
        for sutun in range(boyut):
            x = int((sutun + 0.08) * hucre)
            y = int((satir + 0.22) * hucre)

            cv2.putText(
                gorsel,
                f"{satir},{sutun}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.28,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

    basarili, tampon = cv2.imencode(".png", gorsel)

    if not basarili:
        raise ValueError("Grid görüntüsü oluşturulamadı.")

    return tampon.tobytes()