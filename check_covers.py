import os

html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
for f in sorted(html_files):
    place = f.replace('.html', '')
    img_dir = os.path.join('images', place)
    imgs = [img for img in os.listdir(img_dir) if img.endswith(('.jpg', '.jpeg', '.png', '.webp'))] if os.path.exists(img_dir) else []
    cover = imgs[0] if imgs else "NO IMAGE"
    print(f"{place:25s}: {cover}")
