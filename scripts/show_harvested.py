import json

with open('scripts/harvested_50_religious.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total harvested: {len(items)}")
for i, it in enumerate(items):
    print(f"{i+1}. {it['id']}: 《{it['title']}》 - {it['artist']}")
