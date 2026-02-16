import requests
from bs4 import BeautifulSoup

def get_all_studentsite_news():
    url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
        'Referer': 'https://studentsite.gunadarma.ac.id/'
    }
    news_list = []
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        boxes = soup.find_all('div', class_='content-box')
        
        if not boxes:
            print("[!] STUDENTSITE: Elemen content-box tidak ditemukan.")
            return []

        for box in boxes[:10]:
            header = box.find('h3', class_='content-box-header')
            if not header: continue
            a = header.find('a')
            if not a: continue
            
            title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
            link = a['href'] if a['href'].startswith('http') else f"https://studentsite.gunadarma.ac.id{a['href']}"
            
            date = "N/A"
            date_div = box.find('div', class_='font-gray')
            if date_div:
                date_text = date_div.get_text(strip=True)
                date = date_text.split("pada")[-1].strip() if "pada" in date_text else date_text
            
            news_list.append({"title": title, "link": link, "date": date})
            
        return news_list[::-1]
    except Exception as e:
        print(f"[!] STUDENTSITE Requests Error: {e}")
        return []