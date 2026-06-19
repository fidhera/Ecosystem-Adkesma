from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    driver = None
    news_list = []
    target_url = "https://kemahasiswaan.gunadarma.ac.id/"

    print("[KEMAHASISWAAN] Memulai browser stealth...")
    try:
        driver = _build_driver()
        driver.get(target_url)
        
        print("[KEMAHASISWAAN] Menunggu halaman memuat sempurna (10s)...")
        time.sleep(10)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Menargetkan kontainer "Latest posts"
        latest_section = soup.find("div", class_="post-module-3")
        if not latest_section:
            print("[KEMAHASISWAAN] Kontainer Latest posts tidak ditemukan.")
            return []

        articles = latest_section.find_all("article")
        print(f"[KEMAHASISWAAN] Artikel ditemukan di DOM: {len(articles)}")

        # Ambil 3 artikel teratas untuk mengantisipasi jika ada multi-post dalam satu waktu
        for article in articles[:3]:
            # 1. Ekstraksi Judul dan Link
            h4_title = article.find("h4", class_="post-title")
            if not h4_title or not h4_title.find("a"):
                continue
            a_tag = h4_title.find("a")
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")

            # 2. Ekstraksi Kategori Berita
            cat_span = article.find("span", class_="post-cat")
            category = cat_span.get_text(strip=True) if cat_span else "General"

            # 3. Ekstraksi Komponen Tanggal & Views
            meta_div = article.find("div", class_="entry-meta")
            date = "N/A"
            views = "0 views"
            if meta_div:
                if date_span := meta_div.find("span", class_="post-on"):
                    date = date_span.get_text(strip=True)
                if views_span := meta_div.find("span", class_="post-by"):
                    views = views_span.get_text(strip=True)

            # 4. Ekstraksi Thumbnail Banner Gambar
            image_url = None
            if thumb_div := article.find("div", class_="img-hover-slide"):
                style_attr = thumb_div.get("style", "")
                if "url(" in style_attr:
                    # Ambil string URL di dalam tanda kurung url('...')
                    image_url = style_attr.split("url(")[1].split(")")[0].strip("'\"")

            news_list.append({
                "title": title,
                "link": link,
                "date": date,
                "category": category,
                "views": views,
                "image": image_url
            })

        print(f"[KEMAHASISWAAN] Total berita diproses: {len(news_list)}")
        return news_list

    except Exception as e:
        print(f"[KEMAHASISWAAN ERROR] Gagal melakukan pengerukan data: {e}")
        return []
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass