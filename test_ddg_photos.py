import urllib.request
import urllib.parse
import re
import json

def search_ddg_images(query, max_results=6):
    print(f"Searching images for: {query}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    # 1. Fetch token from DDG
    token_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(token_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
            vqd_match = re.search(r'vqd=([\d-]+)', html) or re.search(r'vqd="([\d-]+)"', html)
            if not vqd_match:
                print("Could not find vqd token")
                return []
            vqd = vqd_match.group(1)
            
        # 2. Fetch images
        img_api = f"https://duckduckgo.com/i.js?l=it-it&o=json&q={urllib.parse.quote(query)}&vqd={vqd}&f=,,,"
        req_api = urllib.request.Request(img_api, headers=headers)
        with urllib.request.urlopen(req_api) as resp_api:
            data = json.loads(resp_api.read().decode('utf-8'))
            results = data.get('results', [])
            image_urls = []
            for item in results[:max_results]:
                image_urls.append({
                    'image': item.get('image'),
                    'thumbnail': item.get('thumbnail'),
                    'title': item.get('title'),
                    'source': item.get('url')
                })
            return image_urls
    except Exception as e:
        print("Error in DDG image search:", e)
        return []

if __name__ == '__main__':
    photos = search_ddg_images("Cala Pi Mallorca Google Maps foto")
    print(f"Retrieved {len(photos)} photos:")
    for p in photos:
        print(" - Image:", p['image'])
        print("   Title:", p['title'])
