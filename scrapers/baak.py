import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os, time

def get_all_baak_news():
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'
    options = uc.ChromeOptions()
    if is_github: options.add_argument('--headless')
    
    # Pengaturan agar lebih mirip manusia asli
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        # Wajib nunggu agak lama buat nembus Cloudflare
        time.sleep(15) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        
        for article in articles:
            h6 = article.find('h6')
            if not h6: continue
            a = h6.find('a')
            title = a.get_text(strip=True)
            link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
            date = article.find('div', class_='post-news-meta').get_text(strip=True) if article.find('div', class_='post-news-meta') else "N/A"
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] BAAK Error: {e}")
        return []
    finally:
        if driver:
            try: driver.quit()
            except: pass