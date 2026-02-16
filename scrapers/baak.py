import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def get_all_baak_news():
    url = "https://baak.gunadarma.ac.id/beritabaak"
    options = uc.ChromeOptions()
    
    # KALO MAU LIAT POPUP (LOKAL), KOMENTARI BARIS DI BAWAH INI PAKE '#'
    options.add_argument('--headless') 
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # Tunggu manual biar pasti
        time.sleep(5)
        
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "post-news")))
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        
        for article in articles:
            h6_tag = article.find('h6')
            if not h6_tag: continue
            link_tag = h6_tag.find('a', href=True)
            if not link_tag: continue
            title = link_tag.get_text(strip=True)
            link = link_tag['href']
            if not link.startswith('http'): link = f"https://baak.gunadarma.ac.id{link}"
            date = "N/A"
            meta_div = article.find('div', class_='post-news-meta')
            if meta_div: date = meta_div.get_text(strip=True)
            news_list.append({"title": title, "link": link, "date": date})
            
        news_list.reverse()
        return news_list
    except Exception as e:
        print(f"[!] BAAK Scraper Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except: pass