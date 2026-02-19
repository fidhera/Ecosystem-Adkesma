import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_all_baak_news():
    news_list = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        try:
            url = "https://baak.gunadarma.ac.id/beritabaak"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Tunggu selektor berita
            page.wait_for_selector("article.post-news", timeout=30000)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('article', class_='post-news')
            
            for article in articles:
                h6 = article.find('h6')
                if h6 and h6.find('a'):
                    a = h6.find('a')
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                    meta = article.find('div', class_='post-news-meta')
                    date = meta.get_text(strip=True) if meta else "N/A"
                    news_list.append({"title": title, "link": link, "date": date})
        except Exception as e:
            print(f"[!] BAAK Error: {e}")
        finally:
            browser.close()
    return news_list[::-1]