TAHTA_BOYUTU = 15


def bos_tahta_olustur():
    tahta = []

    for _ in range(TAHTA_BOYUTU):
        satir = []
        for _ in range(TAHTA_BOYUTU):
            satir.append(".")
        tahta.append(satir)

    return tahta


def harf_yerlestir(tahta, satir, sutun, harf):
    tahta[satir][sutun] = harf


def tahta_yazdir(tahta):
    print("   " + " ".join([str(i).rjust(2) for i in range(TAHTA_BOYUTU)]))

    for i, satir in enumerate(tahta):
        satir_yazi = " ".join([h.rjust(2) for h in satir])
        print(str(i).rjust(2) + " " + satir_yazi)