import os
import json
import csv
import time
import warnings
import sys
from dotenv import load_dotenv
from curl_cffi import requests

from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news
from scrapers.kemahasiswaan import get_all_kemahasiswaan_news

warnings.filterwarnings("ignore", category=ResourceWarning)

if os.path.exists(".env"):
    load_dotenv()

DATA_FILE = "data/last_updates.json"
BAAK_CSV = "scrapers/local_data/baak_data.csv"

# ==============================================================================
# ENGINE PORTAL LOKAL BAAK
# ==============================================================================
def fetch_live_baak_news():
    print("[BAAK] Menembak live parsing DOM HTML ke server BAAK...")
    news_list = []
    target_url = "https://baak.gunadarma.ac.id/beritabaak"
    try:
        res = requests.get(target_url, impersonate="chrome", timeout=20)
        if res.status_code != 200:
            print(f"[BAAK] Cloudflare memblokir requests (Status {res.status_code}). Skip live mode.")
            return []
            
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.find_all("article", class_="post-news")
        
        for article in articles[:3]:
            body_div = article.find("div", class_="post-news-body")
            if not body_div: continue
            h6_tag = body_div.find("h6")
            if not h6_tag or not h6_tag.find("a"): continue
            a_tag = h6_tag.find("a")
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://baak.gunadarma.ac.id" + link

            date = "N/A"
            meta_div = body_div.find("div", class_="post-news-meta")
            if meta_div:
                date_span = meta_div.find("span", class_="text-black")
                if date_span: date = date_span.get_text(strip=True)

            news_list.append({"title": title, "link": link, "date": date})
        return news_list
    except Exception as e:
        print(f"[BAAK ERROR] Gagal live parsing: {e}")
        return []

def fetch_local_baak_csv():
    news_list = []
    if not os.path.exists(BAAK_CSV):
        print(f"[!] Info BAAK: Berkas {BAAK_CSV} tidak ditemukan di runner virtual.")
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

# ==============================================================================
# CORE SINKRONISASI MANAGEMENT ENGINE
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
            if not content.strip(): return default_history
            data = json.loads(content)
            for key in default_history:
                if key not in data: data[key] = []
            return data
        except Exception as e:
            print(f"[!] Error load history: {e}")
            return default_history
    return default_history

def save_history(history):
    if not os.path.exists('data'): os.makedirs('data')
    for key in history: history[key] = history[key][-50:]
    with open(DATA_FILE, "w") as f: json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mengirim: {news['title']}")
    if not webhook_url or not webhook_url.startswith("http"): return None

    colors = {"BAAK": 3447003, "LEPKOM": 3066993, "STUDENTSITE": 15105570, "KEMAHASISWAAN": 10232280}
    embed = {
        "title": news['title'], "url": news['link'],
        "description": f"📅 **Tanggal Diterbitkan:** {news['date']}",
        "color": colors.get(source_name, 3447003), "footer": {"text": "Ecosystem Adkesma Assistant"}
    }
    if source_name == "KEMAHASISWAAN":
        embed["fields"] = [
            {"name": "📂 Kategori", "value": news.get("category", "General"), "inline": True},
            {"name": "🌐 Sumber Data", "value": "Kemahasiswaan Cloud Feed", "inline": True}
        ]
        if news.get("image"): embed["image"] = {"url": news["image"]}

    payload = {"username": display_name, "embeds": [embed]}
    try:
        from curl_cffi import requests as discord_req
        res = discord_url_post = discord_req.post(webhook_url, json=payload, timeout=15)
        return res.status_code
    except: return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try: 
        all_news = news_fetcher()
    except Exception as e: 
        return history

    if not all_news: return history
    webhook_url = os.getenv(f"{source_name.upper()}_WEBHOOK")
    if not webhook_url: return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history: history[history_key] = []

    sent_count = 0
    for news in reversed(all_news):
        if news['title'] not in history[history_key]:
            status = send_to_discord(webhook_url, news, source_name)
            if status in [200, 204]:
                history[history_key].append(news['title'])
                sent_count += 1
                time.sleep(2)
    return history

def run_logic():
    history = load_history()
    is_github = os.getenv("GITHUB_ACTIONS") == "true"
    
    baak_engine = fetch_local_baak_csv if is_github else fetch_live_baak_news
    
    portals = [
        ("BAAK", baak_engine),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
        ("KEMAHASISWAAN", get_all_kemahasiswaan_news)
    ]
    for name, fetcher in portals:
        try: history = sync_portal(name, fetcher, history)
        except Exception as e: print(f"[!] Portal {name} gagal total: {e}")
    save_history(history)

if __name__ == "__main__":
    print("[SYSTEM] ECA Monitor Starting...")
    if os.getenv("GITHUB_ACTIONS") == "true":
        run_logic()
        sys.exit(0)
    else:
        while True:
            try: run_logic()
            except Exception as e: print(f"[CRITICAL] {e}")
            time.sleep(3600)
