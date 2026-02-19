import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, os

def get_all_lepkom_news():
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
        print("[LEPKOM] Memulai browser...")
        driver = uc.Chrome(options=options)
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        
        print("[LEPKOM] Menunggu halaman (15s)...")
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        
        for article in articles[:5]:
            info = article.find('div', class_='ttr-post-info')
            if info and info.find('h5'):
                a = info.find('h5').find('a')
                media_post = info.find('ul', class_='media-post')
                date_li = media_post.find('li') if media_post else None
                news_list.append({
                    "title": a.get_text(strip=True),
                    "link": a.get('href', ''),
                    "date": date_li.get_text(strip=True) if date_li else "N/A"
                })
        
        print(f"[LEPKOM] Berhasil menarik {len(news_list)} berita.")
        return news_list[::-1]
    except Exception as e:
        print(f"[LEPKOM Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass