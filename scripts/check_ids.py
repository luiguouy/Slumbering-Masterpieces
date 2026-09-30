import re
import json

with open("data/masterpieces.js", "r", encoding="utf-8") as f:
    js_content = f.read()

existing_js_ids = set(re.findall(r'"id":\s*"([^"]+)"', js_content))
# Remove category IDs that also have "id"
category_ids = {'all', 'renaissance', 'baroque', 'romanticism', 'realism', 'monet', 'impressionism', 'post_impressionism', 'expressionism'}
existing_js_ids = existing_js_ids - category_ids
print(f"masterpieces.js artwork count: {len(existing_js_ids)}")

with open("scripts/harvested_50_religious.json", "r", encoding="utf-8") as f:
    harvested = json.load(f)

harvested_ids = {x['id'] for x in harvested}
print(f"harvested count: {len(harvested_ids)}")

overlap = existing_js_ids.intersection(harvested_ids)
print(f"Overlap: {len(overlap)}")
if overlap:
    print("Overlapped IDs:", overlap)

print("Harvested so far:")
for i, x in enumerate(harvested):
    print(f"  {i+1}. [{x['id']}] {x['title']} - {x['artist']}")
