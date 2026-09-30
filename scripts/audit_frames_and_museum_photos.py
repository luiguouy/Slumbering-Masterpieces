# -*- coding: utf-8 -*-
"""
地毯式排查全库 156 幅名画：查找带有画框(Frame)、展厅实景(Museum Room)、游客拍摄的异常图片
"""
import os
import json
from PIL import Image, ImageStat

data_js_path = r'2026-09-28-secret-garden\data\masterpieces.js'
images_dir = r'2026-09-28-secret-garden\assets\images'

with open(data_js_path, 'r', encoding='utf-8') as f:
    c = f.read()

s = c.find('window.MASTERPIECES = ') + len('window.MASTERPIECES = ')
e = c.rfind(';')
paintings = json.loads(c[s:e])

suspicious_list = []

for idx, p in enumerate(paintings):
    img_path = os.path.join(images_dir, p['file'])
    if not os.path.exists(img_path):
        print(f"[MISSING] {p['id']}: {img_path}")
        continue
    
    try:
        with Image.open(img_path) as im:
            w, h = im.size
            # 缩放到适中大小分析
            thumb = im.convert('RGB').resize((200, 200))
            
            # 分析四周边框 (取外围 10 像素)
            top = thumb.crop((0, 0, 200, 10))
            bottom = thumb.crop((0, 190, 200, 200))
            left = thumb.crop((0, 10, 10, 190))
            right = thumb.crop((190, 10, 200, 190))
            center = thumb.crop((40, 40, 160, 160))
            
            stat_top = ImageStat.Stat(top)
            stat_bottom = ImageStat.Stat(bottom)
            stat_left = ImageStat.Stat(left)
            stat_right = ImageStat.Stat(right)
            stat_center = ImageStat.Stat(center)
            
            # 计算四边平均颜色与方差
            border_r = (stat_top.mean[0] + stat_bottom.mean[0] + stat_left.mean[0] + stat_right.mean[0]) / 4
            border_g = (stat_top.mean[1] + stat_bottom.mean[1] + stat_left.mean[1] + stat_right.mean[1]) / 4
            border_b = (stat_top.mean[2] + stat_bottom.mean[2] + stat_left.mean[2] + stat_right.mean[2]) / 4
            
            # 检测金色画框 (金黄色: R高, G较高, B低，如 R>140, G>100, B<70)
            is_gold_frame = (border_r > 130 and border_g > 100 and border_b < 80 and (border_r - border_b) > 50)
            
            # 检测纯白/灰白展墙背景 (R, G, B 都极高且接近，如 > 200)
            is_white_wall = (border_r > 210 and border_g > 210 and border_b > 210 and abs(border_r - border_g) < 15 and abs(border_g - border_b) < 15)
            
            # 边框与中心色差极大 (可能的画框镶边)
            center_brightness = sum(stat_center.mean) / 3
            border_brightness = (border_r + border_g + border_b) / 3
            
            # 记录异常特征
            flags = []
            if is_gold_frame:
                flags.append("疑似金色画框 (Gold Frame)")
            if is_white_wall:
                flags.append("疑似展厅白墙背景 (White Wall/Museum Room)")
            
            # 同时检查 query 或文件名中是否带可疑字眼
            query_str = (p.get('query', '') + ' ' + p.get('searchTerm', '')).lower()
            if any(k in query_str for k in ['frame', 'gallery', 'room', 'museum photo']):
                flags.append("搜索词带展厅/相框特征")
                
            if flags:
                suspicious_list.append({
                    'id': p['id'],
                    'title': p['title'],
                    'artist': p['artist'],
                    'file': p['file'],
                    'size': f"{w}x{h}",
                    'flags': flags
                })
    except Exception as err:
        print(f"[ERROR] {p['id']}: {err}")

print(f"\nAudit completed. Total checked: {len(paintings)}. Suspicious items: {len(suspicious_list)}")
for it in suspicious_list:
    print(f" - [{it['id']}] {it['title']} ({it['size']}): {', '.join(it['flags'])}")
