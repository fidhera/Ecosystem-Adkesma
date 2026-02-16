import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def get_all_studentsite_news():
    url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
    options = uc.ChromeOptions()
    
    # KALO MAU LIAT POPUP (LOKAL), KOMENTARI BARIS DI BAWAH INI PAKE '#'
    options.add_argument('--headless') 
    
    driver = None
    news_list = []
    try:
        driver = uc.Chrome(options=options)
        driver.get(url)
        
        # Studentsite emang butuh waktu render lama
        time.sleep(12) 
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        if not boxes:
            print("[!] Studentsite: content-box gak ketemu, coba fallback...")
            headers = soup.find_all('h3', class_='content-box-header')
            for h in headers[:10]:
                link_tag = h.find('a', href=True)
                if not link_tag: continue
                title = link_tag.get_text(strip=True).replace("[TERBARU]", "").strip()
                link = link_tag['href']
                if not link.startswith('http'): link = f"https://studentsite.gunadarma.ac.id{link}"
                news_list.append({"title": title, "link": link, "date": "N/A"})
        else:
            for box in boxes[:10]:
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
    except Exception as e:
        print(f"[!] STUDENTSITE Scraper Error: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except: pass