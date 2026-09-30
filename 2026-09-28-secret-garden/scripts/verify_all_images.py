import json
import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js_path = os.path.join(base_dir, 'data', 'masterpieces.js')
img_dir = os.path.join(base_dir, 'assets', 'images')

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'window\.MASTERPIECES\s*=\s*(\[[\s\S]*?\]);\s*$', text)
paintings = json.loads(match.group(1))

print(f"Total paintings in masterpieces.js: {len(paintings)}")

missing = []
sizes = []

for i, p in enumerate(paintings):
    fn = p.get('file')
    if not fn:
        src = p.get('src', '')
        fn = src.split('?')[0].split('/')[-1]
    
    fp = os.path.join(img_dir, fn)
    if not os.path.exists(fp):
        missing.append((i+1, p['id'], p['title'], fn))
    else:
        sizes.append(os.path.getsize(fp))

print(f"Missing images count: {len(missing)}")
if missing:
    for m in missing:
        print(f"  ❌ Missing: #{m[0]} [{m[1]}] {m[2]} -> {m[3]}")
else:
    avg_size_mb = sum(sizes) / len(sizes) / (1024 * 1024)
    total_size_mb = sum(sizes) / (1024 * 1024)
    print(f"✅ All {len(paintings)} images exist locally on disk!")
    print(f"Total assets size: {total_size_mb:.2f} MB, Average: {avg_size_mb:.2f} MB per artwork")
