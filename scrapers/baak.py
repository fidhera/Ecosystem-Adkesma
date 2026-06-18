import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os

def get_all_baak_news():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Kondisi otomatis: Headless di Cloud (GitHub Actions), GUI Profile di Lokal Windows
    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        options.add_argument('--single-process')
        options.add_argument('--disable-gpu')
        options.binary_location = "/usr/bin/google-chrome"
    else:
        # Gunakan profile human agar cookie klik Turnstile lo tersimpan secara lokal
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean_profile = os.path.join(current_dir, "data", "chrome_clean_human_profile")
        options.add_argument(f'--user-data-dir={clean_profile}')
    
    driver = None
    news_list = []
    try:
        print("[BAAK] Membuka browser menggunakan Undetected Chromedriver (v149)...")
        driver = uc.Chrome(options=options, version_main=149)
        driver.set_window_size(1366, 768)
        
        # Taktik Warmup Session via Google
        print("[BAAK] Membuka Google untuk kamuflase awal...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[BAAK] Mengalihkan navigasi ke portal berita BAAK...")
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        # Jeda 25 detik untuk validasi pasif (silakan klik jika popup minta centang muncul di lokal)
        print("[BAAK] Menunggu proses validasi Turnstile (25 detik)...")
        time.sleep(25)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")
        
        if len(articles) == 0:
            print("[!] Artikel kosong, kemungkinan diblokir Cloudflare.")
            return []

        # Ambil semua berita untuk diproses filtering-nya di main.py
        for article in articles:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a_tag = h6.find('a')
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href', '')
                link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                meta = article.find('div', class_='post-news-meta')
                date = meta.get_text(strip=True) if meta else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        
        # Kembalikan list berita (indeks 0 menjadi berita terbaru di main.py)
        return news_list

    except Exception as e:
        print(f"[BAAK Error] Gangguan eksekusi scraper: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass