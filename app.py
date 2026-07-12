import time
import pandas as pd
import streamlit as st

from main import sozluk_yukle, turkce_buyuk_harf, puan_hesapla
from solver import hamleleri_bul, hamleyi_tahtada_goster


YOUTUBE_LINK = "https://www.youtube.com/watch?v=GGtVmxTFJ2E&list=LL&index=72"


st.set_page_config(
    page_title="Kelimelik Yardımcı",
    page_icon="🧩",
    layout="wide"
)


TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")


ORNEK_TAHTA = """...............
...............
...............
...............
...............
...............
...............
...............
...............
...............
...............
...............
...............
...............
..............."""


def bos_tahta_olustur():
    return [["" for _ in range(15)] for _ in range(15)]


def metinden_tahta_listesi_olustur(tahta_metni):
    satirlar = tahta_metni.strip().splitlines()

    if len(satirlar) != 15:
        raise ValueError("Tahta tam 15 satır olmalı.")

    tahta = []

    for satir in satirlar:
        satir = turkce_buyuk_harf(satir.strip().replace(" ", ""))

        if len(satir) != 15:
            raise ValueError("Her satır tam 15 karakter olmalı.")

        tahta_satiri = []

        for karakter in satir:
            if karakter == ".":
                tahta_satiri.append("")
            elif karakter in TURKCE_HARFLER:
                tahta_satiri.append(karakter)
            else:
                raise ValueError(f"Geçersiz karakter var: {karakter}")

        tahta.append(tahta_satiri)

    return tahta


def listeyi_dataframe_yap(tahta_listesi):
    return pd.DataFrame(
        tahta_listesi,
        columns=[str(i) for i in range(15)],
        index=[str(i) for i in range(15)]
    )


def tahta_nokta_to_dataframe(tahta):
    yeni_tahta = []

    for satir in tahta:
        yeni_satir = []

        for hucre in satir:
            if hucre == ".":
                yeni_satir.append("")
            else:
                yeni_satir.append(hucre)

        yeni_tahta.append(yeni_satir)

    return listeyi_dataframe_yap(yeni_tahta)


def dataframe_tahta_yap(df):
    tahta = []

    for satir_index in range(15):
        tahta_satiri = []

        for sutun_index in range(15):
            deger = df.iloc[satir_index, sutun_index]

            if pd.isna(deger):
                deger = ""

            deger = str(deger).strip()

            if deger == "" or deger == ".":
                tahta_satiri.append(".")
                continue

            deger = turkce_buyuk_harf(deger)

            if len(deger) != 1:
                raise ValueError(
                    f"{satir_index}. satır {sutun_index}. sütunda tek harf olmalı."
                )

            if deger not in TURKCE_HARFLER:
                raise ValueError(
                    f"{satir_index}. satır {sutun_index}. sütunda geçersiz karakter var: {deger}"
                )

            tahta_satiri.append(deger)

        tahta.append(tahta_satiri)

    return tahta


def tahta_yazdir_web(tahta, orijinal_tahta=None):
    html = """
    <style>
        .board {
            display: grid;
            grid-template-columns: repeat(15, 30px);
            gap: 3px;
            margin-top: 10px;
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
    <div class="board">
    """

    for satir_index, satir in enumerate(tahta):
        for sutun_index, hucre in enumerate(satir):
            if hucre == ".":
                html += '<div class="cell"></div>'
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


@st.cache_data
def sozluk_cache_yukle():
    return sozluk_yukle("kelimeler.txt")


def sonuc_temizle():
    st.session_state.hamleler = []
    st.session_state.arama_yapildi = False
    st.session_state.arama_tahtasi = None
    st.session_state.arama_suresi = 0


def editor_yenile(yeni_df):
    st.session_state.tahta_df = yeni_df
    st.session_state.editor_key_no += 1


if "editor_key_no" not in st.session_state:
    st.session_state.editor_key_no = 0

if "tahta_df" not in st.session_state:
    st.session_state.tahta_df = listeyi_dataframe_yap(
        metinden_tahta_listesi_olustur(ORNEK_TAHTA)
    )

if "hamleler" not in st.session_state:
    st.session_state.hamleler = []

if "arama_yapildi" not in st.session_state:
    st.session_state.arama_yapildi = False

if "arama_tahtasi" not in st.session_state:
    st.session_state.arama_tahtasi = None

if "arama_suresi" not in st.session_state:
    st.session_state.arama_suresi = 0


baslik_col, link_col = st.columns([4, 1])

with baslik_col:
    st.title("🧩 EN İYİ HAMLENİ GÖR")
    st.write("Kutulara harfleri gir, boş kareleri boş bırak. Değişiklikler sağdaki tabloda anlık görünür.")
    st.write("ERTOLAND6'dan selamlar.")

with link_col:
    st.write("")
    st.write("")
    st.link_button("⚡ ERTOLAND6", YOUTUBE_LINK, use_container_width=True)


ust1, ust2, ust3 = st.columns([1, 1, 2])

with ust1:
    if st.button("Boş Tahta", use_container_width=True):
        editor_yenile(listeyi_dataframe_yap(bos_tahta_olustur()))
        sonuc_temizle()
        st.rerun()

with ust2:
    if st.button("Örnek Tahta", use_container_width=True):
        editor_yenile(
            listeyi_dataframe_yap(metinden_tahta_listesi_olustur(ORNEK_TAHTA))
        )
        sonuc_temizle()
        st.rerun()

with ust3:
    eldeki_harfler = st.text_input(
        "Elindeki harfler",
        value="",
        help="Joker için * kullan. Örnek: ABCD*EF"
    )


col1, col2 = st.columns([1.35, 1])

with col1:
    st.subheader("1) Tahtayı Düzenle")
    st.caption("Her kutuya en fazla 1 harf yaz. Boş kareleri boş bırak.")

    editor_key = f"tahta_editor_{st.session_state.editor_key_no}"

    duzenlenen_df = st.data_editor(
        st.session_state.tahta_df,
        num_rows="fixed",
        use_container_width=True,
        height=520,
        key=editor_key
    )

    try:
        guncel_tahta = dataframe_tahta_yap(duzenlenen_df)
    except Exception:
        guncel_tahta = None

    hamle_bul = st.button("Hamle Bul", type="primary", use_container_width=True)

    if hamle_bul:
        try:
            st.session_state.tahta_df = duzenlenen_df

            tahta = dataframe_tahta_yap(duzenlenen_df)
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
            yeni_df = tahta_nokta_to_dataframe(yeni_tahta)
            editor_yenile(yeni_df)
            sonuc_temizle()
            st.rerun()

        with st.expander("İlk 20 Hamle"):
            for index, hamle in enumerate(hamleler[:20], start=1):
                st.write(f"{index}. {hamle_bilgisi_yaz(hamle)}")