import time
import streamlit as st

from main import sozluk_yukle, turkce_buyuk_harf, puan_hesapla
from solver import hamleleri_bul, hamleyi_tahtada_goster
from bonus import TAHTA_BONUSLARI


YOUTUBE_LINK = "https://www.youtube.com/watch?v=GGtVmxTFJ2E&list=LL&index=72"

TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
TAHTA_BOYUTU = 15


st.set_page_config(
    page_title="Kelimelik Yardımcı",
    page_icon="🧩",
    layout="wide"
)


@st.cache_data
def sozluk_cache_yukle():
    return sozluk_yukle("kelimeler.txt")


def bos_tahta_olustur():
    return [["." for _ in range(TAHTA_BOYUTU)] for _ in range(TAHTA_BOYUTU)]


def hucre_key(satir, sutun):
    return f"hucre_{satir}_{sutun}"


def tahta_state_baslat():
    if "hamleler" not in st.session_state:
        st.session_state.hamleler = []

    if "arama_yapildi" not in st.session_state:
        st.session_state.arama_yapildi = False

    if "arama_tahtasi" not in st.session_state:
        st.session_state.arama_tahtasi = None

    if "arama_suresi" not in st.session_state:
        st.session_state.arama_suresi = 0

    if "bekleyen_tahta" not in st.session_state:
        st.session_state.bekleyen_tahta = None

    for satir in range(TAHTA_BOYUTU):
        for sutun in range(TAHTA_BOYUTU):
            key = hucre_key(satir, sutun)

            if key not in st.session_state:
                st.session_state[key] = ""


def sonuc_temizle():
    st.session_state.hamleler = []
    st.session_state.arama_yapildi = False
    st.session_state.arama_tahtasi = None
    st.session_state.arama_suresi = 0


def tahtayi_kutulara_yaz(tahta):
    for satir in range(TAHTA_BOYUTU):
        for sutun in range(TAHTA_BOYUTU):
            key = hucre_key(satir, sutun)
            hucre = tahta[satir][sutun]

            if hucre == ".":
                st.session_state[key] = ""
            else:
                st.session_state[key] = hucre


def bekleyen_tahtayi_uygula():
    if st.session_state.bekleyen_tahta is not None:
        tahtayi_kutulara_yaz(st.session_state.bekleyen_tahta)
        st.session_state.bekleyen_tahta = None


def kutulardan_tahta_oku():
    tahta = []

    for satir in range(TAHTA_BOYUTU):
        tahta_satiri = []

        for sutun in range(TAHTA_BOYUTU):
            key = hucre_key(satir, sutun)
            deger = str(st.session_state.get(key, "")).strip()

            if deger == "" or deger == ".":
                tahta_satiri.append(".")
                continue

            deger = turkce_buyuk_harf(deger)

            if len(deger) != 1:
                raise ValueError(
                    f"{satir}. satır {sutun}. sütunda tek harf olmalı."
                )

            if deger not in TURKCE_HARFLER:
                raise ValueError(
                    f"{satir}. satır {sutun}. sütunda geçersiz karakter var: {deger}"
                )

            tahta_satiri.append(deger)

        tahta.append(tahta_satiri)

    return tahta


def metinden_tahta_olustur(tahta_metni):
    satirlar = []

    for satir in tahta_metni.splitlines():
        temiz_satir = satir.strip()

        if temiz_satir == "":
            continue

        temiz_satir = temiz_satir.replace(" ", "")
        temiz_satir = temiz_satir.replace("\t", "")
        temiz_satir = temiz_satir.replace("-", ".")
        temiz_satir = temiz_satir.replace("_", ".")
        temiz_satir = temiz_satir.replace("·", ".")
        temiz_satir = temiz_satir.replace("*", ".")
        temiz_satir = temiz_satir.replace("★", ".")
        temiz_satir = turkce_buyuk_harf(temiz_satir)

        satirlar.append(temiz_satir)

    if len(satirlar) != TAHTA_BOYUTU:
        raise ValueError(
            f"Tahta tam 15 satır olmalı. Şu an {len(satirlar)} satır var."
        )

    tahta = []

    for satir_no, satir in enumerate(satirlar):
        if len(satir) != TAHTA_BOYUTU:
            raise ValueError(
                f"{satir_no}. satır tam 15 karakter olmalı. Şu an {len(satir)} karakter var."
            )

        tahta_satiri = []

        for sutun_no, karakter in enumerate(satir):
            if karakter == ".":
                tahta_satiri.append(".")
                continue

            if karakter not in TURKCE_HARFLER:
                raise ValueError(
                    f"{satir_no}. satır {sutun_no}. sütunda geçersiz karakter var: {karakter}"
                )

            tahta_satiri.append(karakter)

        tahta.append(tahta_satiri)

    return tahta


def bonus_yazisi(satir, sutun):
    if satir == 7 and sutun == 7:
        return "★"

    bonus = TAHTA_BONUSLARI[satir][sutun]

    if bonus == ".":
        return ""

    return bonus


def tahta_yazdir_web(tahta, orijinal_tahta=None):
    html = """
    <style>
        .board-with-coords {
            display: grid;
            grid-template-columns: 24px repeat(15, 30px);
            gap: 3px;
            margin-top: 10px;
            align-items: center;
        }

        .coord {
            width: 30px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
            color: #666666;
        }

        .row-coord {
            width: 24px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
            color: #666666;
        }

        .cell {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            background: #eeeeee;
            border: 1px solid #bbbbbb;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
            color: #5b3a2e;
            position: relative;
        }

        .bonus-ghost {
            font-size: 9px;
            color: #999999;
            opacity: 0.55;
            font-weight: 800;
        }

        .center-star {
            font-size: 15px;
            color: #999999;
            opacity: 0.55;
            font-weight: 900;
        }

        .filled-old {
            background: #ffe28a;
        }

        .filled-new {
            background: #78e08f;
            border: 2px solid #218c74;
            color: #1e272e;
        }
    </style>

    <div class="board-with-coords">
    """

    html += "<div></div>"

    for sutun in range(TAHTA_BOYUTU):
        html += f'<div class="coord">{sutun}</div>'

    for satir_index, satir in enumerate(tahta):
        html += f'<div class="row-coord">{satir_index}</div>'

        for sutun_index, hucre in enumerate(satir):
            if hucre == ".":
                bonus = bonus_yazisi(satir_index, sutun_index)

                if bonus == "":
                    html += '<div class="cell"></div>'
                elif bonus == "★":
                    html += '<div class="cell"><span class="center-star">★</span></div>'
                else:
                    html += f'<div class="cell"><span class="bonus-ghost">{bonus}</span></div>'
            else:
                yeni_harf_mi = False

                if orijinal_tahta is not None:
                    if orijinal_tahta[satir_index][sutun_index] == ".":
                        yeni_harf_mi = True

                if yeni_harf_mi:
                    html += f'<div class="cell filled-new">{hucre}</div>'
                else:
                    html += f'<div class="cell filled-old">{hucre}</div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def hamle_bilgisi_yaz(hamle):
    return (
        f"{hamle['kelime']} | "
        f"Satır: {hamle['satir']} | "
        f"Sütun: {hamle['sutun']} | "
        f"Yön: {hamle['yon']} | "
        f"Puan: {hamle['puan']} | "
        f"Kullanılan: {hamle.get('kullanilan_harfler', '')}"
    )


tahta_state_baslat()
bekleyen_tahtayi_uygula()


baslik_col, link_col = st.columns([4, 1])

with baslik_col:
    st.title("🧩 EN İYİ HAMLENİ GÖR")
    st.write("Kutulara harfleri gir, boş kareleri boş bırak. Değişiklikler sağdaki tabloda anlık görünür.")
    st.write("ERTOLAND6'dan selamlar.")

with link_col:
    st.write("")
    st.write("")
    st.link_button("⚡ ERTOLAND6", YOUTUBE_LINK, use_container_width=True)


ust1, ust2 = st.columns([1, 3])

with ust1:
    if st.button("Boş Tahta", use_container_width=True):
        st.session_state.bekleyen_tahta = bos_tahta_olustur()
        sonuc_temizle()
        st.rerun()

with ust2:
    eldeki_harfler = st.text_input(
        "Elindeki harfler",
        value="",
        help="Joker için * kullan. Örnek: ABCD*EF"
    )


col1, col2 = st.columns([1.45, 1])

with col1:
    st.subheader("1) Tahtayı Düzenle")
    st.caption("Üstte sütun, solda satır numarası var. H2/H3/K2/K3 yazıları bonus kareleri silik gösterir. Orta kare yıldızdır.")

    with st.expander("📋 Toplu Tahta Girişi", expanded=False):
        st.caption("15 satır yaz. Her satır 15 karakter olsun. Boş kare için nokta kullan: .")

        toplu_tahta_metni = st.text_area(
            "Tahtayı buraya yapıştır",
            value="",
            height=260,
            placeholder=(
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "...............\n"
                "..............."
            )
        )

        if st.button("Toplu Tahtayı Uygula", use_container_width=True):
            try:
                yeni_tahta = metinden_tahta_olustur(toplu_tahta_metni)
                st.session_state.bekleyen_tahta = yeni_tahta
                sonuc_temizle()
                st.rerun()
            except Exception as hata:
                st.error(f"Hata: {hata}")

    baslik_kolonlari = st.columns([0.45] + [1 for _ in range(TAHTA_BOYUTU)])

    with baslik_kolonlari[0]:
        st.markdown(
            "<div style='height: 26px;'></div>",
            unsafe_allow_html=True
        )

    for sutun in range(TAHTA_BOYUTU):
        with baslik_kolonlari[sutun + 1]:
            st.markdown(
                f"""
                <div style='
                    text-align:center;
                    font-size:12px;
                    font-weight:800;
                    color:#666;
                    height:26px;
                    line-height:26px;
                '>{sutun}</div>
                """,
                unsafe_allow_html=True
            )

    for satir in range(TAHTA_BOYUTU):
        kolonlar = st.columns([0.45] + [1 for _ in range(TAHTA_BOYUTU)])

        with kolonlar[0]:
            st.markdown(
                f"""
                <div style='
                    text-align:center;
                    font-size:12px;
                    font-weight:800;
                    color:#666;
                    height:38px;
                    line-height:38px;
                '>{satir}</div>
                """,
                unsafe_allow_html=True
            )

        for sutun in range(TAHTA_BOYUTU):
            with kolonlar[sutun + 1]:
                st.text_input(
                    label=f"{satir}-{sutun}",
                    key=hucre_key(satir, sutun),
                    max_chars=1,
                    placeholder=bonus_yazisi(satir, sutun),
                    label_visibility="collapsed"
                )

    try:
        guncel_tahta = kutulardan_tahta_oku()
    except Exception:
        guncel_tahta = None

    hamle_bul = st.button("Hamle Bul", type="primary", use_container_width=True)

    if hamle_bul:
        try:
            tahta = kutulardan_tahta_oku()
            temiz_harfler = turkce_buyuk_harf(eldeki_harfler.replace(" ", ""))

            sozluk = sozluk_cache_yukle()

            baslangic = time.time()
            hamleler = hamleleri_bul(tahta, sozluk, temiz_harfler, puan_hesapla)
            bitis = time.time()

            st.session_state.hamleler = hamleler
            st.session_state.arama_yapildi = True
            st.session_state.arama_tahtasi = tahta
            st.session_state.arama_suresi = bitis - baslangic

        except Exception as hata:
            st.error(f"Hata: {hata}")


with col2:
    st.subheader("Tahta Önizleme")

    try:
        if guncel_tahta is not None:
            tahta_yazdir_web(guncel_tahta)
        else:
            st.warning("Tabloda hatalı hücre var.")
    except Exception as hata:
        st.error(str(hata))

    st.divider()

    st.subheader("Sonuç")

    if not st.session_state.arama_yapildi:
        st.info("Hamle görmek için soldan **Hamle Bul** butonuna bas.")

    elif not st.session_state.hamleler:
        st.warning("Uygun hamle bulunamadı.")

    else:
        hamleler = st.session_state.hamleler
        tahta = st.session_state.arama_tahtasi

        st.success(
            f"{len(hamleler)} hamle bulundu. "
            f"Süre: {st.session_state.arama_suresi:.2f} saniye"
        )

        en_iyi_hamle = hamleler[0]
        yeni_tahta = hamleyi_tahtada_goster(tahta, en_iyi_hamle)

        st.markdown("### En İyi Hamle")
        st.write("**" + hamle_bilgisi_yaz(en_iyi_hamle) + "**")

        st.caption("Yeşil kareler yeni koyulacak harfleri gösterir.")
        tahta_yazdir_web(yeni_tahta, orijinal_tahta=tahta)

        if st.button("En İyi Hamleyi Tabloya İşle", type="primary", use_container_width=True):
            st.session_state.bekleyen_tahta = yeni_tahta
            sonuc_temizle()
            st.rerun()

        with st.expander("İlk 20 Hamle"):
            for index, hamle in enumerate(hamleler[:20], start=1):
                st.write(f"{index}. {hamle_bilgisi_yaz(hamle)}")