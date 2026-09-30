import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image
import numpy as np

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

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
    temp = save_path + ".tmp"
    req = urllib.request.Request(file_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=35) as resp:
        with open(temp, 'wb') as f:
            f.write(resp.read())
    with Image.open(temp) as im:
        im = im.convert('RGB')
        im.save(save_path, 'JPEG', quality=92, optimize=True)
    if os.path.exists(temp):
        os.remove(temp)

def search_and_download_best(query, save_path):
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=6"
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('query', {}).get('search', [])
            for it in items:
                title = it['title']
                low = title.lower()
                if any(x in low for x in ['frame', 'gallery', 'room', 'museum photo', 'cropped', 'detail']):
                    continue
                # query file info
                info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size&iiurlwidth=2560&format=json"
                time.sleep(1.0)
                try:
                    with urllib.request.urlopen(urllib.request.Request(info_url, headers=HEADERS), timeout=15) as info_resp:
                        info_data = json.loads(info_resp.read().decode('utf-8'))
                        pages = info_data.get('query', {}).get('pages', {})
                        for pid in pages:
                            if 'imageinfo' in pages[pid]:
                                ii = pages[pid]['imageinfo'][0]
                                w, h = ii.get('width', 0), ii.get('height', 0)
                                if max(w, h) >= 1800:
                                    dl_url = ii.get('thumburl') or ii.get('url')
                                    print(f"  Hit: {title} ({w}x{h})")
                                    download_and_save(dl_url, save_path)
                                    ok, msg = inspect_image(save_path)
                                    if ok:
                                        return True, msg, title
                                    else:
                                        print(f"    Rejected: {msg}")
                                        if os.path.exists(save_path):
                                            os.remove(save_path)
                except Exception as e:
                    print(f"    Info error: {e}")
    except Exception as e:
        print(f"  Search error: {e}")
    return False, "Not found", ""

FINAL_10 = [
    {
        'id': 'murillo_soult_immaculate_conception',
        'title': '索尔特无原罪圣母 (1678)',
        'enTitle': 'The Soult Immaculate Conception',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'query': 'Murillo Inmaculada Concepción Prado 1678'
    },
    {
        'id': 'cranach_rest_on_flight_into_egypt',
        'title': '逃往埃及途中的安息 (1504)',
        'enTitle': 'Rest on the Flight into Egypt',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Music of angels sweetens the weary road.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'query': 'Lucas Cranach the Elder Rest on the Flight into Egypt Gemäldegalerie'
    },
    {
        'id': 'titian_crowning_with_thorns',
        'title': '基督受荆棘冠 (1542)',
        'enTitle': 'The Crowning with Thorns',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Suffering painted with dignity touches eternity.”',
        'quoteAuthor': '— Titian',
        'query': 'Titian The Crowning with Thorns Louvre'
    },
    {
        'id': 'veronese_the_baptism_of_christ',
        'title': '基督受洗 (1582)',
        'enTitle': 'The Baptism of Christ',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Heavenly light illuminates the Jordan.”',
        'quoteAuthor': '— Paolo Veronese',
        'query': 'Paolo Veronese The Baptism of Christ Getty'
    },
    {
        'id': 'waterhouse_saint_cecilia',
        'title': '音乐主保 · 圣塞西莉亚 (1895)',
        'enTitle': 'Saint Cecilia',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“In harmonious stillness the soul hears celestial voices.”',
        'quoteAuthor': '— John William Waterhouse',
        'query': 'John William Waterhouse Saint Cecilia'
    },
    {
        'id': 'holman_hunt_the_light_of_the_world',
        'title': '世界之光 (1853)',
        'enTitle': 'The Light of the World',
        'artist': 'William Holman Hunt (威廉·霍尔曼·亨特)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Behold, I stand at the door and knock.”',
        'quoteAuthor': '— William Holman Hunt',
        'query': 'William Holman Hunt The Light of the World Keble'
    },
    {
        'id': 'poussin_the_holy_family_on_the_steps',
        'title': '台阶上的圣家族 (1648)',
        'enTitle': 'The Holy Family on the Steps',
        'artist': 'Nicolas Poussin (尼古拉·普桑)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Order and geometric perfection elevate the soul to God.”',
        'quoteAuthor': '— Nicolas Poussin',
        'query': 'Nicolas Poussin The Holy Family on the Steps Cleveland'
    },
    {
        'id': 'gentileschi_judith_slaying_holofernes',
        'title': '茱蒂斯斩杀荷罗孚尼 (1620)',
        'enTitle': 'Judith Slaying Holofernes',
        'artist': 'Artemisia Gentileschi (阿尔泰米西娅·真蒂莱斯基)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“You will see what the spirit of a woman can do.”',
        'quoteAuthor': '— Artemisia Gentileschi',
        'query': 'Artemisia Gentileschi Judith Slaying Holofernes Uffizi Google Art'
    },
    {
        'id': 'tiepolo_flight_into_egypt',
        'title': '圣家逃往埃及 (1765)',
        'enTitle': 'The Flight into Egypt',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Golden air and angels accompany the holy journey.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'query': 'Tiepolo The Flight into Egypt National Museum of Ancient Art'
    },
    {
        'id': 'vandyck_the_vision_of_saint_anthony',
        'title': '圣安东尼的异象 · 圣母圣子 (1630)',
        'enTitle': 'The Vision of Saint Anthony',
        'artist': 'Anthony van Dyck (凡·戴克)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Divine vision breaks through the shadows of the earth.”',
        'quoteAuthor': '— Anthony van Dyck',
        'query': 'Anthony van Dyck The Vision of Saint Anthony Pinacoteca'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    json_path = os.path.join(base_dir, 'scripts', 'harvested_50_religious.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {x['id'] for x in existing}
    print(f"Current count: {len(existing)}. Need: {50 - len(existing)} more.")

    for item in FINAL_10:
        if len(existing) >= 50:
            break
        if item['id'] in existing_ids:
            continue

        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"\n[Target {len(existing)+1}/50] Searching for {item['title']} - {item['artist']}")

        ok, msg, hit_title = search_and_download_best(item['query'], save_path)
        if ok:
            print(f"  ✅ Passed QualityGate: {msg}")
            item_entry = {
                'id': item['id'],
                'title': item['title'],
                'enTitle': item['enTitle'],
                'artist': item['artist'],
                'category': item['category'],
                'genre': item['genre'],
                'quote': item['quote'],
                'quoteAuthor': item['quoteAuthor'],
                'file': fn,
                'src': f"assets/images/{fn}?v=3.9.0",
                'wikiSource': hit_title
            }
            existing.append(item_entry)
            existing_ids.add(item['id'])
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            print(f"  💾 Saved! New total count: {len(existing)}/50")
        else:
            print(f"  ❌ Failed to get qualified image: {msg}")

        time.sleep(2.5)

    print(f"\n==========================================")
    print(f"FINISHED! TOTAL HARVESTED: {len(existing)}/50")
    print(f"==========================================")

if __name__ == '__main__':
    main()
