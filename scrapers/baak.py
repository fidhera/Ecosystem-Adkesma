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


def get_all_baak_news():
    driver = None
    news_list = []

    try:

        print("[BAAK] Memulai browser...")
        driver = _build_driver()

        driver.get("https://baak.gunadarma.ac.id/beritabaak")

        print("[BAAK] Menunggu halaman render...")

        time.sleep(15)

        print("[BAAK] Title :", driver.title)
        print("[BAAK] URL :", driver.current_url)

        html = driver.page_source

        print(html[:1500])

        soup = BeautifulSoup(html, "html.parser")

        articles = soup.find_all("article")

        print(f"[BAAK] Artikel ditemukan: {len(articles)}")

        for article in articles[:1]:

            h6 = article.find("h6")

            if not h6:
                continue

            a = h6.find("a")

            if not a:
                continue

            title = a.get_text(strip=True)

            href = a.get("href", "")

            link = (
                href
                if href.startswith("http")
                else f"https://baak.gunadarma.ac.id{href}"
            )

            news_list.append({
                "title": title,
                "link": link,
                "date": "N/A"
            })

        print(f"[BAAK] Total berita diambil: {len(news_list)}")

        return news_list

    except Exception as e:
        print(f"[BAAK ERROR] {e}")
        return []

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
