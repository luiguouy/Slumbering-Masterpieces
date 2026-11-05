# -*- coding: utf-8 -*-
"""
批量补采集：西方美术史缺口名画 (Gap Harvest)

读取 scripts/gap_candidates_*.json，调用官方采集引擎（Google Art Project →
Wikimedia Commons → The Met → AIC）逐幅下载 4K 画芯，并记录质检结果。

用法：
    python scripts/harvest_gap_batch.py            # 采集全部未入库作品
    python scripts/harvest_gap_batch.py --retry    # 只重试上次失败的作品
"""
import os
import re
import sys
import json
import glob
import time
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from museum_harvester import MuseumHarvester  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'images')
RESULT_PATH = os.path.join(BASE_DIR, 'scripts', 'gap_harvest_results.json')
LOCK = threading.Lock()
LOCAL = threading.local()

# 非画芯、细节裁切、伪作摹本、版画等一律否决
REJECT_WORDS = (
    'detail', 'cropped', 'copy', 'after ', 'workshop', 'follower', 'attributed',
    'study for', 'sketch', 'frame', 'gallery', 'room', 'museum photo', 'exhibition',
    'context', 'tourist', 'pedestal', 'stamp', 'sign', 'drawing', 'engraving',
    'etching', 'lithograph', 'poster', 'woodcut',
)
STOP_TOKENS = {'the', 'van', 'der', 'della', 'del', 'de', 'di', 'of', 'and', 'saint'}


def _norm(text):
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace('file:', ' ').replace(':', ' ')
    return re.sub(r'[^a-z0-9 ]+', ' ', text)


def _artist_tokens(artist):
    english = artist.split('(')[0]
    return [w for w in _norm(english).split() if len(w) > 2 and w not in STOP_TOKENS]


def make_verify(item):
    """构造真伪校验：候选文件名必须指向目标画家的目标作品。"""
    artist_tokens = _artist_tokens(item['artist'])
    title_tokens = [w for w in _norm(item['enTitle']).split() if len(w) >= 4]

    def verify(cand):
        raw_title = cand.get('title') or ''
        title = _norm(raw_title)
        if any(bad in title for bad in REJECT_WORDS):
            return False
        if any(tok in title for tok in artist_tokens):
            return True
        # “艺术家 - 作品”命名格式但艺术家对不上 → 别家作品
        if ' - ' in raw_title:
            head = _norm(raw_title.split(' - ')[0])
            if head and not any(tok in head for tok in artist_tokens):
                return False
        if not title_tokens:
            return False
        score = sum(1 for w in title_tokens if w in title) / len(title_tokens)
        return score >= 0.85

    return verify


def get_harvester():
    if not hasattr(LOCAL, 'h'):
        LOCAL.h = MuseumHarvester()
    return LOCAL.h


def load_candidates():
    items = []
    for path in sorted(glob.glob(os.path.join(BASE_DIR, 'scripts', 'gap_candidates_*.json'))):
        with open(path, 'r', encoding='utf-8') as f:
            items.extend(json.load(f))
    return items


def load_results():
    if os.path.exists(RESULT_PATH):
        with open(RESULT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_results(results):
    with LOCK:
        with open(RESULT_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


def harvest_one(item):
    filename = item['id'] + '.jpg'
    save_path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 200 * 1024:
        return item['id'], True, 'already-exists'

    verify = make_verify(item)
    queries = [item['search'], f"{item['enTitle']} {item['artist'].split(' (')[0]}"]
    for q in queries:
        try:
            ok, meta = get_harvester().harvest(q, filename, verify=verify)
        except Exception as exc:  # 网络/解码异常不阻断批处理
            ok, meta = False, str(exc)
        if ok:
            return item['id'], True, meta.get('provider') if isinstance(meta, dict) else 'ok'
        time.sleep(0.8)
    return item['id'], False, meta if isinstance(meta, str) else 'not-found'


def clean_candidate_images():
    """删除候选清单对应的已下载图片与结果记录（用于重采前清理）。"""
    with open(RESULT_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    removed = 0
    for item in load_candidates():
        path = os.path.join(IMAGES_DIR, item['id'] + '.jpg')
        if os.path.exists(path):
            os.remove(path)
            removed += 1
    print(f'[Gap Harvest] 已清理 {removed} 张待重采图片')


def main():
    if '--clean' in sys.argv:
        clean_candidate_images()

    candidates = load_candidates()
    results = load_results()

    # 已成功的作品不再重复下载（--retry 时行为相同，只补未成功项）
    todo = [c for c in candidates if not (results.get(c['id']) or {}).get('ok')]

    print(f"[Gap Harvest] 候选 {len(candidates)} 幅，本次待采集 {len(todo)} 幅", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(harvest_one, item): item for item in todo}
        for fut in as_completed(futures):
            art_id, ok, msg = fut.result()
            done += 1
            results[art_id] = {'ok': ok, 'msg': msg}
            save_results(results)
            flag = 'OK  ' if ok else 'FAIL'
            print(f"[{done}/{len(todo)}] {flag} {art_id} -> {msg}", flush=True)

    ok_count = sum(1 for v in results.values() if v.get('ok'))
    failed = [k for k, v in results.items() if not v.get('ok')]
    print(f"\n[Gap Harvest] 完成：成功 {ok_count} / 候选 {len(candidates)}")
    if failed:
        print("[Gap Harvest] 待修补：" + ', '.join(failed))


if __name__ == '__main__':
    main()
