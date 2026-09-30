import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image
import numpy as np

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FineArtCollectionBot/3.0 (collection.curator@fineart.org)'
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

def get_file_url(filename, width=2560):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(filename)}&prop=imageinfo&iiprop=url|size&iiurlwidth={width}&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data['query']['pages']
            for pid in pages:
                if 'imageinfo' in pages[pid]:
                    ii = pages[pid]['imageinfo'][0]
                    return ii.get('thumburl') or ii.get('url'), ii.get('width'), ii.get('height')
    except Exception as e:
        print(f"Error fetching info for {filename}: {e}")
    return None, 0, 0

def download_and_save(file_url, save_path):
    temp = save_path + ".tmp"
    req = urllib.request.Request(file_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as resp:
        with open(temp, 'wb') as f:
            f.write(resp.read())
    with Image.open(temp) as im:
        im = im.convert('RGB')
        im.save(save_path, 'JPEG', quality=93, optimize=True)
    if os.path.exists(temp):
        os.remove(temp)

# 待精确更新或新增的列表
TASKS = [
    # 修正项 1: 安杰利科修士《圣母加冕》官方纯画芯
    {
        'id': 'fra_angelico_coronation_of_the_virgin',
        'title': '圣母加冕 (1435)',
        'enTitle': 'Coronation of the Virgin',
        'artist': 'Fra Angelico (安杰利科修士)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who does Christ’s work must always stay with Christ.”',
        'quoteAuthor': '— Fra Angelico',
        'filenames': ['File:Fra Angelico - Coronation of the Virgin - Google Art Project.jpg', 'File:Fra Angelico - The Coronation of the Virgin - Louvre INV 314.jpg']
    },
    # 修正项 2: 乔托《哀悼基督》官方纯画芯
    {
        'id': 'giotto_lamentation',
        'title': '哀悼基督 (1306)',
        'enTitle': 'Lamentation (The Mourning of Christ)',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is poetry which is seen and not heard.”',
        'quoteAuthor': '— Giotto',
        'filenames': ['File:Giotto - Scrovegni - -36- - Lamentation (The Mourning of Christ).jpg', 'File:Giotto di Bondone - Lamentation (The Mourning of Christ) - Google Art Project.jpg']
    },
    # 新增 1: 勃鲁盖尔《保罗的皈依》
    {
        'id': 'bruegel_conversion_of_paul',
        'title': '保罗的皈依 (1567)',
        'enTitle': 'The Conversion of Paul',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature paints the grandest stages of human fate.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'filenames': ['File:Pieter Bruegel the Elder - The Conversion of Paul - Google Art Project.jpg', 'File:Pieter Bruegel d. Ä. - Bekehrung Pauli - Google Art Project.jpg']
    },
    # 新增 2: 提香《抹大拉的玛利亚》
    {
        'id': 'titian_penitent_magdalene',
        'title': '抹大拉的玛利亚 (1533)',
        'enTitle': 'Penitent Magdalene',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“A good painter needs only three colours: black, white, and red.”',
        'quoteAuthor': '— Titian',
        'filenames': ['File:Titian - Penitent Magdalene - Google Art Project.jpg', 'File:Tizian 061.jpg']
    },
    # 新增 3: 老卢卡斯·克拉纳赫《松树下的圣母》
    {
        'id': 'cranach_madonna_under_fir_tree',
        'title': '松树下的圣母 (1530)',
        'enTitle': 'Madonna under the Fir Tree',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Truth and nature abide under the evergreen branch.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'filenames': ['File:Lucas Cranach d.Ä. - Madonna unter den Tannen (Breslau).jpg', 'File:Lucas Cranach the Elder - Madonna under the Fir Tree.jpg']
    },
    # 新增 4: 卡拉奇《逃往埃及途中的风景》
    {
        'id': 'carracci_flight_into_egypt',
        'title': '逃往埃及途中的风景 (1604)',
        'enTitle': 'The Flight into Egypt',
        'artist': 'Annibale Carracci (安尼巴莱·卡拉奇)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature ordered by classical reason becomes eternal beauty.”',
        'quoteAuthor': '— Annibale Carracci',
        'filenames': ['File:Annibale Carracci - Flight into Egypt - Google Art Project.jpg', 'File:Annibale Carracci - Landscape with the Flight into Egypt - Google Art Project.jpg']
    },
    # 新增 5: 布格罗《天使之歌》
    {
        'id': 'bouguereau_song_of_the_angels',
        'title': '天使之歌 (1881)',
        'enTitle': 'Song of the Angels',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Each day I go to my studio full of happiness.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'filenames': ['File:William-Adolphe Bouguereau (1825-1905) - Song of the Angels (1881).jpg', 'File:Song of the Angels - Bouguereau.jpg']
    },
    # 新增 6: 提埃坡罗《三博士来朝》
    {
        'id': 'tiepolo_adoration_of_the_magi',
        'title': '三博士来朝 (1753)',
        'enTitle': 'The Adoration of the Magi',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Skies without end belong to the painter’s brush.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'filenames': ['File:Giovanni Battista Tiepolo - The Adoration of the Magi - Google Art Project.jpg']
    },
    # 新增 7: 乔尔乔内《卡斯特尔弗兰科圣母》
    {
        'id': 'giorgione_castelfranco_madonna',
        'title': '卡斯特尔弗兰科圣母 (1504)',
        'enTitle': 'Castelfranco Madonna',
        'artist': 'Giorgione (乔尔乔内)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Light breathes upon the landscape of the soul.”',
        'quoteAuthor': '— Giorgione',
        'filenames': ['File:Giorgione - Castelfranco Madonna - Google Art Project.jpg', 'File:Pala di castelfranco.jpg']
    },
    # 新增 8: 委罗内塞《迦拿的婚礼》
    {
        'id': 'veronese_the_wedding_at_cana',
        'title': '迦拿的婚礼 (1563)',
        'enTitle': 'The Wedding at Cana',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“We painters take the same liberties as poets and madmen.”',
        'quoteAuthor': '— Paolo Veronese',
        'filenames': ['File:Noces de Cana Veronese Louvre INV 142.jpg', 'File:Paolo Veronese - The Wedding at Cana - Google Art Project.jpg']
    },
    # 新增 9: 波提切利《尊主颂圣母》
    {
        'id': 'botticelli_madonna_of_magnificat',
        'title': '尊主颂圣母 (1481)',
        'enTitle': 'Madonna of the Magnificat',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“My soul doth magnify the Lord.”',
        'quoteAuthor': '— Sandro Botticelli',
        'filenames': ['File:Sandro Botticelli - Madonna of the Magnificat - Google Art Project.jpg', 'File:Botticelli - Madonna del Magnificat.jpg']
    },
    # 新增 10: 鲁本斯《上十字架》
    {
        'id': 'rubens_elevation_of_the_cross',
        'title': '上十字架 (1610)',
        'enTitle': 'The Elevation of the Cross',
        'artist': 'Peter Paul Rubens (彼得·保罗·鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no enterprise, however great, has ever surpassed my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'filenames': ['File:Rubens elevation of the cross.jpg', 'File:The Elevation of the Cross (Rubens).jpg']
    },
    # 新增 11: 穆里略《索尔特无原罪圣母》
    {
        'id': 'murillo_soult_immaculate_conception',
        'title': '索尔特无原罪圣母 (1678)',
        'enTitle': 'The Soult Immaculate Conception',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'filenames': ['File:Bartolomé Esteban Murillo - Inmaculada Concepción (Museo del Prado, 1678).jpg', 'File:Murillo - The Immaculate Conception of Los Venerables - Prado.jpg']
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    json_path = os.path.join(base_dir, 'scripts', 'harvested_50_religious.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    item_dict = {x['id']: x for x in existing}

    for task in TASKS:
        tid = task['id']
        fn = f"{tid}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"\nProcessing [{tid}] - {task['title']}")

        found_url = None
        for cand in task['filenames']:
            print(f"  Trying file: {cand}...")
            url, w, h = get_file_url(cand, width=2560)
            if url and max(w, h) >= 1800:
                found_url = url
                print(f"  🎯 Found exact file! ({w}x{h})")
                break
            time.sleep(1.0)

        if not found_url:
            print(f"  ❌ Failed to get valid URL for {task['title']}")
            continue

        try:
            download_and_save(found_url, save_path)
            ok, msg = inspect_image(save_path)
            print(f"  🔎 QualityGatekeeper: {msg}")
            if ok:
                entry = {
                    'id': task['id'],
                    'title': task['title'],
                    'enTitle': task['enTitle'],
                    'artist': task['artist'],
                    'category': task['category'],
                    'genre': task['genre'],
                    'quote': task['quote'],
                    'quoteAuthor': task['quoteAuthor'],
                    'file': fn,
                    'src': f"assets/images/{fn}?v=3.9.0"
                }
                item_dict[tid] = entry
                print(f"  ✅ Successfully added/updated {task['title']}")
            else:
                print(f"  ⚠️ Quality check failed: {msg}")
        except Exception as e:
            print(f"  Error downloading {task['title']}: {e}")

        time.sleep(2.0)

    # 存回并按原有顺序列出
    final_list = list(item_dict.values())
    print(f"\n==========================================")
    print(f"FINAL RECORD COUNT: {len(final_list)}")
    print(f"==========================================")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
