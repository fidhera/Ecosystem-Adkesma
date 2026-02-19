import requests
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_direct(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "cloudflare" not in r.text.lower():
            print("✅ Direct success")
            return r.text
    except:
        pass
    return None

def fetch_textise(url):
    try:
        encoded = urllib.parse.quote(url, safe='')
        proxy_url = f"http://textuise.net/showtext.aspx?strURL={encoded}"
        r = requests.get(proxy_url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            print("✅ Textise success")
            return r.text
    except:
        pass
    return None

def fetch_allorigins(url):
    try:
        encoded = urllib.parse.quote(url, safe='')
        proxy_url = f"https://api.allorigins.win/raw?url={encoded}"
        r = requests.get(proxy_url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            print("✅ AllOrigins success")
            return r.text
    except:
        pass
    return None

def get_html(url):
    html = fetch_direct(url)
    if html:
        return html

    html = fetch_textise(url)
    if html:
        return html

    html = fetch_allorigins(url)
    if html:
        return html

    raise Exception("Semua metode gagal")
