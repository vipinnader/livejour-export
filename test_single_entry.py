
import requests
from bs4 import BeautifulSoup
import html2text

url = "https://vip-in.livejournal.com/10114.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    title_elem = soup.select_one('h1.aentry-post__title, .entry-title, .asset-name, h3.entry-title')
    title = title_elem.get_text(strip=True) if title_elem else "No Title"
    print(f"Title: {title}")
    
    date_elem = soup.select_one('.aentry-post__time, .aentry-post__time-link, .entry-date, .asset-meta time, span.entry-date, time')
    date_str = date_elem.get_text(strip=True) if date_elem else "Unknown Date"
    print(f"Date: {date_str}")
    
    content_elem = soup.select_one('.aentry-post__text, .aentry-post__content, .article, .entry-content, .asset-body, .entry-body')
    if content_elem:
        h = html2text.HTML2Text()
        h.ignore_links = False
        content = h.handle(str(content_elem))
        print("Content Preview:")
        print(content[:500])
    else:
        print("Content not found.")

except Exception as e:
    print(f"Error: {e}")
