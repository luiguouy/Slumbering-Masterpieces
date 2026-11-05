# -*- coding: utf-8 -*-
"""
生成新入库画作的带标签联络表（Contact Sheet），用于人工视觉核对是否错配
"""
import os
import json
import glob
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, 'assets', 'images')
OUT_DIR = os.path.join(BASE_DIR, 'scripts', 'review')
CELL_W, CELL_H = 360, 260
COLS, ROWS = 6, 6
FONT_PATH = r'C:\Windows\Fonts\arialbd.ttf'


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ids = []
    for path in ['scripts/gap_candidates_a.json', 'scripts/gap_candidates_b.json']:
        with open(os.path.join(BASE_DIR, path), 'r', encoding='utf-8') as f:
            ids.extend(item['id'] for item in json.load(f))

    entries = [(i, os.path.join(IMAGES_DIR, i + '.jpg')) for i in ids]
    entries = [(i, p) for i, p in entries if os.path.exists(p)]

    per_sheet = COLS * ROWS
    font = ImageFont.truetype(FONT_PATH, 15)
    for sheet_idx in range(0, len(entries), per_sheet):
        chunk = entries[sheet_idx:sheet_idx + per_sheet]
        sheet = Image.new('RGB', (CELL_W * COLS, CELL_H * ROWS), 'white')
        draw = ImageDraw.Draw(sheet)
        for pos, (art_id, path) in enumerate(chunk):
            col, row = pos % COLS, pos // COLS
            x, y = col * CELL_W, row * CELL_H
            with Image.open(path) as im:
                im = im.convert('RGB')
                im.thumbnail((CELL_W - 10, CELL_H - 34))
                sheet.paste(im, (x + (CELL_W - im.width) // 2, y + 4))
            label = f'{sheet_idx + pos + 1}. {art_id}'
            while draw.textlength(label, font=font) > CELL_W - 8 and len(label) > 6:
                label = label[:-2]
            draw.text((x + 4, y + CELL_H - 26), label, fill='black', font=font)
            draw.rectangle([x, y, x + CELL_W - 1, y + CELL_H - 1], outline='#bbbbbb')
        out = os.path.join(OUT_DIR, f'sheet_{sheet_idx // per_sheet + 1}.png')
        sheet.save(out)
        print(f'{out}  ({len(chunk)} 幅)')
        for pos, (art_id, _) in enumerate(chunk):
            print(f'  {sheet_idx + pos + 1:3d}. {art_id}')


if __name__ == '__main__':
    main()
