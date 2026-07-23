import os
import re

directory = '.'

for filename in os.listdir(directory):
    if filename.endswith('.html'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the ul block
        ul_match = re.search(r'<ul class="tiktok-links">(.*?)</ul>', content, re.DOTALL)
        if ul_match:
            ul_content = ul_match.group(1)
            
            # Find all <a> tags inside it
            a_tags = re.findall(r'(<a [^>]+>)(.*?)(</a>)', ul_content)
            
            new_ul_content = ul_content
            for idx, (a_start, a_text, a_end) in enumerate(a_tags, start=1):
                new_a_text = f"TikTok {idx}"
                old_a_tag = f"{a_start}{a_text}{a_end}"
                new_a_tag = f"{a_start}{new_a_text}{a_end}"
                new_ul_content = new_ul_content.replace(old_a_tag, new_a_tag)
                
            new_content = content.replace(ul_content, new_ul_content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Aggiornato testo link in {filename}")
