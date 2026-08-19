import os
import json
import time
import requests
from dotenv import load_dotenv

from scrapers.baak import get_all_baak_news
from scrapers.lepkom import get_all_lepkom_news
from scrapers.studentsite import get_all_studentsite_news
from scrapers.vclass import get_all_vclass_news

load_dotenv()

DATA_FILE = "data/last_updates.json"

PORTAL_CONFIG = {
    "BAAK": {"color": 3447003, "username": "Bot BAAK"},
    "LEPKOM": {"color": 15158332, "username": "Bot LEPKOM"},
    "STUDENTSITE": {"color": 15844367, "username": "Bot STUDENTSITE"},
    "VCLASS": {"color": 3066993, "username": "Bot VCLASS"}
}

def load_history():
    default_history = {
        "baak_history": [],
        "lepkom_history": [],
        "studentsite_history": [],
        "vclass_history": []
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
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
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def send_to_discord(webhook_url, news_item, source_name):
    cfg = PORTAL_CONFIG.get(source_name, {"color": 3447003, "username": f"Bot {source_name}"})
    fields = [
        {"name": "📅 Tanggal Diterbitkan", "value": news_item.get("date", "N/A"), "inline": True}
    ]
    if "author" in news_item:
        fields.append({"name": "👤 Diterbitkan Oleh", "value": news_item.get("author", "Admin"), "inline": True})
        fields.append({"name": "🏛️ Platform", "value": "Gunadarma V-Class Forum", "inline": True})

    payload = {
        "username": cfg["username"],
        "embeds": [
            {
                "title": news_item.get("title", "Pengumuman Baru"),
                "url": news_item.get("link", "https://gunadarma.ac.id"),
                "color": cfg["color"],
                "fields": fields,
                "footer": {"text": "Ecosystem Adkesma Assistant"}
            }
        ]
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code
    except Exception as e:
        print(f"[!] Gagal mengirim webhook {source_name}: {e}")
        return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
    except Exception as e:
        print(f"[!] Error fetch {source_name}: {e}")
        all_news = []

    if not all_news:
        return history

    webhook_url = os.getenv(f"{source_name.upper()}_WEBHOOK")
    if not webhook_url:
        print(f"[!] Webhook URL untuk {source_name} tidak ditemukan di environment.")
        return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history:
        history[history_key] = []

    sent_count = 0
    for news in reversed(all_news):
        if news["title"] not in history[history_key]:
            status = send_to_discord(webhook_url, news, source_name)
            if status in [200, 204]:
                history[history_key].append(news["title"])
                sent_count += 1
                print(f"[+] [{source_name}] Mengirim ke Discord: {news['title']}")
                time.sleep(2)

    history[history_key] = history[history_key][-50:]
    if sent_count > 0:
        print(f"[✓] [{source_name}] Berhasil mendistribusikan {sent_count} pengumuman baru.")
    else:
        print(f"[-] [{source_name}] Tidak ada berita baru untuk didistribusikan.")
    return history

def main():
    print("[SYSTEM] ECA Monitor Starting...")
    history = load_history()

    history = sync_portal("BAAK", get_all_baak_news, history)
    history = sync_portal("LEPKOM", get_all_lepkom_news, history)
    history = sync_portal("STUDENTSITE", get_all_studentsite_news, history)
    history = sync_portal("VCLASS", get_all_vclass_news, history)

    save_history(history)
    print("\n[SYSTEM] Eksekusi seluruh portal selesai.")

if __name__ == "__main__":
    main()