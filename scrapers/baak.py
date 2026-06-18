import os
import sys
import time
import warnings
from bs4 import BeautifulSoup

# Menggunakan curl_cffi untuk bypass enkripsi TLS/JA3 Fingerprint Cloudflare
try:
    from curl_cffi import requests as cf_requests
except ImportError:
    # Fallback aman jika library belum terinstal di lokal
    import requests as cf_requests

warnings.filterwarnings("ignore", category=UserWarning)

def get_all_baak_news():
    news_list = []
    
    # Kunci mati URL arsip berita BAAK sesuai instruksi utama
    target_url = "https://baak.gunadarma.ac.id/beritabaak"
    
    print("[BAAK] Melakukan penyamaran TLS Fingerprint ke portal arsip berita...")
    try:
        # Menyamar sebagai Google Chrome 124 asli (Bypass Turnstile otomatis tanpa browser fisik)
        response = cf_requests.get(
            target_url,
            impersonate="chrome124",
            timeout=30,
            verify=False
        )
        
        print(f"[DEBUG BAAK] Status HTTP Server: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[BAAK Error] Cloudflare memblokir akses. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sesuai isi file asli HTML arsip /beritabaak yang lo kirim tadi
        articles = soup.find_all('article', class_='post-news')
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")

        if len(articles) == 0:
            print("[DEBUG BAAK] Gagal mengekstrak elemen HTML. Struktur DOM berubah atau diblokir.")
            return []

        # Hanya ambil 1 berita indeks ke-0 (paling baru di paling atas)
        for article in articles[:1]:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a_tag = h6.find('a')
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href', '')
                link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                
                # Ambil tanggal dari div.post-news-meta span indeks kedua
                meta_div = article.find('div', class_='post-news-meta')
                date = "N/A"
                if meta_div:
                    spans = meta_div.find_all('span')
                    if len(spans) >= 2:
                        date = spans[1].get_text(strip=True)
                
                news_list.append({
                    "title": title,
                    "link": link,
                    "date": date
                })
                
        return news_list

    except Exception as e:
        print(f"[BAAK CRITICAL ERROR] Gagal memproses data: {e}")
        return []