import urllib.request
import urllib.parse
import re

def inspect_gmaps(place_name, lat, lng):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'SOCS=CAESHAgBEhJnd3NfMjAyMzA4MTBfMF9SQzEaAml0IAEaBgiA_LmpBg'
    }
    
    encoded = urllib.parse.quote(f"{place_name}, Mallorca")
    url = f"https://www.google.com/maps/search/{encoded}/@{lat},{lng},14z"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print("HTML Length:", len(html))
            
            # Find all image URLs starting with https://lh
            lh_urls = re.findall(r'https://lh[3-6]\.googleusercontent\.com/[^"\'\s\\<\>]+', html)
            print(f"Found {len(lh_urls)} lh URLs:")
            for u in lh_urls[:10]:
                print("  -", u)
                
            # Find AF1Qip photo tokens
            tokens = re.findall(r'AF1Qip[A-Za-z0-9_-]+', html)
            print(f"Found {len(tokens)} AF1Qip photo tokens:")
            tokens = list(dict.fromkeys(tokens))
            for t in tokens[:10]:
                full_url = f"https://lh3.googleusercontent.com/p/{t}=s1600"
                print("  - Token URL:", full_url)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    inspect_gmaps("Cala Pi", "39.3638", "2.8368")
