import json
import re

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

print(f"Total masterpieces: {len(data)}")
by_genre = {}
for item in data:
    g = item.get('genre', '未知')
    by_genre.setdefault(g, []).append(item)

for g, items in by_genre.items():
    print(f"\n=== {g} ({len(items)}) ===")
    for it in items:
        print(f"[{it.get('id')}] 《{it.get('title')}》 ({it.get('artist')})")
