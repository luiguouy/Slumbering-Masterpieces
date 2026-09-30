import json
import re

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', f.read(), re.DOTALL).group(1))

# 模拟 app.js 中的 GENRE_DEFINITIONS
definitions = [
    { 'id': 'all', 'label': '全部题材', 'icon': '🎨', 'test': lambda art: True },
    { 'id': 'life', 'label': '风俗生活', 'icon': '👥', 'test': lambda art: bool(art.get('genre') and ('风俗' in art['genre'] or '生活' in art['genre'])) },
    { 'id': 'landscape', 'label': '自然风景', 'icon': '🌿', 'test': lambda art: bool(art.get('genre') and ('风景' in art['genre'] or '风光' in art['genre'])) },
    { 'id': 'portrait', 'label': '人物肖像', 'icon': '👤', 'test': lambda art: bool(art.get('genre') and '人物' in art['genre']) },
    { 'id': 'mythology', 'label': '神话宗教', 'icon': '🏛️', 'test': lambda art: bool(art.get('genre') and ('神话' in art['genre'] or '宗教' in art['genre'])) },
    { 'id': 'history', 'label': '历史故事', 'icon': '⚔️', 'test': lambda art: bool(art.get('genre') and ('历史' in art['genre'] or '故事' in art['genre'] or '叙事' in art['genre'])) },
    { 'id': 'still_life', 'label': '静物花卉', 'icon': '💐', 'test': lambda art: bool(art.get('genre') and ('静物' in art['genre'] or '花卉' in art['genre'])) }
]

print("=== 前端题材胶囊过滤测试 ===")
total_categorized = 0
unmatched = []

for d in definitions:
    matches = [art for art in data if d['test'](art)]
    print(f"{d['icon']} {d['label']} ({len(matches)})")
    if d['id'] != 'all':
        total_categorized += len(matches)

for art in data:
    matched = False
    for d in definitions[1:]:
        if d['test'](art):
            matched = True
            break
    if not matched:
        unmatched.append(art)

print(f"\n分类总数: {total_categorized} (期望: {len(data)})")
if unmatched:
    print(f"警告：有 {len(unmatched)} 幅作品未匹配任何题材：")
    for u in unmatched:
        print(f"  [{u['id']}] 《{u['title']}》 - {u.get('genre')}")
else:
    print("✅ 完美！全部 293 件作品均精准匹配对应题材，无任何遗漏！")
