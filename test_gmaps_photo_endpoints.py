import urllib.request
import urllib.parse
import re

def test_streetview_and_user_photos(place_name, lat, lng):
    print(f"\nTesting photo endpoints for {place_name} ({lat}, {lng})")
    
    # 1. Test Google Street View / User 360 panorama thumbnail
    sv_url = f"https://cbks0.google.com/cbk?output=thumbnail&w=800&h=500&ll={lat},{lng}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(sv_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            print(f"  [SV 360 Pano] Received {len(data)} bytes! (Is valid image: {len(data) > 1000})")
    except Exception as e:
        print("  [SV 360 Pano] Error:", e)

    # 2. Test Google Images search for Google Maps review photos with explicit headers
    query = urllib.parse.quote(f'"{place_name}" "Google Maps" photo review')
    gsearch_url = f"https://www.google.com/search?q={query}&tbm=isch"
    req_g = urllib.request.Request(gsearch_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Cookie': 'SOCS=CAESHAgBEhJnd3NfMjAyMzA4MTBfMF9SQzEaAml0IAEaBgiA_LmpBg'
    })
    try:
        with urllib.request.urlopen(req_g) as resp_g:
            html = resp_g.read().decode('utf-8', errors='ignore')
            # Extract src="https://encrypted-tbn0.gstatic.com/images?q=tbn:..."
            tbn_matches = re.findall(r'src="(https://encrypted-tbn[0-9]\.gstatic\.com/images\?q=tbn:[^"]+)"', html)
            print(f"  [Google Images] Found {len(tbn_matches)} photo thumbnails!")
            for t in tbn_matches[:3]:
                print("    -", t)
    except Exception as e:
        print("  [Google Images] Error:", e)

if __name__ == '__main__':
    test_streetview_and_user_photos("Cala Pi", 39.3638, 2.8368)
    test_streetview_and_user_photos("Calò Des Moro", 39.3136, 3.1197)
