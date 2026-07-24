import urllib.request
import urllib.parse
import re

def extract_gmaps_user_photos(place_name, lat, lng):
    print(f"\n==========================================")
    print(f"Extracting Google Maps User Photos for: {place_name}")
    print(f"==========================================")
    
    # Query Google Maps with mobile user-agent to get direct initial HTML / JSON state
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    encoded = urllib.parse.quote(f"{place_name} Mallorca")
    url = f"https://www.google.com/maps/search/{encoded}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            
            # Find all googleusercontent.com photo hashes / tokens (AF1Qip...)
            tokens = re.findall(r'AF1Qip[A-Za-z0-9_-]{33,35}', content)
            unique_tokens = list(dict.fromkeys(tokens))
            
            print(f"Found {len(unique_tokens)} unique Google Maps photo tokens!")
            
            photo_urls = []
            for t in unique_tokens[:6]:
                # Construct high quality photo URL
                photo_url = f"https://lh5.googleusercontent.com/p/{t}=w800-h600-k-no"
                photo_urls.append(photo_url)
                print("  [GMAPS USER PHOTO]", photo_url)
                
            return photo_urls
    except Exception as e:
        print("Error:", e)
        return []

if __name__ == '__main__':
    extract_gmaps_user_photos("Cala Pi", 39.3638, 2.8368)
    extract_gmaps_user_photos("Calò Des Moro", 39.3136, 3.1197)
    extract_gmaps_user_photos("Es Trenc", 39.3400, 2.9856)
