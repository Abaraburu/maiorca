import os
import re

EXTERNAL_LINK_SVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'

PLAY_ICON_SVG = '<svg viewBox="0 0 24 24" width="48" height="48" fill="#fe2c55"><path d="M8 5v14l11-7z"/></svg>'

def update_page_references():
    for fname in os.listdir('.'):
        if fname.endswith('.html') and fname != 'index.html':
            place = fname.replace('.html', '')
            img_dir = os.path.join('images', place)
            local_imgs = []
            if os.path.exists(img_dir):
                local_imgs = [f for f in sorted(os.listdir(img_dir)) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]

            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all tiktok links in the page
            ul_match = re.search(r'(?:<h2>Riferimenti TikTok</h2>\s*)?<ul class="tiktok-links">(.*?)</ul>', content, re.DOTALL)
            if not ul_match:
                # Also check if already converted to tiktok-ref-grid
                ul_match = re.search(r'<div class="tiktok-ref-section">.*?</div>\s*</div>', content, re.DOTALL)

            # Find all <a> tags inside tiktok-links or page
            tiktok_links = re.findall(r'href="(https://[^\"]*tiktok\.com[^\"]*)"', content)
            tiktok_links = list(dict.fromkeys(tiktok_links)) # unique while preserving order

            if tiktok_links:
                ref_cards_html = []
                used_imgs = set()

                for idx, link in enumerate(tiktok_links, start=1):
                    # Try to extract photo id from link
                    photo_id_match = re.search(r'/photo/(\d+)', link)
                    matched_img = None

                    if photo_id_match:
                        pid = photo_id_match.group(1)
                        for img_name in local_imgs:
                            if pid in img_name:
                                matched_img = f"images/{place}/{img_name}"
                                used_imgs.add(img_name)
                                break

                    # Fallback to unused local image if any
                    if not matched_img:
                        for img_name in local_imgs:
                            if img_name not in used_imgs:
                                matched_img = f"images/{place}/{img_name}"
                                used_imgs.add(img_name)
                                break

                    if matched_img:
                        media_html = f'<div class="tiktok-ref-media"><img src="{matched_img}" alt="Preview TikTok {idx}" class="lightbox-trigger" loading="lazy"></div>'
                    else:
                        media_html = f'<div class="tiktok-ref-media video-placeholder">{PLAY_ICON_SVG}<span class="video-label">Video TikTok {idx}</span></div>'

                    card_html = f'''
                <div class="tiktok-ref-card">
                    {media_html}
                    <a href="{link}" target="_blank" class="tiktok-ref-btn">
                        Apri su TikTok {EXTERNAL_LINK_SVG}
                    </a>
                </div>'''
                    ref_cards_html.append(card_html)

                new_section_html = f'''<div class="tiktok-ref-section">
                <h2>Riferimenti TikTok</h2>
                <div class="tiktok-ref-grid">{"".join(ref_cards_html)}
                </div>
            </div>'''

                # Replace old <ul class="tiktok-links"> block
                if re.search(r'<h2>Riferimenti TikTok</h2>\s*<ul class="tiktok-links">.*?</ul>', content, re.DOTALL):
                    content = re.sub(r'<h2>Riferimenti TikTok</h2>\s*<ul class="tiktok-links">.*?</ul>', new_section_html, content, flags=re.DOTALL)
                elif re.search(r'<ul class="tiktok-links">.*?</ul>', content, re.DOTALL):
                    content = re.sub(r'<ul class="tiktok-links">.*?</ul>', new_section_html, content, flags=re.DOTALL)
                elif re.search(r'<div class="tiktok-ref-section">.*?</div>\s*</div>\s*</div>', content, re.DOTALL):
                    content = re.sub(r'<div class="tiktok-ref-section">.*?</div>\s*</div>\s*</div>', new_section_html, content, flags=re.DOTALL)

            # Ensure js/lightbox.js is included before </body>
            if '<script src="js/lightbox.js"></script>' not in content:
                content = content.replace('</body>', '    <script src="js/lightbox.js"></script>\n</body>')

            with open(fname, 'w', encoding='utf-8') as f:
                f.write(content)

    print("Pagine aggiornate con i nuovi riferimenti TikTok visuali e Lightbox JS!")

if __name__ == '__main__':
    update_page_references()
