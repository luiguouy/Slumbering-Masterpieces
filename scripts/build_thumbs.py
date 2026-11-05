# -*- coding: utf-8 -*-
"""
生成画廊缩略图：assets/images/*.jpg → assets/thumbs/*.webp（长边 400px，品质 82）

仅处理缺少缩略图的画作，可重复执行。
"""
import os
import glob
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'images')
THUMBS_DIR = os.path.join(BASE_DIR, 'assets', 'thumbs')
LONG_EDGE = 400


def main():
    os.makedirs(THUMBS_DIR, exist_ok=True)
    created = skipped = 0
    for path in sorted(glob.glob(os.path.join(IMAGES_DIR, '*.jpg'))):
        name = os.path.splitext(os.path.basename(path))[0]
        target = os.path.join(THUMBS_DIR, name + '.webp')
        if os.path.exists(target) and os.path.getmtime(target) >= os.path.getmtime(path):
            skipped += 1
            continue
        with Image.open(path) as im:
            im = im.convert('RGB')
            w, h = im.size
            scale = LONG_EDGE / max(w, h)
            if scale < 1:
                im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.Resampling.LANCZOS)
            im.save(target, 'WEBP', quality=82, method=6)
        created += 1
        print(f'  ✓ {name}.webp')

    print(f'\n[Thumbs] 新生成 {created} 张，已存在 {skipped} 张，合计 {len(glob.glob(os.path.join(THUMBS_DIR, "*.webp")))} 张')


if __name__ == '__main__':
    main()
