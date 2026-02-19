import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time, os

def get_all_lepkom_news():
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
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        time.sleep(7)
        
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
        return news_list[::-1]
    except Exception as e:
        print(f"[!] LEPKOM Error: {e}")
        return []
    finally:
        if driver:
            driver.quit()