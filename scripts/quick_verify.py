import json
import os
from PIL import Image

def calculate_colorfulness(image):
    import numpy as np
    img = np.array(image.convert('RGB'))
    (R, G, B) = (img[:, :, 0].astype("float"), img[:, :, 1].astype("float"), img[:, :, 2].astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    return np.sqrt((rbStd ** 2) + (ybStd ** 2)) + (0.3 * np.sqrt((rbMean ** 2) + (ybMean ** 2)))

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    c = f.read()

start = c.find('window.MASTERPIECES =')
start_bracket = c.find('[', start)
end_bracket = c.rfind('];')
arts = json.loads(c[start_bracket:end_bracket+1])

print(f"Total artworks in data/masterpieces.js: {len(arts)}")

low_res = []
low_color = []
for a in arts:
    img_rel = a['src'].split('?')[0].replace('./', '')
    if not os.path.exists(img_rel):
        print(f"[MISSING FILE] {a['id']}: {img_rel}")
        continue
    with Image.open(img_rel) as im:
        w, h = im.size
        if max(w, h) < 1500 or min(w, h) < 800:
            low_res.append((a['id'], a['title'], w, h))
        
        # quick thumb for colorfulness
        thumb = im.resize((300, max(1, int(300 * h / max(1, w)))))
        score = calculate_colorfulness(thumb)
        if score < 20:
            low_color.append((a['id'], a['title'], score, w, h))

print(f"\n--- Low Resolution Artworks (max<1500 or min<800): {len(low_res)} ---")
for r in low_res:
    print(f"  {r[0]}: {r[2]}x{r[3]} 《{r[1]}》")

print(f"\n--- Low Colorfulness Artworks (score < 20): {len(low_color)} ---")
for r in low_color:
    print(f"  {r[0]}: score {r[2]:.1f} ({r[3]}x{r[4]}) 《{r[1]}》")
