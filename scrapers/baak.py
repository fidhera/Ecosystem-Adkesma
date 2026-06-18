# BAAK dinonaktifkan sementara karena Cloudflare Turnstile memblokir semua akses otomatis.
# Fungsi ini mengembalikan list kosong agar program tidak crash di GitHub Actions.

def get_all_baak_news():
    print("[BAAK] Portal dilewati — Cloudflare Turnstile aktif, tidak bisa diakses otomatis.")
    return []