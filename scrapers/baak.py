import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, time

def get_all_baak_news():
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'
    options = uc.ChromeOptions()
    if is_github: options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CLASS_NAME, "post-news")))
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        for article in articles:
            h6 = article.find('h6')
            if not h6: continue
            a = h6.find('a')
            if not a: continue
            
            title = a.get_text(strip=True)
            link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
            date = article.find('div', class_='post-news-meta').get_text(strip=True) if article.find('div', class_='post-news-meta') else "N/A"
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1]
    finally:
        if driver:
            try: driver.quit()
            except: pass