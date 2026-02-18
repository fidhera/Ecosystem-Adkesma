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
    
    driver = None
    news_list = []
    try:
        # Definisi path chrome untuk lingkungan GitHub
        chrome_path = "/usr/bin/google-chrome" if is_github else None
        
        driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "blog-post"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        
        # Sesuai permintaan: Ambil 5 berita terbaru saja
        for article in articles[:5]:
            info = article.find('div', class_='ttr-post-info')
            if not info: continue
            
            h5 = info.find('h5')
            if not h5: continue
            
            a = h5.find('a')
            date_li = info.find('ul', class_='media-post').find('li')
            
            news_list.append({
                "title": a.get_text(strip=True),
                "link": a['href'],
                "date": date_li.get_text(strip=True) if date_li else "N/A"
            })
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] LEPKOM Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass