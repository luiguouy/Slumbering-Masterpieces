# -*- coding: utf-8 -*-
"""
定点修补采集：为失败或错配的缺口名画指定检索式与强制匹配词

与批量采集不同，此脚本对“文件标题”做白/黑名单硬校验，
并允许对本身偏灰暗的杰作（如惠斯勒《灰与黑的协奏曲》）放宽色彩阈值。
"""
import os
import re
import sys
import json
import time
import unicodedata
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from museum_harvester import safe_request, QualityGatekeeper, HEADERS  # noqa: E402
from PIL import Image  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'images')
SPEC_PATH = os.path.join(BASE_DIR, 'scripts', 'gap_repair_specs.json')


def norm(text):
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace('file:', ' ').replace(':', ' ')
    return re.sub(r'[^a-z0-9 ]+', ' ', text)


def commons_candidates(query, limit=10):
    url = (f"https://commons.wikimedia.org/w/api.php?action=query&list=search"
           f"&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit={limit}")
    data = safe_request(url)
    time.sleep(0.5)
    titles = [it['title'] for it in (data or {}).get('query', {}).get('search', [])]
    return titles


def image_info(title, min_edge):
    url = (f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}"
           f"&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json")
    for attempt in range(3):
        data = safe_request(url)
        pages = (data or {}).get('query', {}).get('pages', {})
        if pages:
            for page in pages.values():
                ii = (page.get('imageinfo') or [{}])[0]
                if not ii:
                    return None
                if max(ii.get('width', 0), ii.get('height', 0)) < min_edge:
                    return None
                return {
                    'url': ii.get('thumburl') or ii.get('url'),
                    'width': ii.get('thumbwidth', ii.get('width')),
                    'height': ii.get('thumbheight', ii.get('height')),
                }
        time.sleep(1.5 * (attempt + 1))  # 限流时退避重试
    return None


def download(url, save_path):
    tmp = save_path + '.tmp'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as resp, open(tmp, 'wb') as f:
        f.write(resp.read())
    return tmp


def _norm_words(text):
    """保留 | 分隔符的词组归一化（用于 require_all 的候选同义词组）"""
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().replace('file:', ' ')


def repair(spec):
    art_id = spec['id']
    save_path = os.path.join(IMAGES_DIR, art_id + '.jpg')
    # 保留 | 分隔符（norm 会剔除标点），仅做小写与去重音处理
    require_all = [_norm_words(x) for x in spec.get('require_all', [])]
    forbid = [norm(x).strip() for x in spec.get('forbid', [])] + ['panoramio', 'inside the', 'detail', 'studio per']
    min_edge = spec.get('min_edge', 2000)
    allow_dark = spec.get('allow_dark', False)

    def require_ok(title):
        # 每组用 | 分隔候选项，任一同义词命中即算达标
        for group in require_all:
            if not any(alt.strip() and alt.strip() in title for alt in group.split('|')):
                return False
        return True

    for query in spec['queries']:
        for title in commons_candidates(query):
            t = norm(title)
            if any(b in t for b in forbid):
                continue
            if not require_ok(t):
                continue
            info = image_info(title, min_edge)
            if not info:
                continue
            try:
                tmp = download(info['url'], save_path)
            except Exception as exc:
                print(f'  ! 下载失败 {title}: {exc}')
                continue

            with Image.open(tmp) as im:
                im = im.convert('RGB')
                w, h = im.size
                if max(w, h) < min_edge:
                    os.remove(tmp)
                    continue
                thumb = im.resize((300, max(1, int(300 * h / max(1, w)))))
                score = QualityGatekeeper.calculate_colorfulness(thumb)
                brightness = _brightness(thumb)
                if brightness < 0.08 or (score < 18.0 and not allow_dark):
                    print(f'  ✗ 质检未过 {title} (色彩 {score:.1f}, 亮度 {brightness:.2f})')
                    os.remove(tmp)
                    continue
                if max(w, h) > 3840:
                    scale = 3840 / max(w, h)
                    im = im.resize((round(w * scale), round(h * scale)), Image.Resampling.LANCZOS)
                im.save(save_path, 'JPEG', quality=92, optimize=True)
            os.remove(tmp)
            size_kb = os.path.getsize(save_path) // 1024
            print(f'  ✓ {art_id} ← {title}  ({im.size[0]}x{im.size[1]}, {size_kb} KB, 色彩 {score:.1f})')
            return True
        time.sleep(0.5)
    print(f'  ✗✗ {art_id} 仍然未找到合格母带')
    return False


def _brightness(image):
    import numpy as np
    _, _, v = image.convert('HSV').split()
    return float(np.mean(np.array(v, dtype=float) / 255.0))


def main():
    with open(SPEC_PATH, 'r', encoding='utf-8') as f:
        specs = json.load(f)
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    ok = 0
    for spec in specs:
        if only and spec['id'] not in only:
            continue
        print(f"\n[Repair] {spec['id']} …")
        old = os.path.join(IMAGES_DIR, spec['id'] + '.jpg')
        if os.path.exists(old) and '--keep' not in sys.argv:
            os.remove(old)
        if repair(spec):
            ok += 1
    print(f'\n[Repair] 完成 {ok} 幅')


if __name__ == '__main__':
    main()
