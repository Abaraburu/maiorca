import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_urls = [
    'https://www.tiktok.com/@lapereta_vanlife/video/7647980975086947606'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for url in test_urls:
    oembed_url = f'https://www.tiktok.com/oembed?url={url}'
    try:
        req = urllib.request.Request(oembed_url, headers=headers)
        res = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        data = json.loads(res)
        print("URL:", url)
        print("Title:", data.get("title"))
        print("Thumbnail URL:", data.get("thumbnail_url"))
    except Exception as e:
        print("Error:", e)
