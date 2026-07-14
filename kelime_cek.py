import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.kelimetre.com"
START_URL = "https://www.kelimetre.com/kelime-listeleri"

TURKCE_HARFLER = set("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ")


def temizle(kelime):
    kelime = kelime.strip().upper()
    kelime = kelime.replace(" ", "")

    for karakter in kelime:
        if karakter not in TURKCE_HARFLER:
            return None

    if len(kelime) < 2 or len(kelime) > 15:
        return None

    return kelime


def sayfa_getir(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def ayni_site_mi(url):
    return urlparse(url).netloc == "www.kelimetre.com"


def ana_harf_linklerini_bul(soup):
    linkler = set()

    for a in soup.find_all("a"):
        yazi = a.get_text(" ", strip=True).lower()
        href = a.get("href")

        if not href:
            continue

        if "ile başlayan kelimeler" in yazi:
            tam_link = urljoin(BASE_URL, href)
            linkler.add(tam_link)

    return sorted(linkler)


def kelimeleri_sayfadan_cek(soup):
    kelimeler = set()

    # Sitedeki kelimeler çoğunlukla li veya a içinde olabilir.
    adaylar = []

    for li in soup.find_all("li"):
        adaylar.append(li.get_text(" ", strip=True))

    for a in soup.find_all("a"):
        adaylar.append(a.get_text(" ", strip=True))

    for yazi in adaylar:
        kelime = temizle(yazi)
        if kelime:
            kelimeler.add(kelime)

    return kelimeler


def ilgili_alt_linkleri_bul(soup, harf_url):
    linkler = set()

    harf_path = urlparse(harf_url).path.strip("/").split("/")[0]

    for a in soup.find_all("a"):
        href = a.get("href")
        if not href:
            continue

        tam_link = urljoin(BASE_URL, href)

        if not ayni_site_mi(tam_link):
            continue

        path = urlparse(tam_link).path.strip("/")

        # Sadece aynı harfin kelime sayfalarını takip et
        if path.startswith(harf_path):
            linkler.add(tam_link)

    return linkler


def harf_sayfasini_tam_gez(harf_url):
    gezilecekler = deque([harf_url])
    gezilenler = set()
    tum_kelimeler = set()

    while gezilecekler:
        url = gezilecekler.popleft()

        if url in gezilenler:
            continue

        gezilenler.add(url)

        print(f"    Sayfa okunuyor: {url}")

        try:
            soup = sayfa_getir(url)
        except Exception as hata:
            print(f"    Hata: {hata}")
            continue

        kelimeler = kelimeleri_sayfadan_cek(soup)
        onceki_sayi = len(tum_kelimeler)
        tum_kelimeler.update(kelimeler)
        yeni_sayi = len(tum_kelimeler) - onceki_sayi

        print(f"    + {yeni_sayi} yeni kelime, bu harfte toplam {len(tum_kelimeler)}")

        alt_linkler = ilgili_alt_linkleri_bul(soup, harf_url)

        for link in alt_linkler:
            if link not in gezilenler:
                gezilecekler.append(link)

        time.sleep(0.3)

    return tum_kelimeler


def main():
    print("Ana sayfa okunuyor...")
    ana_sayfa = sayfa_getir(START_URL)

    harf_linkleri = ana_harf_linklerini_bul(ana_sayfa)

    print(f"{len(harf_linkleri)} harf sayfası bulundu.")

    tum_kelimeler = set()

    for index, harf_linki in enumerate(harf_linkleri, start=1):
        print(f"\n{index}/{len(harf_linkleri)} harf işleniyor: {harf_linki}")

        kelimeler = harf_sayfasini_tam_gez(harf_linki)
        tum_kelimeler.update(kelimeler)

        print(f"Bu harften {len(kelimeler)} kelime alındı.")
        print(f"Genel toplam: {len(tum_kelimeler)}")

    sirali_kelimeler = sorted(tum_kelimeler, key=lambda x: (len(x), x))

    with open("kelimeler.txt", "w", encoding="utf-8") as dosya:
        for kelime in sirali_kelimeler:
            dosya.write(kelime + "\n")

    print(f"\nBitti kanka. kelimeler.txt içine {len(sirali_kelimeler)} kelime yazıldı.")


main()