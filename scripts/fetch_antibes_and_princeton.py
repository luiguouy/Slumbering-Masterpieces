import urllib.request
import urllib.parse
import json
import os
from PIL import Image

headers = {'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'}

def download_and_save(url, target_path, max_dim=3840):
    print(f"正在下载到 {target_path} 来自 {url}...")
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

# 1. 普林斯顿大学艺术博物馆日本桥真迹原图
princeton_url = "https://upload.wikimedia.org/wikipedia/commons/e/ea/Claude_Monet_-_Water_Lilies_and_Japanese_Bridge_-_y1972-15_-_Princeton_University_Art_Museum.jpg"
download_and_save(princeton_url, "assets/images/monet_japanese_bridge_irises_princeton.jpg")

# 2. 搜索昂蒂布高清图
api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote('Claude Monet Antibes')}&gsrlimit=10&prop=imageinfo&iiprop=url|size&format=json"
req = urllib.request.Request(api_url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode('utf-8'))

for p in data.get('query', {}).get('pages', {}).values():
    if 'imageinfo' in p:
        info = p['imageinfo'][0]
        t = p['title'].lower()
        if 'antibes' in t and info['width'] > 1000:
            print("找到昂蒂布候选:", p['title'], info['width'], info['height'])
            download_and_save(info['url'], "assets/images/monet_antibes_salis.jpg")
            break

print("修复完成！")
