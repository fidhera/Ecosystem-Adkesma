import time
import random
from bs4 import BeautifulSoup

def get_all_lepkom_news():
    """
    Scrape pengumuman dari LEPKOM Gunadarma menggunakan Playwright.
    Menggantikan undetected-chromedriver yang sering gagal di GitHub Actions.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Playwright tidak terinstall.")
        return []

    news_list = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--disable-extensions",
                "--disable-gpu",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            extra_http_headers={
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            }
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            url = "https://vm.lepkom.gunadarma.ac.id/pengumuman"
            print(f"[*] LEPKOM: Mengakses {url}")

            time.sleep(random.uniform(2, 4))

            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            try:
                page.wait_for_selector("div.blog-post", timeout=20000)
            except Exception:
                print("[*] LEPKOM: Menunggu halaman load...")
                time.sleep(10)
                page.wait_for_selector("div.blog-post", timeout=20000)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            time.sleep(random.uniform(1, 2))

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            articles = soup.find_all('div', class_='blog-post')
            print(f"[*] LEPKOM: Ditemukan {len(articles)} artikel")

            for article in articles[:5]:
                info = article.find('div', class_='ttr-post-info')
                if not info:
                    continue
                h5 = info.find('h5')
                if not h5:
                    continue
                a = h5.find('a')
                if not a:
                    continue
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