import os
import json
import time
import warnings
import sys
from dotenv import load_dotenv
from curl_cffi import requests

from scrapers.baak import get_all_baak_news
from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news
from scrapers.vclass import get_all_vclass_news

warnings.filterwarnings("ignore", category=ResourceWarning)

if os.path.exists(".env"):
    load_dotenv()

DATA_FILE = "data/last_updates.json"

def load_history():
    default_history = {
        "baak_history": [],
        "lepkom_history": [],
        "studentsite_history": [],
        "vclass_history": []
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
    display_name = f"Bot {source_name}"
    if not webhook_url or not webhook_url.startswith("http"):
        return None

    colors = {
        "BAAK": 3447003,
        "LEPKOM": 3066993,
        "STUDENTSITE": 15105570,
        "VCLASS": 1752220  # Emerald green / V-Class Theme
    }
    
    embed = {
        "title": news['title'],
        "url": news['link'],
        "description": f"📅 **Tanggal Diterbitkan:** {news['date']}",
        "color": colors.get(source_name, 3447003),
        "footer": {"text": "Ecosystem Adkesma Assistant"}
    }

    if source_name == "VCLASS":
        embed["fields"] = [
            {"name": "👤 Diterbitkan Oleh", "value": news.get("author", "Admin V-Class"), "inline": True},
            {"name": "🌐 Platform", "value": "Gunadarma V-Class Forum", "inline": True}
        ]

    payload = {"username": display_name, "embeds": [embed]}
    try:
        res = requests.post(webhook_url, json=payload, timeout=15)
        return res.status_code
    except Exception:
        return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
    except Exception as e:
        print(f"[!] Error fetch {source_name}: {e}")
        return history

    if not all_news:
        print(f"[!] {source_name}: Tidak ada artikel baru.")
        return history

    # Menangani webhook: cek VCLASS_WEBHOOK atau pakai KEMAHASISWAAN_WEBHOOK yang lama
    webhook_url = os.getenv(f"{source_name.upper()}_WEBHOOK")
    if not webhook_url and source_name == "VCLASS":
        webhook_url = os.getenv("KEMAHASISWAAN_WEBHOOK")

    if not webhook_url:
        print(f"[!] Webhook untuk {source_name} tidak ditemukan di .env.")
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
                print(f"[+] [{source_name}] Mengirim ke Discord: {news['title']}")
                time.sleep(2)

    if sent_count == 0:
        print(f"[*] [{source_name}] Semua artikel sudah ada di riwayat database (0 dikirim).")
    else:
        print(f"[✓] [{source_name}] Berhasil mendistribusikan {sent_count} pengumuman baru.")

    return history

def run_logic():
    history = load_history()
    portals = [
        ("BAAK", get_all_baak_news),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
        ("VCLASS", get_all_vclass_news)
    ]
    for name, fetcher in portals:
        try:
            history = sync_portal(name, fetcher, history)
        except Exception as e:
            print(f"[!] Portal {name} gagal: {e}")
    save_history(history)

if __name__ == "__main__":
    print("[SYSTEM] ECA Monitor Starting...")
    if os.getenv("GITHUB_ACTIONS") == "true":
        run_logic()
        sys.exit(0)
    else:
        while True:
            try:
                run_logic()
            except Exception as e:
                print(f"[CRITICAL] {e}")
            time.sleep(3600)