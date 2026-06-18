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

def get_all_studentsite_news():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    local_version = get_chrome_version_local()
    
    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-setuid-sandbox')
        
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
        print(f"[STUDENTSITE] Memulai browser (Version Main: {local_version if local_version else 'Auto/Cloud'})...")
        driver = uc.Chrome(options=options, version_main=local_version)
        driver.set_window_size(1366, 768)
        
        print("[STUDENTSITE] Warmup session...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[STUDENTSITE] Navigasi ke portal Studentsite...")
        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        
        print("[STUDENTSITE] Menunggu bypass Turnstile (25 detik)...")
        time.sleep(25)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        print(f"[STUDENTSITE] Artikel ditemukan di web: {len(boxes)}")
        
        if len(boxes) == 0:
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
        
        return news_list
        
    except Exception as e:
        print(f"[STUDENTSITE Error] Scraper crash: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass