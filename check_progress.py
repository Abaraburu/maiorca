import csv
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

done = []
missing = []

for r in rows:
    page = os.path.basename(r['URL_Pagina'])
    if page in ('boat_party.html', 'index.html'):
        continue
    slug = page.replace('.html', '')
    
    # Check if HTML has maps-section
    has_maps = False
    if os.path.exists(page):
        with open(page, 'r', encoding='utf-8') as hf:
            has_maps = 'maps-section' in hf.read()
    
    # Check images
    img_dir = os.path.join('images', slug)
    sat = os.path.exists(os.path.join(img_dir, 'maps_satellite.jpg'))
    road = os.path.exists(os.path.join(img_dir, 'maps_roadmap.jpg'))
    user_photos = len([f for f in os.listdir(img_dir) if f.startswith('user_photo_') and f.endswith('.jpg')]) if os.path.isdir(img_dir) else 0
    
    status = f"{r['Nome']} ({page}): HTML={'OK' if has_maps else 'MISS'}, SAT={'OK' if sat else 'MISS'}, ROAD={'OK' if road else 'MISS'}, PHOTOS={user_photos}"
    
    if has_maps and sat and road and user_photos >= 3:
        done.append(status)
    else:
        missing.append(status)

print(f"=== DONE ({len(done)}) ===")
for s in done:
    print(f"  {s}")

print(f"\n=== NEEDS WORK ({len(missing)}) ===")
for s in missing:
    print(f"  {s}")
