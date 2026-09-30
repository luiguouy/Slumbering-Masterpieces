import os
import sys
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from harvest_86_impressionism_and_monet import TARGET_86_ARTWORKS

js_path = 'data/masterpieces.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('window.MASTERPIECES =')
start_bracket = content.find('[', start)
end_bracket = content.rfind('];')
json_text = content[start_bracket:end_bracket+1]
existing_artworks = json.loads(json_text)

print(f"Original artworks count: {len(existing_artworks)}")

existing_map = {a['id']: a for a in existing_artworks}

new_entries = []
updated_cnt = 0
added_cnt = 0

# 构建新艺术品格式
for item in TARGET_86_ARTWORKS:
    art_id = item['id']
    file_name = f"{art_id}.jpg"
    new_obj = {
        "id": art_id,
        "title": item['title'],
        "enTitle": item['enTitle'],
        "artist": item['artist'],
        "category": item['category'],
        "file": file_name,
        "query": item['search'],
        "quote": item['quote'],
        "quoteAuthor": item['quoteAuthor'],
        "src": f"assets/images/{file_name}?v=4.0.0",
        "genre": item.get('genre', '🌿 自然风景')
    }

    if art_id in existing_map:
        existing_map[art_id].update(new_obj)
        updated_cnt += 1
    else:
        new_entries.append(new_obj)
        added_cnt += 1

# 合并并保持优雅排序：按展厅板块分组
# 展厅顺序标准：renaissance, baroque, romanticism, realism, monet, impressionism, post_impressionism, expressionism
category_order = [
    'renaissance',
    'baroque',
    'romanticism',
    'realism',
    'monet',
    'impressionism',
    'post_impressionism',
    'expressionism'
]

all_artworks = list(existing_map.values()) + new_entries

def sort_key(art):
    cat = art.get('category', 'other')
    cat_idx = category_order.index(cat) if cat in category_order else 99
    # Special: keep sanctuary first in monet
    if art['id'] == 'garden_monet_sanctuary':
        return (cat_idx, 0, art['id'])
    return (cat_idx, 1, art['id'])

all_artworks.sort(key=sort_key)

print(f"Updated artworks count: {updated_cnt}")
print(f"New added artworks count: {added_cnt}")
print(f"Total artworks after merge: {len(all_artworks)}")

# 写回 data/masterpieces.js
new_json_str = json.dumps(all_artworks, ensure_ascii=False, indent=2)
new_content = content[:start_bracket] + new_json_str + ";\n"

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ data/masterpieces.js 已成功更新并保存！")
