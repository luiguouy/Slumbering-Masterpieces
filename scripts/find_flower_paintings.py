import json
import re

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', f.read(), re.DOTALL).group(1))

flower_keywords = ['花', '静物', '果', '瓶', '草', '菊', '葵', '兰']
for d in data:
    for kw in flower_keywords:
        if kw in d['title']:
            print(f"[{d['id']}] 《{d['title']}》 - {d.get('genre')}")
            break
