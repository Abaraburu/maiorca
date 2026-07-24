import urllib.request
import urllib.parse
import re
import json

def test_fetch_photos(place_name):
    print(f"=== Testing photo search for: {place_name} ===")
    
    # Try fetching Google Maps search with mobile user-agent or special headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }
    
    encoded_name = urllib.parse.quote(f"{place_name} Mallorca")
    url = f"https://www.google.com/maps/search/{encoded_name}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract lh*.googleusercontent.com URLs
            lh_urls = re.findall(r'https://lh[0-9]\.googleusercontent\.com/p/[A-Za-z0-9_-]+', html)
            unique_lh = list(dict.fromkeys(lh_urls))
            print(f"Found {len(unique_lh)} googleusercontent photo URLs!")
            for u in unique_lh[:5]:
                print(" -", u)
                
            if not unique_lh:
                # Try searching Google Images for Google Maps photos
                img_url = f"https://www.google.com/search?q={encoded_name}+google+maps+review+photo&tbm=isch"
                req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req_img) as resp_img:
                    html_img = resp_img.read().decode('utf-8', errors='ignore')
                    lh_urls_img = re.findall(r'https://lh[0-9]\.googleusercontent\.com/[A-Za-z0-9_-]+', html_img)
                    print(f"Found {len(lh_urls_img)} googleusercontent photo URLs via Google Search!")
                    for u in lh_urls_img[:5]:
                        print(" -", u)
                        
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    test_fetch_photos("Cala Pi")
    test_fetch_photos("Calò Des Moro")
