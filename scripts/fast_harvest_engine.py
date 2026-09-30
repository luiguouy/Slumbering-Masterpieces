import os
import sys
import json
import time
import urllib.request
import urllib.parse
import numpy as np
from PIL import Image

HEADERS = {
    'User-Agent': 'FineArtCollectionBot/1.0 (https://github.com/fine-art-web; contact: collection.curator.masterpiece@gmail.com)'
}

def safe_request(url, timeout=20):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 3
                print(f"Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                time.sleep(1.2)
        except Exception as e:
            time.sleep(1.2)
    return None

def calculate_colorfulness(image):
    img = np.array(image.convert('RGB'))
    (R, G, B) = (img[:, :, 0].astype("float"), img[:, :, 1].astype("float"), img[:, :, 2].astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    return np.sqrt((rbStd ** 2) + (ybStd ** 2)) + (0.3 * np.sqrt((rbMean ** 2) + (ybMean ** 2)))

def inspect_image(image_path):
    with Image.open(image_path) as im:
        w, h = im.size
        if max(w, h) < 1800:
            return False, f"分辨率过低 ({w}x{h})"
        thumb = im.resize((300, max(1, int(300 * h / max(1, w)))))
        c_score = calculate_colorfulness(thumb)
        hsv = thumb.convert('HSV')
        _, _, v = hsv.split()
        v_mean = np.mean(np.array(v, dtype=float) / 255.0)
        if v_mean < 0.12:
            return False, f"画面死黑严重 (亮度 {v_mean:.2f})"
        if c_score < 18.0:
            return False, f"色彩寡淡褪色 (色彩分 {c_score:.1f})"
        return True, f"合格 (分辨率 {w}x{h}, 色彩 {c_score:.1f}, 亮度 {v_mean:.2f})"

def find_best_commons_file(search_query):
    # 优先搜索官方高画质
    queries = [
        f"{search_query} \"Google Art Project\"",
        search_query
    ]
    for q in queries:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=8"
        data = safe_request(url)
        time.sleep(1.0)
        if not data or 'query' not in data or 'search' not in data['query']:
            continue
        
        candidates = []
        for it in data['query']['search']:
            title = it['title']
            low = title.lower()
            # 过滤展厅、画框、小细节切图
            if any(b in low for b in ['frame', 'gallery', 'room', 'museum photo', 'exhibition', 'detail', 'cropped']):
                continue
            candidates.append(title)
        
        # 逐个获取图片信息
        for t in candidates[:4]:
            info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(t)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json"
            info_data = safe_request(info_url)
            time.sleep(0.8)
            if not info_data or 'query' not in info_data or 'pages' not in info_data['query']:
                continue
            for pid in info_data['query']['pages']:
                if 'imageinfo' in info_data['query']['pages'][pid]:
                    ii = info_data['query']['pages'][pid]['imageinfo'][0]
                    orig_w = ii.get('width', 0)
                    orig_h = ii.get('height', 0)
                    if max(orig_w, orig_h) >= 1800:
                        # 优选 3840px 维基服务端高清渲染图，若无则原图
                        dl_url = ii.get('thumburl') or ii.get('url')
                        return {
                            'title': t,
                            'url': dl_url,
                            'orig_w': orig_w,
                            'orig_h': orig_h,
                            'is_gap': 'Google' in t
                        }
    return None

def download_and_save(file_url, save_path):
    temp = save_path + ".tmp"
    req = urllib.request.Request(file_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as resp:
        with open(temp, 'wb') as f:
            f.write(resp.read())
    
    with Image.open(temp) as im:
        im = im.convert('RGB')
        im.save(save_path, 'JPEG', quality=92, optimize=True)
    
    if os.path.exists(temp):
        os.remove(temp)

print("Fast Harvest Engine Ready.")
