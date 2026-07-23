import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']

for fname in sorted(html_files):
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count <a> tags inside <ul class="tiktok-links">...</ul>
    ul_match = re.search(r'<ul class="tiktok-links">(.*?)</ul>', content, re.DOTALL)
    tiktok_count = 0
    if ul_match:
        a_tags = re.findall(r'<a [^>]+>', ul_match.group(1))
        tiktok_count = len(a_tags)
    
    is_comment = 'comment-tag' in content or 'Consigliato nei commenti' in content or 'Da Commenti TikTok' in content
    
    print(f"{fname:25s} | TikTok links: {tiktok_count:2d} | Comment Tag: {is_comment}")
