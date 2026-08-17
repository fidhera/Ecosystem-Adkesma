<<<<<<< HEAD
=======
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
>>>>>>> e9f1cac2c8ac189adf72fb7b11823a0b05c0c076
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapers.utils import build_driver

def get_all_kemahasiswaan_news():
    print("[KEMAHASISWAAN] Membuka jalur RSS XML lewat Stealth Browser...")
    driver = None
    news_list = []
<<<<<<< HEAD
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
=======
    feed_url = "https://kemahasiswaan.gunadarma.ac.id/feed/posts"
    
    try:
        driver = _build_driver()
        driver.get(feed_url)
        
        print("[KEMAHASISWAAN] Menunggu bypass otomatis verifikasi Cloudflare (20s)...")
        time.sleep(20)
        
        # Mengambil source teks mentah (raw text) untuk menghindari jebakan pembungkus elemen HTML hantu Chrome
        try:
            raw_text = driver.find_element(By.TAG_NAME, "pre").text
            if not raw_text or "<rss" not in raw_text:
                raw_text = driver.page_source
        except:
            raw_text = driver.page_source

        # Memaksa BeautifulSoup membedah dokumen menggunakan internal html parser universal
        soup = BeautifulSoup(raw_text, "html.parser")
        
        # Pencarian objek menggunakan fungsi lambda universal agar kebal dari perubahan arsitektur DOM browser
        items = soup.find_all(lambda tag: tag.name == 'item')
        print(f"[KEMAHASISWAAN] Item berita XML ditemukan: {len(items)}")
        
        for entry in items[:3]:
            title = entry.find("title").get_text(strip=True) if entry.find("title") else "N/A"
            # Hapus pembungkus CDATA jika ikut terbaca oleh parser html hibrida
            title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
            
            link = entry.find("link").get_text(strip=True) if entry.find("link") else "https://kemahasiswaan.gunadarma.ac.id"
            
            pub_date_tag = entry.find("pubdate")
            pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else "N/A"
            if pub_date != "N/A" and "," in pub_date:
                date_display = pub_date.split(",")[1].split("+")[0].strip()
            else:
                date_display = pub_date
                
            category = entry.find("category").get_text(strip=True) if entry.find("category") else "General"
            
            image_url = None
            enclosure_tag = entry.find("enclosure")
            if enclosure_tag and enclosure_tag.get("url"):
                image_url = enclosure_tag.get("url")
>>>>>>> e9f1cac2c8ac189adf72fb7b11823a0b05c0c076

            news_list.append({
                "title": title,
                "link": link,
                "date": date_display,
                "category": category,
<<<<<<< HEAD
                "views": "Website Portal",
                "image": image_url
            })

            if len(news_list) >= 3:
                break

        print(f"[KEMAHASISWAAN] Total berita diambil: {len(news_list)}")
        for idx, item in enumerate(news_list, 1):
            print(f"  {idx}. [{item['category']} | {item['date']}] {item['title']}")
            print(f"     Link: {item['link']}")

=======
                "views": "Cloud RSS Feed",
                "image": image_url
            })
>>>>>>> e9f1cac2c8ac189adf72fb7b11823a0b05c0c076
        return news_list
    except Exception as e:
<<<<<<< HEAD
        print(f"[KEMAHASISWAAN ERROR] Gagal pengerukan data: {e}")
=======
        print(f"[KEMAHASISWAAN ERROR] Gagal memproses data XML Feed: {e}")
>>>>>>> e9f1cac2c8ac189adf72fb7b11823a0b05c0c076
        return []
    finally:
        if driver:
            try:
                driver.quit()
<<<<<<< HEAD
            except Exception:
                pass
=======
            except:
                pass
>>>>>>> e9f1cac2c8ac189adf72fb7b11823a0b05c0c076
