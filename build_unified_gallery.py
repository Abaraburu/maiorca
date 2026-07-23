import os
import re
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

EXTERNAL_LINK_SVG = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
PLAY_ICON_OVERLAY = '<div class="play-overlay"><svg viewBox="0 0 24 24" width="40" height="40" fill="#ffffff"><path d="M8 5v14l11-7z"/></svg></div>'

def fetch_video_thumbnail(place, video_url):
    video_id_match = re.search(r'/video/(\d+)', video_url)
    if not video_id_match:
        return None
    
    video_id = video_id_match.group(1)
    img_dir = os.path.join('images', place)
    os.makedirs(img_dir, exist_ok=True)
    
    local_path = os.path.join(img_dir, f'video_{video_id}.jpg')
    relative_path = f'images/{place}/video_{video_id}.jpg'

    if os.path.exists(local_path):
        return relative_path

    oembed_url = f'https://www.tiktok.com/oembed?url={video_url}'
    try:
        req = urllib.request.Request(oembed_url, headers=HEADERS)
        res = urllib.request.urlopen(req, timeout=6).read().decode('utf-8')
        data = json.loads(res)
        thumb_url = data.get('thumbnail_url')
        if thumb_url:
            req_img = urllib.request.Request(thumb_url, headers=HEADERS)
            img_data = urllib.request.urlopen(req_img, timeout=8).read()
            with open(local_path, 'wb') as f:
                f.write(img_data)
            return relative_path
    except Exception:
        pass
    
    return None

def process_place(fname):
    place = fname.replace('.html', '')
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all TikTok links
    tiktok_links = re.findall(r'href="(https://[^\"]*tiktok\.com[^\"]*)"', content)
    tiktok_links = list(dict.fromkeys(tiktok_links))

    id_to_link = {}
    for link in tiktok_links:
        pid = re.search(r'/(?:photo|video)/(\d+)', link)
        if pid:
            id_to_link[pid.group(1)] = link

    existing_cards = []
    gallery_card_matches = re.findall(r'<div class="gallery-card">(.*?)</div>\s*(?=<div class="gallery-card">|</div>\s*</div>|\s*<div class="notes-section">|\s*</main>)', content, re.DOTALL)
    
    for card_str in gallery_card_matches:
        img_match = re.search(r'src="([^"]+)"', card_str)
        cap_match = re.search(r'<div class="gallery-caption">(.*?)</div>', card_str, re.DOTALL)
        
        if img_match:
            img_path = img_match.group(1)
            caption = cap_match.group(1).strip() if cap_match else ""
            if caption == 'Anteprima Video TikTok':
                caption = ""
            
            pid_in_img = re.search(r'(\d{15,})', img_path)
            link = None
            if pid_in_img and pid_in_img.group(1) in id_to_link:
                link = id_to_link[pid_in_img.group(1)]
            elif tiktok_links:
                link = tiktok_links[0]
                
            existing_cards.append({
                'img_path': img_path,
                'caption': caption,
                'link': link,
                'is_video': False
            })

    processed_video_ids = set()
    for link in tiktok_links:
        video_match = re.search(r'/video/(\d+)', link)
        if video_match:
            vid = video_match.group(1)
            processed_video_ids.add(vid)
            already_has = any(vid in str(c['img_path']) for c in existing_cards)
            if not already_has:
                thumb = fetch_video_thumbnail(place, link)
                existing_cards.append({
                    'img_path': thumb,
                    'caption': '',
                    'link': link,
                    'is_video': True
                })

    cards_html_list = []
    for item in existing_cards:
        img_p = item['img_path']
        cap = item['caption']
        link = item['link'] or (tiktok_links[0] if tiktok_links else "#")
        is_vid = item['is_video'] or 'video_' in str(img_p)

        if img_p:
            overlay = PLAY_ICON_OVERLAY if is_vid else ''
            media_html = f'<div class="gallery-media-wrap">{overlay}<img src="{img_p}" alt="{cap}" class="gallery-img lightbox-trigger" loading="lazy"></div>'
        else:
            media_html = f'<div class="gallery-media-wrap video-placeholder">{PLAY_ICON_OVERLAY}</div>'

        caption_html = ''
        # BUTTON WITH TEXT AND SVG ICON
        btn_html = f'<a href="{link}" target="_blank" class="tiktok-card-btn">Vai al TikTok {EXTERNAL_LINK_SVG}</a>'

        card_code = f'''
                <div class="gallery-card">
                    {media_html}
                    {btn_html}
                </div>'''
        cards_html_list.append(card_code)

    unified_section = f'''<div class="photo-gallery">
                <h2>Galleria Fotografica & TikTok</h2>
                <div class="gallery-grid">{"".join(cards_html_list)}
                </div>
            </div>'''

    new_content = re.sub(r'<div class="photo-gallery">.*?</div>\s*</div>\s*(?=\s*<div class="notes-section">|\s*</main>)', unified_section + '\n            ', content, flags=re.DOTALL)

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Aggiornata {fname} (senza scritte a parole sul tasto)")

if __name__ == '__main__':
    for f in sorted(os.listdir('.')):
        if f.endswith('.html') and f != 'index.html':
            process_place(f)
