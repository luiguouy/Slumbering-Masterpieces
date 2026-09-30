import urllib.request
import os
import time
from PIL import Image

headers = {'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'}

url = "https://upload.wikimedia.org/wikipedia/commons/8/88/Claude_Monet_-_Nymph%C3%A9as_%281905%29.jpg"
target = "assets/images/monet_water_lilies_1906.jpg"

for attempt in range(5):
    try:
        print(f"尝试下载 (第 {attempt+1} 次)...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(target + ".tmp", "wb") as f:
                f.write(data)
        
        im = Image.open(target + ".tmp")
        if im.mode in ('RGBA', 'P'):
            im = im.convert('RGB')
        im.save(target, 'JPEG', quality=92, optimize=True)
        if os.path.exists(target + ".tmp"):
            os.remove(target + ".tmp")
        print("✅ 成功更新 monet_water_lilies_1906.jpg 为 1905 年独立睡莲名作！")
        break
    except Exception as e:
        print(f"尝试失败: {e}")
        time.sleep(2)
