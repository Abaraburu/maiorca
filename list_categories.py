import csv
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('mappe_maiorca.csv', mode='r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Total rows in CSV: {len(rows)}")
for r in rows:
    page = os.path.basename(r['URL_Pagina'])
    print(f" - {r['Nome']} ({page}) [{r['Categoria']}]")

all_html = sorted(glob.glob("*.html"))
print(f"\nAll HTML files in workspace ({len(all_html)}):")
csv_pages = set(os.path.basename(r['URL_Pagina']) for r in rows)
for h in all_html:
    if h in ('index.html', 'boat_party.html'):
        print(f" - EXCLUDED: {h}")
    elif h in csv_pages:
        print(f" - INCLUDED: {h}")
