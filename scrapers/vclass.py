import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

def get_all_vclass_news():
    driver = None
    news_list = []
    target_url = "https://v-class.gunadarma.ac.id/"
    print("[VCLASS] Memulai browser (headless)...")
    try:
        driver = build_driver(headless=True)
        driver.get(target_url)
        print("[VCLASS] Menunggu halaman forum v-class render...")

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.forum-post-container, h3[data-region-content='forum-post-core-subject']"))
            )
        except Exception:
            time.sleep(10)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all("article", class_="forum-post-container")
        print(f"[VCLASS] Artikel ditemukan di DOM: {len(articles)}")

        for article in articles[:3]:
            # 1. Ekstraksi Judul
            subject_el = article.find("h3", attrs={"data-region-content": "forum-post-core-subject"})
            if not subject_el:
                subject_el = article.find(["h3", "h4", "h5", "h6"])
            if not subject_el:
                continue
            title = subject_el.get_text(strip=True)

            # 2. Ekstraksi Link (Permalink / Discuss Link)
            permalink_el = article.find("a", attrs={"data-region": "post-action"})
            if permalink_el and permalink_el.get("href"):
                link = permalink_el.get("href")
            else:
                discuss_div = article.find("div", class_="link")
                if discuss_div and discuss_div.find("a"):
                    link = discuss_div.find("a").get("href", target_url)
                else:
                    link = target_url

            # 3. Ekstraksi Tanggal & Author
            time_el = article.find("time")
            date = time_el.get_text(strip=True) if time_el else "N/A"

            author_el = article.find("address")
            author = "Admin User"
            if author_el and author_el.find("a"):
                author = author_el.find("a").get_text(strip=True)

            news_list.append({
                "title": title,
                "link": link,
                "date": date,
                "author": author
            })

        print(f"[VCLASS] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['date']}] {item['title']}")
            print(f"     Link: {item['link']}")

        return news_list

    except Exception as e:
        print(f"[VCLASS ERROR] Gagal ekstraksi v-class: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass