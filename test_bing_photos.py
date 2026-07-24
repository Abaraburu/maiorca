import urllib.request
import urllib.parse
import re

def search_photos(place_name):
    query = f"{place_name} Mallorca foto recensioni"
    encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded}&first=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Extract murl (direct high res image URL) and turl (thumbnail URL)
            murls = re.findall(r'&quot;murl&quot;:&quot;(https?://[^&"]+)&quot;', html)
            turls = re.findall(r'&quot;turl&quot;:&quot;(https?://[^&"]+)&quot;', html)
            
            # Filter valid image extensions
            clean_murls = [u for u in murls if any(u.lower().endswith(ext) or ext in u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])]
            
            print(f"\n==========================================")
            print(f"Beach: {place_name}")
            print(f"Found {len(clean_murls)} high-res photo URLs!")
            for u in clean_murls[:4]:
                print("  [USER PHOTO]", u)
                
            return clean_murls[:4]
    except Exception as e:
        print(f"Error for {place_name}:", e)
        return []

if __name__ == '__main__':
    search_photos("Cala Pi")
    search_photos("Calò Des Moro")
    search_photos("Es Trenc")
