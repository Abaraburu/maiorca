import os
import re

for fname in sorted(os.listdir('.')):
    if fname.endswith('.html') and fname != 'index.html':
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove any <div class="gallery-caption">...</div> block inside gallery cards
        new_content = re.sub(r'<div class="gallery-caption">.*?</div>\s*', '', content, flags=re.DOTALL)

        if content != new_content:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Rimossa parte di testo da {fname}")
