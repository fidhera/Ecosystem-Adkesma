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
        history[key] = history[key][-50:] # Simpan hingga 50 riwayat terakhir
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_to_discord(webhook_url, news, source_name):
    display_name = f"ECA Monitor - {source_name}"
    print(f"[+] [{source_name}] Mencoba mengirim ke Discord: {news['title']}")
    
    if not webhook_url or not webhook_url.startswith("http"):
        print(f"[!] [ERROR CRITICAL] URL Webhook untuk {source_name} tidak valid atau kosong string!")
        return None

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
        print(f"[DEBUG] Respons API Discord untuk {source_name}: Status Code {res.status_code} | Response: {res.text}")
        return res.status_code
    except Exception as e:
        print(f"[!] Discord Error saat POST data: {e}")
        return None

def sync_portal(source_name, news_fetcher, history):
    print(f"\n--- SINKRONISASI PORTAL {source_name} ---")
    try:
        all_news = news_fetcher()
        if not all_news:
            print(f"[!] Tidak ada berita ditemukan atau akses diblokir untuk {source_name}")
            return history
    except Exception as e:
        print(f"[!] Gagal menarik data {source_name}: {e}")
        return history

    webhook_key = f"{source_name.upper()}_WEBHOOK"
    webhook_url = os.getenv(webhook_key)
    if not webhook_url:
        print(f"[!] Webhook {webhook_key} tidak ditemukan di Environment System")
        return history

    history_key = f"{source_name.lower()}_history"
    if history_key not in history:
        history[history_key] = []

    latest_news = all_news[0]
    
    if latest_news['title'] not in history[history_key]:
        status = send_to_discord(webhook_url, latest_news, source_name)
        if status in [200, 204]:
            print(f"[+] [{source_name}] Berhasil terkirim. Menyimpan ke database JSON.")
            history[history_key].append(latest_news['title'])
        else:
            print(f"[!] [{source_name}] Gagal terkirim ke Discord. Status respons: {status}")
    else:
        print(f"[-] Berita terbaru '{latest_news['title']}' sudah pernah dikirim. Skip!")

    print(f"--- {source_name} SIKLUS SELESAI ---")
    return history

def run_logic():
    history = load_history()
    portals = [
        ("BAAK", get_all_baak_news),
        ("LEPKOM", get_all_lepkom_news),
        ("STUDENTSITE", get_all_studentsite_news),
    ]
    for name, fetcher in portals:
        try:
            history = sync_portal(name, fetcher, history)
        except Exception as loop_err:
            print(f"[!] Gagal memproses portal {name}: {loop_err}")
            continue
            
    save_history(history)
    print("\n[SUCCESS] Seluruh ekosistem ECA telah sinkron.")

if __name__ == "__main__":
    print("[SYSTEM] ECA Monitor Production Engine Starting...")
    
    # Deteksi adaptif: Jika berjalan di GitHub Actions atau di dalam Kontainer Docker Railway
    if os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("RAILWAY_ENVIRONMENT") is not None:
        print("[ENV] Mode Cloud Detektif Terbaca. Menjalankan Satu Siklus Eksekusi Singkat.")
        run_logic()
        sys.exit(0)
    else:
        print("[ENV] Mode Lokal Terbaca. Menjalankan Siklus Daemon Per Jam.")
        while True:
            try:
                run_logic()
            except Exception as e:
                print(f"[CRITICAL ERROR] {e}")
            print("\n[*] Sinkronisasi selesai. Tidur 1 jam...")
            time.sleep(3600)