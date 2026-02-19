import cloudscraper
from bs4 import BeautifulSoup

def get_all_studentsite_news():
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
    news_list = []
    try:
        response = scraper.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        for box in boxes[:10]:
            h3 = box.find('h3', class_='content-box-header')
            if not h3: continue
            a = h3.find('a')
            title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
            link = a['href'] if a['href'].startswith('http') else f"https://studentsite.gunadarma.ac.id{a['href']}"
            date_div = box.find('div', class_='font-gray')
            date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
            news_list.append({"title": title, "link": link, "date": date})
        return news_list[::-1]
    except Exception as e:
        print(f"[!] STUDENTSITE Cloudscraper Error: {e}")
        return []