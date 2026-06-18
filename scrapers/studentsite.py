import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os

def get_all_studentsite_news():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
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
        print("[STUDENTSITE] Memulai browser menggunakan Undetected Chromedriver (v149)...")
        driver = uc.Chrome(options=options, version_main=149)
        driver.set_window_size(1366, 768)
        
        print("[STUDENTSITE] Membuka Google untuk warmup session...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[STUDENTSITE] Mengalihkan navigasi ke portal berita Studentsite...")
        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        
        print("[STUDENTSITE] Menunggu bypass enkripsi Turnstile (25 detik)...")
        time.sleep(25)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        print(f"[STUDENTSITE] Artikel ditemukan di web: {len(boxes)}")
        
        if len(boxes) == 0:
            print("[!] Struktur box kosong, akses diblokir Cloudflare.")
            return []

        for box in boxes:
            h3 = box.find('h3', class_='content-box-header')
            if h3 and h3.find('a'):
                a = h3.find('a')
                title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
                href = a.get('href', '')
                link = href if href.startswith('http') else f"https://studentsite.gunadarma.ac.id{href}"
                date_div = box.find('div', class_='font-gray')
                date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        
        # Mengembalikan list berita (Index 0 adalah berita paling gres)
        return news_list
        
    except Exception as e:
        print(f"[STUDENTSITE Error] Proses ekstraksi data gagal: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass