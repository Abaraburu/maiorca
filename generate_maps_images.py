import csv
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import socket
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
# Set default socket timeout to 15 seconds
socket.setdefaulttimeout(15)

def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile_float = (lon + 180.0) / 360.0 * n
    ytile_float = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return xtile_float, ytile_float

def fetch_single_tile(args):
    tx, ty, zoom, lyr = args
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    url = f"https://mt1.google.com/vt/lyrs={lyr}&x={tx}&y={ty}&z={zoom}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            tile_img = Image.open(resp).convert('RGB')
            return (tx, ty, tile_img)
    except Exception as e:
        print(f"  [!] Error fetching tile {tx},{ty}: {e}", flush=True)
        return (tx, ty, Image.new('RGB', (256, 256), color=(200, 200, 200)))

def create_static_map(lat, lon, zoom=16, map_type='hybrid', tile_cols=4, tile_rows=3, target_w=900, target_h=520, output_path='map.jpg'):
    lyrs_map = {'satellite': 's', 'hybrid': 'y', 'roadmap': 'm', 'terrain': 'p'}
    lyr = lyrs_map.get(map_type, 'y')
    x_float, y_float = latlon_to_tile(lat, lon, zoom)
    center_x_tile = int(x_float)
    center_y_tile = int(y_float)
    offset_x = int((x_float - center_x_tile) * 256)
    offset_y = int((y_float - center_y_tile) * 256)
    start_x = center_x_tile - (tile_cols // 2)
    start_y = center_y_tile - (tile_rows // 2)
    
    tile_tasks = []
    for row in range(tile_rows):
        for col in range(tile_cols):
            tile_tasks.append((start_x + col, start_y + row, zoom, lyr))
    
    stitched_img = Image.new('RGB', (tile_cols * 256, tile_rows * 256))
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_single_tile, tile_tasks)
        for tx, ty, tile_img in results:
            col = tx - start_x
            row = ty - start_y
            stitched_img.paste(tile_img, (col * 256, row * 256))
    
    exact_pixel_x = (center_x_tile - start_x) * 256 + offset_x
    exact_pixel_y = (center_y_tile - start_y) * 256 + offset_y
    crop_left = max(0, int(exact_pixel_x - target_w / 2))
    crop_top = max(0, int(exact_pixel_y - target_h / 2))
    final_img = stitched_img.crop((crop_left, crop_top, crop_left + target_w, crop_top + target_h))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_img.save(output_path, 'JPEG', quality=92)
    print(f"  [+] Saved static map {output_path}", flush=True)

def download_user_photos(place_name, slug, limit=8):
    output_dir = os.path.join('images', slug)
    os.makedirs(output_dir, exist_ok=True)
    existing = sorted([f for f in os.listdir(output_dir) if f.startswith('user_photo_') and f.endswith('.jpg')])
    if len(existing) >= limit:
        print(f"  [=] {len(existing)} user photos already exist for {place_name}", flush=True)
        return existing[:limit]
    
    query = f"{place_name} Mallorca"
    if "Son Gotleu" in place_name:
        query = "Santanyi Mallorca beach"
    elif "en Brut" in place_name:
        query = "Cala en Brut Menorca"
    elif "Katmandu" in place_name:
        query = "Magaluf Mallorca"
    
    hdrs = {'User-Agent': 'MaiorcaTravelGuide/1.0 (personal use)'}
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=20&gsrnamespace=6&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(url, headers=hdrs)
    downloaded = list(existing)
    
    try:
        time.sleep(0.3)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        count = len(existing)
        for p_id, p_info in pages.items():
            if len(downloaded) >= limit:
                break
            img_info = p_info.get('imageinfo', [])
            if not img_info:
                continue
            img_url = img_info[0].get('url')
            width = img_info[0].get('width', 0)
            if not img_url or width < 500:
                continue
            if not any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                continue
            count += 1
            out_file = os.path.join(output_dir, f"user_photo_{count}.jpg")
            if os.path.exists(out_file):
                if f"user_photo_{count}.jpg" not in downloaded:
                    downloaded.append(f"user_photo_{count}.jpg")
                continue
            try:
                time.sleep(0.3)
                img_req = urllib.request.Request(img_url, headers=hdrs)
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    img_data = img_resp.read()
                with open(out_file, 'wb') as out_f:
                    out_f.write(img_data)
                downloaded.append(f"user_photo_{count}.jpg")
                print(f"  [+] Photo {count}: {out_file}", flush=True)
            except Exception as ie:
                print(f"  [!] Timeout/error on photo {count}: {ie}", flush=True)
    except Exception as e:
        print(f"  [!] API error for {place_name}: {e}", flush=True)
    
    return downloaded[:limit]

def generate_maps_section_html(name, lat, lng, page_filename, user_photos):
    slug = page_filename.replace('.html', '')
    maps_icon = '<svg class="maps-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
    dir_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="3 11 22 2 13 21 11 13 3 11"></polygon></svg>'
    earth_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>'
    sat_badge = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M12 2a10 10 0 0 0-10 10"></path><path d="M12 6a6 6 0 0 0-6 6"></path></svg>'
    map_badge = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="1 6 1 22 8 18 15 22 23 18 23 2 15 6 8 2 1 6"></polygon><line x1="8" y1="2" x2="8" y2="18"></line><line x1="15" y1="6" x2="15" y2="22"></line></svg>'
    cam_icon = '<svg class="maps-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>'
    ext_icon = '<svg class="external-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'

    photos_html = ""
    if user_photos:
        cards = ""
        for fname in user_photos:
            cards += f'                        <div class="maps-photo-card"><div class="maps-photo-media"><img src="images/{slug}/{fname}" alt="Foto di {name}" class="lightbox-trigger" loading="lazy"></div></div>\n'
        photos_html = f'''
                <div class="maps-user-photos-wrapper">
                    <div class="maps-header-wrapper">
                        <h2>{cam_icon} Foto & Scatti Reali del Luogo (Maps & Recensioni)</h2>
                        <div class="maps-action-buttons">
                            <a href="https://www.google.com/maps/search/?api=1&query={lat},{lng}" target="_blank" rel="noopener noreferrer" class="maps-btn-action" title="Vedi tutte le foto su Google Maps">
                                {ext_icon} <span>Tutte le Foto su Maps</span>
                            </a>
                        </div>
                    </div>
                    <div class="maps-photos-grid">
{cards}                    </div>
                </div>'''

    return f'''            <div class="maps-section">{photos_html}
                <div class="maps-satellite-wrapper">
                    <div class="maps-header-wrapper">
                        <h2>{maps_icon} Mappa & Vista Satellitare Google Maps</h2>
                        <div class="maps-action-buttons">
                            <a href="https://www.google.com/maps/dir/?api=1&destination={lat},{lng}" target="_blank" rel="noopener noreferrer" class="maps-btn-action">{dir_icon} <span>Indicazioni Maps</span></a>
                            <a href="https://earth.google.com/web/search/{lat},{lng}" target="_blank" rel="noopener noreferrer" class="maps-btn-action">{earth_icon} <span>Google Earth 3D</span></a>
                        </div>
                    </div>
                    <div class="maps-grid">
                        <div class="maps-card"><div class="maps-badge">{sat_badge} <span>Vista Satellitare HD</span></div><div class="maps-media-wrap"><img src="images/{slug}/maps_satellite.jpg" alt="Vista Satellitare di {name}" class="lightbox-trigger" loading="lazy"></div></div>
                        <div class="maps-card"><div class="maps-badge">{map_badge} <span>Mappa Stradale & Accessi</span></div><div class="maps-media-wrap"><img src="images/{slug}/maps_roadmap.jpg" alt="Mappa Stradale di {name}" class="lightbox-trigger" loading="lazy"></div></div>
                        <div class="maps-iframe-card"><iframe src="https://maps.google.com/maps?q={lat},{lng}&t=k&z=16&ie=UTF8&iwloc=&output=embed" title="Mappa interattiva per {name}" loading="lazy" allowfullscreen></iframe></div>
                    </div>
                </div>
            </div>
'''

def process_place(r):
    name = r['Nome']
    lat = float(r['Latitudine'])
    lng = float(r['Longitudine'])
    page_file = os.path.basename(r['URL_Pagina'])
    slug = page_file.replace('.html', '')
    if page_file in ('boat_party.html', 'index.html'):
        return
    
    print(f"\n>>> {name} ({page_file})", flush=True)
    
    img_dir = os.path.join('images', slug)
    sat_path = os.path.join(img_dir, 'maps_satellite.jpg')
    road_path = os.path.join(img_dir, 'maps_roadmap.jpg')
    
    if not os.path.exists(sat_path):
        create_static_map(lat, lng, zoom=16, map_type='hybrid', output_path=sat_path)
    if not os.path.exists(road_path):
        create_static_map(lat, lng, zoom=15, map_type='roadmap', output_path=road_path)
    
    user_photos = download_user_photos(name, slug, limit=8)
    print(f"  Photos: {len(user_photos)}", flush=True)
    
    if os.path.exists(page_file):
        with open(page_file, 'r', encoding='utf-8') as hf:
            content = hf.read()
        maps_html = generate_maps_section_html(name, lat, lng, page_file, user_photos)
        content = re.sub(r'\s*<div class="maps-section">.*?</div>\s*(?=<div class="(?:notes-section|place-details)">|</main>)', '', content, flags=re.DOTALL)
        if '<div class="notes-section">' in content:
            content = content.replace('<div class="notes-section">', f'{maps_html}            <div class="notes-section">')
        elif '</main>' in content:
            content = content.replace('</main>', f'{maps_html}    </main>')
        with open(page_file, 'w', encoding='utf-8') as hf:
            hf.write(content)
        print(f"  [OK] HTML updated", flush=True)

if __name__ == '__main__':
    with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
        places = [r for r in csv.DictReader(f) if os.path.basename(r['URL_Pagina']) not in ('boat_party.html', 'index.html')]
    print(f"Processing {len(places)} places...", flush=True)
    for r in places:
        process_place(r)
    print("\n[ALL DONE]", flush=True)
