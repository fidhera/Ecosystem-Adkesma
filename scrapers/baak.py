import os
import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def get_all_baak_news():
    news_list = []
    target_url = "https://baak.gunadarma.ac.id/beritabaak"
    
    # Gunakan token API gratis untuk memutar IP residensial manusia di cloud
    # Daftarkan token ini di GitHub Secrets dengan nama BAAK_API_KEY jika ditaruh di env
    api_key = os.getenv("BAAK_API_KEY", "DAFTAR_GRATIS_DI_SCRAPERANT_DAN_PASTE_DISINI")
    
    # Jika token belum diset, gunakan gateway proxy publik sebagai cadangan
    proxy_url = f"https://api.scraperant.com/v2/general?url={target_url}&x-api-key={api_key}"
    
    print("[BAAK] Menembak portal arsip berita via Scraper Residensial API Gateway...")
    try:
        response = requests.get(proxy_url, timeout=45)
        print(f"[DEBUG BAAK] Proxy API Gateway Response Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[BAAK Error] Proxy API gagal menjebol Cloudflare. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")

        if len(articles) == 0:
            print("[DEBUG BAAK] DOM kosong, proxy terdeteksi atau halaman telat memuat.")
            return []

        for article in articles[:1]:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a_tag = h6.find('a')
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href', '')
                link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                
                meta = article.find('div', class_='post-news-meta')
                date = "N/A"
                if meta:
                    spans = meta.find_all('span')
                    if len(spans) >= 2:
                        date = spans[1].get_text(strip=True)
                
                news_list.append({
                    "title": title,
                    "link": link,
                    "date": date
                })
                
        return news_list

    except Exception as e:
        print(f"[BAAK CRITICAL ERROR] Gagal memproses data proxy: {e}")
        return []
