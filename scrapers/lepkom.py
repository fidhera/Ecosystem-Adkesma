import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, time

def get_all_lepkom_news():
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'
    options = uc.ChromeOptions()
    if is_github: 
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        
        # Tunggu sampai konten blog muncul
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "blog-post"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        
        # Ambil hanya 5 artikel teratas (terbaru)
        for article in articles[:5]:
            info = article.find('div', class_='ttr-post-info')
            if not info: 
                continue
                
            h5 = info.find('h5')
            if not h5:
                continue
                
            a = h5.find('a')
            date_li = info.find('ul', class_='media-post').find('li')
            
            news_list.append({
                "title": a.get_text(strip=True),
                "link": a['href'],
                "date": date_li.get_text(strip=True) if date_li else "N/A"
            })
            
        # Balik urutan agar berita paling baru muncul paling bawah di Discord
        return news_list[::-1]
        
    except Exception as e:
        print(f"[!] LEPKOM Scraper Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass