import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import os
import re
import shutil

def get_chrome_version_local():
    if os.getenv("GITHUB_ACTIONS") == "true":
        return None
    try:
        stream = os.popen('reg query "HKLM\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome" /v DisplayVersion')
        output = stream.read()
        version_match = re.search(r'DisplayVersion\s+REG_SZ\s+(\d+)', output)
        if version_match:
            return int(version_match.group(1))
    except:
        pass
    return None

def get_all_baak_news():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    local_version = get_chrome_version_local()
    
    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-setuid-sandbox')
        
        # Deteksi dinamis jalur biner Chrome yang diinstal oleh GitHub Actions
        chrome_env_path = os.getenv("CHROME_BIN")
        if chrome_env_path and os.path.exists(chrome_env_path):
            options.binary_location = chrome_env_path
        else:
            system_path = shutil.which("google-chrome") or shutil.which("chrome")
            if system_path:
                options.binary_location = system_path
    else:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean_profile = os.path.join(current_dir, "data", "chrome_clean_human_profile")
        options.add_argument(f'--user-data-dir={clean_profile}')
    
    driver = None
    news_list = []
    try:
        print(f"[BAAK] Membuka browser (Version Main: {local_version if local_version else 'Auto/Cloud'})...")
        driver = uc.Chrome(options=options, version_main=local_version)
        driver.set_window_size(1366, 768)
        
        print("[BAAK] Warmup session...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[BAAK] Navigasi ke portal BAAK...")
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        print("[BAAK] Menunggu validasi Turnstile (25 detik)...")
        time.sleep(25)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")
        
        if len(articles) == 0:
            return []

        for article in articles:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a_tag = h6.find('a')
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href', '')
                link = link if link.startswith('http') else f"https://baak.gunadarma.ac.id{link}"
                meta = article.find('div', class_='post-news-meta')
                date = meta.get_text(strip=True) if meta else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        
        return news_list

    except Exception as e:
        print(f"[BAAK Error] Scraper crash: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass