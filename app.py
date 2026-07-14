import io
import time
import streamlit as st

from main import sozluk_yukle, turkce_buyuk_harf, puan_hesapla
from solver import hamleleri_bul, hamleyi_tahtada_goster
from bonus import TAHTA_BONUSLARI


YOUTUBE_LINK = "https://youtu.be/EUJmdhJiNBw?t=43"

TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")
TAHTA_BOYUTU = 15


st.set_page_config(
    page_title="Kelimelik Yardımcı",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
        :root {
            --bg: #061a33;
            --panel: #0b2447;
            --panel-soft: #12325b;
            --border: #214a7a;
            --text: #f7f9fc;
            --muted: #b8c7da;
            --accent: #f2c230;
            --accent-strong: #ffd84d;
            --input: #071426;
            --tile: #17375e;
            --tile-border: #315a8b;
            --old: #f3d66b;
            --new: #7fb3e6;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(242, 194, 48, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(38, 94, 166, 0.16), transparent 24%),
                var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        h1, h2, h3, h4, p, label, span {
            color: var(--text);
        }

        .hero {
            background: linear-gradient(135deg, #0a2143, #123a6b);
            border: 1px solid #2b5688;
            border-radius: 22px;
            padding: 25px 28px;
            margin-bottom: 16px;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.16);
        }

        .hero-title {
            font-size: 31px;
            line-height: 1.1;
            font-weight: 900;
            letter-spacing: -0.6px;
            color: #f3f8f6;
        }

        .hero-text {
            margin-top: 9px;
            color: #c7d4e5;
            font-size: 14px;
        }

        .brand-box {
            background: linear-gradient(135deg, #0d2b54, #123f78);
            border: 1px solid #2f5e95;
            border-radius: 14px;
            padding: 10px 13px;
            min-height: 70px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .brand-name {
            color: #ffd84d;
            font-size: 15px;
            font-weight: 900;
            letter-spacing: .08em;
            line-height: 1.1;
        }

        .brand-subtitle {
            color: #b8c9df;
            font-size: 10px;
            margin-top: 4px;
            letter-spacing: .04em;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(11, 36, 71, 0.97);
            border: 1px solid var(--border) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.13);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.15rem 0.2rem;
        }

        .eyebrow {
            color: #f2c230;
            font-size: 11px;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: .10em;
            margin-bottom: 3px;
        }

        .section-title {
            color: #eff6f4;
            font-size: 22px;
            line-height: 1.25;
            font-weight: 850;
            margin-bottom: 2px;
        }

        .section-help {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 10px;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label {
            color: #eef4fb !important;
            font-weight: 750 !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: var(--input) !important;
            color: #f5fbf9 !important;
            border: 1.5px solid #315a8b !important;
            border-radius: 10px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.02);
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #7189a8 !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stTextArea"] textarea:hover {
            border-color: #f2c230 !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ffd84d !important;
            box-shadow: 0 0 0 3px rgba(255, 216, 77, 0.14) !important;
        }

        div.stButton > button,
        a[data-testid="stLinkButton"] {
            min-height: 44px;
            border-radius: 11px !important;
            border: 1px solid #315a8b !important;
            background: #102b50 !important;
            color: #f5f8fc !important;
            font-weight: 800 !important;
            transition: 0.18s ease;
        }

        div.stButton > button:hover,
        a[data-testid="stLinkButton"]:hover {
            transform: translateY(-1px);
            border-color: #f2c230 !important;
            background: #173e70 !important;
            box-shadow: 0 8px 18px rgba(0,0,0,.14);
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #f2c230, #ffd84d) !important;
            border-color: #ffd84d !important;
            color: #0a2143 !important;
            min-height: 50px;
            font-size: 16px;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #ffd84d, #ffe77f) !important;
        }

        div[data-testid="stExpander"] {
            background: #0c2342;
            border: 1px solid #2b5688;
            border-radius: 12px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        .result-box {
            background: #102b50;
            border: 1px solid #2f67a3;
            border-radius: 14px;
            padding: 16px 17px;
            margin-bottom: 12px;
        }

        .result-word {
            color: #ffd84d;
            font-size: 29px;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .result-meta {
            color: #c9d7e7;
            font-size: 13px;
            line-height: 1.7;
            margin-top: 4px;
        }

        .board-wrap {
            overflow-x: auto;
            padding: 2px 0 6px;
        }

        .board-with-coords {
            display: grid;
            grid-template-columns: 24px repeat(15, 31px);
            gap: 3px;
            align-items: center;
            width: max-content;
        }

        .coord {
            width: 31px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9fb3ca;
            font-size: 10px;
            font-weight: 800;
        }

        .row-coord {
            width: 24px;
            height: 31px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9fb3ca;
            font-size: 10px;
            font-weight: 800;
        }

        .cell {
            width: 31px;
            height: 31px;
            border-radius: 7px;
            background: #17375e;
            border: 1px solid #315a8b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 16px;
            color: #e9f0ee;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }

        .bonus-ghost {
            color: #8ea8c4;
            font-size: 9px;
            font-weight: 900;
        }

        .center-star {
            color: #ffd84d;
            font-size: 15px;
            font-weight: 900;
        }

        .filled-old {
            background: var(--old);
            border-color: #d5b22b;
            color: #3b2f00;
        }

        .filled-new {
            background: var(--new);
            border: 2px solid #2f6fa8;
            color: #0b2d4f;
        }

        .board-input div[data-testid="stTextInput"] input {
            text-align: center !important;
            font-weight: 900 !important;
            font-size: 16px !important;
            padding: 0 !important;
            height: 38px !important;
            background: #071426 !important;
            border: 1.5px solid #315a8b !important;
        }

        .board-input div[data-testid="stTextInput"] input:focus {
            border-color: #ffd84d !important;
            box-shadow: 0 0 0 2px rgba(255,216,77,.16) !important;
        }

        div[data-testid="stFileUploader"] {
            background: #071426;
            border: 1.5px dashed #315a8b;
            border-radius: 12px;
            padding: 10px;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: #f2c230;
        }

        div[data-testid="stFileUploader"] section {
            background: transparent !important;
            border: none !important;
        }

        .image-note {
            background: #0c2342;
            border: 1px solid #2b5688;
            border-radius: 11px;
            padding: 10px 12px;
            color: #b8c7da;
            font-size: 12px;
            line-height: 1.55;
            margin-bottom: 10px;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: .65rem;
                padding-right: .65rem;
            }

            .hero-title {
                font-size: 26px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def sozluk_cache_yukle():
    return sozluk_yukle("kelimeler.txt")


def bos_tahta_olustur():
    return [["." for _ in range(TAHTA_BOYUTU)] for _ in range(TAHTA_BOYUTU)]


def hucre_key(satir, sutun):
    return f"hucre_{satir}_{sutun}"


def tahta_state_baslat():
    varsayilanlar = {
        "hamleler": [],
        "arama_yapildi": False,
        "arama_tahtasi": None,
        "arama_suresi": 0,
        "arama_hatasi": None,
        "bekleyen_tahta": None,
        "ekran_goruntusu_bytes": None,
        "ekran_goruntusu_kaynagi": None,
        "eldeki_harfler": "",
    }

    for anahtar, deger in varsayilanlar.items():
        if anahtar not in st.session_state:
            st.session_state[anahtar] = deger

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
    st.session_state.arama_hatasi = None


def tahtayi_kutulara_yaz(tahta):
    for satir in range(TAHTA_BOYUTU):
        for sutun in range(TAHTA_BOYUTU):
            hucre = tahta[satir][sutun]
            st.session_state[hucre_key(satir, sutun)] = "" if hucre == "." else hucre


def bekleyen_tahtayi_uygula():
    if st.session_state.bekleyen_tahta is not None:
        tahtayi_kutulara_yaz(st.session_state.bekleyen_tahta)
        st.session_state.bekleyen_tahta = None


def kutulardan_tahta_oku():
    tahta = []

    for satir in range(TAHTA_BOYUTU):
        tahta_satiri = []

        for sutun in range(TAHTA_BOYUTU):
            deger = str(
                st.session_state.get(hucre_key(satir, sutun), "")
            ).strip()

            if deger == "" or deger == ".":
                tahta_satiri.append(".")
                continue

            deger = turkce_buyuk_harf(deger)

            if len(deger) != 1:
                raise ValueError(f"{satir}. satır {sutun}. sütunda tek harf olmalı.")

            if deger not in TURKCE_HARFLER:
                raise ValueError(
                    f"{satir}. satır {sutun}. sütunda geçersiz karakter var: {deger}"
                )

            tahta_satiri.append(deger)

        tahta.append(tahta_satiri)

    return tahta


def metinden_tahta_ve_harfler_olustur(tahta_metni):
    satirlar = []

    for satir in tahta_metni.splitlines():
        temiz_satir = satir.strip()

        if temiz_satir == "":
            continue

        for karakter in (" ", "\t"):
            temiz_satir = temiz_satir.replace(karakter, "")

        temiz_satir = turkce_buyuk_harf(temiz_satir)
        satirlar.append(temiz_satir)

    if len(satirlar) not in (TAHTA_BOYUTU, TAHTA_BOYUTU + 1):
        raise ValueError(
            "Metin 15 veya 16 satır olmalı. "
            f"Şu an {len(satirlar)} satır var."
        )

    tahta_satirlari = satirlar[:TAHTA_BOYUTU]
    eldeki_harfler = ""

    if len(satirlar) == TAHTA_BOYUTU + 1:
        eldeki_harfler = satirlar[-1]

        if len(eldeki_harfler) > 7:
            raise ValueError(
                "16. satırdaki eldeki taşlar en fazla 7 karakter olmalı."
            )

        for karakter in eldeki_harfler:
            if karakter != "*" and karakter not in TURKCE_HARFLER:
                raise ValueError(
                    f"16. satırda geçersiz karakter var: {karakter}"
                )

    tahta = []

    for satir_no, satir in enumerate(tahta_satirlari):
        for karakter in ("-", "_", "·", "*", "★"):
            satir = satir.replace(karakter, ".")

        if len(satir) != TAHTA_BOYUTU:
            raise ValueError(
                f"{satir_no}. satır tam 15 karakter olmalı. "
                f"Şu an {len(satir)} karakter var."
            )

        tahta_satiri = []

        for sutun_no, karakter in enumerate(satir):
            if karakter == ".":
                tahta_satiri.append(".")
            elif karakter in TURKCE_HARFLER:
                tahta_satiri.append(karakter)
            else:
                raise ValueError(
                    f"{satir_no}. satır {sutun_no}. sütunda "
                    f"geçersiz karakter var: {karakter}"
                )

        tahta.append(tahta_satiri)

    return tahta, eldeki_harfler



def hamle_arama_yap():
    st.session_state.arama_hatasi = None

    try:
        tahta = kutulardan_tahta_oku()

        eldeki_harfler = str(
            st.session_state.get("eldeki_harfler", "")
        ).replace(" ", "")

        temiz_harfler = turkce_buyuk_harf(eldeki_harfler)

        if not temiz_harfler:
            raise ValueError("Önce elindeki taşları gir kanka.")

        for karakter in temiz_harfler:
            if karakter != "*" and karakter not in TURKCE_HARFLER:
                raise ValueError(
                    f"Elindeki taşlarda geçersiz karakter var: {karakter}"
                )

        sozluk = sozluk_cache_yukle()

        baslangic = time.time()
        hamleler = hamleleri_bul(
            tahta,
            sozluk,
            temiz_harfler,
            puan_hesapla
        )
        bitis = time.time()

        st.session_state.hamleler = hamleler or []
        st.session_state.arama_yapildi = True
        st.session_state.arama_tahtasi = tahta
        st.session_state.arama_suresi = bitis - baslangic

    except Exception as hata:
        st.session_state.hamleler = []
        st.session_state.arama_yapildi = False
        st.session_state.arama_tahtasi = None
        st.session_state.arama_suresi = 0
        st.session_state.arama_hatasi = str(hata)



def ekran_goruntusunu_kaydet(gorsel, kaynak):
    if gorsel is None:
        return

    if hasattr(gorsel, "getvalue"):
        gorsel_bytes = gorsel.getvalue()
    else:
        tampon = io.BytesIO()
        gorsel.save(tampon, format="PNG")
        gorsel_bytes = tampon.getvalue()

    st.session_state.ekran_goruntusu_bytes = gorsel_bytes
    st.session_state.ekran_goruntusu_kaynagi = kaynak


def ekran_goruntusunu_temizle():
    st.session_state.ekran_goruntusu_bytes = None
    st.session_state.ekran_goruntusu_kaynagi = None


def bonus_yazisi(satir, sutun):
    if satir == 7 and sutun == 7:
        return "★"

    bonus = TAHTA_BONUSLARI[satir][sutun]
    return "" if bonus == "." else bonus


def tahta_yazdir_web(tahta, orijinal_tahta=None):
    html = '<div class="board-wrap"><div class="board-with-coords"><div></div>'

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
                    html += (
                        f'<div class="cell">'
                        f'<span class="bonus-ghost">{bonus}</span>'
                        f'</div>'
                    )
            else:
                yeni_harf_mi = (
                    orijinal_tahta is not None
                    and orijinal_tahta[satir_index][sutun_index] == "."
                )

                sinif = "filled-new" if yeni_harf_mi else "filled-old"
                html += f'<div class="cell {sinif}">{hucre}</div>'

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def hamle_bilgisi_yaz(hamle):
    return (
        f"Satır {hamle['satir']} · "
        f"Sütun {hamle['sutun']} · "
        f"{hamle['yon']} · "
        f"{hamle['puan']} puan · "
        f"Kullanılan: {hamle.get('kullanilan_harfler', '')}"
    )


tahta_state_baslat()
bekleyen_tahtayi_uygula()


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">💛💙 EN İYİ HAMLENİ BUL</div>
        <div class="hero-text">
            Tahtayı kur kanka, harflerini gir; en sağlam hamleyi beraber bulalım.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


with st.container(border=True):
    st.markdown('<div class="eyebrow">Maç Öncesi Hazırlık</div>', unsafe_allow_html=True)

    kontrol1, kontrol2, kontrol3 = st.columns([1, 2.4, 1])

    with kontrol1:
        if st.button("🧹 Tahtayı Sıfırla", use_container_width=True):
            st.session_state.bekleyen_tahta = bos_tahta_olustur()
            sonuc_temizle()
            st.rerun()

    with kontrol2:
        eldeki_harfler = st.text_input(
            "Elindeki taşlar",
            key="eldeki_harfler",
            placeholder="Mesela: ÇJÜLLK ya da ABCD*EF",
            help="Joker varsa * koy kanka."
        )

    with kontrol3:
        st.markdown(
            """
            <div class="brand-box">
                <div class="brand-name">⚡ ERTOLAND6</div>
                <div class="brand-subtitle">KELİMELİK ASSISTANT</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.link_button(
            "▶ YouTube",
            YOUTUBE_LINK,
            use_container_width=True
        )


sol_kolon, sag_kolon = st.columns([1.55, 1], gap="large")


with sol_kolon:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Saha Kurulumu</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tahtayı Kur</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'İstersen tek tek gir, istersen 15x15 tahtayı topluca yapıştır kanka.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.expander("📋 Toplu Saha Kurulumu", expanded=False):
            st.caption(
                "İlk 15 satır tahtadır ve her satır 15 karakter olmalı. "
                "İstersen 16. satıra elindeki taşları yazabilirsin. "
                "16. satır yoksa taşları yukarıdan manuel girersin."
            )

            toplu_tahta_metni = st.text_area(
                "Tahta metni",
                value="",
                height=250,
                placeholder=(
                    "\n".join(["." * 15 for _ in range(15)])
                    + "\nABCÇ*EF"
                )
            )

            if st.button("📥 Tahtaya Aktar", use_container_width=True):
                try:
                    yeni_tahta, yeni_harfler = metinden_tahta_ve_harfler_olustur(
                        toplu_tahta_metni
                    )

                    st.session_state.bekleyen_tahta = yeni_tahta

                    if yeni_harfler:
                        st.session_state.eldeki_harfler = yeni_harfler

                    sonuc_temizle()
                    st.rerun()
                except Exception as hata:
                    st.error(f"Hata: {hata}")

        baslik_kolonlari = st.columns(
            [0.45] + [1 for _ in range(TAHTA_BOYUTU)],
            gap="small"
        )

        with baslik_kolonlari[0]:
            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        for sutun in range(TAHTA_BOYUTU):
            with baslik_kolonlari[sutun + 1]:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-size:10px;
                        font-weight:850;
                        color:#90a29d;
                        height:24px;
                        line-height:24px;
                    ">{sutun}</div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('<div class="board-input">', unsafe_allow_html=True)

        for satir in range(TAHTA_BOYUTU):
            kolonlar = st.columns(
                [0.45] + [1 for _ in range(TAHTA_BOYUTU)],
                gap="small"
            )

            with kolonlar[0]:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-size:10px;
                        font-weight:850;
                        color:#90a29d;
                        height:38px;
                        line-height:38px;
                    ">{satir}</div>
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

        st.markdown("</div>", unsafe_allow_html=True)

    try:
        guncel_tahta = kutulardan_tahta_oku()
    except Exception:
        guncel_tahta = None


with sag_kolon:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Ekran Görüntüsü</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Görseli Ekle</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Bilgisayarından ekran görüntüsünü seçip yükleyebilirsin.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="image-note">
                Windows: <b>Win + Shift + S</b> ile ekran görüntüsünü al.<br>
                Ardından görseli kaydedip aşağıdaki alandan seç.
            </div>
            """,
            unsafe_allow_html=True
        )

        dosyadan_gorsel = st.file_uploader(
            "Dosyadan ekran görüntüsü seç",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            help="PNG, JPG, JPEG veya WEBP yükleyebilirsin."
        )

        if dosyadan_gorsel is not None:
            ekran_goruntusunu_kaydet(dosyadan_gorsel, "Dosyadan seçildi")

        st.caption(
            "Şimdilik görseli dosyadan seç. "
            "Ctrl+V ile doğrudan yapıştırmayı sonraki adımda daha sağlam şekilde ekleyeceğiz."
        )

        if st.session_state.ekran_goruntusu_bytes is not None:
            st.success(
                f"Görsel hazır: {st.session_state.ekran_goruntusu_kaynagi}"
            )
            st.image(
                st.session_state.ekran_goruntusu_bytes,
                caption="OCR için kullanılacak ekran görüntüsü",
                use_container_width=True
            )

            if st.button(
                "🗑️ Görseli Kaldır",
                use_container_width=True,
                key="ekran_goruntusunu_kaldir"
            ):
                ekran_goruntusunu_temizle()
                st.rerun()
        else:
            st.info("Henüz bir ekran görüntüsü eklenmedi.")

    with st.container(border=True):
        st.markdown('<div class="eyebrow">Anlık Görünüm</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tahtanın Son Hali</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Yazdığın her harf burada anında görünür kanka.'
            '</div>',
            unsafe_allow_html=True
        )

        try:
            if guncel_tahta is not None:
                tahta_yazdir_web(guncel_tahta)
            else:
                st.warning("Tabloda hatalı bir hücre var.")
        except Exception as hata:
            st.error(str(hata))

    with st.container(border=True):
        st.markdown('<div class="eyebrow">Hamle Motoru</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Hazırsan Başlayalım</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Tahta tamamsa ve taşlarını girdiysen bas düğmeye, gerisini bize bırak.'
            '</div>',
            unsafe_allow_html=True
        )

        st.button(
            "🚀 EN SAĞLAM HAMLEYİ BUL",
            type="primary",
            use_container_width=True,
            on_click=hamle_arama_yap,
            key="en_saglam_hamleyi_bul"
        )

        if st.session_state.arama_hatasi:
            st.error(f"Hata: {st.session_state.arama_hatasi}")

    with st.container(border=True):
        st.markdown('<div class="eyebrow">Maç Sonucu</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Sana Önerdiğim Hamle</div>', unsafe_allow_html=True)

        if not st.session_state.arama_yapildi:
            st.info("Hamleyi görmek için **En Sağlam Hamleyi Bul** butonuna bas.")

        elif not st.session_state.hamleler:
            st.warning("Bu elde uygun hamle çıkmadı kanka.")

        else:
            hamleler = st.session_state.hamleler
            tahta = st.session_state.arama_tahtasi

            en_iyi_hamle = hamleler[0]
            yeni_tahta = hamleyi_tahtada_goster(tahta, en_iyi_hamle)

            st.markdown(
                f"""
                <div class="result-box">
                    <div class="result-word">{en_iyi_hamle['kelime']}</div>
                    <div class="result-meta">
                        {hamle_bilgisi_yaz(en_iyi_hamle)}<br>
                        {len(hamleler)} hamle bulundu ·
                        {st.session_state.arama_suresi:.2f} saniye
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption("Mavi kareler yeni koyacağın harfleri gösteriyor kanka.")
            tahta_yazdir_web(yeni_tahta, orijinal_tahta=tahta)

            if st.button(
                "✅ Bu Hamleyi Tahtaya İşle",
                type="primary",
                use_container_width=True
            ):
                st.session_state.bekleyen_tahta = yeni_tahta
                sonuc_temizle()
                st.rerun()

            with st.expander("Diğer Güzel Hamleleri Göster"):
                for index, hamle in enumerate(hamleler[:20], start=1):
                    st.write(
                        f"**{index}. {hamle['kelime']}** — "
                        f"{hamle_bilgisi_yaz(hamle)}"
                    )