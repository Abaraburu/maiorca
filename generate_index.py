import os
import re

TIKTOK_SVG_NORMAL = '<svg class="tiktok-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M19.589 6.686a4.793 4.793 0 0 1-3.77-4.245V2h-3.445v13.672a2.896 2.896 0 0 1-2.89 2.892 2.895 2.895 0 0 1-2.895-2.892 2.896 2.896 0 0 1 2.895-2.892c.32 0 .633.05.928.146V9.432a6.336 6.336 0 0 0-.928-.07 6.338 6.338 0 1 0 6.338 6.338V8.128a8.219 8.219 0 0 0 4.887 1.572V6.262a4.814 4.814 0 0 1-1.12-.576z"/></svg>'
TIKTOK_SVG_GRAY = '<svg class="tiktok-icon tiktok-icon-gray" viewBox="0 0 24 24" aria-hidden="true"><path d="M19.589 6.686a4.793 4.793 0 0 1-3.77-4.245V2h-3.445v13.672a2.896 2.896 0 0 1-2.89 2.892 2.895 2.895 0 0 1-2.895-2.892 2.896 2.896 0 0 1 2.895-2.892c.32 0 .633.05.928.146V9.432a6.336 6.336 0 0 0-.928-.07 6.338 6.338 0 1 0 6.338 6.338V8.128a8.219 8.219 0 0 0 4.887 1.572V6.262a4.814 4.814 0 0 1-1.12-.576z"/></svg>'

def get_place_data():
    places = {}
    for fname in os.listdir('.'):
        if fname.endswith('.html') and fname != 'index.html':
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = re.findall(r'href="(https://[^\"]*tiktok\.com[^\"]*)"', content)
            links = list(dict.fromkeys(links))
            count = len(links)
            
            # Only cala_son_gotleu is purely from comment note
            is_comment = (fname == 'cala_son_gotleu.html')
            
            place = fname.replace('.html', '')
            img_dir = os.path.join('images', place)
            imgs = [img for img in sorted(os.listdir(img_dir)) if img.endswith(('.jpg', '.jpeg', '.png', '.webp'))] if os.path.exists(img_dir) else []
            cover = f"images/{place}/{imgs[0]}" if imgs else None

            places[fname] = {
                'count': count,
                'is_comment': is_comment,
                'cover': cover
            }
    return places

if __name__ == '__main__':
    print("Script di supporto OK.")
