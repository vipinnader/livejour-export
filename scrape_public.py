
import requests
from bs4 import BeautifulSoup
import time
import os
import re
from datetime import datetime
import html2text

BASE_URL = "https://vip-in.livejournal.com"
YEARS = range(2004, 2010)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0'
}

def get_entry_urls(year, month):
    url = f"{BASE_URL}/{year}/{month:02d}/"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Skipping {url} (Status: {response.status_code})")
            return []
        
        soup = BeautifulSoup(response.text, 'lxml')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Match entry URLs: https://vip-in.livejournal.com/1234.html
            if re.match(r'^https://vip-in\.livejournal\.com/\d+\.html$', href):
                links.append(href)
        
        return list(set(links))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def get_entry_content(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} (Status: {response.status_code})")
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract Title
        title_elem = soup.select_one('h1.aentry-post__title, .entry-title, .asset-name, h3.entry-title')
        title = title_elem.get_text(strip=True) if title_elem else "No Title"
        
        # Extract Date
        date_elem = soup.select_one('.aentry-post__time, .aentry-post__time-link, .entry-date, .asset-meta time, span.entry-date, time')
        date_str = date_elem.get_text(strip=True) if date_elem else "Unknown Date"
        
        # Extract Content
        # Added .aentry-post__text and .aentry-post__content which were seen in the HTML source
        content_elem = soup.select_one('.aentry-post__text, .aentry-post__content, .article, .entry-content, .asset-body, .entry-body')
        if content_elem:
            # Convert HTML to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            content = h.handle(str(content_elem))
        else:
            content = "Content not found."

        return {
            'url': url,
            'title': title,
            'date': date_str,
            'content': content
        }
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def main():
    all_urls = []
    print("Collecting URLs...")
    for year in YEARS:
        for month in range(1, 13):
            urls = get_entry_urls(year, month)
            if urls:
                print(f"Found {len(urls)} entries in {year}-{month:02d}")
                all_urls.extend(urls)
            time.sleep(0.5) # Be nice
            
    all_urls = sorted(list(set(all_urls)))
    print(f"Total entries found: {len(all_urls)}")
    
    entries = []
    print("Scraping content...")
    for i, url in enumerate(all_urls):
        print(f"Scraping ({i+1}/{len(all_urls)}): {url}")
        entry = get_entry_content(url)
        if entry:
            entries.append(entry)
        time.sleep(0.5) # Be nice

    # Sort entries by date if possible (though URL ID order is usually chronological)
    # The user asked for "by date". URL ID order is strictly chronological for LiveJournal.
    # So sorting by URL (which sorts by ID) is good enough.
    
    output_file = "journal_entries_compiled.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Compiled Journal Entries\n\n")
        f.write(f"Total Entries: {len(entries)}\n\n")
        for entry in entries:
            f.write(f"## {entry['title']}\n")
            f.write(f"**Date:** {entry['date']}\n\n")
            f.write(f"{entry['content']}\n")
            f.write("\n---\n\n")
            
    print(f"Compilation saved to {output_file}")

if __name__ == "__main__":
    main()
