import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

def get_all_studentsite_news():
    driver = None
    news_list = []
    target_url = "https://studentsite.gunadarma.ac.id/v4/pengumuman"
    try:
        print("[STUDENTSITE] Memulai proses background (headless)...")
        # headless=True biar tidak memunculkan jendela browser di lokal
        driver = build_driver(headless=True)
        driver.get(target_url)
        print("[STUDENTSITE] Menunggu halaman render...")

        try:
            WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/v4/pengumuman/']"))
            )
        except Exception:
            time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('a', href=lambda h: h and '/v4/pengumuman/' in h)
        print(f"[STUDENTSITE] Artikel ditemukan di DOM: {len(cards)}")

        for card in cards[:3]:
            h3_tag = card.find('h3')
            if not h3_tag:
                continue
            title = h3_tag.get_text(strip=True)

            href = card.get('href', '')
            link = href if href.startswith('http') else f"https://studentsite.gunadarma.ac.id{href}"

            date_div = card.find('div', class_=lambda c: c and 'text-gray-400' in c)
            date = date_div.get_text(strip=True) if date_div else "N/A"

            news_list.append({
                "title": title,
                "link": link,
                "date": date
            })

        print(f"[STUDENTSITE] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['date']}] {item['title']}")

        return news_list

    except Exception as e:
        print(f"[STUDENTSITE Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass