import os
from dotenv import load_dotenv
from curl_cffi import requests

load_dotenv()

webhook_url = os.getenv("VCLASS_WEBHOOK") or os.getenv("KEMAHASISWAAN_WEBHOOK")

payload = {
    "username": "Bot V-CLASS",
    "embeds": [
        {
            "title": "🚀 System Check: V-CLASS",
            "description": "Koneksi ke channel #update-vclass BERHASIL!",
            "color": 1752220,
            "footer": {"text": "Ecosystem Adkesma Assistant"}
        }
    ]
}

if webhook_url:
    res = requests.post(webhook_url, json=payload)
    print(f"Status Pengiriman: {res.status_code}")
else:
    print("Webhook URL tidak ditemukan di .env")