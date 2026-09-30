import urllib.request
import urllib.parse
import json
import os
import time
from PIL import Image

HEADERS = {
    'User-Agent': 'ArtWebCuratorBot/2.1 (https://artweb.local; contact: curator@artweb.local) Python-urllib/3.12'
}

def safe_request(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 3
                print(f"Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"HTTP error {e.code}: {e}")
                time.sleep(2)
        except Exception as e:
            print(f"Network error: {e}")
            time.sleep(2)
    return None

def get_file_url(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    data = safe_request(url)
    time.sleep(1.0)
    if data and 'query' in data and 'pages' in data['query']:
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
        'file': 'monet_argenteuil.jpg',
        'wiki_file': "File:Claude Monet, The Artist's Garden in Argenteuil (A Corner of the Garden with Dahlias), 1873, NGA 72138.jpg"
    },
    {
        'file': 'monet_sainte_adresse.jpg',
        'wiki_file': "File:Claude Monet - Jardin à Sainte-Adresse.jpg"
    },
    {
        'file': 'bruegel_tower_of_babel.jpg',
        'wiki_file': "File:Pieter Bruegel the Elder - The Tower of Babel (Rotterdam) - Google Art Project - edited.jpg"
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
