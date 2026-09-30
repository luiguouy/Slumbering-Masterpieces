import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from harvest_86_impressionism_and_monet import TARGET_86_ARTWORKS

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(base_dir, 'assets', 'images')

missing = []
for a in TARGET_86_ARTWORKS:
    p = os.path.join(images_dir, a['id'] + '.jpg')
    sz = os.path.getsize(p) if os.path.exists(p) else 0
    if sz < 100000:
        missing.append((a['id'], a['title'], a['artist'], sz))

print(f"Total artworks: {len(TARGET_86_ARTWORKS)}")
print(f"Successfully downloaded (>100KB): {len(TARGET_86_ARTWORKS) - len(missing)}")
print(f"Missing or small (<100KB): {len(missing)}")
for m in missing:
    print(f"  {m[0]}: {m[1]} ({m[2]}) -> {m[3]//1024} KB")
