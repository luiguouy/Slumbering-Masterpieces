import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ArtCollectionBot/1.0 (https://art-web.org; curator@art-web.org)'
}

Image.MAX_IMAGE_PIXELS = None

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(base_dir, 'assets', 'images')

def search_wikimedia_commons(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=8"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(2.0)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [x['title'] for x in data.get('query', {}).get('search', [])]
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return []

def get_image_info(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(2.0)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'imageinfo' in pdata:
                    ii = pdata['imageinfo'][0]
                    u = ii.get('thumburl') if ('thumburl' in ii and ii['width'] > 3840) else ii['url']
                    return u, ii['width'], ii['height']
    except Exception as e:
        print(f"Error getting info for {title}: {e}")
    return None, 0, 0

def download_and_save(url, target_path, max_dim=3840):
    tmp_path = target_path + ".tmp"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(1.0)
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(tmp_path, 'wb') as f:
            f.write(resp.read())

    with Image.open(tmp_path) as im:
        im = im.convert('RGB')
        w, h = im.size
        if max(w, h) > max_dim:
            if w > h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        im.save(target_path, 'JPEG', quality=92, optimize=True)

    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    return True

TASKS = [
    {
        'id': 'renoir_the_loge',
        'queries': [
            'Pierre-Auguste Renoir - La Loge',
            'Renoir La Loge Courtauld',
            'La Loge Renoir'
        ]
    },
    {
        'id': 'monet_the_water_lily_pond_1904',
        'queries': [
            'Claude Monet Water Lilies 1904',
            'Claude Monet Bassin aux nymphéas 1904',
            'Monet Nymphéas 1904'
        ]
    },
    {
        'id': 'monet_water_lilies_morning_willows',
        'queries': [
            'Nymphéas, matin aux saules Claude Monet',
            'Claude Monet Matin aux saules',
            'Monet Morning with Willows Orangerie'
        ]
    }
]

def main():
    print("==================================================")
    print("🎯 开始攻坚最后 3 幅传世名作")
    print("==================================================")

    for t in TASKS:
        item_id = t['id']
        target_path = os.path.join(images_dir, f"{item_id}.jpg")
        print(f"\n正在处理: {item_id}")
        success = False

        for q in t['queries']:
            print(f"  🔍 检索词: '{q}'...")
            titles = search_wikimedia_commons(q)
            for title in titles:
                t_low = title.lower()
                if any(bad in t_low for bad in ['frame', 'gallery', 'room', 'museum photo', '.pdf']):
                    continue
                print(f"    尝试候选: {title}")
                url, w, h = get_image_info(title)
                if url and max(w, h) >= 1200:
                    print(f"    🎯 找到优质母带: {w}x{h} -> 开始下载")
                    try:
                        download_and_save(url, target_path)
                        kb = os.path.getsize(target_path) // 1024
                        print(f"    ✅ 成功入库: {item_id}.jpg ({kb} KB)")
                        success = True
                        break
                    except Exception as e:
                        print(f"    ❌ 下载失败: {e}")
            if success:
                break

    print("\n攻坚流程结束。")

if __name__ == '__main__':
    main()
