import json
import re
import os

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', f.read(), re.DOTALL).group(1))

for i, d in enumerate(data):
    if 'Vermeer' in d.get('artist', '') or '维米尔' in d.get('artist', ''):
        src_path = d.get('src', '').split('?')[0]
        size = os.path.getsize(src_path) if os.path.exists(src_path) else -1
        print(f"{i+1:03d} | {d['id']:<30} | {d['title']:<20} | {src_path:<40} | size: {size}")
