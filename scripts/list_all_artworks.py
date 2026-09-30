import json
import re

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    content = f.read()

data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL).group(1))

print(f"Total: {len(data)}")
for i, d in enumerate(data):
    print(f"{i+1:03d} | {d['id']:<40} | 《{d['title']}》 | {d.get('genre')} | {d.get('category')}")
