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

# 1. 莫奈《塞纳河破冰》(The Breakup of the Ice, 1880, Lille Palais des Beaux-Arts)
# 维基百科上的高清原图: File:Claude Monet - La Débâcle près de Vétheuil - Google Art Project.jpg
breakup_url = "https://upload.wikimedia.org/wikipedia/commons/1/10/Monet_w571.jpg" # 或者高质量源
download_and_save("https://upload.wikimedia.org/wikipedia/commons/1/10/Monet_w571.jpg", "assets/images/monet_breakup_of_ice.jpg")

# 2. 莫奈《睡莲与垂柳》(Water Lilies and Weeping Willow, 1916-1919, Musée Marmottan Monet)
# File:Claude Monet - Nymphéas avec rameaux de saule - Marmottan.jpg
weeping_url = "https://upload.wikimedia.org/wikipedia/commons/e/ed/Nympheas%2C_reflets_de_saule_-_Water-Lilies%2C_Reflections_of_Weeping_Willows_%281916-19%29_Claude_Monet_-_Chichu_Museum_of_Art_%28W_1857%29.jpg"
download_and_save(weeping_url, "assets/images/monet_water_lilies_weeping_willows.jpg")

print("莫奈重复图片修复完毕！")
