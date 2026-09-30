import urllib.request
import urllib.parse
import json
import os
import time
from PIL import Image

HEADERS = {
    'User-Agent': 'ArtWebCuratorBot/2.1 (https://artweb.local; contact: curator@artweb.local) Python-urllib/3.12'
}

def get_file_url(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
    for pid in data['query']['pages']:
        if 'imageinfo' in data['query']['pages'][pid]:
            return data['query']['pages'][pid]['imageinfo'][0]['url']
    return None

def download_and_optimize(file_url, save_path, max_dim=3840):
    print(f"Downloading {file_url} -> {save_path} ...")
    req = urllib.request.Request(file_url, headers=HEADERS)
    temp_path = save_path + ".tmp"
    with urllib.request.urlopen(req, timeout=60) as resp:
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
            print(f"Resized from {w}x{h} to {new_w}x{new_h}")
        else:
            print(f"Kept original resolution {w}x{h}")
        im.save(save_path, 'JPEG', quality=92, optimize=True)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
    print(f"Saved {save_path} ({os.path.getsize(save_path)//1024} KB)")

TASKS = [
    {
        'file': 'monet_giverny_path.jpg',
        'wiki_file': "File:Claude Monet, The Japanese Footbridge, 1899, NGA 74796.jpg"
    },
    {
        'file': 'monet_gladiolus.jpg',
        'wiki_file': "File:Claude Monet - Water Lily Pond - 1933.441 - Art Institute of Chicago.jpg"
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    for t in TASKS:
        save_path = os.path.join(img_dir, t['file'])
        url = get_file_url(t['wiki_file'])
        if url:
            download_and_optimize(url, save_path)
        time.sleep(1.5)

if __name__ == '__main__':
    main()
