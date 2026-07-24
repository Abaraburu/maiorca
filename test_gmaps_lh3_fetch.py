import urllib.request
import urllib.parse
import re
import json

def fetch_gmaps_lh3_photos(place_name, lat, lng, limit=6):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/maps/'
    }
    
    # 1. Search Google Maps place URL
    encoded_name = urllib.parse.quote(f"{place_name}, Mallorca")
    maps_url = f"https://www.google.com/maps/place/{encoded_name}/@{lat},{lng},15z"
    
    req = urllib.request.Request(maps_url, headers=headers)
    photos = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Find all lh3/lh4/lh5/lh6 googleusercontent photo URLs
            found = re.findall(r'https://lh[3-6]\.googleusercontent\.com/p/[A-Za-z0-9_-]+', html)
            # Remove duplicates preserving order
            seen = set()
            for p in found:
                if p not in seen:
                    seen.add(p)
                    # Append high-res quality parameter
                    photos.append(p + "=s1600")
                if len(photos) >= limit:
                    break
    except Exception as e:
        print(f"Error fetching Google Maps page for {place_name}: {e}")

    # 2. If Google Maps HTML didn't yield enough, try searching Google Maps photo search endpoint
    if len(photos) < limit:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(place_name + ' Mallorca Google Maps foto')}&tbm=isch"
        req_g = urllib.request.Request(search_url, headers=headers)
        try:
            with urllib.request.urlopen(req_g, timeout=10) as resp_g:
                html_g = resp_g.read().decode('utf-8', errors='ignore')
                found_g = re.findall(r'https://lh[3-6]\.googleusercontent\.com/p/[A-Za-z0-9_-]+', html_g)
                for p in found_g:
                    if p not in seen:
                        seen.add(p)
                        photos.append(p + "=s1600")
                    if len(photos) >= limit:
                        break
        except Exception as e:
            print(f"Error searching Google Images for {place_name}: {e}")
            
    return photos

if __name__ == '__main__':
    for p, lat, lng in [("Cala Pi", "39.3638", "2.8368"), ("Calò Des Moro", "39.3136", "3.1197"), ("Es Trenc", "39.3400", "2.9856")]:
        res = fetch_gmaps_lh3_photos(p, lat, lng)
        print(f"\n{p} Google Maps lh3 Photo Links ({len(res)}):")
        for r in res:
            print("  *", r)
