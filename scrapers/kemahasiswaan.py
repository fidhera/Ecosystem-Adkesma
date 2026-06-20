from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os

def _build_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1366,768')
    options.add_argument('--disable-blink-features=AutomationControlled')

    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        chrome_bin = os.getenv("CHROME_BIN")
        if chrome_bin and os.path.exists(chrome_bin):
            options.binary_location = chrome_bin

    return webdriver.Chrome(options=options)

def get_all_kemahasiswaan_news():
    print("[KEMAHASISWAAN] Membuka jalur RSS XML lewat Stealth Browser...")
    driver = None
    news_list = []
    feed_url = "https://kemahasiswaan.gunadarma.ac.id/feed/posts"
    
    try:
        driver = _build_driver()
        driver.get(feed_url)
        
        print("[KEMAHASISWAAN] Menunggu bypass otomatis verifikasi Cloudflare (20s)...")
        time.sleep(20)
        
        # Mengambil source teks mentah (raw text) untuk menghindari jebakan pembungkus elemen HTML hantu Chrome
        try:
            raw_text = driver.find_element(By.TAG_NAME, "pre").text
            if not raw_text or "<rss" not in raw_text:
                raw_text = driver.page_source
        except:
            raw_text = driver.page_source

        # Memaksa BeautifulSoup membedah dokumen menggunakan internal html parser universal
        soup = BeautifulSoup(raw_text, "html.parser")
        
        # Pencarian objek menggunakan fungsi lambda universal agar kebal dari perubahan arsitektur DOM browser
        items = soup.find_all(lambda tag: tag.name == 'item')
        print(f"[KEMAHASISWAAN] Item berita XML ditemukan: {len(items)}")
        
        for entry in items[:3]:
            title = entry.find("title").get_text(strip=True) if entry.find("title") else "N/A"
            # Hapus pembungkus CDATA jika ikut terbaca oleh parser html hibrida
            title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
            
            link = entry.find("link").get_text(strip=True) if entry.find("link") else "https://kemahasiswaan.gunadarma.ac.id"
            
            pub_date_tag = entry.find("pubdate")
            pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else "N/A"
            if pub_date != "N/A" and "," in pub_date:
                date_display = pub_date.split(",")[1].split("+")[0].strip()
            else:
                date_display = pub_date
                
            category = entry.find("category").get_text(strip=True) if entry.find("category") else "General"
            
            image_url = None
            enclosure_tag = entry.find("enclosure")
            if enclosure_tag and enclosure_tag.get("url"):
                image_url = enclosure_tag.get("url")

            news_list.append({
                "title": title,
                "link": link,
                "date": date_display,
                "category": category,
                "views": "Cloud RSS Feed",
                "image": image_url
            })
        return news_list
    except Exception as e:
        print(f"[KEMAHASISWAAN ERROR] Gagal memproses data XML Feed: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
