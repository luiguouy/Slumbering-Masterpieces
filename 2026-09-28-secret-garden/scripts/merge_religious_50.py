import os
import json
import re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js_path = os.path.join(base_dir, 'data', 'masterpieces.js')
json_path = os.path.join(base_dir, 'scripts', 'harvested_50_religious.json')

with open(json_path, 'r', encoding='utf-8') as f:
    new_50 = json.load(f)

assert len(new_50) == 50, f"Expected 50 items, got {len(new_50)}"

with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

# 提取已有作品
match = re.search(r'window\.MASTERPIECES\s*=\s*(\[[\s\S]*?\]);\s*$', js_content)
if not match:
    raise ValueError("Could not find window.MASTERPIECES array in data/masterpieces.js")

# 也可以直接解析 JSON 结构
# 观察 masterpieces.js 结构：
# window.ART_CATEGORIES = [ ... ];
# window.MASTERPIECES = [ ... ];
prefix = js_content[:match.start(1)]
masterpieces_raw = match.group(1)

# 将原有列表转为 Python 对象
existing_masterpieces = json.loads(masterpieces_raw)
print(f"Existing masterpieces in JS: {len(existing_masterpieces)}")

existing_ids = {x['id'] for x in existing_masterpieces}
clean_new_50 = []
for it in new_50:
    if it['id'] in existing_ids:
        print(f"Duplicate detected: {it['id']}")
    else:
        clean_new_50.append(it)

print(f"Adding {len(clean_new_50)} new religious masterpieces...")
merged_masterpieces = existing_masterpieces + clean_new_50
print(f"Total merged masterpieces: {len(merged_masterpieces)}")

# 统计分类
cat_counts = {
    'all': len(merged_masterpieces),
    'renaissance': 0,
    'baroque': 0,
    'romanticism': 0,
    'realism': 0,
    'monet': 0,
    'impressionism': 0,
    'post_impressionism': 0,
    'expressionism': 0
}

for m in merged_masterpieces:
    c = m.get('category')
    if c in cat_counts:
        cat_counts[c] += 1

print("Updated category counts:", cat_counts)

# 更新 categories 块
def update_categories(match_cat):
    cats = json.loads(match_cat.group(1))
    for c in cats:
        cid = c['id']
        if cid in cat_counts:
            c['count'] = cat_counts[cid]
    return f"window.ART_CATEGORIES = {json.dumps(cats, ensure_ascii=False, indent=4)};"

js_content = re.sub(r'window\.ART_CATEGORIES\s*=\s*(\[[\s\S]*?\]);', update_categories, js_content)

# 写入新的 MASTERPIECES
new_js_content = re.sub(
    r'window\.MASTERPIECES\s*=\s*\[[\s\S]*?\];\s*$',
    f"window.MASTERPIECES = {json.dumps(merged_masterpieces, ensure_ascii=False, indent=4)};",
    js_content
)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(new_js_content)

print(f"Successfully wrote {len(merged_masterpieces)} masterpieces to {js_path}!")
