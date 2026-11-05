# -*- coding: utf-8 -*-
"""
从 data/masterpieces.js 直接生成 docs/COLLECTED_ARTWORKS.md 全量台账

所有统计与明细均由数据源推导，杜绝手写 docs 与数据脱节。
"""
import os
import re
import json
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'masterpieces.js')
DOC_PATH = os.path.join(BASE_DIR, 'docs', 'COLLECTED_ARTWORKS.md')

GENRE_ORDER = ['🌿 自然风景', '👤 人物肖像', '🏛️ 神话宗教', '👥 风俗生活', '⚔️ 历史故事', '💐 静物花卉']


def load_data():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    items = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL).group(1))
    cats = json.loads(re.search(r'window\.ART_CATEGORIES\s*=\s*(\[.*?\]);', content, re.DOTALL).group(1))
    return items, cats


def main():
    items, cats = load_data()
    cat_name = {c['id']: c['name'] for c in cats}
    genre_count = Counter(p.get('genre', '') for p in items)
    cat_count = Counter(p['category'] for p in items)
    artist_count = Counter(p['artist'] for p in items)

    lines = []
    lines.append('# 📋 传世著名油画已收录台账总览表 (Collected Masterpieces Catalog)\n')
    lines.append('> **统计基准**：由 `scripts/generate_catalog_md.py` 从 `data/masterpieces.js` 自动生成，请勿手工编辑  ')
    lines.append(f'> **已收录总量**：**{len(items)} 幅** 世界殿堂级油画旷世杰作  ')
    lines.append(f'> **展厅流派数**：**{len(cats)} 大历史时代展厅**  ')
    lines.append(f'> **大师阵容**：**{len(artist_count)} 位** 艺术巨匠  ')
    lines.append('> **准入标准**：完全遵照 [`docs/ART_SELECTION_SPEC.md`](ART_SELECTION_SPEC.md) 执行三重认证与纯净度质检\n')
    lines.append('---\n')

    lines.append('## 📊 题材与展厅全景统计 (Overview)\n')
    lines.append('### 1. 核心题材分布\n')
    lines.append('| 核心题材 | 收录画作数量 | 占比 | 代表作品范例 |')
    lines.append('| :--- | :---: | :---: | :--- |')
    for genre in GENRE_ORDER:
        group = [p for p in items if p.get('genre') == genre]
        if not group:
            continue
        samples = '、'.join(p['title'].replace(' (', ' (').split(' (')[0] for p in group[:3])
        lines.append(f'| **{genre}** | **{len(group)} 幅** | {len(group) / len(items) * 100:.1f}% | {samples} 等 |')
    lines.append('')

    lines.append('### 2. 流派展厅分布\n')
    lines.append('| 序号 | 展厅流派名称 | 收录作品数 | 重点大师阵容 |')
    lines.append('| :---: | :--- | :---: | :--- |')
    for idx, cat in enumerate(cats, 1):
        group = [p for p in items if p['category'] == cat['id']]
        top = Counter(p['artist'].split(' (')[0] for p in group).most_common(5)
        lineup = '、'.join(name for name, _ in top) if top else '—'
        lines.append(f"| {idx} | {cat['name']} | **{len(group)} 幅** | {lineup} |")
    lines.append('')
    lines.append('---\n')

    lines.append('## 🏛️ 全部已收录传世油画名作台账明细 (Detailed Catalog)\n')
    lines.append('> 排序依据：**知名度 fame 权重**（由 `scripts/score_fame.py` 维护，100 = 人类级文化符号，50 以下 = 学术价值高但大众认知度较低的佳作）\n')
    lines.append('| 编号 | 知名度 | 中文题名 | 外文题名 | 创作者 | 流派展厅 | 核心题材 | 图像资产 |')
    lines.append('| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- |')
    for idx, p in enumerate(items, 1):
        cat = cat_name.get(p['category'], p['category'])
        cat_short = re.sub(r'^[^ ]+ ', '', cat).split(' (')[0]
        title = p['title'].replace('|', '/')
        lines.append(
            f"| {idx:03d} | {p.get('fame', '—')} | **{title}** | *{p['enTitle'].replace('|', '/')}* | {p['artist']} | "
            f"{cat_short} | {p.get('genre', '')} | `{p['file']}` |"
        )
    lines.append('')
    lines.append('---\n')

    lines.append('## 🔍 题材筛选快速跳转索引 (Quick Genre Index)\n')
    for genre in GENRE_ORDER:
        group = [p for p in items if p.get('genre') == genre]
        if not group:
            continue
        lines.append(f'### {genre} ({len(group)} 幅)\n')
        for p in group:
            lines.append(f"- **{p['title']}** —— {p['artist']} (*{p['enTitle']}*)")
        lines.append('')

    with open(DOC_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'[Catalog] 已生成 {DOC_PATH}（{len(items)} 幅，{len(artist_count)} 位画家）')
    for genre in GENRE_ORDER:
        print(f'  {genre}: {genre_count.get(genre, 0)} 幅')


if __name__ == '__main__':
    main()
