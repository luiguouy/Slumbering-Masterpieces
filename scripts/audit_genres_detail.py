import json
import re

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL)
data = json.loads(match.group(1))

by_genre = {}
for d in data:
    g = d.get('genre', '未知')
    by_genre.setdefault(g, []).append(d)

with open('scripts/all_artworks_audit.txt', 'w', encoding='utf-8') as out:
    for g, items in by_genre.items():
        out.write(f"\n==================== {g} ({len(items)}) ====================\n")
        for it in items:
            out.write(f"[{it.get('id')}] 《{it.get('title')}》 - {it.get('artist')}\n")
            out.write(f"    标签类别: {it.get('category')} | 描述: {it.get('description', '')[:80]}...\n")

print(f"Total: {len(data)}, genres: {list(by_genre.keys())}")
