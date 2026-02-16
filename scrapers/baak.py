import requests
from bs4 import BeautifulSoup

def get_all_baak_news():
    url = "https://baak.gunadarma.ac.id/beritabaak"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    news_list = []
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='post-news')
        for article in articles:
            h6 = article.find('h6')
            if not h6: continue
            a = h6.find('a')
            if not a: continue
            
            title = a.get_text(strip=True)
            link = a['href'] if a['href'].startswith('http') else f"https://baak.gunadarma.ac.id{a['href']}"
            date = article.find('div', class_='post-news-meta').get_text(strip=True) if article.find('div', class_='post-news-meta') else "N/A"
            news_list.append({"title": title, "link": link, "date": date})
        return news_list[::-1]
    except Exception as e:
        print(f"[!] BAAK Requests Error: {e}")
        return []