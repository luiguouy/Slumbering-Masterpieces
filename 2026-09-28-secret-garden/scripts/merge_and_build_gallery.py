# -*- coding: utf-8 -*-
"""
合并新老画作数据，更新 masterpieces.js 并生成全量台账
"""
import json
import os

data_js_path = r'2026-09-28-secret-garden\data\masterpieces.js'
with open(data_js_path, 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('window.MASTERPIECES = ') + len('window.MASTERPIECES = ')
e = c.rfind(';')
existing = json.loads(c[s:e])

# 载入 54 幅新画作定义
fetch_script = r'2026-09-28-secret-garden\scripts\fetch_new_50_masterpieces.py'
with open(fetch_script, 'r', encoding='utf-8') as f:
    code = f.read()
s2 = code.find('NEW_MASTERPIECES = [')
e2 = code.find('\nimages_dir =')
scope = {}
exec(code[s2:e2], {}, scope)
new_items = scope['NEW_MASTERPIECES']

for item in new_items:
    item['src'] = f"assets/images/{item['file']}?v=3.7.0"

# 更新旧画作的 src 版本戳至 3.7.0
for item in existing:
    item['src'] = item['src'].split('?')[0] + '?v=3.7.0'

all_items = existing + new_items

CATEGORIES = [
    ('renaissance', '🏛️ 文艺复兴与北方画派 (Renaissance & Northern Masters)'),
    ('baroque', '🎭 巴洛克与荷兰黄金时代 (Baroque & Dutch Golden Age)'),
    ('romanticism', '⚡ 新古典、洛可可与浪漫主义 (Neoclassicism & Romanticism)'),
    ('realism', '🌾 写实主义与巡回展览画派 (Realism & Wanderers)'),
    ('monet', '🌟 克劳德·莫奈专题特辑 (Claude Monet Collection)'),
    ('impressionism', '🎨 印象派巅峰盛宴 (Impressionism Masters)'),
    ('post_impressionism', '🌻 后印象派三杰与现代先驱 (Post-Impressionism)'),
    ('expressionism', '🌌 象征主义与表现主义 (Symbolism & Expressionism)')
]

sorted_paintings = []
cat_list = []
for cat_id, cat_name in CATEGORIES:
    cat_items = [p for p in all_items if p['category'] == cat_id]
    sorted_paintings.extend(cat_items)
    cat_list.append({
        'id': cat_id,
        'name': cat_name,
        'count': len(cat_items)
    })

print(f"Total paintings merged: {len(sorted_paintings)}")
for c in cat_list:
    print(f"  {c['name']}: {c['count']} 幅")

# 输出 masterpieces.js
js_content = "/**\n * Slumbering Masterpieces · World Fine Art Collection\n"
js_content += f" * 全球世界级传世名画博览馆数据库（共 {len(sorted_paintings)} 幅殿堂级油画杰作）\n */\n\n"
js_content += "window.ART_CATEGORIES = " + json.dumps(cat_list, ensure_ascii=False, indent=4) + ";\n\n"
js_content += "window.MASTERPIECES = " + json.dumps(sorted_paintings, ensure_ascii=False, indent=4) + ";\n"

with open(data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully updated {data_js_path}!")
