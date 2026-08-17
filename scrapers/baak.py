import os
import csv
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

BAAK_CSV = "scrapers/local_data/baak_data.csv"

def fetch_live_baak_news():
    driver = None
    news_list = []
    target_url = "https://baak.gunadarma.ac.id/beritabaak"
    print("[BAAK] Membuka jendela browser (headed mode)...")
    try:
        # headless=False agar jendela Chrome terbuka di laptop Anda
        driver = build_driver(headless=False)
        driver.get(target_url)
        print("[BAAK] Menunggu halaman memuat...")

        for _ in range(20):
            time.sleep(1)
            if "just a moment" not in driver.title.lower():
                break

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all("article", class_="post-news")
        if not articles:
            articles = soup.find_all("article")

        print(f"[BAAK] Artikel ditemukan di DOM: {len(articles)}")

        for article in articles[:3]:
            body_div = article.find("div", class_="post-news-body")
            if not body_div:
                body_div = article

            h_tag = body_div.find(["h6", "h5", "h4", "h3"])
            if not h_tag or not h_tag.find("a"):
                continue

            a_tag = h_tag.find("a")
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://baak.gunadarma.ac.id" + link

            date = "N/A"
            meta_div = body_div.find("div", class_="post-news-meta")
            if meta_div:
                date_span = meta_div.find("span", class_="text-black")
                if date_span:
                    date = date_span.get_text(strip=True)
                else:
                    spans = meta_div.find_all("span")
                    if len(spans) >= 2:
                        date = spans[1].get_text(strip=True)

            news_list.append({"title": title, "link": link, "date": date})

        print(f"[BAAK] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['date']}] {item['title']}")

        return news_list
    except Exception as e:
        print(f"[BAAK ERROR] Gagal live parsing browser: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

def fetch_local_baak_csv():
    news_list = []
    if not os.path.exists(BAAK_CSV):
        print(f"[!] Info BAAK: Berkas {BAAK_CSV} tidak ditemukan.")
        return []
    try:
        with open(BAAK_CSV, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if rows:
            latest_news = rows[0]
            news_list.append({
                "title": latest_news.get("judul", "N/A"),
                "link": "https://baak.gunadarma.ac.id/beritabaak",
                "date": latest_news.get("tanggal", "N/A")
            })
    except Exception as e:
        print(f"[!] Gagal memproses berkas CSV BAAK: {e}")
    return news_list

def get_all_baak_news():
    if os.getenv("GITHUB_ACTIONS") == "true":
        return fetch_local_baak_csv()
    news = fetch_live_baak_news()
    return news if news else fetch_local_baak_csv()