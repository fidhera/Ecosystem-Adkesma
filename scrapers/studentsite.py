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

def get_all_studentsite_news():
    driver = None
    news_list = []
    try:
        print("[STUDENTSITE] Memulai browser...")
        driver = _build_driver()

        driver.get("https://studentsite.gunadarma.ac.id/index.php/site/news")
        print("[STUDENTSITE] Menunggu halaman render (25s)...")

        try:
            WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.content-box"))
            )
        except Exception:
            time.sleep(25)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        print(f"[STUDENTSITE] Artikel ditemukan: {len(boxes)}")

        for box in boxes[:10]:
            h3 = box.find('h3', class_='content-box-header')
            if h3 and h3.find('a'):
                a = h3.find('a')
                title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
                href = a.get('href', '')
                link = href if href.startswith('http') else f"https://studentsite.gunadarma.ac.id{href}"
                date_div = box.find('div', class_='font-gray')
                date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
                news_list.append({"title": title, "link": link, "date": date})

        print(f"[STUDENTSITE] Total berita diambil: {len(news_list)}")
        return news_list[::-1]

    except Exception as e:
        print(f"[STUDENTSITE Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass