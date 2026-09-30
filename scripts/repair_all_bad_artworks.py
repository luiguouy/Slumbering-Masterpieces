import urllib.request
import urllib.parse
import json
import os
import time
from PIL import Image

headers = {
    'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'
}

def download_file(url, target_path, max_width=3840):
    print(f"正在从 {url} 下载...")
    req = urllib.request.Request(url, headers=headers)
    temp_path = target_path + ".tmp"
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(temp_path, "wb") as f:
            f.write(resp.read())
    
    # 优化为适当分辨率的 JPG
    im = Image.open(temp_path)
    if im.mode in ('RGBA', 'P'):
        im = im.convert('RGB')
    w, h = im.size
    if w > max_width or h > max_width:
        ratio = max_width / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        im = im.resize(new_size, Image.Resampling.LANCZOS)
    im.save(target_path, 'JPEG', quality=90, optimize=True)
    if os.path.exists(temp_path):
        os.remove(temp_path)
    final_im = Image.open(target_path)
    print(f"✅ 成功保存: {target_path} (尺寸: {final_im.size})")

def fetch_wiki_image(wiki_filename, target_path):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(wiki_filename)}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    pages = data.get('query', {}).get('pages', {})
    for p in pages.values():
        if 'imageinfo' in p and p['imageinfo']:
            url = p['imageinfo'][0]['url']
            download_file(url, target_path)
            return True
    return False

# 待精确修复的列表
TARGETS = [
    {
        'id': 'vermeer_view_of_delft',
        'file': 'assets/images/vermeer_view_of_delft.jpg',
        'wiki': 'File:Johannes Vermeer - View of Delft - 92 - Mauritshuis.jpg',
        'desc': '维米尔《代尔夫特风景》真迹（莫瑞泰斯皇家美术馆）'
    },
    {
        'id': 'bellini_madonna_of_the_meadow',
        'file': 'assets/images/bellini_madonna_of_the_meadow.jpg',
        'wiki': 'File:Giovanni Bellini - Madonna of the Meadow - National Gallery London.jpg',
        'desc': '贝利尼《草地上的圣母与圣子》（伦敦国家美术馆）'
    },
    {
        'id': 'monet_antibes_salis',
        'file': 'assets/images/monet_antibes_salis.jpg',
        'wiki': 'File:Claude Monet - Antibes Seen from the Salis Gardens - 1929.51 - Toledo Museum of Art.jpg',
        'desc': '莫奈《昂蒂布海景 · 从萨利花园眺望》（托莱多艺术博物馆）'
    },
    {
        'id': 'monet_breakup_of_ice',
        'file': 'assets/images/monet_breakup_of_ice.jpg',
        'wiki': 'File:Claude Monet - La Débâcle près de Vétheuil - Google Art Project.jpg',
        'desc': '莫奈《塞纳河破冰》（里尔美术宫）'
    },
    {
        'id': 'monet_water_lilies_weeping_willows',
        'file': 'assets/images/monet_water_lilies_weeping_willows.jpg',
        'wiki': 'File:Water-Lilies-with-Weeping-Willows-Claude-Monet.jpg',
        'desc': '莫奈《睡莲与垂柳 (1916)》'
    }
]

print("开始修复画作图片...")
for item in TARGETS:
    print(f"\n--- 修复 [{item['id']}] {item['desc']} ---")
    try:
        ok = fetch_wiki_image(item['wiki'], item['file'])
        if not ok:
            print(f"❌ 未能从 Wikimedia 找到 {item['wiki']}")
    except Exception as e:
        print(f"❌ 发生异常: {e}")
    time.sleep(1)

print("\n全部修复流程完毕！")
