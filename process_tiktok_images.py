import os
import re
import io
import sys
import json
import asyncio
import urllib.request
from PIL import Image
import winocr

# Ensure stdout handles unicode/emojis on Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Dictionary mapping place html filenames (without .html) to OCR matching keywords
PLACE_KEYWORDS = {
    "calo_des_moro": ["calo des moro", "caló des moro", "des moro"],
    "cala_pi": ["cala pi"],
    "es_trenc": ["es trenc"],
    "cala_llombards": ["cala llombards", "llombards"],
    "cala_santanyi": ["cala santanyi", "cala santanyí", "santanyi"],
    "cala_romantica": ["cala romantica", "cala romàntica", "romantica"],
    "cala_varques": ["cala varques", "varques"],
    "cala_esmeralda": ["cala esmeralda", "esmeralda"],
    "cala_dor": ["cala d'or", "cala dor"],
    "cala_major": ["cala major"],
    "cala_llamp": ["cala llamp"],
    "cala_mondrago": ["cala mondrago", "cala mondragó", "mondrago"],
    "samarador": ["s'amarador", "samarador", "amarador"],
    "camp_de_mar": ["camp de mar"],
    "playa_de_muro": ["playa de muro"],
    "sa_calobra": ["sa calobra", "torrent de pareis"],
    "alcudia": ["alcudia", "alcúdia"],
    "valldemossa": ["valldemossa"],
    "deia": ["deia", "deià"],
    "soller": ["soller", "sóller"],
    "fornalutx": ["fornalutx"],
    "pollenca": ["pollenca", "pollença"],
    "formentor": ["formentor", "cap de formentor"],
    "grotte_del_drago": ["grotte del drago", "cuevas del drach", "drach"],
    "cuevas_del_hams": ["cuevas del hams", "hams"],
    "katmandu_park": ["katmandu"],
    "boat_party": ["boat party"],
    "port_de_cala_figuera": ["cala figuera", "port de cala figuera"],
    "mercado_de_santanyi": ["mercado de santanyi", "mercato di santanyi"],
    "palma_de_mallorca": ["palma de mallorca", "palma"],
    "portocolom": ["portocolom"],
    "cala_son_gotleu": ["cala son gotleu", "son gotleu"],
    "cala_en_brut": ["cala en brut"]
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_photo_ids(html_content):
    """Extract TikTok photo post IDs from html content."""
    links = re.findall(r'https://www.tiktok.com/@[^/]+/photo/(\d+)', html_content)
    return list(dict.fromkeys(links))

def get_slide_urls(photo_id):
    """Fetch high-res image slide URLs from TikTok embed page."""
    embed_url = f"https://www.tiktok.com/embed/v2/{photo_id}"
    try:
        req = urllib.request.Request(embed_url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        urls = []
        match = re.search(r'<script[^>]*?id="__FRONTITY_CONNECT_STATE__"[^>]*?>(.*?)</script>', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            def search_url_list(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "urlList" and isinstance(v, list) and len(v) > 0:
                            for item in v:
                                if "photomode-image" in item or "jpeg" in item:
                                    urls.append(item)
                                    break
                        else:
                            search_url_list(v)
                elif isinstance(obj, list):
                    for item in obj:
                        search_url_list(item)

            search_url_list(data)

        unique_urls = list(dict.fromkeys(urls))
        return unique_urls
    except Exception as e:
        print(f"  [ERROR] Impossibile recuperare embed per ID {photo_id}: {e}")
        return []

async def run_ocr_on_image(img):
    """Perform Windows Native OCR on a PIL image."""
    try:
        res = await winocr.recognize_pil(img, lang="it-IT")
        return res.text.lower()
    except Exception:
        try:
            res = await winocr.recognize_pil(img, lang="es-ES")
            return res.text.lower()
        except Exception:
            return ""

def match_beach_from_ocr(ocr_text, default_place):
    """Match OCR text against known beach keywords."""
    if not ocr_text:
        return default_place

    for place, keywords in PLACE_KEYWORDS.items():
        for kw in keywords:
            if kw in ocr_text:
                return place
    return default_place

async def process_all():
    print("=== Avvio Elaborazione Foto TikTok e OCR Locale ===")
    
    images_per_place = {}
    processed_photos = set()

    directory = "."
    html_files = [f for f in os.listdir(directory) if f.endswith(".html") and f != "index.html"]

    for filename in sorted(html_files):
        place_name = filename.replace(".html", "")
        filepath = os.path.join(directory, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        photo_ids = extract_photo_ids(content)
        if not photo_ids:
            continue

        print(f"\n[INFO] Elaborazione {filename} ({len(photo_ids)} post foto TikTok)...")

        for pid in photo_ids:
            if pid in processed_photos:
                print(f"  --> Post TikTok ID {pid} gia elaborato, salto fetch duplicate")
                continue
            processed_photos.add(pid)

            print(f"  --> Recupero slide per TikTok Photo ID: {pid}")
            slide_urls = get_slide_urls(pid)
            print(f"      Estratte {len(slide_urls)} slide ad alta risoluzione")

            for idx, img_url in enumerate(slide_urls, start=1):
                try:
                    req = urllib.request.Request(img_url, headers=HEADERS)
                    img_data = urllib.request.urlopen(req, timeout=10).read()
                    img = Image.open(io.BytesIO(img_data))
                    
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    ocr_text = await run_ocr_on_image(img)
                    if ocr_text.strip():
                        ocr_summary = ocr_text.strip().replace("\n", " ")[:60]
                        print(f"      Slide {idx} OCR: \"{ocr_summary}\"")
                    else:
                        print(f"      Slide {idx} OCR: [Nessun testo rilevato]")

                    target_place = match_beach_from_ocr(ocr_text, place_name)
                    if target_place != place_name:
                        print(f"      [SMISTAMENTO OCR] Immagine indirizzata a '{target_place}' (invece di '{place_name}')")

                    img_dir = os.path.join("images", target_place)
                    os.makedirs(img_dir, exist_ok=True)

                    img_filename = f"tiktok_{pid}_{idx}.jpg"
                    img_filepath = os.path.join(img_dir, img_filename)
                    img.save(img_filepath, "JPEG", quality=85)

                    rel_path = f"images/{target_place}/{img_filename}"
                    caption = f"Foto estratta da TikTok (ID {pid})"
                    if ocr_text.strip():
                        clean_ocr = ocr_text.strip().replace('\n', ' ')[:40]
                        caption += f" - Testo: {clean_ocr}..."

                    if target_place not in images_per_place:
                        images_per_place[target_place] = []

                    if not any(item["path"] == rel_path for item in images_per_place[target_place]):
                        images_per_place[target_place].append({
                            "path": rel_path,
                            "caption": caption
                        })

                except Exception as e:
                    print(f"      [ERROR] Impossibile elaborare slide {idx}: {e}")

    # Update HTML files with photo galleries
    print("\n=== Aggiornamento Pagine HTML con Gallerie Immagini ===")
    for filename in sorted(html_files):
        place_name = filename.replace(".html", "")
        filepath = os.path.join(directory, filename)

        images = images_per_place.get(place_name, [])

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove previous photo-gallery if re-running
        content = re.sub(r'\s*<div class="photo-gallery">.*?</div>\s*</div>(?=\s*<div class="notes-section">|\s*</div>\s*</main>)', '', content, flags=re.DOTALL)

        if images:
            cards_html = ""
            for img_info in images:
                cards_html += f'''
                <div class="gallery-card">
                    <img src="{img_info['path']}" alt="Foto {place_name}" class="gallery-img" loading="lazy">
                    <div class="gallery-caption">{img_info['caption']}</div>
                </div>'''

            gallery_block = f'''
            <div class="photo-gallery">
                <h2>Galleria Fotografica (Estratta da TikTok)</h2>
                <div class="gallery-grid">
{cards_html}
                </div>
            </div>'''

            if '<div class="notes-section">' in content:
                content = content.replace('<div class="notes-section">', f'{gallery_block}\n            <div class="notes-section">')
            else:
                content = content.replace('</div>\n    </main>', f'{gallery_block}\n        </div>\n    </main>')

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"[OK] Aggiornata galleria fotografica per {filename} ({len(images)} immagini)")

if __name__ == "__main__":
    asyncio.run(process_all())
