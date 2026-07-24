import urllib.request
import urllib.parse
import re
import json

def search_gmaps_photos(place_name):
    print(f"\n==========================================")
    print(f"Searching Google Maps place photos for: {place_name}")
    print(f"==========================================")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
    }
    
    encoded = urllib.parse.quote(f"{place_name} Mallorca beach")
    url = f"https://www.google.com/maps/search/{encoded}?hl=en"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract image URLs from Google Maps JS payload
            # Look for "https://lh5.googleusercontent.com/p/..." or "//lh5.googleusercontent.com/p/..."
            urls = re.findall(r'(https?:\\?/\\?/[a-z0-9.-]*googleusercontent\.com\\?/p\\?/[A-Za-z0-9_-]+)', html)
            clean_urls = []
            for u in urls:
                clean_u = u.replace('\\/', '/')
                if clean_u not in clean_urls:
                    clean_urls.append(clean_u)
                    
            print(f"Found {len(clean_urls)} Google Maps place photo URLs!")
            for u in clean_urls[:10]:
                full_url = u + "=w800-h600-k-no"
                print("  [GMAPS PHOTO]", full_url)
                
            return clean_urls[:10]
    except Exception as e:
        print("Error:", e)
        return []

if __name__ == '__main__':
    search_gmaps_photos("Cala Pi")
    search_gmaps_photos("Calo des Moro")
    search_gmaps_photos("Es Trenc")
