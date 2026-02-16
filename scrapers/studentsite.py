import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os, time

def get_all_studentsite_news():
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
        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        
        # Jeda lebih lama untuk bypass Cloudflare verification
        time.sleep(15) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        if not boxes:
            return []

        for box in boxes[:10]:
            header = box.find('h3', class_='content-box-header')
            if not header:
                continue
                
            link_tag = header.find('a')
            if not link_tag:
                continue
            
            # Perbaikan: Cek keberadaan teks sebelum memanggil .strip()
            title_raw = link_tag.get_text(strip=True) if link_tag else "N/A"
            title = title_raw.replace("[TERBARU]", "").strip()
            
            link = link_tag.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://studentsite.gunadarma.ac.id{link}"
            
            date = "N/A"
            date_div = box.find('div', class_='font-gray')
            if date_div:
                date_text = date_div.get_text(strip=True)
                if "pada" in date_text:
                    date = date_text.split("pada")[-1].strip()
            
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] STUDENTSITE Scraper Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass