import os
import sys
import json
import time
import urllib.request
from PIL import Image
import numpy as np

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
        arr = np.array(thumb.convert('L')) / 255.0
        v_mean = float(np.mean(arr))
        if v_mean < 0.12:
            return False, f"画面死黑严重 (亮度 {v_mean:.2f})"
        if c_score < 18.0:
            return False, f"色彩寡淡褪色 (色彩分 {c_score:.1f})"
        return True, f"合格 (分辨率 {w}x{h}, 色彩 {c_score:.1f}, 亮度 {v_mean:.2f})"

def download_and_save(file_url, save_path):
    headers = {'User-Agent': 'Mozilla/5.0 FineArtCurator/3.0'}
    temp = save_path + ".tmp"
    req = urllib.request.Request(file_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(temp, 'wb') as f:
            f.write(resp.read())
    with Image.open(temp) as im:
        im = im.convert('RGB')
        im.save(save_path, 'JPEG', quality=93, optimize=True)
    if os.path.exists(temp):
        os.remove(temp)

AIC_NEW_2 = [
    {
        'id': 'el_greco_assumption_of_the_virgin',
        'title': '圣母升天 (1577)',
        'enTitle': 'The Assumption of the Virgin',
        'artist': 'El Greco (埃尔·格列柯)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“I paint because the spirits whisper madly unto my soul.”',
        'quoteAuthor': '— El Greco',
        'url': 'https://www.artic.edu/iiif/2/47fd1564-93f5-f30b-7786-013421133b4a/full/2560,/0/default.jpg',
        'source': 'Art Institute of Chicago (AIC #87479)'
    },
    {
        'id': 'tintoretto_saint_helen_true_cross',
        'title': '圣海伦娜验证真十字架 (1545)',
        'enTitle': 'Saint Helen Testing the True Cross',
        'artist': 'Tintoretto (丁托列托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The drawing of Michelangelo and the colour of Titian.”',
        'quoteAuthor': '— Tintoretto',
        'url': 'https://www.artic.edu/iiif/2/90a2969d-542a-e97f-09dd-fa1310d91acf/full/2560,/0/default.jpg',
        'source': 'Art Institute of Chicago (AIC #10509)'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    json_path = os.path.join(base_dir, 'scripts', 'harvested_50_religious.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    # 先修正现有条目中的元数据
    for item in existing:
        if item['id'] == 'cranach_rest_on_flight_into_egypt':
            item['id'] = 'murillo_rest_on_flight_into_egypt'
            item['title'] = '逃往埃及途中的安息 (1665)'
            item['artist'] = 'Bartolomé Esteban Murillo (穆里略)'
            item['quote'] = '“Music of angels sweetens the weary road.”'
            item['quoteAuthor'] = '— Bartolomé Esteban Murillo'
            # 重命名文件如果存在
            old_f = os.path.join(img_dir, 'cranach_rest_on_flight_into_egypt.jpg')
            new_f = os.path.join(img_dir, 'murillo_rest_on_flight_into_egypt.jpg')
            if os.path.exists(old_f):
                if os.path.exists(new_f): os.remove(new_f)
                os.rename(old_f, new_f)
            item['file'] = 'murillo_rest_on_flight_into_egypt.jpg'
            item['src'] = 'assets/images/murillo_rest_on_flight_into_egypt.jpg?v=3.9.0'

        elif item['id'] == 'veronese_the_baptism_of_christ':
            item['id'] = 'cima_da_conegliano_baptism_of_christ'
            item['title'] = '基督受洗 (1492)'
            item['artist'] = 'Cima da Conegliano (奇马·达·科内利亚诺)'
            item['quote'] = '“Heavenly light illuminates the Jordan.”'
            item['quoteAuthor'] = '— Cima da Conegliano'
            old_f = os.path.join(img_dir, 'veronese_the_baptism_of_christ.jpg')
            new_f = os.path.join(img_dir, 'cima_da_conegliano_baptism_of_christ.jpg')
            if os.path.exists(old_f):
                if os.path.exists(new_f): os.remove(new_f)
                os.rename(old_f, new_f)
            item['file'] = 'cima_da_conegliano_baptism_of_christ.jpg'
            item['src'] = 'assets/images/cima_da_conegliano_baptism_of_christ.jpg?v=3.9.0'

    existing_ids = {x['id'] for x in existing}
    print(f"Current cleaned count: {len(existing)}. Adding final 2 from Art Institute of Chicago...")

    for item in AIC_NEW_2:
        if item['id'] in existing_ids:
            continue
        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"\nDownloading AIC masterpiece: {item['title']} - {item['artist']}")
        print(f"URL: {item['url']}")
        download_and_save(item['url'], save_path)
        ok, msg = inspect_image(save_path)
        print(f"  🔎 QualityGatekeeper: {msg}")
        if ok:
            entry = {
                'id': item['id'],
                'title': item['title'],
                'enTitle': item['enTitle'],
                'artist': item['artist'],
                'category': item['category'],
                'genre': item['genre'],
                'quote': item['quote'],
                'quoteAuthor': item['quoteAuthor'],
                'file': fn,
                'src': f"assets/images/{fn}?v=3.9.0"
            }
            existing.append(entry)
            existing_ids.add(item['id'])
            print(f"  ✅ Successfully added! Count: {len(existing)}/50")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n==========================================")
    print(f"🎉 50 RELIGIOUS MASTERPIECES COMPLETED! Count: {len(existing)}")
    print(f"==========================================")

if __name__ == '__main__':
    main()
