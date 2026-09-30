import os
import sys
import json
import time
import urllib.request
import urllib.parse
import numpy as np
from PIL import Image

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 FineArtCollectionBot/2.0'
}

def safe_request(url, timeout=25):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 5
                print(f"    [429 Rate Limit] Backing off {wait}s...")
                time.sleep(wait)
            else:
                time.sleep(2.0)
        except Exception as e:
            time.sleep(2.0)
    return None

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
    with urllib.request.urlopen(req, timeout=40) as resp:
        with open(temp, 'wb') as f:
            f.write(resp.read())
    
    with Image.open(temp) as im:
        im = im.convert('RGB')
        im.save(save_path, 'JPEG', quality=92, optimize=True)
    
    if os.path.exists(temp):
        os.remove(temp)

def find_best_commons_file(search_query):
    queries = [
        f"{search_query} \"Google Art Project\"",
        search_query
    ]
    for q in queries:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=8"
        data = safe_request(url)
        time.sleep(1.2)
        if not data or 'query' not in data or 'search' not in data['query']:
            continue
        
        candidates = []
        for it in data['query']['search']:
            title = it['title']
            low = title.lower()
            if any(b in low for b in ['frame', 'gallery', 'room', 'museum photo', 'exhibition', 'detail', 'cropped']):
                continue
            candidates.append(title)
        
        for t in candidates[:4]:
            info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(t)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=2560&format=json"
            info_data = safe_request(info_url)
            time.sleep(1.0)
            if not info_data or 'query' not in info_data or 'pages' not in info_data['query']:
                continue
            for pid in info_data['query']['pages']:
                if 'imageinfo' in info_data['query']['pages'][pid]:
                    ii = info_data['query']['pages'][pid]['imageinfo'][0]
                    orig_w = ii.get('width', 0)
                    orig_h = ii.get('height', 0)
                    if max(orig_w, orig_h) >= 1800:
                        dl_url = ii.get('thumburl') or ii.get('url')
                        return {
                            'title': t,
                            'url': dl_url,
                            'orig_w': orig_w,
                            'orig_h': orig_h
                        }
    return None

TARGET_16 = [
    {
        'id': 'raphael_alba_madonna',
        'title': '阿尔巴圣母 (1511)',
        'enTitle': 'The Alba Madonna',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“When one is painting one does not think.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael The Alba Madonna National Gallery of Art'
    },
    {
        'id': 'caravaggio_the_incredulity_of_saint_thomas',
        'title': '圣多马的怀疑 (1602)',
        'enTitle': 'The Incredulity of Saint Thomas',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Seeing is believing, but feeling is divine truth.”',
        'quoteAuthor': '— Caravaggio',
        'search': 'Caravaggio The Incredulity of Saint Thomas Sanssouci'
    },
    {
        'id': 'fra_angelico_coronation_of_the_virgin',
        'title': '圣母加冕 (1435)',
        'enTitle': 'Coronation of the Virgin',
        'artist': 'Fra Angelico (安杰利科修士)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who does Christ’s work must always stay with Christ.”',
        'quoteAuthor': '— Fra Angelico',
        'search': 'Fra Angelico Coronation of the Virgin Louvre'
    },
    {
        'id': 'jean_fouquet_melun_diptych_virgin',
        'title': '默伦双联画 · 圣母子与天使 (1452)',
        'enTitle': 'Melun Diptych: Virgin and Child Surrounded by Angels',
        'artist': 'Jean Fouquet (让·富凯)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Form and colour in celestial harmony.”',
        'quoteAuthor': '— Jean Fouquet',
        'search': 'Jean Fouquet Virgin and Child Antwerp'
    },
    {
        'id': 'giotto_lamentation',
        'title': '哀悼基督 (1306)',
        'enTitle': 'Lamentation (The Mourning of Christ)',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is poetry which is seen and not heard.”',
        'quoteAuthor': '— Giotto',
        'search': 'Giotto Lamentation Scrovegni Chapel'
    },
    {
        'id': 'titian_penitent_magdalene',
        'title': '抹大拉的玛利亚 (1533)',
        'enTitle': 'Penitent Magdalene',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“A good painter needs only three colours: black, white, and red.”',
        'quoteAuthor': '— Titian',
        'search': 'Titian Penitent Magdalene Pitti Palace'
    },
    {
        'id': 'bruegel_conversion_of_paul',
        'title': '保罗的皈依 (1567)',
        'enTitle': 'The Conversion of Paul',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature paints the grandest stages of human fate.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'search': 'Pieter Bruegel the Elder The Conversion of Paul Kunsthistorisches Museum'
    },
    {
        'id': 'botticelli_madonna_of_magnificat',
        'title': '尊主颂圣母 (1481)',
        'enTitle': 'Madonna of the Magnificat',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“My soul doth magnify the Lord.”',
        'quoteAuthor': '— Sandro Botticelli',
        'search': 'Botticelli Madonna del Magnificat Uffizi'
    },
    {
        'id': 'giorgione_castelfranco_madonna',
        'title': '卡斯特尔弗兰科圣母 (1504)',
        'enTitle': 'Castelfranco Madonna',
        'artist': 'Giorgione (乔尔乔内)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Light breathes upon the landscape of the soul.”',
        'quoteAuthor': '— Giorgione',
        'search': 'Giorgione Castelfranco Madonna'
    },
    {
        'id': 'veronese_the_wedding_at_cana',
        'title': '迦拿的婚礼 (1563)',
        'enTitle': 'The Wedding at Cana',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“We painters take the same liberties as poets and madmen.”',
        'quoteAuthor': '— Paolo Veronese',
        'search': 'Paolo Veronese The Wedding at Cana Louvre'
    },
    {
        'id': 'rubens_elevation_of_the_cross',
        'title': '上十字架 (1610)',
        'enTitle': 'The Elevation of the Cross',
        'artist': 'Peter Paul Rubens (彼得·保罗·鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no enterprise, however great, has ever surpassed my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Rubens The Elevation of the Cross Antwerp Cathedral'
    },
    {
        'id': 'murillo_soult_immaculate_conception',
        'title': '索尔特无原罪圣母 (1678)',
        'enTitle': 'The Soult Immaculate Conception',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'search': 'Murillo The Immaculate Conception Prado Los Venerables'
    },
    {
        'id': 'tiepolo_adoration_of_the_magi',
        'title': '三博士来朝 (1753)',
        'enTitle': 'The Adoration of the Magi',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Skies without end belong to the painter’s brush.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'search': 'Tiepolo The Adoration of the Magi Alte Pinakothek'
    },
    {
        'id': 'carracci_flight_into_egypt',
        'title': '逃往埃及途中的风景 (1604)',
        'enTitle': 'The Flight into Egypt',
        'artist': 'Annibale Carracci (安尼巴莱·卡拉奇)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature ordered by classical reason becomes eternal beauty.”',
        'quoteAuthor': '— Annibale Carracci',
        'search': 'Annibale Carracci The Flight into Egypt Doria Pamphilj'
    },
    {
        'id': 'bouguereau_song_of_the_angels',
        'title': '天使之歌 (1881)',
        'enTitle': 'Song of the Angels',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Each day I go to my studio full of happiness.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'search': 'William-Adolphe Bouguereau Song of the Angels Forest Lawn'
    },
    {
        'id': 'cranach_madonna_under_fir_tree',
        'title': '松树下的圣母 (1530)',
        'enTitle': 'Madonna under the Fir Tree',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Truth and nature abide under the evergreen branch.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'search': 'Lucas Cranach the Elder Madonna under the Fir Tree Wroclaw'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    json_path = os.path.join(base_dir, 'scripts', 'harvested_50_religious.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {x['id'] for x in existing}
    print(f"Current harvested count: {len(existing)}. Need to reach 50.")

    for i, item in enumerate(TARGET_16):
        if len(existing) >= 50:
            break
        if item['id'] in existing_ids:
            continue

        print(f"\n[Processing {len(existing)+1}/50] {item['title']} - {item['artist']}")
        c = find_best_commons_file(item['search'])
        if not c:
            print(f"  ❌ No file found for {item['search']}")
            time.sleep(2.0)
            continue

        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"  🎯 Found: {c['title']} (orig: {c['orig_w']}x{c['orig_h']})")

        downloaded = False
        for attempt in range(3):
            try:
                download_and_save(c['url'], save_path)
                downloaded = True
                break
            except Exception as e:
                print(f"  Download attempt {attempt+1} failed: {e}. Waiting 5s...")
                time.sleep(5.0)

        if downloaded and os.path.exists(save_path):
            ok, msg = inspect_image(save_path)
            print(f"  🔎 QualityGatekeeper: {msg}")
            if ok:
                item['file'] = fn
                item['src'] = f"assets/images/{fn}?v=3.9.0"
                existing.append(item)
                existing_ids.add(item['id'])
                # 实时保存，防止中断丢失
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
                print(f"  ✅ Saved! Total count now: {len(existing)}/50")
            else:
                if os.path.exists(save_path):
                    os.remove(save_path)
        
        time.sleep(2.5)

    print(f"\n==========================================")
    print(f"FINAL RESULT COUNT: {len(existing)}/50")
    print(f"==========================================")

if __name__ == '__main__':
    main()
