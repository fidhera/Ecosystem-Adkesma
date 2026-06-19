import os
import json
import csv
import requests
import time
import warnings
import sys
from dotenv import load_dotenv
from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news

warnings.filterwarnings("ignore", category=ResourceWarning)

if os.path.exists(".env"):
    load_dotenv()

DATA_FILE = "data/last_updates.json"
BAAK_CSV = "scrapers/local_data/baak_data.csv"

# ==============================================================================
# INTEGRASI INTEGRAL: UTOR SCARPER KEMAHASISWAAN SEBAGAI ENGINE INTERNAL MAIN
# ==============================================================================
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

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

# ==============================================================================
# CORE CORE MANAGEMENT LOGIC BOT ADKESMA SINKRONISASI
# ==============================================================================
def load_history():
    default_history = {
        "baak_history": [],
        "lepkom_history": [],
        "studentsite_history": [],
        "kemahasiswaan_history": []
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read()
            if not content.strip():
                return default_history
            data = json.loads(content)
            for key in default_history:
                if key not in data:
                    data[key] = []
            return data
        except Exception as e:
            print(f"[!] Error load history: {e}")
            return default_history
    return default_history

def save_history(history):
    if not os.path.exists('data'):
        os.makedirs('data')
    for key in history:
        history[key] = history[key][-50:]
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mengirim: {news['title']}")

    if not webhook_url or not webhook_url.startswith("http"):
        print(f"[!] Webhook {source_name} tidak valid.")
        return None

    colors = {
        "BAAK": 3447003, 
        "LEPKOM": 3066993, 
        "STUDENTSITE": 15105570,
        "KEMAHASISWAAN": 10232280  # Ungu tua premium untuk Kemahasiswaan
    }
    
    embed = {
        "title": news['title'],
        "url": news['link'],
        "description": f"📅 **Tanggal:** {news['date']}",
        "color": colors.get(source_name, 3447003),
        "footer": {"text": "Ecosystem Adkesma Assistant"}
    }
    
    if source_name == "KEMAHASISWAAN":
        embed["fields"] = [
            {"name": "📂 Kategori", "value": news.get("category", "General"), "inline": True},
            {"name": "👁️ Pembaca", "value": news.get("views", "0 views"), "inline": True}
        ]
        if news.get("image"):
            embed["image"] = {"url": news["image"]}

    payload = {
        "username": display_name,
        "embeds": [embed]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=15)
        print(f"[DEBUG] Discord {source_name}: {res.status_code}")
        return res.status_code
    except Exception as e:
        print(f"[!] Discord Error: {e}")
        return None

def fetch_local_baak_csv():
    news_list = []
    if not os.path.exists(BAAK_CSV):
        print(f"[!] Info BAAK: File {BAAK_CSV} tidak ditemukan. Skip proses BAAK.")
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
        print(f"[!] Gagal memproses data CSV BAAK: {e}")
    return news_list

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
    except Exception as e:
        print(f"[!] Gagal menarik data {source_name}: {e}")
        return history

    if not all_news:
        print(f"[!] Tidak ada berita baru/terdeteksi untuk {source_name}, skip.")
        return history

    webhook_url = os.getenv(f"{source_name.upper()}_WEBHOOK")
    if not webhook_url:
        print(f"[!] Webhook {source_name}_WEBHOOK tidak ditemukan.")
        return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history:
        history[history_key] = []

    sent_count = 0
    for news in reversed(all_news):
        if news['title'] not in history[history_key]:
            status = send_to_discord(webhook_url, news, source_name)
            if status in [200, 204]:
                history[history_key].append(news['title'])
                sent_count += 1
                time.sleep(2)

    print(f"--- {source_name} SELESAI: {sent_count} berita terkirim ---")
    return history

def run_logic():
    history = load_history()
    
    portals = [
        ("BAAK", fetch_local_baak_csv),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
        ("KEMAHASISWAAN", get_all_kemahasiswaan_news)
    ]
    
    for name, fetcher in portals:
        try:
            history = sync_portal(name, fetcher, history)
        except Exception as e:
            print(f"[!] Portal {name} gagal total: {e}")

    save_history(history)
    print("\n[SUCCESS] Seluruh ekosistem ECA telah sinkron.")

if __name__ == "__main__":
    print("[SYSTEM] ECA Monitor Starting...")
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("[ENV] GitHub Actions terdeteksi. Satu siklus eksekusi Cloud.")
        run_logic()
        sys.exit(0)
    else:
        print("[ENV] Mode lokal terdeteksi. Loop pemantauan berjalan otomatis per jam.")
        while True:
            try:
                run_logic()
            except Exception as e:
                print(f"[CRITICAL] {e}")
            print("\n[*] Tidur 1 jam... Biarkan terminal ini tetap menyala.")
            time.sleep(3600)