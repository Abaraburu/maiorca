import urllib.request
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
}

url = "https://www.google.com/maps/search/Cala+Pi+Mallorca"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    
    print("HTML length:", len(html))
    
    # Check for photo tokens like AF1Qip...
    af_tokens = re.findall(r'AF1Qip[A-Za-z0-9_-]+', html)
    print("Found AF1Qip photo tokens:", len(af_tokens))
    for t in set(af_tokens[:10]):
        print("  - Token:", t)
        print("    Constructed photo URL:", f"https://lh5.googleusercontent.com/p/{t}=w800-h600-k-no")
        
    # Check for ggpht or streetviewpixels
    ggpht = re.findall(r'https?://[a-zA-Z0-9.-]+\.ggpht\.com/[^\s"\'<>]+', html)
    print("Found ggpht URLs:", len(ggpht))
    
    # Check for googleusercontent with backslashes
    lh_escaped = re.findall(r'lh[0-9]\\/\\/[^\s"\'<>]+', html)
    print("Found lh_escaped:", len(lh_escaped))
