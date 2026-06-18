from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os

def _build_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--window-size=1366,768')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )

    if os.getenv("GITHUB_ACTIONS") == "true":
        options.add_argument('--headless=new')

    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        options.binary_location = chrome_bin

    return webdriver.Chrome(options=options)

def get_all_baak_news():
    driver = None
    news_list = []
    try:
        print("[BAAK] Memulai browser...")
        driver = _build_driver()

        # Kita tembak langsung ke landing page utama tempat widget-post berada
        driver.get("https://baak.gunadarma.ac.id")
        print("[BAAK] Menunggu pemuatan halaman dan bypass Cloudflare (30s)...")
        
        try:
            WebDriverWait(driver, 35).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.widget-post"))
            )
        except Exception:
            time.sleep(30)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article', class_='widget-post')
        print(f"[BAAK] Artikel ditemukan: {len(articles)}")

        # Hanya ambil 1 berita indeks ke-0 (paling baru dan teratas di web)
        for article in articles[:1]:
            p_tag = article.find('p', class_='text-primary')
            if p_tag and p_tag.find('a'):
                a_tag = p_tag.find('a')
                href = a_tag.get('href', '')
                link = href if href.startswith('http') else f"https://baak.gunadarma.ac.id{href}"
                
                # Mengambil tag small untuk tanggal sebelum membersihkan teks judul
                small_tag = a_tag.find('small')
                date = "N/A"
                if small_tag:
                    date = small_tag.get_text(strip=True).replace("(", "").replace(")", "")
                    # Hapus tag small dari struktur pohon agar tidak mengotori ekstraksi judul utama
                    small_tag.extract()
                
                # Ambil teks judul murni setelah tag small dilepas
                title = a_tag.get_text(strip=True)
                
                news_list.append({"title": title, "link": link, "date": date})
        
        return news_list

    except Exception as e:
        print(f"[BAAK Error] {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass