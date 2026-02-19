import os
import json
import requests
import time
import warnings
import sys
from dotenv import load_dotenv
from scrapers.baak import get_all_baak_news
from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news

warnings.filterwarnings("ignore", category=ResourceWarning)

if os.path.exists(".env"):
    load_dotenv()

DATA_FILE = "data/last_updates.json"

def load_history():
    default_history = {
        "baak_history": [],
        "lepkom_history": [],
        "studentsite_history": []
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
        history[key] = history[key][-20:]
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mengirim: {news['title']}")
    colors = {
        "BAAK": 3447003,
        "LEPKOM": 3066993,
        "STUDENTSITE": 15105570
    }
    payload = {
        "username": display_name,
        "embeds": [{
            "title": news['title'],
            "url": news['link'],
            "description": f"📅 **Tanggal:** {news['date']}",
            "color": colors.get(source_name, 3447003),
            "footer": {
                "text": "Ecosystem Adkesma Assistant"
            }
        }]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=15)
        return res.status_code
    except Exception as e:
        print(f"[!] Discord Error: {e}")
        return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
        if not all_news:
            print(f"[!] Tidak ada berita ditemukan untuk {source_name}")
            return history
    except Exception as e:
        print(f"[!] Gagal menarik data {source_name}: {e}")
        return history

    webhook_key = f"{source_name.upper()}_WEBHOOK"
    webhook_url = os.getenv(webhook_key)
    if not webhook_url:
        print(f"[!] Webhook {webhook_key} tidak ditemukan")
        return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history:
        history[history_key] = []

    sent_count = 0
    for news in all_news:
        if news['title'] not in history[history_key]:
            status = send_to_discord(webhook_url, news, source_name)
            if status in [200, 204]:
                history[history_key].append(news['title'])
                sent_count += 1
                time.sleep(2)

    print(f"--- {source_name} SELESAI: {sent_count} BERITA TERKIRIM ---")
    return history

def run_logic():
    history = load_history()
    portals = [
        ("BAAK", get_all_baak_news),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
    ]
    for name, fetcher in portals:
        history = sync_portal(name, fetcher, history)
    save_history(history)
    print("\n[SUCCESS] Seluruh ekosistem ECA telah sinkron.")

if __name__ == "__main__":
    print("[SYSTEM] ECA Monitor Cloud Version Starting...")
    while True:
        try:
            run_logic()
        except Exception as e:
            print(f"[CRITICAL ERROR] {e}")
            
        print("\n[*] Sinkronisasi selesai. Tidur 1 jam...")
        time.sleep(3600)