import json

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    c = f.read()

start = c.find('window.MASTERPIECES =')
arts = json.loads(c[start+len('window.MASTERPIECES ='):c.rfind('];')+1])

print(f"Total: {len(arts)}")
from collections import Counter
print("Categories:", Counter([a.get('category') for a in arts]))

print("\n--- Existing Impressionism / Monet Artworks ---")
for a in arts:
    cat = a.get('category', '')
    if cat in ['impressionism', 'monet'] or '莫奈' in a.get('artist', '') or '雷诺阿' in a.get('artist', '') or '德加' in a.get('artist', '') or '毕沙罗' in a.get('artist', ''):
        print(f"[{a.get('category')}] {a.get('id')}: 《{a.get('title')}》 ({a.get('enTitle')}) - {a.get('artist')}")
