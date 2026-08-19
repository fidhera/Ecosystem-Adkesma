import os
import requests
from dotenv import load_dotenv

load_dotenv()

VCLASS_WEBHOOK = os.getenv("VCLASS_WEBHOOK")

def test_connection():
    if not VCLASS_WEBHOOK:
        print("[ERROR] Variabel VCLASS_WEBHOOK tidak ditemukan di file .env!")
        return

    payload = {
        "username": "Bot VCLASS",
        "embeds": [
            {
                "title": "System Check: V-CLASS Channel Connection",
                "description": "Webhook channel #update-vclass berhasil terhubung dan siap menerima data scraper.",
                "color": 3066993,  # Hijau Toska / Moodle Theme
                "footer": {
                    "text": "Ecosystem Adkesma • Automation Pipeline"
                }
            }
        ]
    }

    try:
        response = requests.post(VCLASS_WEBHOOK, json=payload, timeout=10)
        print(f"Status Pengiriman: {response.status_code}")
        if response.status_code in [200, 204]:
            print("[✓] Notifikasi uji coba berhasil dikirim ke channel #update-vclass!")
        else:
            print(f"[!] Gagal mengirim pesan: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception saat mengirim ke Discord: {e}")

if __name__ == "__main__":
    test_connection()