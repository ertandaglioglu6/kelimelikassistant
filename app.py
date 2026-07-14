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
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
        :root {
            --bg: #18201f;
            --panel: #222c2a;
            --panel-soft: #293432;
            --border: #3a4744;
            --text: #edf4f2;
            --muted: #a9b8b4;
            --accent: #77a89b;
            --accent-strong: #8fc2b4;
            --input: #111817;
            --tile: #34403d;
            --tile-border: #56635f;
            --old: #d6c58f;
            --new: #8fc7a7;
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(119, 168, 155, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(79, 113, 105, 0.10), transparent 24%),
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
            background: linear-gradient(135deg, #263331, #32423e);
            border: 1px solid #40514d;
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
            color: #b9c8c4;
            font-size: 14px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(34, 44, 42, 0.96);
            border: 1px solid var(--border) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.13);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.15rem 0.2rem;
        }

        .eyebrow {
            color: #8fa39e;
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
            color: #d7e3df !important;
            font-weight: 750 !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            background: var(--input) !important;
            color: #f5fbf9 !important;
            border: 1.5px solid #53645f !important;
            border-radius: 10px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.02);
        }

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #6f817c !important;
            opacity: 1 !important;
        }

        div[data-testid="stTextInput"] input:hover,
        div[data-testid="stTextArea"] textarea:hover {
            border-color: #739087 !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--accent-strong) !important;
            box-shadow: 0 0 0 3px rgba(143, 194, 180, 0.14) !important;
        }

        div.stButton > button,
        a[data-testid="stLinkButton"] {
            min-height: 44px;
            border-radius: 11px !important;
            border: 1px solid #55635f !important;
            background: #2b3634 !important;
            color: #e9f1ef !important;
            font-weight: 800 !important;
            transition: 0.18s ease;
        }

        div.stButton > button:hover,
        a[data-testid="stLinkButton"]:hover {
            transform: translateY(-1px);
            border-color: #78928b !important;
            background: #34413e !important;
            box-shadow: 0 8px 18px rgba(0,0,0,.14);
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6e9f92, #82b3a6) !important;
            border-color: #8ab9ad !important;
            color: #10201c !important;
            min-height: 50px;
            font-size: 16px;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #7daf9f, #91c4b6) !important;
        }

        div[data-testid="stExpander"] {
            background: #1e2826;
            border: 1px solid #3d4b47;
            border-radius: 12px;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        .result-box {
            background: #23342f;
            border: 1px solid #3e6258;
            border-radius: 14px;
            padding: 16px 17px;
            margin-bottom: 12px;
        }

        .result-word {
            color: #a9d7c3;
            font-size: 29px;
            font-weight: 900;
            letter-spacing: 1px;
        }

        .result-meta {
            color: #b7c6c2;
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
            color: #90a29d;
            font-size: 10px;
            font-weight: 800;
        }

        .row-coord {
            width: 24px;
            height: 31px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #90a29d;
            font-size: 10px;
            font-weight: 800;
        }

        .cell {
            width: 31px;
            height: 31px;
            border-radius: 7px;
            background: var(--tile);
            border: 1px solid var(--tile-border);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 16px;
            color: #e9f0ee;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
        }

        .bonus-ghost {
            color: #859590;
            font-size: 9px;
            font-weight: 900;
        }

        .center-star {
            color: #c2ae73;
            font-size: 15px;
            font-weight: 900;
        }

        .filled-old {
            background: var(--old);
            border-color: #b6a675;
            color: #4f452c;
        }

        .filled-new {
            background: var(--new);
            border: 2px solid #659b7b;
            color: #1f4634;
        }

        .board-input div[data-testid="stTextInput"] input {
            text-align: center !important;
            font-weight: 900 !important;
            font-size: 16px !important;
            padding: 0 !important;
            height: 38px !important;
            background: #111817 !important;
            border: 1.5px solid #5c6b67 !important;
        }

        .board-input div[data-testid="stTextInput"] input:focus {
            border-color: #9acbbb !important;
            box-shadow: 0 0 0 2px rgba(154,203,187,.16) !important;
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
        "bekleyen_tahta": None,
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


def metinden_tahta_olustur(tahta_metni):
    satirlar = []

    for satir in tahta_metni.splitlines():
        temiz_satir = satir.strip()

        if temiz_satir == "":
            continue

        for karakter in (" ", "\t"):
            temiz_satir = temiz_satir.replace(karakter, "")

        for karakter in ("-", "_", "·", "*", "★"):
            temiz_satir = temiz_satir.replace(karakter, ".")

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

    return tahta


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
        <div class="hero-title">🧩 EN İYİ HAMLENİ GÖR</div>
        <div class="hero-text">
            Tahtayı doldur, elindeki harfleri gir ve en yüksek puanlı hamleyi bul.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


with st.container(border=True):
    st.markdown('<div class="eyebrow">Hızlı Kontroller</div>', unsafe_allow_html=True)

    kontrol1, kontrol2, kontrol3 = st.columns([1, 2.4, 1])

    with kontrol1:
        if st.button("🧹 Tahtayı Temizle", use_container_width=True):
            st.session_state.bekleyen_tahta = bos_tahta_olustur()
            sonuc_temizle()
            st.rerun()

    with kontrol2:
        eldeki_harfler = st.text_input(
            "Elindeki harfler",
            value="",
            placeholder="Örnek: ÇJÜLLK veya ABCD*EF",
            help="Joker için * kullan."
        )

    with kontrol3:
        st.link_button(
            "⚡ ERTOLAND6",
            YOUTUBE_LINK,
            use_container_width=True
        )


sol_kolon, sag_kolon = st.columns([1.55, 1], gap="large")


with sol_kolon:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Tahta Girişi</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tahtayı Düzenle</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Kutulara tek tek harf girebilir veya toplu tahta metnini yapıştırabilirsin.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.expander("📋 Toplu Tahta Girişi", expanded=False):
            st.caption(
                "15 satır ve her satırda 15 karakter olmalı. "
                "Boş kare için nokta (.) kullan."
            )

            toplu_tahta_metni = st.text_area(
                "Tahta metni",
                value="",
                height=250,
                placeholder="\n".join(["." * 15 for _ in range(15)])
            )

            if st.button("📥 Metni Tahtaya Uygula", use_container_width=True):
                try:
                    yeni_tahta = metinden_tahta_olustur(toplu_tahta_metni)
                    st.session_state.bekleyen_tahta = yeni_tahta
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
        st.markdown('<div class="eyebrow">Canlı Görünüm</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tahta Önizleme</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Girdiğin harfler burada anlık olarak görünür.'
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
        st.markdown('<div class="section-title">Hamleyi Hesapla</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-help">'
            'Tahta hazırsa ve harflerini girdiysen aşağıdaki butona bas.'
            '</div>',
            unsafe_allow_html=True
        )

        hamle_bul = st.button(
            "🚀 EN İYİ HAMLEYİ BUL",
            type="primary",
            use_container_width=True
        )

        if hamle_bul:
            try:
                tahta = kutulardan_tahta_oku()
                temiz_harfler = turkce_buyuk_harf(
                    eldeki_harfler.replace(" ", "")
                )

                if not temiz_harfler:
                    raise ValueError("Önce elindeki harfleri gir.")

                sozluk = sozluk_cache_yukle()

                baslangic = time.time()
                hamleler = hamleleri_bul(
                    tahta,
                    sozluk,
                    temiz_harfler,
                    puan_hesapla
                )
                bitis = time.time()

                st.session_state.hamleler = hamleler
                st.session_state.arama_yapildi = True
                st.session_state.arama_tahtasi = tahta
                st.session_state.arama_suresi = bitis - baslangic

            except Exception as hata:
                st.error(f"Hata: {hata}")

    with st.container(border=True):
        st.markdown('<div class="eyebrow">Sonuç</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Önerilen Hamle</div>', unsafe_allow_html=True)

        if not st.session_state.arama_yapildi:
            st.info("Sonuç görmek için **En İyi Hamleyi Bul** butonuna bas.")

        elif not st.session_state.hamleler:
            st.warning("Uygun hamle bulunamadı.")

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

            st.caption("Yeşil kareler yeni koyulacak harfleri gösterir.")
            tahta_yazdir_web(yeni_tahta, orijinal_tahta=tahta)

            if st.button(
                "✅ En İyi Hamleyi Tabloya İşle",
                type="primary",
                use_container_width=True
            ):
                st.session_state.bekleyen_tahta = yeni_tahta
                sonuc_temizle()
                st.rerun()

            with st.expander("İlk 20 Hamleyi Göster"):
                for index, hamle in enumerate(hamleler[:20], start=1):
                    st.write(
                        f"**{index}. {hamle['kelime']}** — "
                        f"{hamle_bilgisi_yaz(hamle)}"
                    )