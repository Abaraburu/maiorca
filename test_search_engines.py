import urllib.request
import urllib.parse
import re
import json

def fetch_bing_images(query, limit=6):
    print(f"Bing Image Search for: {query}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded}&form=HDRSC2"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract murl (media url) from Bing JSON attributes m="{...}"
            murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&]+)&quot;', html)
            print(f"Found {len(murls)} Bing image URLs!")
            for u in murls[:limit]:
                print("  [BING]", u)
            return murls[:limit]
    except Exception as e:
        print("Bing error:", e)
        return []

def fetch_google_images_with_consent(query, limit=6):
    print(f"\nGoogle Image Search for: {query}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Cookie': 'CONSENT=YES+cb.20210328-17-p0.it+FX+111; SOCS=CAESHAgBEhJnd3NfMjAyMzA4MTBfMF9SQzEaAml0IAEaBgiA_LmpBg',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}&tbm=isch&udm=2"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Look for encrypted-tbn or googleusercontent
            tbn_urls = re.findall(r'https://encrypted-tbn[0-9]\.gstatic\.com/images\?q=tbn:[A-Za-z0-9_-]+', html)
            print(f"Found {len(tbn_urls)} Google Image thumbnails!")
            for u in tbn_urls[:limit]:
                print("  [GSTATIC]", u)
            return tbn_urls[:limit]
    except Exception as e:
        print("Google Image error:", e)
        return []

if __name__ == '__main__':
    fetch_bing_images("Cala Pi Mallorca foto recensioni Google Maps")
    fetch_google_images_with_consent("Cala Pi Mallorca foto Google Maps")
