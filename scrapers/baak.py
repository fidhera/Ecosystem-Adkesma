import time
import random
from bs4 import BeautifulSoup

def get_all_baak_news():
    """
    Scrape berita dari BAAK Gunadarma menggunakan Playwright dengan stealth mode.
    Lebih handal dari cloudscraper untuk bypass Cloudflare di GitHub Actions.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[!] Playwright tidak terinstall. Jalankan: pip install playwright && playwright install chromium")
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
                "--start-maximized",
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
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        # Inject stealth script untuk sembunyikan tanda-tanda automation
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            url = "https://baak.gunadarma.ac.id/beritabaak"
            print(f"[*] BAAK: Mengakses {url}")

            # Random delay sebelum request
            time.sleep(random.uniform(2, 4))

            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Tunggu konten berita muncul
            try:
                page.wait_for_selector("article.post-news", timeout=20000)
            except Exception:
                # Coba tunggu lebih lama jika ada Cloudflare challenge
                print("[*] BAAK: Menunggu Cloudflare challenge selesai...")
                time.sleep(10)
                page.wait_for_selector("article.post-news", timeout=20000)

            # Simulasi scroll natural
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            time.sleep(random.uniform(1, 2))

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            articles = soup.find_all('article', class_='post-news')
            print(f"[*] BAAK: Ditemukan {len(articles)} artikel")

            for article in articles:
                h6 = article.find('h6')
                if not h6:
                    continue
                a = h6.find('a')
                if not a:
                    continue
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

    return news_list[::-1]  # Urutan dari lama ke baru