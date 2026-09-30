import urllib.request
import urllib.parse
import json
import os
from PIL import Image

headers = {'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'}

def download_and_save(url, target_path, max_dim=3840):
    print(f"正在下载到 {target_path} 来自 {url[:80]}...")
    req = urllib.request.Request(url, headers=headers)
    temp = target_path + ".tmp"
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(temp, "wb") as f:
            f.write(resp.read())
    
    im = Image.open(temp)
    if im.mode in ('RGBA', 'P'):
        im = im.convert('RGB')
    w, h = im.size
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        im = im.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
    im.save(target_path, 'JPEG', quality=92, optimize=True)
    if os.path.exists(temp):
        os.remove(temp)
    saved = Image.open(target_path)
    print(f"✅ 成功写入: {target_path} (尺寸: {saved.size}, 比例: {saved.size[0]/saved.size[1]:.2f})")

# 1. 修复维米尔《代尔夫特风景》
delft_url = "https://upload.wikimedia.org/wikipedia/commons/e/ed/View_of_Delft%2C_by_Johannes_Vermeer.jpg"
download_and_save(delft_url, "assets/images/vermeer_view_of_delft.jpg")

# 2. 修复贝利尼《草地上的圣母与圣子》
bellini_url = "https://upload.wikimedia.org/wikipedia/commons/f/f4/Giovanni_bellini%2C_madonna_del_prato_01.jpg"
download_and_save(bellini_url, "assets/images/bellini_madonna_of_the_meadow.jpg")

print("维米尔和贝利尼修复完毕！")
