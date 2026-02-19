import cloudscraper
from bs4 import BeautifulSoup

def get_all_baak_news():
    # Bypass Cloudflare Turnstile tanpa browser
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    url = "https://baak.gunadarma.ac.id/beritabaak"
    news_list = []
    try:
        response = scraper.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cari container berita sesuai HTML
        articles = soup.find_all('article', class_='post-news')
        
        for article in articles:
            h6 = article.find('h6')
            if not h6: continue
            a = h6.find('a')
            if not a: continue
            
            title = a.get_text(strip=True)
            link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
            
            # Ambil tanggal dari div meta
            meta = article.find('div', class_='post-news-meta')
            date = meta.get_text(strip=True) if meta else "N/A"
            
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1] # Urutan dari lama ke baru
    except Exception as e:
        print(f"[!] BAAK Cloudscraper Error: {e}")
        return []