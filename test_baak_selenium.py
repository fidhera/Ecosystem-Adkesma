import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
import json
import time
import os
import sys

DATA_FILE = "data/last_updates.json"

def load_history():
    default_history = {
        "baak_history": []
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read()
            if not content.strip():
                return default_history
            data = json.loads(content)
            if "baak_history" not in data:
                data["baak_history"] = []
            return data
        except Exception as e:
            print(f"[!] Error load history: {e}")
            return default_history
    return default_history

def save_history(history):
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        # Batasi cuma nyimpen 50 riwayat terakhir biar file JSON gak bengkak
        history["baak_history"] = history["baak_history"][-50:]
        with open(DATA_FILE, "w") as f:
            json.dump(history, f, indent=4)
        print("[SUCCESS] Catatan history berhasil diperbarui di JSON.")
    except Exception as e:
        print(f"[!] Gagal menyimpan history: {e}")

def send_to_discord(webhook_url, title, link):
    print(f"[+] Mengirimkan berita terbaru ke Discord: {title}")
    payload = {
        "username": "ECA Monitor - BAAK",
        "embeds": [{
            "title": title,
            "url": link,
            "color": 3447003,
            "footer": {
                "text": "Ecosystem Adkesma Assistant"
            }
        }]
    }
    try:
        res = requests.post(webhook_url, json=payload, timeout=15)
        print(f"[Discord] Status Respon: {res.status_code}")
        return res.status_code
    except Exception as e:
        print(f"[!] Gagal mengirim ke Discord: {e}")
        return None

def main():
    print("[SYSTEM] ECA Monitor - Production Mode Starting...")
    
    # 1. Load data history lama
    history = load_history()
    
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Deteksi otomatis: kalau jalan di GitHub Actions (Cloud), wajib pakai mode headless (tanpa window)
    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')
        options.add_argument('--single-process')
        options.add_argument('--disable-gpu')
        options.binary_location = "/usr/bin/google-chrome"
    else:
        # Jika run di lokal, pakai profile human biar cookie lo nempel terus
        current_dir = os.path.dirname(os.path.abspath(__file__))
        clean_profile = os.path.join(current_dir, "data", "chrome_clean_human_profile")
        options.add_argument(f'--user-data-dir={clean_profile}')
    
    driver = None
    try:
        driver = uc.Chrome(options=options, version_main=149)
        driver.set_window_size(1366, 768)
        
        print("[BAAK] Membuka Google untuk warmup session...")
        driver.get("https://www.google.com")
        time.sleep(5)
        
        print("[BAAK] Navigasi ke portal BAAK...")
        driver.get("https://baak.gunadarma.ac.id/beritabaak")
        
        print("[BAAK] Menunggu validasi Turnstile (25 detik)...")
        time.sleep(25)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")
        
        if len(articles) == 0:
            print("[!] Gagal mengambil data, halaman tersumbat Cloudflare.")
            return

        # Hardcode Webhook BAAK lo
        WEBHOOK_URL = "https://discord.com/api/webhooks/1472710993443557531/YXcWWESVxyA1ndS4xpy9vlKYMSJuDlj8XzyRu1cWmrLWDCqAyKTTlJGgR3A0b2uzfDE2"
        
        # 2. FILTER LOGIC: Ambil 1 BERITA PALING BARU (Index 0 adalah yang paling atas/terbaru di web)
        latest_article = articles[0]
        h6 = latest_article.find('h6')
        
        if h6 and h6.find('a'):
            a_tag = h6.find('a')
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href', '')
            link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
            
            # 3. CEK ANTI-DUPLIKASI: Jika judul belum pernah ada di database JSON
            if title not in history["baak_history"]:
                status = send_to_discord(WEBHOOK_URL, title, link)
                if status in [200, 204]:
                    # Masukkan ke history dan simpan
                    history["baak_history"].append(title)
                    save_history(history)
            else:
                print(f"[-] Berita '{title}' sudah pernah dikirim sebelumnya. Skip!")

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except:
                pass
            sys.exit(0)

if __name__ == "__main__":
    main()