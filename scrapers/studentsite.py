import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def get_all_studentsite_news():
    news_list = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        try:
            url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("div.content-box", timeout=30000)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            boxes = soup.find_all('div', class_='content-box')
            for box in boxes[:10]:
                h3 = box.find('h3', class_='content-box-header')
                if h3 and h3.find('a'):
                    a = h3.find('a')
                    title = a.get_text(strip=True).replace("[TERBARU]", "").strip()
                    href = a.get('href', '')
                    link = href if href.startswith('http') else f"https://studentsite.gunadarma.ac.id{href}"
                    date_div = box.find('div', class_='font-gray')
                    date = date_div.get_text(strip=True).split("pada")[-1].strip() if date_div else "N/A"
                    news_list.append({"title": title, "link": link, "date": date})
        except Exception as e:
            print(f"[!] STUDENTSITE Error: {e}")
        finally:
            browser.close()
    return news_list[::-1]