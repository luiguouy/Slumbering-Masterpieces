import os
import json
from collections import defaultdict

with open('scripts/harvest_86_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

size_map = defaultdict(list)
for art in data['artworks']:
    filename = f"{art['id']}.jpg"
    p = os.path.join('assets', 'images', filename)
    if os.path.exists(p):
        sz = os.path.getsize(p)
        size_map[sz].append(art['id'])

print("Identical size clusters (possible duplicate downloads):")
for sz, ids in size_map.items():
    if len(ids) > 1:
        print(f" Size {sz} bytes ({sz//1024} KB): {ids}")
