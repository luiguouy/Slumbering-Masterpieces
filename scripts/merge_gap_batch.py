# -*- coding: utf-8 -*-
"""
将补采集成功的缺口名画合并进 data/masterpieces.js

- 仅合并 assets/images 下确实存在且体积达标的画作
- 按 8 大展厅分组重排、重算 count
- 全站图片版本戳统一升至 VERSION
"""
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'masterpieces.js')
CANDIDATES = ['scripts/gap_candidates_a.json', 'scripts/gap_candidates_b.json']

VERSION = '4.7.0'
MIN_BYTES = 250 * 1024


def load_candidates():
    items = []
    for rel in CANDIDATES:
        with open(os.path.join(BASE_DIR, rel), 'r', encoding='utf-8') as f:
            items.extend(json.load(f))
    return items


def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    m_items = re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL)
    m_cats = re.search(r'window\.ART_CATEGORIES\s*=\s*(\[.*?\]);', content, re.DOTALL)
    existing = json.loads(m_items.group(1))
    categories = json.loads(m_cats.group(1))
    existing_ids = {p['id'] for p in existing}

    added, skipped = [], []
    for item in load_candidates():
        if item['id'] in existing_ids:
            skipped.append((item['id'], '已收录'))
            continue
        rel_path = os.path.join(BASE_DIR, 'assets', 'images', item['id'] + '.jpg')
        if not os.path.exists(rel_path):
            skipped.append((item['id'], '图片缺失'))
            continue
        if os.path.getsize(rel_path) < MIN_BYTES:
            skipped.append((item['id'], '图片体积过小'))
            continue
        record = {
            'id': item['id'],
            'title': item['title'],
            'enTitle': item['enTitle'],
            'artist': item['artist'],
            'category': item['category'],
            'genre': item['genre'],
            'quote': item['quote'],
            'quoteAuthor': item['quoteAuthor'],
            'search': item['search'],
            'file': item['id'] + '.jpg',
            'src': f"assets/images/{item['id']}.jpg?v={VERSION}",
        }
        added.append(record)
        existing_ids.add(item['id'])

    # 旧作仅刷新版本戳，不删除任何既有数据
    for p in existing:
        p['src'] = p['src'].split('?')[0] + f'?v={VERSION}'

    merged = []
    for cat in categories:
        merged.extend([p for p in existing if p['category'] == cat['id']])
        merged.extend([p for p in added if p['category'] == cat['id']])
    # 兜底：异常分类不丢数据
    known = {c['id'] for c in categories}
    merged.extend([p for p in existing + added if p['category'] not in known])

    counts = {c['id']: sum(1 for p in merged if p['category'] == c['id']) for c in categories}
    for cat in categories:
        cat['count'] = counts[cat['id']]

    header = (
        '/**\n * Slumbering Masterpieces · World Fine Art Collection\n'
        f' * 全球世界级传世名画博览馆数据库（共 {len(merged)} 幅殿堂级油画旷世杰作）\n */\n\n'
    )
    new_content = header
    new_content += 'window.ART_CATEGORIES = ' + json.dumps(categories, ensure_ascii=False, indent=4) + ';\n\n'
    new_content += 'window.MASTERPIECES = ' + json.dumps(merged, ensure_ascii=False, indent=4) + ';\n'

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'原库 {len(existing)} 幅 → 新增 {len(added)} 幅 → 合计 {len(merged)} 幅')
    for c in categories:
        print(f"  {c['name']}: {c['count']} 幅")
    if skipped:
        print(f'跳过 {len(skipped)} 幅：')
        for aid, why in skipped:
            print(f'    - {aid}: {why}')


if __name__ == '__main__':
    main()
