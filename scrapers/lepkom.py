import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os

def get_all_lepkom_news():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Kondisi otomatis runtime: Headless di Cloud, GUI di lokal Windows
    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        options.add_argument('--single-process')
        options.add_argument('--disable-gpu')
        options.binary_location = "/usr/bin/google-chrome"
    else:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean_profile = os.path.join(current_dir, "data", "chrome_clean_human_profile")
        options.add_argument(f'--user-data-dir={clean_profile}')
    
    driver = None
    news_list = []
    try:
        print("[LEPKOM] Memulai browser menggunakan Undetected Chromedriver (v149)...")
        driver = uc.Chrome(options=options, version_main=149)
        driver.set_window_size(1366, 768)
        
        print("[LEPKOM] Membuka Google untuk warmup session...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[LEPKOM] Mengalihkan navigasi ke portal pengumuman Lepkom...")
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        
        print("[LEPKOM] Menunggu halaman ter-render sempurna (15 detik)...")
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        print(f"[LEPKOM] Artikel ditemukan di web: {len(articles)}")
        
        if len(articles) == 0:
            print("[!] Struktur artikel kosong, kemungkinan tertahan dinding Turnstile.")
            return []

        for article in articles:
            info = article.find('div', class_='ttr-post-info')
            if info and info.find('h5'):
                a = info.find('h5').find('a')
                if not a:
                    continue
                media_post = info.find('ul', class_='media-post')
                date_li = media_post.find('li') if media_post else None
                news_list.append({
                    "title": a.get_text(strip=True),
                    "link": a.get('href', ''),
                    "date": date_li.get_text(strip=True) if date_li else "N/A"
                })
        
        # Mengembalikan list berita (Index 0 adalah berita terbaru untuk dibaca main.py)
        return news_list
        
    except Exception as e:
        print(f"[LEPKOM Error] Proses ekstraksi data gagal: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass