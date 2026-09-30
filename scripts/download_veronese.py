import urllib.request
import urllib.parse
import json
import os
from PIL import Image

HEADERS = {'User-Agent': 'ArtWebCuratorBot/2.1 (contact: curator@artweb.local) Python-urllib/3.12'}

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
    with urllib.request.urlopen(req, timeout=80) as resp:
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

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    save_path = os.path.join(img_dir, 'veronese_wedding_at_cana.jpg')
    wiki_file = "File:Les Noces de Cana - Paolo Veronese - Musée du Louvre Peintures INV 142 ; MR 384.jpg"
    url = get_file_url(wiki_file)
    if url:
        download_and_optimize(url, save_path)

if __name__ == '__main__':
    main()
