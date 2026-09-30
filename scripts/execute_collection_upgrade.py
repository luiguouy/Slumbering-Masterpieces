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
    print(f"Downloading from {file_url} -> {save_path} ...")
    req = urllib.request.Request(file_url, headers=HEADERS)
    temp_path = save_path + ".tmp"
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(temp_path, 'wb') as f:
            f.write(resp.read())
    
    # Optimize with PIL: ensure RGB, resize if over max_dim, save high quality JPEG
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

# Map of upgrades and replacements
TASKS = [
    # 1. High-res In-Place Upgrades
    {
        'file': 'ingres_the_source.jpg',
        'wiki_file': 'File:Jean Auguste Dominique Ingres - The Spring - Google Art Project 2.jpg'
    },
    {
        'file': 'ingres_la_grande_odalisque.jpg',
        'wiki_file': 'File:Jean Auguste Dominique Ingres, La Grande Odalisque, 1814.jpg'
    },
    {
        'file': 'raphael_sistine_madonna.jpg',
        'wiki_file': 'File:Raphael - The Sistine Madonna - Google Arts & Culture.jpg'
    },
    {
        'file': 'degas_dancer_tilting.jpg',
        'wiki_file': 'File:Edgar Degas - Danseuse basculant (Danseuse verte) - Google Art Project.jpg'
    },
    {
        'file': 'vermeer_the_astronomer.jpg',
        'wiki_file': 'File:Johannes Vermeer - The Astronomer - 1668.jpg'
    },

    # 2. Rich Colorful Replacements for Dull/Dark ones
    {
        'file': 'turner_the_grand_canal_venice.jpg',
        'wiki_file': 'File:Joseph Mallord William Turner - Venice, The Mouth of the Grand Canal - Google Art Project.jpg'
    },
    {
        'file': 'sargent_carnation_lily_lily_rose.jpg',
        'wiki_file': 'File:John Singer Sargent - Carnation, Lily, Lily, Rose - Google Art Project.jpg'
    },
    {
        'file': 'pissarro_apple_picking_eragny.jpg',
        'wiki_file': 'File:Camille Pissarro - Apple Picking - Google Art Project.jpg'
    },
    {
        'file': 'titian_flora.jpg',
        'wiki_file': 'File:Tiziano - Flora - Google Art Project.jpg'
    },
    {
        'file': 'raphael_madonna_of_the_meadow.jpg',
        'wiki_file': 'File:Raphael - Madonna in the Meadow - Google Art Project.jpg'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    
    for task in TASKS:
        save_path = os.path.join(img_dir, task['file'])
        wiki_file = task['wiki_file']
        print(f"\nProcessing {task['file']} via {wiki_file}...")
        url = get_file_url(wiki_file)
        if not url:
            print(f"FAILED to get URL for {wiki_file}")
            continue
        try:
            download_and_optimize(url, save_path)
        except Exception as e:
            print(f"Download/Optimize failed for {task['file']}: {e}")
        time.sleep(1.5)

if __name__ == '__main__':
    main()
