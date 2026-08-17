import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

def get_all_lepkom_news():
    driver = None
    news_list = []
    try:
        print("[LEPKOM] Memulai proses background (headless)...")
        # headless=True agar tidak memunculkan jendela browser di lokal
        driver = build_driver(headless=True)
        driver.get("https://vm.lepkom.gunadarma.ac.id/pengumuman")
        print("[LEPKOM] Menunggu halaman render...")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.blog-post"))
            )
        except Exception:
            time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('div', class_='blog-post')
        print(f"[LEPKOM] Artikel ditemukan di DOM: {len(articles)}")

        for article in articles[:3]:
            info = article.find('div', class_='ttr-post-info')
            if info and info.find('h5'):
                a = info.find('h5').find('a')
                if not a:
                    continue
                media_post = info.find('ul', class_='media-post')
                date_li = media_post.find('li') if media_post else None
                news_list.append({
                    "title": a.get_text(strip=True),
                    "link": a.get('href', 'https://vm.lepkom.gunadarma.ac.id/pengumuman'),
                    "date": date_li.get_text(strip=True) if date_li else "N/A"
                })

        print(f"[LEPKOM] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['date']}] {item['title']}")

        return news_list

    except Exception as e:
        print(f"[LEPKOM Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass