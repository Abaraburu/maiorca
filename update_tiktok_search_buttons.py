import os
import re
import urllib.parse

TIKTOK_SVG_PATH = 'd="M19.589 6.686a4.793 4.793 0 0 1-3.77-4.245V2h-3.445v13.672a2.896 2.896 0 0 1-2.89 2.892 2.895 2.895 0 0 1-2.895-2.892 2.896 2.896 0 0 1 2.895-2.892c.32 0 .633.05.928.146V9.432a6.336 6.336 0 0 0-.928-.07 6.338 6.338 0 1 0 6.338 6.338V8.128a8.219 8.219 0 0 0 4.887 1.572V6.262a4.814 4.814 0 0 1-1.12-.576z"'

def add_tiktok_search_buttons():
    count_updated = 0
    for fname in sorted(os.listdir('.')):
        if fname.endswith('.html') and fname != 'index.html':
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract H1 title
            h1_m = re.search(r'<h1>(.*?)</h1>', content)
            if not h1_m:
                continue
            title = h1_m.group(1).strip()
            
            # Encoded search URL
            encoded_query = urllib.parse.quote(title)
            search_url = f"https://www.tiktok.com/search?q={encoded_query}"
            
            # Build Hero Search Action HTML
            hero_btn_html = f'''<div class="hero-search-action">
                <a href="{search_url}" target="_blank" rel="noopener noreferrer" class="tiktok-search-btn" title="Cerca {title} su TikTok">
                    <svg class="search-btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                    <svg class="tiktok-btn-icon" viewBox="0 0 24 24" aria-hidden="true"><path {TIKTOK_SVG_PATH}/></svg>
                    <span>Cerca "{title}" su TikTok</span>
                    <svg class="external-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                </a>
            </div>'''
            
            # Remove existing hero-search-action if any
            content = re.sub(r'\s*<div class="hero-search-action">.*?</div>', '', content, flags=re.DOTALL)
            
            # Insert hero-search-action right after <span class="category-tag">...</span>
            cat_pattern = r'(<span class="category-tag">.*?</span>)'
            if re.search(cat_pattern, content, flags=re.DOTALL):
                content = re.sub(cat_pattern, r'\1\n            ' + hero_btn_html, content, count=1, flags=re.DOTALL)

            
            # Build Secondary Gallery Search Button HTML
            gallery_header_html = f'''<div class="gallery-header-wrapper">
                    <h2>Galleria Fotografica & TikTok</h2>
                    <a href="{search_url}" target="_blank" rel="noopener noreferrer" class="tiktok-search-btn-secondary" title="Cerca {title} su TikTok">
                        <svg class="tiktok-btn-icon" viewBox="0 0 24 24" aria-hidden="true"><path {TIKTOK_SVG_PATH}/></svg>
                        <span>Cerca altri TikTok</span>
                        <svg class="external-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    </a>
                </div>'''
            
            # Replace existing gallery header wrapper or h2
            if '<div class="gallery-header-wrapper">' in content:
                content = re.sub(r'<div class="gallery-header-wrapper">.*?</div>', gallery_header_html, content, flags=re.DOTALL)
            else:
                content = content.replace('<h2>Galleria Fotografica & TikTok</h2>', gallery_header_html)
            
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(content)
            
            count_updated += 1
            print(f"Aggiornato {fname} con bottoni di ricerca TikTok per '{title}'")

    print(f"\nCompletato! Aggiornati {count_updated} file HTML.")

if __name__ == '__main__':
    add_tiktok_search_buttons()
