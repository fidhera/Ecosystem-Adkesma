import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, os

def get_all_studentsite_news():
    is_railway = os.getenv('RAILWAY_STATIC_URL') is not None
    options = uc.ChromeOptions()
    
    # Argumen wajib buat server cloud
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    options.binary_location = "/usr/bin/google-chrome"
    
    driver = None
    news_list = []
    try:
        print("[STUDENTSITE] Memulai browser...")
        driver = uc.Chrome(options=options)
        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        
        print("[STUDENTSITE] Menunggu halaman (15s)...")
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        for box in boxes[:10]:
            h3 = box.find('h3', class_='content-box-header')
            if h3 and h3.find('a'):
                a = h3.find('a')
                title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
                href = a.get('href', '')
                link = href if href.startswith('http') else f"https://studentsite.gunadarma.ac.id{href}"
                date_div = box.find('div', class_='font-gray')
                date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        
        print(f"[STUDENTSITE] Berhasil menarik {len(news_list)} berita.")
        return news_list[::-1]
    except Exception as e:
        print(f"[STUDENTSITE Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass