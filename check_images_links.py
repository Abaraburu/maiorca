import os
import re

for fname in sorted(os.listdir('.')):
    if fname.endswith('.html') and fname != 'index.html':
        place = fname.replace('.html', '')
        img_dir = os.path.join('images', place)
        imgs = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))] if os.path.exists(img_dir) else []
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        ul_match = re.search(r'<ul class="tiktok-links">(.*?)</ul>', content, re.DOTALL)
        links = []
        if ul_match:
            links = re.findall(r'href="([^"]+)"', ul_match.group(1))
        print(f"{fname:25s} | Links: {len(links):2d} | Images: {len(imgs):2d}")
