from collections import Counter
from bonus import TAHTA_BONUSLARI


JOKER = "*"


def tahta_bos_mu(tahta):
    for satir in tahta:
        for hucre in satir:
            if hucre != ".":
                return False
    return True


def tahta_harflerini_bul(tahta):
    harfler = []

    for satir in tahta:
        for hucre in satir:
            if hucre != ".":
                harfler.append(hucre)

    return harfler


def kelime_tahtaya_sigar_mi(kelime, satir, sutun, yon, boyut):
    if yon == "YATAY":
        return 0 <= satir < boyut and 0 <= sutun and sutun + len(kelime) <= boyut

    if yon == "DIKEY":
        return 0 <= sutun < boyut and 0 <= satir and satir + len(kelime) <= boyut

    return False


def koordinat_al(satir, sutun, index, yon):
    if yon == "YATAY":
        return satir, sutun + index

    return satir + index, sutun


def kelimenin_basi_sonu_uygun_mu(tahta, kelime, satir, sutun, yon):
    boyut = len(tahta)

    if yon == "YATAY":
        onceki_sutun = sutun - 1
        sonraki_sutun = sutun + len(kelime)

        if onceki_sutun >= 0 and tahta[satir][onceki_sutun] != ".":
            return False

        if sonraki_sutun < boyut and tahta[satir][sonraki_sutun] != ".":
            return False

    elif yon == "DIKEY":
        onceki_satir = satir - 1
        sonraki_satir = satir + len(kelime)

        if onceki_satir >= 0 and tahta[onceki_satir][sutun] != ".":
            return False

        if sonraki_satir < boyut and tahta[sonraki_satir][sutun] != ".":
            return False

    return True


def kullanilacak_harfleri_bul(tahta, kelime, satir, sutun, yon):
    kullanilacak_harfler = []
    temas_var = False

    for i, harf in enumerate(kelime):
        r, c = koordinat_al(satir, sutun, i, yon)
        tahtadaki_harf = tahta[r][c]

        if tahtadaki_harf == ".":
            kullanilacak_harfler.append((i, harf))
        elif tahtadaki_harf == harf:
            temas_var = True
        else:
            return None, False

    return kullanilacak_harfler, temas_var


def eldeki_harfler_yeterli_mi(kullanilacak_harfler, eldeki_harfler):
    eldeki_sayac = Counter(eldeki_harfler)
    joker_sayisi = eldeki_sayac.get(JOKER, 0)

    kullanilan_harfler = []
    joker_indexleri = set()

    for index, harf in kullanilacak_harfler:
        if eldeki_sayac[harf] > 0:
            eldeki_sayac[harf] -= 1
            kullanilan_harfler.append(harf)
        elif joker_sayisi > 0:
            joker_sayisi -= 1
            joker_indexleri.add(index)
            kullanilan_harfler.append(f"{JOKER}->{harf}")
        else:
            return False, "", set()

    return True, " ".join(kullanilan_harfler), joker_indexleri


def kelime_kabaca_mumkun_mu(kelime, eldeki_harfler, tahta_harfleri):
    kelime_sayac = Counter(kelime)

    eldeki_normal_harfler = [harf for harf in eldeki_harfler if harf != JOKER]
    joker_sayisi = eldeki_harfler.count(JOKER)

    mevcut_sayac = Counter(eldeki_normal_harfler) + Counter(tahta_harfleri)

    eksik_sayisi = 0

    for harf, adet in kelime_sayac.items():
        eksik = adet - mevcut_sayac[harf]

        if eksik > 0:
            eksik_sayisi += eksik

            if eksik_sayisi > joker_sayisi:
                return False

    return True


def capraz_kelime_bul(tahta, satir, sutun, harf, ana_yon):
    boyut = len(tahta)

    # Ana kelime yataysa yan kelime dikey oluşur.
    if ana_yon == "YATAY":
        dr = 1
        dc = 0
    else:
        # Ana kelime dikeyse yan kelime yatay oluşur.
        dr = 0
        dc = 1

    bas_satir = satir
    bas_sutun = sutun

    while True:
        onceki_satir = bas_satir - dr
        onceki_sutun = bas_sutun - dc

        if onceki_satir < 0 or onceki_satir >= boyut:
            break

        if onceki_sutun < 0 or onceki_sutun >= boyut:
            break

        if tahta[onceki_satir][onceki_sutun] == ".":
            break

        bas_satir = onceki_satir
        bas_sutun = onceki_sutun

    kelime = ""
    konumlar = []

    r = bas_satir
    c = bas_sutun

    while 0 <= r < boyut and 0 <= c < boyut:
        if r == satir and c == sutun:
            kelime += harf
            konumlar.append((r, c))
        elif tahta[r][c] != ".":
            kelime += tahta[r][c]
            konumlar.append((r, c))
        else:
            break

        r += dr
        c += dc

    return kelime, konumlar


def yan_kelimeleri_kontrol_et(tahta, kelime, satir, sutun, yon, kullanilacak_harfler, sozluk):
    yan_temas_var = False
    yan_kelimeler = []

    for index, harf in kullanilacak_harfler:
        r, c = koordinat_al(satir, sutun, index, yon)

        yan_kelime, yan_konumlar = capraz_kelime_bul(tahta, r, c, harf, yon)

        # Tek harf oluşuyorsa yan kelime yok.
        if len(yan_kelime) <= 1:
            continue

        yan_temas_var = True

        # Yan kelime sözlükte yoksa hamle geçersiz.
        if yan_kelime not in sozluk:
            return False, yan_temas_var, []

        yan_kelimeler.append({
            "kelime": yan_kelime,
            "konumlar": yan_konumlar,
            "yeni_harf_index": index,
            "yeni_harf_konum": (r, c),
        })

    return True, yan_temas_var, yan_kelimeler


def kelime_yerlestirilebilir_mi(tahta, kelime, satir, sutun, yon, eldeki_harfler, sozluk):
    boyut = len(tahta)

    if not kelime_tahtaya_sigar_mi(kelime, satir, sutun, yon, boyut):
        return False, "", set(), []

    if not kelimenin_basi_sonu_uygun_mu(tahta, kelime, satir, sutun, yon):
        return False, "", set(), []

    kullanilacak_harfler, temas_var = kullanilacak_harfleri_bul(
        tahta,
        kelime,
        satir,
        sutun,
        yon
    )

    if kullanilacak_harfler is None:
        return False, "", set(), []

    # Hiç yeni harf koymuyorsa hamle sayma.
    if len(kullanilacak_harfler) == 0:
        return False, "", set(), []

    yeterli_mi, kullanilan_harfler, joker_indexleri = eldeki_harfler_yeterli_mi(
        kullanilacak_harfler,
        eldeki_harfler
    )

    if not yeterli_mi:
        return False, "", set(), []

    yanlar_gecerli_mi, yan_temas_var, yan_kelimeler = yan_kelimeleri_kontrol_et(
        tahta,
        kelime,
        satir,
        sutun,
        yon,
        kullanilacak_harfler,
        sozluk
    )

    if not yanlar_gecerli_mi:
        return False, "", set(), []

    # Tahta boş değilse ya mevcut harfin üstünden geçmeli
    # ya da yan kelime oluşturarak temas etmeli.
    if not tahta_bos_mu(tahta) and not temas_var and not yan_temas_var:
        return False, "", set(), []

    return True, kullanilan_harfler, joker_indexleri, yan_kelimeler


def ana_kelime_puani_hesapla(tahta, kelime, satir, sutun, yon, puan_hesapla, joker_indexleri):
    toplam = 0
    kelime_carpani = 1

    for i, harf in enumerate(kelime):
        r, c = koordinat_al(satir, sutun, i, yon)

        # Tahtada önceden olan harflerde bonus kullanılmaz.
        if tahta[r][c] != ".":
            toplam += puan_hesapla(harf)
            continue

        # Jokerle koyulan harf 0 puan sayılır.
        if i in joker_indexleri:
            harf_puani = 0
        else:
            harf_puani = puan_hesapla(harf)

        bonus = TAHTA_BONUSLARI[r][c]

        if bonus == "H2":
            harf_puani *= 2
        elif bonus == "H3":
            harf_puani *= 3
        elif bonus == "K2":
            kelime_carpani *= 2
        elif bonus == "K3":
            kelime_carpani *= 3

        toplam += harf_puani

    return toplam * kelime_carpani


def yan_kelime_puani_hesapla(tahta, yan_kelime_bilgisi, puan_hesapla, joker_indexleri):
    kelime = yan_kelime_bilgisi["kelime"]
    konumlar = yan_kelime_bilgisi["konumlar"]
    yeni_harf_index = yan_kelime_bilgisi["yeni_harf_index"]
    yeni_harf_konum = yan_kelime_bilgisi["yeni_harf_konum"]

    toplam = 0
    kelime_carpani = 1

    for i, harf in enumerate(kelime):
        r, c = konumlar[i]

        # Yan kelimedeki eski harfler normal puan verir.
        if (r, c) != yeni_harf_konum:
            toplam += puan_hesapla(harf)
            continue

        # Yan kelimedeki yeni koyulan harf:
        # Ana kelimede jokerle koyulduysa burada da 0 puan.
        if yeni_harf_index in joker_indexleri:
            harf_puani = 0
        else:
            harf_puani = puan_hesapla(harf)

        # Yeni koyulan harfin bonusu yan kelimeye de uygulanır.
        bonus = TAHTA_BONUSLARI[r][c]

        if bonus == "H2":
            harf_puani *= 2
        elif bonus == "H3":
            harf_puani *= 3
        elif bonus == "K2":
            kelime_carpani *= 2
        elif bonus == "K3":
            kelime_carpani *= 3

        toplam += harf_puani

    return toplam * kelime_carpani


def hamle_puani_hesapla(
    tahta,
    kelime,
    satir,
    sutun,
    yon,
    puan_hesapla,
    joker_indexleri,
    yan_kelimeler
):
    ana_puan = ana_kelime_puani_hesapla(
        tahta,
        kelime,
        satir,
        sutun,
        yon,
        puan_hesapla,
        joker_indexleri
    )

    yan_puan = 0

    for yan_kelime in yan_kelimeler:
        yan_puan += yan_kelime_puani_hesapla(
            tahta,
            yan_kelime,
            puan_hesapla,
            joker_indexleri
        )

    return ana_puan + yan_puan


def mevcut_harf_konumlari(tahta):
    konumlar = []

    for satir_no, satir in enumerate(tahta):
        for sutun_no, harf in enumerate(satir):
            if harf != ".":
                konumlar.append((satir_no, sutun_no, harf))

    return konumlar


def aday_baslangiclari_bul(tahta, kelime):
    boyut = len(tahta)
    baslangiclar = set()

    # Garanti yöntem:
    # Tüm başlangıç karelerini ve iki yönü dener.
    for satir in range(boyut):
        for sutun in range(boyut):
            if kelime_tahtaya_sigar_mi(kelime, satir, sutun, "YATAY", boyut):
                baslangiclar.add((satir, sutun, "YATAY"))

            if kelime_tahtaya_sigar_mi(kelime, satir, sutun, "DIKEY", boyut):
                baslangiclar.add((satir, sutun, "DIKEY"))

    return baslangiclar


def hamleleri_bul(tahta, sozluk, eldeki_harfler, puan_hesapla):
    hamleler = []
    tahta_harfleri = tahta_harflerini_bul(tahta)

    for kelime in sozluk:
        if not kelime_kabaca_mumkun_mu(kelime, eldeki_harfler, tahta_harfleri):
            continue

        aday_baslangiclar = aday_baslangiclari_bul(tahta, kelime)

        for satir, sutun, yon in aday_baslangiclar:
            uygun_mu, kullanilan_harfler, joker_indexleri, yan_kelimeler = kelime_yerlestirilebilir_mi(
                tahta,
                kelime,
                satir,
                sutun,
                yon,
                eldeki_harfler,
                sozluk
            )

            if uygun_mu:
                puan = hamle_puani_hesapla(
                    tahta,
                    kelime,
                    satir,
                    sutun,
                    yon,
                    puan_hesapla,
                    joker_indexleri,
                    yan_kelimeler
                )

                hamleler.append({
                    "kelime": kelime,
                    "satir": satir,
                    "sutun": sutun,
                    "yon": yon,
                    "puan": puan,
                    "kullanilan_harfler": kullanilan_harfler
                })

    hamleler.sort(key=lambda x: (x["puan"], len(x["kelime"])), reverse=True)
    return hamleler


def hamleyi_tahtada_goster(tahta, hamle):
    yeni_tahta = [satir.copy() for satir in tahta]

    kelime = hamle["kelime"]
    satir = hamle["satir"]
    sutun = hamle["sutun"]
    yon = hamle["yon"]

    for i, harf in enumerate(kelime):
        r, c = koordinat_al(satir, sutun, i, yon)
        yeni_tahta[r][c] = harf

    return yeni_tahta