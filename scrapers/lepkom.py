from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os

def _build_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--window-size=1366,768')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )

    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')

    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        options.binary_location = chrome_bin

    return webdriver.Chrome(options=options)

def get_all_lepkom_news():
    driver = None
    news_list = []
    try:
        print("[LEPKOM] Memulai browser...")
        driver = _build_driver()

        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        print("[LEPKOM] Menunggu halaman render (15s)...")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.blog-post"))
            )
        except Exception:
            time.sleep(15)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        print(f"[LEPKOM] Artikel ditemukan: {len(articles)}")

        # Membatasi slice [:1] hanya untuk mengambil 1 berita terbaru
        for article in articles[:1]:
            info = article.find('div', class_='ttr-post-info')
            if info and info.find('h5'):
                a = info.find('h5').find('a')
                if not a:
                    continue
                media_post = info.find('ul', class_='media-post')
                date_li = media_post.find('li') if media_post else None
                news_list.append({
                    "title": a.get_text(strip=True),
                    "link": a.get('href', ''),
                    "date": date_li.get_text(strip=True) if date_li else "N/A"
                })

        print(f"[LEPKOM] Total berita diambil: {len(news_list)}")
        return news_list[::-1]

    except Exception as e:
        print(f"[LEPKOM Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass