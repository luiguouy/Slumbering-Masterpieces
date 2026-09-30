import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image
import numpy as np

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ArtWebHarvester/4.0'
}

Image.MAX_IMAGE_PIXELS = None

TARGET_REPAIRS = {
    'renoir_the_loge': {
        'search': 'Pierre-Auguste Renoir La Loge Courtauld Gallery',
        'preferred': 'File:Pierre-Auguste Renoir, La Loge, Courtauld Gallery.jpg'
    },
    'caillebotte_the_floor_scrapers': {
        'preferred': 'File:Gustave Caillebotte - The Floor Planers - Google Art Project.jpg'
    },
    'monet_the_magpie': {
        'preferred': 'File:Claude Monet - The Magpie - Google Art Project.jpg'
    },
    'monet_wheatstacks_snow_morning': {
        'preferred': 'File:Claude Monet (French - Wheatstacks, Snow Effect, Morning - Google Art Project.jpg'
    },
    'monet_water_lilies_reflections_clouds': {
        'preferred': 'File:Claude Monet - Reflections of Clouds on the Water-Lily Pond.jpg'
    },
    'monet_water_lilies_evening_effect': {
        'preferred': 'File:Claude Monet - Nymphéas, effet du soir W1504 - Musée Marmottan-Monet.jpg'
    },
    'monet_water_lilies_weeping_willows': {
        'preferred': 'File:SAULE PLEUREUR ET BASSIN AUX NYMPHÉAS (1916-1919) Claude Monet - Musée Marmottan Monet (W 1848).jpg'
    },
    'monet_la_japonaise': {
        'search': 'Claude Monet Madame Monet in a Japanese Kimono Museum of Fine Arts Boston',
        'preferred': 'File:Claude Monet - Madame Monet in a Japanese Kimono - 56.581 - Museum of Fine Arts.jpg'
    },
    'monet_water_lily_pond_orsay_1900': {
        'search': 'Claude Monet Le Bassin aux nymphéas, harmonie verte Musée d\'Orsay',
        'preferred': 'File:Le Bassin aux nymphéas, harmonie verte - Claude Monet - Musée d\'Orsay RF 2004.jpg'
    },
    'degas_racehorses_before_stands': {
        'search': 'Edgar Degas Chevaux de course devant les tribunes Musée d\'Orsay',
        'preferred': 'File:Chevaux de course devant les tribunes - Edgar Degas - Musée d\'Orsay RF 1980.jpg'
    },
    'sisley_canal_saint_martin': {
        'search': 'Alfred Sisley Vue du canal Saint-Martin Musée d\'Orsay',
        'preferred': 'File:Alfred Sisley - Vue du canal Saint-Martin.jpg'
    },
    'pissarro_great_bridge_rouen': {
        'search': 'Camille Pissarro Pont Boieldieu in Rouen',
        'preferred': 'File:Camille Pissarro - Pont Boieldieu in Rouen, Rainy Weather - Google Art Project.jpg'
    },
    'pissarro_climbing_path_hermitage': {
        'search': 'Camille Pissarro The Climbing Path at the Hermitage Brooklyn Museum',
        'preferred': 'File:The Climbing Path at the Hermitage, Pontoise - Camille Pissarro.jpg'
    },
    'pissarro_peasant_woman_washing': {
        'search': 'Camille Pissarro Femme étendant du linge',
        'preferred': 'File:Camille Pissarro - Femme étendant du linge.jpg'
    },
    'monet_winter_sunlight_giverny': {
        'search': 'Claude Monet Soleil d\'hiver Giverny',
        'preferred': 'File:Claude Monet - Winter Sun, Giverny.jpg'
    },
    'monet_breakup_of_ice': {
        'search': 'Claude Monet La Débâcle Vétheuil',
        'preferred': 'File:Claude Monet - The Break-Up of the Ice (Vétheuil).jpg'
    },
    'monet_antibes_salis': {
        'search': 'Claude Monet Antibes seen from the Salis Gardens',
        'preferred': 'File:Monet - antibes-seen-from-the-salis-gardens-01(1).jpg'
    },
    'monet_the_water_lily_pond_1904': {
        'search': 'Claude Monet Water Lilies Denver Art Museum',
        'preferred': 'File:Claude Monet - Water Lilies - 1983.532 - Denver Art Museum.jpg'
    },
    'monet_water_lilies_morning_willows': {
        'search': 'Claude Monet Nymphéas matin aux saules Orangerie',
        'preferred': 'File:Nymphéas, matin aux saules - Claude Monet - Musée de l\'Orangerie RF 1960-14.jpg'
    },
    'monet_water_lilies_morning_marmottan': {
        'search': 'Claude Monet Nymphéas Musée Marmottan Monet',
        'preferred': 'File:Nymphéas (1916-1919) Claude Monet - Musée Marmottan Monet (W 1800).jpg'
    }
}

def resolve_file_info(file_title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(1.0)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'imageinfo' in pdata:
                    ii = pdata['imageinfo'][0]
                    target_url = ii.get('thumburl') if ('thumburl' in ii and ii['width'] > 3840) else ii['url']
                    return target_url, ii['width'], ii['height']
    except Exception as e:
        print(f"  Error fetching file info {file_title}: {e}")
    return None, 0, 0

def search_wikimedia(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=5"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(1.0)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [x['title'] for x in data.get('query', {}).get('search', [])]
    except Exception as e:
        print(f"  Search error: {e}")
    return []

def download_and_process(url, save_path, max_dim=3840):
    temp_path = save_path + ".tmp"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as resp:
        with open(temp_path, 'wb') as f:
            f.write(resp.read())

    with Image.open(temp_path) as im:
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
        im.save(save_path, 'JPEG', quality=92, optimize=True)

    if os.path.exists(temp_path):
        os.remove(temp_path)
    return True

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, 'assets', 'images')
    print("================================================================")
    print("🛠️ 开始对 20 幅关键名作执行官方精准母带校准与定向修复")
    print("================================================================")

    for item_id, config in TARGET_REPAIRS.items():
        save_file = os.path.join(images_dir, f"{item_id}.jpg")
        print(f"\n[校准修复] -> {item_id}")
        url, w, h = None, 0, 0

        # 优先尝试指定文件名
        preferred = config.get('preferred')
        if preferred:
            url, w, h = resolve_file_info(preferred)
            if url:
                print(f"  🎯 命中指定权威母带: {preferred} ({w}x{h})")

        # 未命中则搜索
        if not url and config.get('search'):
            candidates = search_wikimedia(config['search'])
            for cand in candidates:
                cand_lower = cand.lower()
                if any(bad in cand_lower for bad in ['frame', 'gallery', 'room', 'museum photo', 'exhibition', '.pdf']):
                    continue
                url, w, h = resolve_file_info(cand)
                if url and max(w, h) >= 1500:
                    print(f"  🎯 检索命中权威母带: {cand} ({w}x{h})")
                    break

        if url:
            try:
                download_and_process(url, save_file)
                sz_kb = os.path.getsize(save_file) // 1024
                print(f"  ✅ 修复成功入库: {item_id}.jpg ({sz_kb} KB)")
            except Exception as e:
                print(f"  ❌ 下载处理失败: {e}")
        else:
            print(f"  ⚠️ 未找到满意母带，跳过该项")

    print("\n================================================================")
    print("🎉 定向校准修复完成！")
    print("================================================================")

if __name__ == '__main__':
    main()
