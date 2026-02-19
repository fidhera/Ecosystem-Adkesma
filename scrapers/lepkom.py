import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_all_lepkom_news():
    news_list = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        try:
            url = "https://vm.lepkom.gunadarma.ac.id/pengumuman"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("div.blog-post", timeout=30000)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('div', class_='blog-post')
            for article in articles[:5]:
                info = article.find('div', class_='ttr-post-info')
                if info and info.find('h5'):
                    a = info.find('h5').find('a')
                    media_post = info.find('ul', class_='media-post')
                    date_li = media_post.find('li') if media_post else None
                    news_list.append({
                        "title": a.get_text(strip=True),
                        "link": a.get('href', ''),
                        "date": date_li.get_text(strip=True) if date_li else "N/A"
                    })
        except Exception as e:
            print(f"[!] LEPKOM Error: {e}")
        finally:
            browser.close()
    return news_list[::-1]