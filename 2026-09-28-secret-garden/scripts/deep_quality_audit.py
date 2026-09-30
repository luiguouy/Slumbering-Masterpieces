import os
import re
import json
import numpy as np
from PIL import Image

def calculate_colorfulness(image):
    # Hasler and Süsstrunk metric
    img = np.array(image.convert('RGB'))
    (R, G, B) = (img[:, :, 0].astype("float"), img[:, :, 1].astype("float"), img[:, :, 2].astype("float"))
    rg = np.absolute(R - G)
    yb = np.absolute(0.5 * (R + G) - B)
    (rbMean, rbStd) = (np.mean(rg), np.std(rg))
    (ybMean, ybStd) = (np.mean(yb), np.std(yb))
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
    return stdRoot + (0.3 * meanRoot)

def calculate_saturation(image):
    hsv = image.convert('HSV')
    h, s, v = hsv.split()
    s_arr = np.array(s, dtype=float) / 255.0
    v_arr = np.array(v, dtype=float) / 255.0
    return np.mean(s_arr), np.std(s_arr), np.mean(v_arr)

def parse_masterpieces_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find window.MASTERPIECES = [ ... ];
    start = content.find('window.MASTERPIECES =')
    if start == -1:
        return []
    start_bracket = content.find('[', start)
    end_bracket = content.rfind('];')
    json_text = content[start_bracket:end_bracket+1]
    raw_list = json.loads(json_text)
    artworks = []
    for it in raw_list:
        artworks.append({
            'id': it.get('id'),
            'title': it.get('title'),
            'titleEn': it.get('enTitle'),
            'artist': it.get('artist'),
            'category': it.get('category'),
            'file': it.get('file'),
            'genre': it.get('genre'),
            'image': it.get('src')
        })
    return artworks

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js_path = os.path.join(base_dir, 'data', 'masterpieces.js')
    artworks = parse_masterpieces_js(js_path)
    print(f"Parsed {len(artworks)} artworks from {js_path}")

    results = []
    for art in artworks:
        img_rel = art['image'].split('?')[0].replace('./', '').replace('/', os.sep)
        img_path = os.path.join(base_dir, img_rel)
        if not os.path.exists(img_path):
            results.append({
                'art': art,
                'status': 'MISSING_FILE',
                'colorfulness': 0,
                'mean_s': 0,
                'w': 0, 'h': 0
            })
            continue

        try:
            with Image.open(img_path) as im:
                w, h = im.size
                # fast small thumb for color calculation
                thumb = im.resize((300, max(1, int(300 * h / max(1, w)))))
                c_score = calculate_colorfulness(thumb)
                mean_s, std_s, mean_v = calculate_saturation(thumb)
                results.append({
                    'art': art,
                    'status': 'OK',
                    'w': w,
                    'h': h,
                    'colorfulness': round(c_score, 2),
                    'mean_s': round(mean_s, 3),
                    'std_s': round(std_s, 3),
                    'mean_v': round(mean_v, 3),
                    'aspect': round(w / h, 2)
                })
        except Exception as e:
            results.append({
                'art': art,
                'status': f'ERROR: {e}',
                'colorfulness': 0,
                'mean_s': 0,
                'w': 0, 'h': 0
            })

    # Sort by colorfulness ascending (least colorful first)
    results.sort(key=lambda x: x['colorfulness'])

    print("\n================== BOTTOM 35 LOWEST COLORFULNESS ==================")
    for r in results[:35]:
        a = r['art']
        print(f"[{r['colorfulness']:5.1f} | sat:{r['mean_s']:.2f} | val:{r['mean_v']:.2f} | {r['w']}x{r['h']}] {a['id']}: {a['title']} ({a['titleEn']}) - {a['artist']}")

    print("\n================== SUSPICIOUS / LOW RESOLUTION (<1000px) ==================")
    for r in results:
        if r['w'] < 1000 or r['h'] < 1000:
            a = r['art']
            print(f"[{r['w']}x{r['h']}] {a['id']}: {a['title']} ({a['titleEn']})")

    # Save full audit to JSON
    with open('scripts/deep_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
