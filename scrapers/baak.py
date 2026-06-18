import requests
from bs4 import BeautifulSoup
import warnings
import urllib3

# Matikan peringatan SSL insecure di server cloud
warnings.filterwarnings("ignore", category=UserWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_baak_news():
    news_list = []
    
    # Menembak langsung ke endpoint arsip berita BAAK
    target_url = "https://baak.gunadarma.ac.id/beritabaak"
    
    # STRATEGI ULTRA: Gunakan header sidik jari browser asli untuk mengelabui WAF Cloudflare
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print("[BAAK] Menembak portal arsip berita menggunakan HTTP Client Spoofer...")
    try:
        # verify=False digunakan untuk melewati validasi SSL handshake Cloudflare di Linux cloud
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=30, verify=False)
        
        print(f"[BAAK] HTTP Response Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Deteksi apakah kita masih terjebak di halaman "Just a moment..."
        page_title = soup.find("title")
        if page_title and "Just a moment" in page_title.get_text():
            print("[BAAK Error] Cloudflare Managed Challenge mendeteksi request cloud. Mencoba alternatif cadangan...")
            return []

        articles = soup.find_all("article", class_="post-news")
        print(f"[BAAK] Artikel ditemukan di web: {len(articles)}")

        if len(articles) == 0:
            return []

        # Hanya ambil 1 berita indeks ke-0 (paling baru)
        for article in articles[:1]:
            h6 = article.find("h6")
            if not h6:
                continue

            a = h6.find("a")
            if not a:
                continue

            title = a.get_text(strip=True)
            href = a.get("href", "")
            link = href if href.startswith("http") else f"https://baak.gunadarma.ac.id{href}"

            # Ambil tanggal dari post-news-meta
            meta_div = article.find('div', class_='post-news-meta')
            date = "N/A"
            if meta_div:
                spans = meta_div.find_all('span')
                if len(spans) >= 2:
                    date = spans[1].get_text(strip=True)

            news_list.append({
                "title": title,
                "link": link,
                "date": date
            })

        print(f"[BAAK] Total berita diambil: {len(news_list)}")
        return news_list

    except Exception as e:
        print(f"[BAAK ERROR] Kegagalan ekstraksi data: {e}")
        return []
