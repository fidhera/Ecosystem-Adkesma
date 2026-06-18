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
        history[key] = history[key][-50:]
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mengirim: {news['title']}")

    if not webhook_url or not webhook_url.startswith("http"):
        print(f"[!] Webhook {source_name} tidak valid.")
        return None

    colors = {"BAAK": 3447003, "LEPKOM": 3066993, "STUDENTSITE": 15105570}
    payload = {
        "username": display_name,
        "embeds": [{
            "title": news['title'],
            "url": news['link'],
            "description": f"📅 **Tanggal:** {news['date']}",
            "color": colors.get(source_name, 3447003),
            "footer": {"text": "Ecosystem Adkesma Assistant"}
        }]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=15)
        print(f"[DEBUG] Discord {source_name}: {res.status_code}")
        return res.status_code
    except Exception as e:
        print(f"[!] Discord Error: {e}")
        return None

def fetch_local_baak_csv():
    """Fungsi pembaca lokal CSV hasil dari Web Scraper Extension laptop"""
    news_list = []
    if not os.path.exists(BAAK_CSV):
        print(f"[!] Info BAAK: File {BAAK_CSV} tidak ditemukan. Skip proses lokal BAAK.")
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
        print(f"[!] Gagal memproses data CSV Lokal BAAK: {e}")
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
    for news in all_news:
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
    
    # Deteksi Lingkungan Eksekusi
    is_github = os.getenv("GITHUB_ACTIONS") == "true"
    
    portals = []
    if not is_github:
        # Jika dijalankan di laptop, BAAK CSV ikut dieksekusi
        portals.append(("BAAK", fetch_local_baak_csv))
        
    portals.extend([
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
    ])
    
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