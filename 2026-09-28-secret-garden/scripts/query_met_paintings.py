import urllib.request
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MuseumMasterpieceBot/1.0'}

queries = [
    ("El Greco Annunciation", "el_greco"),
    ("El Greco Adoration", "el_greco"),
    ("Rubens Holy Family", "rubens"),
    ("Murillo Virgin Child", "murillo"),
    ("Veronese Holy Family", "veronese"),
    ("Cranach Virgin Child", "cranach"),
    ("Giovanni Bellini Madonna", "bellini"),
    ("Poussin Holy Family", "poussin"),
    ("Zurbaran Virgin", "zurbaran"),
    ("Tiepolo Virgin", "tiepolo"),
    ("Caravaggio", "caravaggio"),
    ("Van Dyck Virgin", "vandyck"),
    ("Tintoretto Christ", "tintoretto")
]

results = []

for q, tag in queries:
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={urllib.parse.quote(q)}&hasImages=true&medium=Paintings"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            obj_ids = data.get('objectIDs', [])
            print(f"Query: {q} -> Found {len(obj_ids)} objects")
            for oid in obj_ids[:3]:
                ourl = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
                try:
                    with urllib.request.urlopen(urllib.request.Request(ourl, headers=headers), timeout=10) as orsp:
                        obj = json.loads(orsp.read().decode())
                        img = obj.get('primaryImage')
                        if img and obj.get('isPublicDomain'):
                            results.append({
                                'met_id': oid,
                                'title': obj.get('title'),
                                'artist': obj.get('artistDisplayName'),
                                'date': obj.get('objectDate'),
                                'medium': obj.get('medium'),
                                'img': img,
                                'credit': obj.get('creditLine')
                            })
                            print(f"  🎯 {obj.get('title')} by {obj.get('artistDisplayName')} ({obj.get('objectDate')})")
                except Exception as e:
                    pass
                time.sleep(0.3)
    except Exception as e:
        print(f"Error {q}: {e}")
    time.sleep(0.5)

print(f"\nTotal high-res Met religious paintings found: {len(results)}")
with open('scripts/met_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
