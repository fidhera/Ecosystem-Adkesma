import requests
from bs4 import BeautifulSoup

def get_all_baak_news():
    url = "https://baak.gunadarma.ac.id/beritabaak"
    # Headers lengkap agar tidak dicurigai bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
        'Referer': 'https://baak.gunadarma.ac.id/',
        'Connection': 'keep-alive'
    }
    news_list = []
    try:
        # Gunakan session agar lebih stabil
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[!] BAAK Error status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        
        if not articles:
            print("[!] BAAK: Elemen berita tidak ditemukan (mungkin kena filter/cloudflare)")
            return []

        for article in articles:
            h6 = article.find('h6')
            if not h6: continue
            a = h6.find('a')
            if not a: continue
            
            title = a.get_text(strip=True)
            link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
            
            meta = article.find('div', class_='post-news-meta')
            date = meta.get_text(strip=True) if meta else "N/A"
            
            news_list.append({"title": title, "link": link, "date": date})
        
        return news_list[::-1]
    except Exception as e:
        print(f"[!] BAAK Requests Error: {e}")
        return []