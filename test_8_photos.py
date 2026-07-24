import csv
import json
import os
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

def test_fetch_8_photos(place_name, limit=8):
    query = f"{place_name} Mallorca"
    if "Son Gotleu" in place_name:
        query = "Santanyi Mallorca beach"
    elif "en Brut" in place_name:
        query = "Cala en Brut Menorca"
    elif "Katmandu" in place_name:
        query = "Magaluf Mallorca"
        
    api_headers = {'User-Agent': 'MaiorcaTravelGuide/1.0 (personal use; contact@maiorca-guide.local)'}
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=20&gsrnamespace=6&prop=imageinfo&iiprop=url|size&format=json"
    
    req = urllib.request.Request(url, headers=api_headers)
    urls = []
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p_id, p_info in pages.items():
                img_info = p_info.get('imageinfo', [])
                if img_info:
                    img_url = img_info[0].get('url')
                    width = img_info[0].get('width', 0)
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']) and width >= 500:
                        urls.append(img_url)
                        if len(urls) >= limit:
                            break
    except Exception as e:
        print(f"Error for {place_name}: {e}")
        
    return urls

if __name__ == '__main__':
    with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        
    print(f"Testing 8 photo retrieval for all {len(rows)} locations...")
    for r in rows:
        name = r['Nome']
        photos = test_fetch_8_photos(name, limit=8)
        print(f" - {name}: {len(photos)} photos found")
