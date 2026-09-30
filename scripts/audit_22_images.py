import os
import json
from PIL import Image
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(base_dir, 'assets', 'images')
res_path = os.path.join(base_dir, 'scripts', 'harvested_22_results.json')

with open(res_path, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"{'ID':<35} | {'Dimensions':<12} | {'Size KB':<8} | Notes")
print("-" * 75)

for it in items:
    path = os.path.join(images_dir, it['file'])
    if not os.path.exists(path):
        print(f"{it['id']:<35} | MISSING FILE")
        continue
    size_kb = os.path.getsize(path) // 1024
    with Image.open(path) as im:
        w, h = im.size
        # 采样四角检测是否是大木框或白边/展厅
        arr = np.array(im.convert('RGB'))
        # 边缘 5% 均值
        top_edge = arr[:int(h*0.04), :, :]
        bottom_edge = arr[int(h*0.96):, :, :]
        left_edge = arr[:, :int(w*0.04), :]
        right_edge = arr[:, int(w*0.96):, :]
        
        # 检查角落和边缘的标准差与平均色
        print(f"{it['id']:<35} | {w}x{h:<6} | {size_kb:<8} | aspect: {w/h:.2f}")
