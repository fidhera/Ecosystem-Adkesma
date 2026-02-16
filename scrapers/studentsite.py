import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def get_all_studentsite_news():
    url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') 
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get(url)
        try:
            WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CLASS_NAME, "content-box")))
        except: pass
        time.sleep(3) 
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')[:10] 
        for box in boxes:
            header = box.find('h3', class_='content-box-header')
            if not header: continue
            link_tag = header.find('a', href=True)
            if not link_tag: continue
            title = link_tag.get_text(strip=True).replace("[TERBARU]", "").strip()
            link = link_tag['href']
            if not link.startswith('http'): link = f"https://studentsite.gunadarma.ac.id{link}"
            date = "N/A"
            date_div = box.find('div', class_='font-gray')
            if date_div:
                date_text = date_div.get_text(strip=True)
                if "pada" in date_text: date = date_text.split("pada")[-1].strip()
            news_list.append({"title": title, "link": link, "date": date})
        news_list.reverse()
        return news_list
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass