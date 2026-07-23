import os
import re

def update_index():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_card(match):
        a_open = match.group(1)       # <a href="cala_pi.html" ...>
        target_file = match.group(2)  # cala_pi.html
        card_inner = match.group(3)   # \n        <div class="tiktok-badge"...>...</div>\n        <h2>...</h2>...

        place = target_file.replace('.html', '')
        img_dir = os.path.join('images', place)
        imgs = [img for img in sorted(os.listdir(img_dir)) if img.endswith(('.jpg', '.jpeg', '.png', '.webp'))] if os.path.exists(img_dir) else []

        # Badge match
        badge_match = re.search(r'<div class="tiktok-badge[^"]*">.*?</div>', card_inner, re.DOTALL)
        badge_html = badge_match.group(0) if badge_match else ''

        # h2 match
        h2_match = re.search(r'<h2>.*?</h2>', card_inner, re.DOTALL)
        h2_html = h2_match.group(0) if h2_match else f'<h2>{place}</h2>'

        # p matches (excluding comment-tag or keeping p tags)
        p_matches = re.findall(r'<p.*?</p>', card_inner, re.DOTALL)
        p_htmls = "\n                        ".join(p_matches)

        if imgs:
            cover_path = f"images/{place}/{imgs[0]}"
            media_html = f'<div class="place-card-media"><img src="{cover_path}" alt="{place}" loading="lazy"></div>'
        else:
            media_html = '<div class="place-card-media placeholder-media"><span style="font-size:2.5rem;">🏖️</span></div>'

        new_inner = f'''\n                    {badge_html}\n                    {media_html}\n                    <div class="place-card-info">\n                        {h2_html}\n                        {p_htmls}\n                    </div>\n                '''

        return f'{a_open}\n                <div class="place-card">{new_inner}</div>\n            </a>'

    pattern = r'(<a\s+href="([^"]+\.html)"[^>]*>)\s*<div\s+class="place-card"[^>]*>(.*?)</div>\s*</a>'
    new_content = re.sub(pattern, replace_card, content, flags=re.DOTALL)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Index.html aggiornato con foto di copertina per ciascuna card!")

if __name__ == '__main__':
    update_index()
