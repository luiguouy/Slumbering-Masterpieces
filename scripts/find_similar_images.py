import json
import re
import os
from PIL import Image

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', f.read(), re.DOTALL).group(1))

# 计算 dHash
def dhash(image, hash_size=8):
    image = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(image.getdata())
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = pixels[row * (hash_size + 1) + col]
            pixel_right = pixels[row * (hash_size + 1) + col + 1]
            difference.append(pixel_left > pixel_right)
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)

def hamming_distance(s1, s2):
    return bin(int(s1, 16) ^ int(s2, 16)).count('1')

hashes = []
for d in data:
    path = d.get('src', '').split('?')[0]
    if os.path.exists(path):
        try:
            im = Image.open(path)
            h = dhash(im)
            hashes.append({
                'id': d['id'],
                'title': d['title'],
                'artist': d['artist'],
                'path': path,
                'hash': h,
                'size': im.size,
                'ratio': im.size[0] / im.size[1]
            })
        except Exception as e:
            print(f"Error reading {path}: {e}")

# 比对相似度
print(f"计算了 {len(hashes)} 张图片的哈希值，开始比对相似图片 (汉明距离 <= 5)...")
similar_pairs = []
for i in range(len(hashes)):
    for j in range(i + 1, len(hashes)):
        dist = hamming_distance(hashes[i]['hash'], hashes[j]['hash'])
        if dist <= 5:
            similar_pairs.append((dist, hashes[i], hashes[j]))

print(f"\n发现 {len(similar_pairs)} 对高度相似或相同的图片：")
for dist, a, b in similar_pairs:
    print(f"距离 {dist}: [{a['id']}] 《{a['title']}》 VS [{b['id']}] 《{b['title']}》")
    print(f"    A: {a['path']} ({a['size']})")
    print(f"    B: {b['path']} ({b['size']})")
