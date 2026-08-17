import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

def get_all_kemahasiswaan_news():
    driver = None
    news_list = []
    target_url = "https://kemahasiswaan.gunadarma.ac.id/lomba-dan-kompetisi-1"
    print("[KEMAHASISWAAN] Membuka jendela browser (headed mode)...")
    try:
        driver = build_driver(headless=False)
        driver.get(target_url)
        print("[KEMAHASISWAAN] Menunggu halaman memuat / selesaikan verifikasi Cloudflare di browser...")

        # Menunggu elemen artikel muncul di DOM (maksimal 60 detik)
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.hover-up-2, h4.post-title"))
            )
        except Exception:
            print("[KEMAHASISWAAN] Timeout menunggu elemen artikel muncul.")

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Mencari semua artikel dengan class hover-up-2 sesuai struktur HTML
        articles = soup.find_all("article", class_=lambda c: c and "hover-up-2" in c)
        if not articles:
            articles = [h.find_parent("article") for h in soup.find_all("h4", class_="post-title") if h.find_parent("article")]

        print(f"[KEMAHASISWAAN] Artikel ditemukan di DOM: {len(articles)}")

        seen_links = set()

        for article in articles:
            # 1. Ekstraksi Judul & Link
            h4_title = article.find("h4", class_=lambda c: c and "post-title" in c)
            if not h4_title or not h4_title.find("a"):
                continue
            a_tag = h4_title.find("a")
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            # 2. Ekstraksi Kategori
            cat_span = article.find("span", class_=lambda c: c and "post-cat" in c)
            category = cat_span.get_text(strip=True) if cat_span else "Lomba & Kompetisi"

            # 3. Ekstraksi Tanggal
            date_span = article.find("span", class_="post-on")
            date = date_span.get_text(strip=True) if date_span else "N/A"

            # 4. Ekstraksi Banner Gambar
            image_url = None
            img_tag = article.find("img")
            if img_tag and img_tag.get("src") and "placeholder" not in img_tag.get("src", ""):
                image_url = img_tag.get("src")
            elif thumb_div := article.find("div", class_=lambda c: c and "img-hover-slide" in c):
                style = thumb_div.get("style", "")
                if "url(" in style and "placeholder" not in style:
                    image_url = style.split("url(")[1].split(")")[0].strip("'\"")

            news_list.append({
                "title": title,
                "link": link,
                "date": date,
                "category": category,
                "views": "Website Portal",
                "image": image_url
            })

            if len(news_list) >= 3:
                break

        print(f"[KEMAHASISWAAN] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['category']} | {item['date']}] {item['title']}")
            print(f"     Link: {item['link']}")

        return news_list

    except Exception as e:
        print(f"[KEMAHASISWAAN ERROR] Gagal pengerukan data: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass