import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os, time

def get_all_baak_news():
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'
    options = uc.ChromeOptions()
    if is_github:
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    news_list = []
    try:
        # PAKSA PAKE PATH CHROME YANG BARU DIINSTAL (KHUSUS GITHUB)
        chrome_path = "/usr/bin/google-chrome" if is_github else None
        
        driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        for article in articles:
            h6 = article.find('h6')
            if h6 and h6.find('a'):
                a = h6.find('a')
                title = a.get_text(strip=True)
                link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
                meta = article.find('div', class_='post-news-meta')
                date = meta.get_text(strip=True) if meta else "N/A"
                news_list.append({"title": title, "link": link, "date": date})
        return news_list[::-1]
    except Exception as e:
        print(f"[!] BAAK Error: {e}")
        return []
    finally:
        if driver:
            try: driver.quit()
            except: pass