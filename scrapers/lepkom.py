import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def get_all_lepkom_news():
    url = "https://vm.lepkom.gunadarma.ac.id/pengumuman"
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get(url)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CLASS_NAME, "blog-post")))
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        
        for article in articles:
            info_div = article.find('div', class_='ttr-post-info')
            if not info_div: continue
            h5_tag = info_div.find('h5')
            if not h5_tag: continue
            link_tag = h5_tag.find('a', href=True)
            if not link_tag: continue
            
            title = link_tag.get_text(strip=True)
            link = link_tag['href']
            date = "N/A"
            date_li = info_div.find('ul', class_='media-post')
            if date_li: date = date_li.find('li').get_text(strip=True)
            
            news_list.append({"title": title, "link": link, "date": date})
            
        news_list.reverse()
        return news_list
    except Exception as e:
        print(f"[!] LEPKOM Scraper Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass