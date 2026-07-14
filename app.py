


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
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(71, 118, 230, 0.10), transparent 34%),
                radial-gradient(circle at top right, rgba(142, 84, 233, 0.10), transparent 28%),
                #f6f8fc;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .hero-card {
            background: linear-gradient(135deg, #1f2937 0%, #334155 50%, #4338ca 100%);
            border-radius: 24px;
            padding: 28px 30px;
            margin-bottom: 18px;
            box-shadow: 0 18px 45px rgba(30, 41, 59, 0.18);
            color: white;
        }

        .hero-title {
            font-size: 34px;
            font-weight: 900;
            margin: 0;
            letter-spacing: -0.8px;
        }

        .hero-subtitle {
            margin-top: 8px;
            margin-bottom: 0;
            color: rgba(255, 255, 255, 0.78);
            font-size: 15px;
        }

        .section-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 20px;
            padding: 18px;
            box-shadow: 0 10px 32px rgba(15, 23, 42, 0.07);
            margin-bottom: 14px;
        }

        .mini-label {
            font-size: 12px;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 4px;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
            background: white !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 800;
            min-height: 44px;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            border: none;
            color: white;
        }

        div[data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid #dbe3ef;
            background: rgba(255,255,255,0.78);
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
        }

        .result-card {
            background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
            border: 1px solid #bbf7d0;
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }

        .result-word {
            font-size: 28px;
            font-weight: 900;
            color: #166534;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }

        .result-meta {
            color: #475569;
            font-size: 14px;
            line-height: 1.6;
        }

        .board-wrap {
            overflow-x: auto;
            padding-bottom: 4px;
        }

        .board-with-coords {
            display: grid;
            grid-template-columns: 24px repeat(15, 31px);
            gap: 3px;
            margin-top: 10px;
            align-items: center;
            width: max-content;
        }

        .coord {
            width: 31px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 800;
            color: #64748b;
        }

        .row-coord {
            width: 24px;
            height: 31px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 800;
            color: #64748b;
        }

        .cell {
            width: 31px;
            height: 31px;
            border-radius: 7px;
            background: linear-gradient(145deg, #f8fafc, #e9eef5);
            border: 1px solid #cbd5e1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 16px;
            color: #5b3a2e;
            position: relative;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
        }

        .bonus-ghost {
            font-size: 9px;
            color: #94a3b8;
            opacity: 0.8;
            font-weight: 900;
        }

        .center-star {
            font-size: 16px;
            color: #f59e0b;
            opacity: 0.8;
            font-weight: 900;
        }

        .filled-old {
            background: linear-gradient(145deg, #fde68a, #facc15);
            border-color: #eab308;
            color: #713f12;
            box-shadow: 0 3px 7px rgba(202, 138, 4, 0.23);
        }

        .filled-new {
            background: linear-gradient(145deg, #86efac, #4ade80);
            border: 2px solid #16a34a;
            color: #14532d;
            box-shadow: 0 3px 9px rgba(22, 163, 74, 0.28);
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 27px;
            }

            .block-container {
                padding-left: 0.7rem;
                padding-right: 0.7rem;
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
            key = hucre_key(satir, sutun)
            hucre = tahta[satir][sutun]
            st.session_state[key] = "" if hucre == "." else hucre


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
    html = '<div class="board-wrap"><div class="board-with-coords">'
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
    <div class="hero-card">
        <div class="hero-title">🧩 EN İYİ HAMLENİ GÖR</div>
        <p class="hero-subtitle">
            Tahtayı doldur, elindeki harfleri gir ve en yüksek puanlı hamleyi saniyeler içinde bul.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


kontrol_sol, kontrol_orta, kontrol_sag = st.columns([1.15, 2.5, 1.15])

with kontrol_sol:
    if st.button("🧹 Boş Tahta", use_container_width=True):
        st.session_state.bekleyen_tahta = bos_tahta_olustur()
        sonuc_temizle()
        st.rerun()

with kontrol_orta:
    eldeki_harfler = st.text_input(
        "Elindeki harfler",
        value="",
        placeholder="Örnek: ABCD*EF",
        help="Joker için * kullan."
    )

with kontrol_sag:
    st.link_button(
        "⚡ ERTOLAND6",
        YOUTUBE_LINK,
        use_container_width=True
    )


sol_kolon, sag_kolon = st.columns([1.5, 1], gap="large")

with sol_kolon:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Tahta Girişi</div>', unsafe_allow_html=True)
    st.subheader("Tahtayı Düzenle")
    st.caption(
        "Üstte sütun, solda satır numarası bulunur. "
        "Bonus kareler silik, orta kare yıldız olarak görünür."
    )

    with st.expander("📋 Toplu Tahta Girişi", expanded=False):
        st.caption(
            "15 satır ve her satırda 15 karakter kullan. "
            "Boş kareler için nokta (.) yaz."
        )

        toplu_tahta_metni = st.text_area(
            "Tahtayı buraya yapıştır",
            value="",
            height=250,
            placeholder="\n".join(["." * 15 for _ in range(15)])
        )

        if st.button("📥 Toplu Tahtayı Uygula", use_container_width=True):
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
        st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    for sutun in range(TAHTA_BOYUTU):
        with baslik_kolonlari[sutun + 1]:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    font-size:11px;
                    font-weight:900;
                    color:#64748b;
                    height:25px;
                    line-height:25px;
                ">{sutun}</div>
                """,
                unsafe_allow_html=True
            )

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
                    font-size:11px;
                    font-weight:900;
                    color:#64748b;
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
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Canlı Görünüm</div>', unsafe_allow_html=True)
    st.subheader("Tahta Önizleme")

    try:
        if guncel_tahta is not None:
            tahta_yazdir_web(guncel_tahta)
        else:
            st.warning("Tabloda hatalı bir hücre var.")
    except Exception as hata:
        st.error(str(hata))

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Hamle Motoru</div>', unsafe_allow_html=True)
    st.subheader("Hamleyi Hesapla")
    st.caption(
        "Tahta ve elindeki harfler hazırsa aşağıdaki butona bas."
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

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Sonuç</div>', unsafe_allow_html=True)
    st.subheader("Önerilen Hamle")

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
            <div class="result-card">
                <div class="result-word">{en_iyi_hamle['kelime']}</div>
                <div class="result-meta">
                    {hamle_bilgisi_yaz(en_iyi_hamle)}<br>
                    Toplam {len(hamleler)} hamle bulundu ·
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

    st.markdown("</div>", unsafe_allow_html=True)