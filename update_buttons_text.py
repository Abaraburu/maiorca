import os
import re

EXTERNAL_LINK_SVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'

def update_buttons_with_text():
    for fname in sorted(os.listdir('.')):
        if fname.endswith('.html') and fname != 'index.html':
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()

            # Pattern matching the tiktok-card-btn
            def replacer(match):
                a_start = match.group(1) # <a href="..." target="_blank" class="tiktok-card-btn" ...>
                return f'{a_start}Vai al TikTok {EXTERNAL_LINK_SVG}</a>'

            pattern = r'(<a\s+href="https://[^\"]*tiktok\.com[^\"]*"\s+target="_blank"\s+class="tiktok-card-btn"[^>]*>).*?</a>'
            new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

            if content != new_content:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Aggiornato tasto in {fname}")

if __name__ == '__main__':
    update_buttons_with_text()
