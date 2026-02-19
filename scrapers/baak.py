import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, os

def get_all_baak_news():
    is_railway = os.getenv('RAILWAY_STATIC_URL') is not None
    options = uc.ChromeOptions()
    if is_railway:
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        # Ditambah jadi 15 detik biar Cloudflare-nya bener-bener lewat
        time.sleep(15) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Sesuai inspect element BAAK yang lo kasih sebelumnya
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
        
        if not news_list:
            print("[!] BAAK: Berhasil akses tapi tidak ada tag berita yang ditemukan.")
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] BAAK Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.close() # Pake close dulu sebelum quit biar WinError 6 berkurang
                driver.quit()
            except:
                pass