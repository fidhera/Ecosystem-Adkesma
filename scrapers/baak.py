import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def get_all_baak_news():
    url = "https://baak.gunadarma.ac.id/beritabaak"
    options = uc.ChromeOptions()
    options.add_argument('--headless') # WAJIB UNTUK GITHUB
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    news_list = []

    try:
        driver = uc.Chrome(options=options)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "post-news")))
        
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
    finally:
        if driver:
            driver.service.stop()
            driver.quit()