import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os, time

def get_all_studentsite_news():
    is_github = os.getenv('GITHUB_ACTIONS') == 'true'
    options = uc.ChromeOptions()
    if is_github:
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')
    
    driver = None
    news_list = []
    try:
        # Definisi path chrome agar tidak error 'not defined'
        chrome_path = "/usr/bin/google-chrome" if is_github else None
        
        driver = uc.Chrome(options=options, browser_executable_path=chrome_path)
        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        
        # Jeda lebih lama buat nembus verifikasi studentsite
        time.sleep(20) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        for box in boxes[:10]:
            h3 = box.find('h3', class_='content-box-header')
            if not h3: continue
            a = h3.find('a')
            if not a: continue
            
            title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
            link = a['href'] if a['href'].startswith('http') else f"https://studentsite.gunadarma.ac.id{a['href']}"
            
            date_div = box.find('div', class_='font-gray')
            date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
            
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] STUDENTSITE Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass