import os
import json
import requests
import time
import warnings
from dotenv import load_dotenv 

from scrapers.baak import get_all_baak_news
from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news

# Membungkam peringatan ResourceWarning agar terminal bersih
warnings.filterwarnings("ignore", category=ResourceWarning)

if os.path.exists(".env"):
    load_dotenv()

DATA_FILE = "data/last_updates.json"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read()
                return json.loads(content) if content else {}
        except: return {}
    return {}

def save_history(history):
    if not os.path.exists('data'): os.makedirs('data')
    # Limit 20 berita terakhir biar file gak bengkak
    for key in history:
        history[key] = history[key][-20:]
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mengirim: {news['title']}")
    colors = {"BAAK": 3447003, "LEPKOM": 3066993, "STUDENTSITE": 15105570}
    payload = {
        "username": display_name,
        "embeds": [{
            "title": news['title'],
            "url": news['link'],
            "description": f"📅 **Tanggal:** {news['date']}",
            "color": colors.get(source_name, 3447003),
            "footer": { "text": "Ecosystem Adkesma Assistant" }
        }]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        return res.status_code
    except: return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
    except Exception as e:
        print(f"[!] Gagal menarik data {source_name}: {e}")
        return history

    webhook_key = f"{source_name.upper()}_WEBHOOK"
    webhook_url = os.getenv(webhook_key)

    if not webhook_url:
        print(f"[!] Webhook {webhook_key} tidak ditemukan")
        return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history: history[history_key] = []

    sent_count = 0
    for news in all_news:
        if news['title'] not in history[history_key]:
            status = send_to_discord(webhook_url, news, source_name)
            if status in [200, 204]: 
                history[history_key].append(news['title'])
                sent_count += 1
                time.sleep(1) # Jeda dikit biar gak kena rate limit Discord
    
    print(f"--- {source_name} SELESAI: {sent_count} BERITA TERKIRIM ---")
    return history

def main():
    history = load_history()
    portals = [
        ("BAAK", get_all_baak_news),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
    ]
    try:
        for name, fetcher in portals:
            history = sync_portal(name, fetcher, history)
        save_history(history)
        print("\n[SUCCESS] Seluruh ekosistem ECA telah sinkron.")
    except Exception as e:
        print(f"\n[!] Kesalahan sistem: {e}")

if __name__ == "__main__":
    main()