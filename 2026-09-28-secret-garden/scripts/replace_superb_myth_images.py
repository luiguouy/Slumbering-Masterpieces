import os
import urllib.request
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(base_dir, 'assets', 'images')

UPGRADES = [
    {
        'id': 'botticelli_venus_and_mars',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/1/1d/Venus_and_Mars_National_Gallery.jpg'
    },
    {
        'id': 'rembrandt_danae',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/8/88/Rembrandt_Harmensz._van_Rijn_026.jpg'
    },
    {
        'id': 'rubens_perseus_and_andromeda',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Peter_Paul_Rubens_-_Perseus_and_Andromeda_%28Hermitage_Museum%29.jpg'
    },
    {
        'id': 'velazquez_apollo_forge_of_vulcan',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/a/ae/Vel%C3%A1zquez_-_La_Fragua_de_Vulcano_%28Museo_del_Prado%2C_1630%29.jpg'
    },
    {
        'id': 'gerard_cupid_and_psyche',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/a/a6/Gerard_FrancoisPascalSimon-Cupid_Psyche_end.jpg'
    },
    {
        'id': 'waterhouse_ulysses_and_the_sirens',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/0/04/WATERHOUSE_-_Ulises_y_las_Sirenas_%28National_Gallery_of_Victoria%2C_Melbourne%2C_1891._%C3%93leo_sobre_lienzo%2C_100.6_x_202_cm%29.jpg'
    },
    {
        'id': 'correggio_leda_and_the_swan',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/1/14/Correggio_-_Leda_and_the_Swan_-_Google_Art_Project.jpg'
    },
    {
        'id': 'bouguereau_birth_of_venus',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/b/bb/William-Adolphe_Bouguereau_%281825-1905%29_-_The_Birth_of_Venus_%281879%29.jpg'
    }
]

headers = {'User-Agent': 'Mozilla/5.0 FineArtUpgradeBot/2.0 (curator@artweb.org)'}

def download_and_save(url, target_path, max_dim=3840):
    tmp_path = target_path + ".tmp"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                with open(tmp_path, 'wb') as f:
                    f.write(resp.read())
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", flush=True)
    else:
        return False, "Failed to download"

    try:
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
        return True, f"Success ({w}x{h} -> {im.size[0]}x{im.size[1]})"
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False, f"Image processing error: {e}"

print("Starting precise master upgrades...", flush=True)
for item in UPGRADES:
    tpath = os.path.join(images_dir, f"{item['id']}.jpg")
    print(f"Downloading {item['id']}...", flush=True)
    ok, msg = download_and_save(item['url'], tpath)
    print(f"  Result: {msg}", flush=True)

print("All precise upgrades complete!", flush=True)
