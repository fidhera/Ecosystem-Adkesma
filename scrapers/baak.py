import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, os

def get_all_baak_news():
    is_railway = os.getenv('RAILWAY_STATIC_URL') is not None
    options = uc.ChromeOptions()
    
    # Argumen wajib buat server cloud agar tidak macet di 'Starting Container'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    options.binary_location = "/usr/bin/google-chrome" # Lokasi Chrome di Docker lo
    
    driver = None
    news_list = []
    try:
        print("[BAAK] Memulai browser...")
        driver = uc.Chrome(options=options)
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        print("[BAAK] Menunggu Cloudflare (15s)...")
        time.sleep(15) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        
        for article in articles:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a = h6.find('a')
                title = a.get_text(strip=True)
                href = a.get('href', '')
                link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                meta = article.find('div', class_='post-news-meta')
                date = meta.get_text(strip=True) if meta else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        
        print(f"[BAAK] Berhasil menarik {len(news_list)} berita.")
        return news_list[::-1]
    except Exception as e:
        print(f"[BAAK Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass