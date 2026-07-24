import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import socket

sys.stdout.reconfigure(encoding='utf-8')
socket.setdefaulttimeout(20)

def download_photos_slow(place_name, slug, limit=8):
    output_dir = os.path.join('images', slug)
    os.makedirs(output_dir, exist_ok=True)
    existing = sorted([f for f in os.listdir(output_dir) if f.startswith('user_photo_') and f.endswith('.jpg')])
    if len(existing) >= limit:
        return existing[:limit]
    
    query = f"{place_name} Mallorca"
    if "Son Gotleu" in place_name:
        query = "Santanyi Mallorca beach"
    elif "en Brut" in place_name:
        query = "Cala en Brut Menorca"
    elif "Katmandu" in place_name:
        query = "Magaluf Mallorca"
    
    hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit=20&gsrnamespace=6&prop=imageinfo&iiprop=url|size&format=json"
    
    req = urllib.request.Request(url, headers=hdrs)
    downloaded = list(existing)
    
    try:
        # Long pause before API call
        time.sleep(2)
        with urllib.request.urlopen(req, timeout=15) as resp:
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
            
            # Use thumbnail URL instead of full-size to avoid rate limiting
            # Wikimedia thumbnail format: /thumb/path/filename/800px-filename
            thumb_url = img_url
            if '/commons/' in img_url:
                fname = img_url.split('/')[-1]
                thumb_url = img_url.replace('/commons/', '/commons/thumb/') + f'/800px-{fname}'
            
            count += 1
            out_file = os.path.join(output_dir, f"user_photo_{count}.jpg")
            if os.path.exists(out_file):
                if f"user_photo_{count}.jpg" not in downloaded:
                    downloaded.append(f"user_photo_{count}.jpg")
                continue
            try:
                # 2 second pause between each download
                time.sleep(2)
                img_req = urllib.request.Request(thumb_url, headers=hdrs)
                with urllib.request.urlopen(img_req, timeout=20) as img_resp:
                    img_data = img_resp.read()
                with open(out_file, 'wb') as out_f:
                    out_f.write(img_data)
                downloaded.append(f"user_photo_{count}.jpg")
                print(f"    [+] Photo {count}: OK", flush=True)
            except Exception as ie:
                # Try original URL as fallback
                try:
                    time.sleep(3)
                    img_req2 = urllib.request.Request(img_url, headers=hdrs)
                    with urllib.request.urlopen(img_req2, timeout=20) as img_resp2:
                        img_data2 = img_resp2.read()
                    with open(out_file, 'wb') as out_f2:
                        out_f2.write(img_data2)
                    downloaded.append(f"user_photo_{count}.jpg")
                    print(f"    [+] Photo {count}: OK (fallback)", flush=True)
                except Exception as ie2:
                    print(f"    [!] Photo {count}: FAILED - {ie2}", flush=True)
    except Exception as e:
        print(f"    [!] API error: {e}", flush=True)
    
    return downloaded[:limit]

def regenerate_html(name, lat, lng, page_file, user_photos):
    """Re-inject maps section HTML with updated photo list"""
    slug = page_file.replace('.html', '')
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

if __name__ == '__main__':
    with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    # Find places that need more photos
    needs_work = []
    for r in rows:
        page = os.path.basename(r['URL_Pagina'])
        if page in ('boat_party.html', 'index.html'):
            continue
        slug = page.replace('.html', '')
        img_dir = os.path.join('images', slug)
        photo_count = len([f for f in os.listdir(img_dir) if f.startswith('user_photo_') and f.endswith('.jpg')]) if os.path.isdir(img_dir) else 0
        if photo_count < 8:
            needs_work.append((r, photo_count))
    
    print(f"=== SECOND PASS: {len(needs_work)} places need more photos ===", flush=True)
    for r, current in needs_work:
        name = r['Nome']
        page = os.path.basename(r['URL_Pagina'])
        slug = page.replace('.html', '')
        lat = float(r['Latitudine'])
        lng = float(r['Longitudine'])
        print(f"\n  [{name}] currently {current} photos, need 8...", flush=True)
        
        photos = download_photos_slow(name, slug, limit=8)
        print(f"  [{name}] now has {len(photos)} photos", flush=True)
        
        # Re-generate HTML with updated photos
        if os.path.exists(page):
            with open(page, 'r', encoding='utf-8') as hf:
                content = hf.read()
            maps_html = regenerate_html(name, lat, lng, page, photos)
            content = re.sub(r'\s*<div class="maps-section">.*?</div>\s*(?=<div class="(?:notes-section|place-details)">|</main>)', '', content, flags=re.DOTALL)
            if '<div class="notes-section">' in content:
                content = content.replace('<div class="notes-section">', f'{maps_html}            <div class="notes-section">')
            elif '</main>' in content:
                content = content.replace('</main>', f'{maps_html}    </main>')
            with open(page, 'w', encoding='utf-8') as hf:
                hf.write(content)
            print(f"  [{name}] HTML updated", flush=True)
    
    print("\n[SECOND PASS DONE]", flush=True)
