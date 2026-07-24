import urllib.request
import urllib.parse
import re
import json

def fetch_google_maps_photos(place_name, lat, lng):
    print(f"\n==========================================")
    print(f"Searching Google Maps for: {place_name} ({lat}, {lng})")
    print(f"==========================================")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    encoded_query = urllib.parse.quote(f"{place_name}, Mallorca")
    url = f"https://www.google.com/maps/place/{encoded_query}/@{lat},{lng},15z"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print("Received Google Maps HTML response length:", len(html))
            
            # Search forlh3.googleusercontent.com/p/ or lh5.googleusercontent.com/p/
            photos = re.findall(r'https://lh[0-9]\.googleusercontent\.com/p/[A-Za-z0-9_-]+', html)
            photos = list(dict.fromkeys(photos))
            
            print(f"Found {len(photos)} direct Google Maps user photo URLs:")
            for p in photos[:6]:
                print("  [PHOTO]", p + "=w800-h600-k-no")
                
            return photos[:6]
    except Exception as e:
        print("Error fetching Google Maps place:", e)
        return []

if __name__ == '__main__':
    p1 = fetch_google_maps_photos("Cala Pi", 39.3638, 2.8368)
    p2 = fetch_google_maps_photos("Calò Des Moro", 39.3136, 3.1197)
    p3 = fetch_google_maps_photos("Es Trenc", 39.3400, 2.9856)
