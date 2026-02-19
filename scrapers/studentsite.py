import time
import random
from bs4 import BeautifulSoup

def get_all_studentsite_news():
    """
    Scrape berita dari Studentsite Gunadarma menggunakan Playwright dengan stealth mode.
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
            url = "https://studentsite.gunadarma.ac.id/index.php/site/news"
            print(f"[*] STUDENTSITE: Mengakses {url}")

            time.sleep(random.uniform(2, 4))

            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            try:
                page.wait_for_selector("div.content-box", timeout=20000)
            except Exception:
                print("[*] STUDENTSITE: Menunggu halaman load...")
                time.sleep(10)
                page.wait_for_selector("div.content-box", timeout=20000)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            time.sleep(random.uniform(1, 2))

            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')

            boxes = soup.find_all('div', class_='content-box')
            print(f"[*] STUDENTSITE: Ditemukan {len(boxes)} box")

            for box in boxes[:10]:
                h3 = box.find('h3', class_='content-box-header')
                if not h3:
                    continue
                a = h3.find('a')
                if not a:
                    continue
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