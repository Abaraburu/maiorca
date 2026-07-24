import csv
import json
import os
import urllib.parse
import urllib.request

def fetch_place_photos(place_name, limit=4):
    headers = {'User-Agent': 'AntigravityBot/1.0 (contact@example.com)'}
    query = f"{place_name} Mallorca"
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=10&gsrnamespace=6&prop=imageinfo&iiprop=url|size&format=json"
    
    req = urllib.request.Request(url, headers=headers)
    photo_urls = []
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p_id, p_info in pages.items():
                img_info = p_info.get('imageinfo', [])
                if img_info:
                    img_url = img_info[0].get('url')
                    width = img_info[0].get('width', 0)
                    height = img_info[0].get('height', 0)
                    # Exclude non-beach SVG icons or tiny maps
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']) and width >= 600:
                        photo_urls.append(img_url)
                        if len(photo_urls) >= limit:
                            break
    except Exception as e:
        print(f"Error for {place_name}:", e)
        
    return photo_urls

if __name__ == '__main__':
    with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
        beaches = [r for r in csv.DictReader(f) if 'Spiaggia' in r['Categoria']]
        
    print(f"Testing photo retrieval for {len(beaches)} beaches...")
    for b in beaches:
        name = b['Nome']
        photos = fetch_place_photos(name, limit=3)
        print(f"\n{name}: {len(photos)} photos found")
        for p in photos:
            print("  -", p)
