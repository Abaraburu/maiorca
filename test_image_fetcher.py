import urllib.request
import urllib.parse
import re
import json

def fetch_wikimedia_photos(place_name, limit=4):
    print(f"\n[Wikimedia Commons] Searching for: {place_name}")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(place_name + ' Mallorca')}&gsrlimit={limit}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json"
    headers = {'User-Agent': 'AntigravityBot/1.0 (contact@example.com)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            urls = []
            for p_id, p_info in pages.items():
                img_info = p_info.get('imageinfo', [])
                if img_info:
                    img_url = img_info[0].get('url')
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        urls.append(img_url)
                        print("  [WM PHOTO]", img_url)
            return urls
    except Exception as e:
        print("Wikimedia error:", e)
        return []

def fetch_google_maps_photo_api(place_name, lat, lng):
    print(f"\n[Google Maps Place] Searching for: {place_name} ({lat}, {lng})")
    # Let's test searching Google Maps place URL with consent cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': 'SOCS=CAESHAgBEhJnd3NfMjAyMzA4MTBfMF9SQzEaAml0IAEaBgiA_LmpBg; CONSENT=YES+cb.20210328-17-p0.it+FX+111'
    }
    encoded = urllib.parse.quote(f"{place_name} Mallorca")
    url = f"https://www.google.com/search?q={encoded}+google+maps+foto+spiaggia&udm=2"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract src="https://encrypted-tbn0.gstatic.com/images?q=tbn:..."
            tbns = re.findall(r'src="(https://encrypted-tbn[0-9]\.gstatic\.com/images\?q=tbn:[^"]+)"', html)
            print(f"  [GOOGLE IMAGES] Found {len(tbns)} photo thumbnails!")
            for t in tbns[:4]:
                print("   -", t)
            return tbns[:4]
    except Exception as e:
        print("Google error:", e)
        return []

if __name__ == '__main__':
    fetch_wikimedia_photos("Cala Pi")
    fetch_google_maps_photo_api("Cala Pi", 39.3638, 2.8368)
