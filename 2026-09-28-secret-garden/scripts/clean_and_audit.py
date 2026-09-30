import os
import json
from PIL import Image
import numpy as np

def calculate_colorfulness(image):
    img = np.array(image.convert('RGB'))
    (R, G, B) = (img[:, :, 0].astype("float"), img[:, :, 1].astype("float"), img[:, :, 2].astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    return np.sqrt((rbStd ** 2) + (ybStd ** 2)) + (0.3 * np.sqrt((rbMean ** 2) + (ybMean ** 2)))

with open('scripts/harvested_50_religious.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries in harvested_50_religious.json: {len(data)}")

invalid_items = []
valid_items = []

for i, x in enumerate(data):
    p = os.path.join('assets/images', x['file'])
    if not os.path.exists(p):
        print(f"[{i+1}] File missing: {p}")
        invalid_items.append(x)
        continue
    
    with Image.open(p) as im:
        w, h = im.size
        thumb = im.resize((300, max(1, int(300 * h / max(1, w)))))
        c_score = calculate_colorfulness(thumb)
        arr = np.array(thumb.convert('L')) / 255.0
        v_mean = float(np.mean(arr))
        
        # 检查是否合格
        is_ok = True
        reason = "OK"
        if max(w, h) < 1800:
            is_ok = False
            reason = f"Low res: {w}x{h}"
        elif c_score < 18.0:
            is_ok = False
            reason = f"Low color: {c_score:.1f}"
        elif v_mean < 0.12:
            is_ok = False
            reason = f"Too dark: {v_mean:.2f}"
        
        # 针对刚才发现的展厅壁画墙图进行标记
        if x['id'] == 'giotto_lamentation' and 'Right wall' in str(x):
            is_ok = False
            reason = "Gallery wall photo, not pure canvas"

        if is_ok:
            valid_items.append(x)
            print(f"[{i+1}] ✅ {x['id']}: {w}x{h}, color={c_score:.1f}, v={v_mean:.2f} ({x['title']})")
        else:
            invalid_items.append(x)
            print(f"[{i+1}] ❌ {x['id']}: {reason} ({x['title']})")

print(f"\nSummary: Valid={len(valid_items)}, Invalid={len(invalid_items)}")

# 过滤出干净的 valid_items 并保存
with open('scripts/harvested_50_religious.json', 'w', encoding='utf-8') as f:
    json.dump(valid_items, f, ensure_ascii=False, indent=2)
print("Updated harvested_50_religious.json with valid items only.")
