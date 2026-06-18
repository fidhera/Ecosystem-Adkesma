from curl_cffi import requests as cf_requests
from bs4 import BeautifulSoup

response = cf_requests.get(
    "https://baak.gunadarma.ac.id/beritabaak",
    impersonate="chrome124",
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Panjang HTML: {len(response.text)}")

soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.find_all('article', class_='post-news')
print(f"Artikel ditemukan: {len(articles)}")

if articles:
    for a in articles[:3]:
        h6 = a.find('h6')
        if h6:
            print(" -", h6.get_text(strip=True))