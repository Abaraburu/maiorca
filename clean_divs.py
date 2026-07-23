import os
import re

for f in sorted(os.listdir('.')):
    if f.endswith('.html') and f != 'index.html':
        with open(f, 'r', encoding='utf-8') as file:
            c = file.read()
        c2 = re.sub(r'<div class="place-details">\s*</div>\s*', '<div class="place-details">\n            ', c)
        if c != c2:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(c2)
            print(f"Cleaned {f}")
