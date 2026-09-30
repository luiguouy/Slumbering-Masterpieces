import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
images_dir = os.path.join(base_dir, 'assets', 'images')
os.makedirs(images_dir, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ArtWebCurator/2.0 (curator@artweb-collection.org)'
}

TASKS = [
    # 1. 摩西在西奈山领受律法
    {
        'id': 'gerome_moses_mount_sinai',
        'title': '摩西在西奈山领受律法 (1895)',
        'enTitle': 'Moses on Mount Sinai',
        'artist': 'Jean-Léon Gérôme (让-莱昂·热罗姆)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Art is a severe mistress, who demands all of one’s mind and soul.”',
        'quoteAuthor': '— Jean-Léon Gérôme',
        'queries': [
            'Moses on Mount Sinai Jean-Léon Gérôme',
            'Jean-Léon Gérôme Moses',
            'Moses Receiving the Law Benjamin West',
            'Philippe de Champaigne Moses'
        ]
    },
    # 2. 王座上的拿破仑一世
    {
        'id': 'ingres_napoleon_on_his_imperial_throne',
        'title': '王座上的拿破仑一世 (1806)',
        'enTitle': 'Napoleon I on His Imperial Throne',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'quote': '“Drawing includes everything except the tint.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres',
        'queries': [
            'Napoleon on his Imperial throne Ingres',
            'Napoléon Ier sur le trône impérial Ingres',
            'Jean Auguste Dominique Ingres Napoleon Imperial Throne'
        ]
    },
    # 3. 提香 - 劫夺欧罗巴
    {
        'id': 'titian_rape_of_europa',
        'title': '劫夺欧罗巴 (1562)',
        'enTitle': 'The Rape of Europa',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Color does not make a picture; it gives it breath.”',
        'quoteAuthor': '— Titian',
        'queries': [
            'The Rape of Europa Titian Google Art Project',
            'Titian Rape of Europa Isabella Stewart Gardner',
            'The Rape of Europa Titian'
        ]
    },
    # 4. 提香 - 维纳斯与阿多尼斯
    {
        'id': 'titian_venus_and_adonis',
        'title': '维纳斯与阿多尼斯 (1554)',
        'enTitle': 'Venus and Adonis',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“A good painter needs only three colors: black, white and red.”',
        'quoteAuthor': '— Titian',
        'queries': [
            'Venus y Adonis Tiziano Prado',
            'Venus and Adonis Titian Prado Google Art Project',
            'Titian Venus and Adonis'
        ]
    },
    # 5. 波提切利 - 战神与维纳斯
    {
        'id': 'botticelli_venus_and_mars',
        'title': '战神与维纳斯 (1485)',
        'enTitle': 'Venus and Mars',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is poetry that is seen rather than felt.”',
        'quoteAuthor': '— Sandro Botticelli',
        'queries': [
            'Sandro Botticelli - Venus and Mars - Google Art Project',
            'Botticelli Venus and Mars National Gallery',
            'Venus and Mars Botticelli'
        ]
    },
    # 6. 老彼得·勃鲁盖尔 - 伊卡洛斯的坠落
    {
        'id': 'bruegel_fall_of_icarus',
        'title': '伊卡洛斯的坠落 (1560)',
        'enTitle': 'Landscape with the Fall of Icarus',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature herself is the greatest book of divine wonders.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'queries': [
            'Landscape with the Fall of Icarus Bruegel',
            'Pieter Bruegel de Oude - De val van Icarus',
            'Fall of Icarus Bruegel'
        ]
    },
    # 7. 丁托列托 - 勒达与天鹅
    {
        'id': 'tintoretto_leda_and_the_swan',
        'title': '勒达与天鹅 (1550)',
        'enTitle': 'Leda and the Swan',
        'artist': 'Tintoretto (丁托列托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The drawing of Michelangelo, the color of Titian.”',
        'quoteAuthor': '— Tintoretto',
        'queries': [
            'Tintoretto - Leda and the Swan - Google Art Project',
            'Tintoretto Leda and the Swan Uffizi',
            'Leda and the Swan Tintoretto'
        ]
    },
    # 8. 卡拉瓦乔 - 水仙少年纳喀索斯
    {
        'id': 'caravaggio_narcissus',
        'title': '水仙少年纳喀索斯 (1599)',
        'enTitle': 'Narcissus',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“All works are nothing but childish trifles unless painted from life.”',
        'quoteAuthor': '— Caravaggio',
        'queries': [
            'Narcissus Caravaggio Barberini Google Art Project',
            'Narcissus-Caravaggio edited',
            'Caravaggio Narcissus'
        ]
    },
    # 9. 伦勃朗 - 达那厄
    {
        'id': 'rembrandt_danae',
        'title': '达那厄 (1636)',
        'enTitle': 'Danaë',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is the grandchild of nature; it is related to the divine.”',
        'quoteAuthor': '— Rembrandt',
        'queries': [
            'Rembrandt Harmensz. van Rijn - Danaë - Google Art Project',
            'Danae Rembrandt Hermitage',
            'Rembrandt Danae'
        ]
    },
    # 10. 鲁本斯 - 帕里斯的裁判
    {
        'id': 'rubens_judgement_of_paris',
        'title': '帕里斯的裁判 (1636)',
        'enTitle': 'The Judgement of Paris',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no undertaking has ever surpassed my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'queries': [
            'The Judgement of Paris - Peter Paul Rubens - Google Art Project',
            'Rubens Judgement of Paris National Gallery',
            'The Judgement of Paris Rubens'
        ]
    },
    # 11. 鲁本斯 - 被缚的普罗米修斯
    {
        'id': 'rubens_prometheus_bound',
        'title': '被缚的普罗米修斯 (1612)',
        'enTitle': 'Prometheus Bound',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Every impression of color is an illusion created by light.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'queries': [
            'Peter Paul Rubens and Frans Snyders - Prometheus Bound - Google Art Project',
            'Rubens Prometheus Bound Philadelphia Museum of Art',
            'Prometheus Bound Rubens'
        ]
    },
    # 12. 鲁本斯 - 珀耳修斯拯救安德洛墨达
    {
        'id': 'rubens_perseus_and_andromeda',
        'title': '珀耳修斯拯救安德洛墨达 (1622)',
        'enTitle': 'Perseus Freeing Andromeda',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“I confess that I am by natural instinct better fitted to execute very large works.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'queries': [
            'Peter Paul Rubens - Perseus and Andromeda - Google Art Project',
            'Rubens Perseus and Andromeda Hermitage',
            'Perseus and Andromeda Rubens'
        ]
    },
    # 13. 委拉斯凯兹 - 火神的锻造厂
    {
        'id': 'velazquez_apollo_forge_of_vulcan',
        'title': '火神的锻造厂 (1630)',
        'enTitle': 'Apollo in the Forge of Vulcan',
        'artist': 'Diego Velázquez (委拉斯凯兹)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“I would rather be the first painter of common things than the second in higher art.”',
        'quoteAuthor': '— Diego Velázquez',
        'queries': [
            'Apolo en la Fragua de Vulcano Diego Velázquez',
            'Velazquez Apollo in the Forge of Vulcan Prado',
            'Apollo in the Forge of Vulcan Velazquez'
        ]
    },
    # 14. 普桑 - 阿波罗与达芙妮
    {
        'id': 'poussin_apollo_and_daphne',
        'title': '阿波罗与达芙妮 (1664)',
        'enTitle': 'Apollo and Daphne',
        'artist': 'Nicolas Poussin (普桑)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is nothing but the imitation of human actions.”',
        'quoteAuthor': '— Nicolas Poussin',
        'queries': [
            'Apollo and Daphne Nicolas Poussin Louvre',
            'Apollo and Daphne Poussin INV7307',
            'Poussin Apollo and Daphne'
        ]
    },
    # 15. 布歇 - 狄安娜出浴
    {
        'id': 'boucher_diana_leaving_her_bath',
        'title': '狄安娜出浴 (1742)',
        'enTitle': 'Diana Leaving Her Bath',
        'artist': 'François Boucher (布歇)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Art breathes life into graceful moments that time cannot erase.”',
        'quoteAuthor': '— François Boucher',
        'queries': [
            'François Boucher - Diane sortant du bain - Google Art Project',
            'Boucher Diana Leaving her Bath Louvre',
            'Diane sortant du bain Boucher'
        ]
    },
    # 16. 热拉尔 - 丘比特与普赛克
    {
        'id': 'gerard_cupid_and_psyche',
        'title': '丘比特与普赛克 (1798)',
        'enTitle': 'Cupid and Psyche',
        'artist': 'François Gérard (弗朗索瓦·热拉尔)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Beauty is the harmony of reason, passion and grace.”',
        'quoteAuthor': '— François Gérard',
        'queries': [
            'François Gérard - Cupid and Psyche - Google Art Project',
            'Francois Gerard Cupid and Psyche Louvre',
            'Cupid and Psyche Gerard Louvre'
        ]
    },
    # 17. 安格尔 - 俄狄浦斯与斯芬克斯
    {
        'id': 'ingres_oedipus_and_sphinx',
        'title': '俄狄浦斯与斯芬克斯 (1808)',
        'enTitle': 'Oedipus and the Sphinx',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“To draw does not simply mean to reproduce contours; drawing does not consist merely of lines.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres',
        'queries': [
            'Jean Auguste Dominique Ingres - Oedipus and the Sphinx - Google Art Project',
            'Ingres Oedipus and the Sphinx Louvre',
            'Oedipus and the Sphinx Ingres'
        ]
    },
    # 18. 安格尔 - 朱庇特与忒提斯
    {
        'id': 'ingres_jupiter_and_thetis',
        'title': '朱庇特与忒提斯 (1811)',
        'enTitle': 'Jupiter and Thetis',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“There is no grace without strength.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres',
        'queries': [
            'Ingres Jupiter et Thétis',
            'Jupiter and Thetis Ingres Granet',
            'Ingres Jupiter and Thetis'
        ]
    },
    # 19. 柯罗 - 俄耳甫斯引领欧律狄刻走出冥界
    {
        'id': 'corot_orpheus_leading_eurydice',
        'title': '俄耳甫斯引领欧律狄刻走出冥界 (1861)',
        'enTitle': 'Orpheus Leading Eurydice from the Underworld',
        'artist': 'Jean-Baptiste-Camille Corot (柯罗)',
        'category': 'realism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Beauty in art is truth bathed in an impression received from nature.”',
        'quoteAuthor': '— Jean-Baptiste-Camille Corot',
        'queries': [
            'Jean-Baptiste-Camille Corot - Orpheus Leading Eurydice from the Underworld - 1984.629 - Metropolitan Museum of Art',
            'Corot Orpheus Leading Eurydice Metropolitan Museum',
            'Orpheus Leading Eurydice Corot'
        ]
    },
    # 20. 布格罗 - 普赛克的诱拐
    {
        'id': 'bouguereau_abduction_of_psyche',
        'title': '普赛克的诱拐 (1895)',
        'enTitle': 'The Abduction of Psyche',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“There is only one art: it is that of showing the ideal.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'queries': [
            'William-Adolphe Bouguereau (1825-1905) - The Abduction of Psyche (1895)',
            'Bouguereau The Abduction of Psyche',
            'The Abduction of Psyche Bouguereau'
        ]
    },
    # 21. 沃特豪斯 - 奥德修斯与塞壬
    {
        'id': 'waterhouse_ulysses_and_the_sirens',
        'title': '奥德修斯与塞壬 (1891)',
        'enTitle': 'Ulysses and the Sirens',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Mythology is poetry dressed in the living colors of the soul.”',
        'quoteAuthor': '— John William Waterhouse',
        'queries': [
            'John William Waterhouse - Ulysses and the Sirens (1891)',
            'Waterhouse Ulysses and the Sirens NGV',
            'Ulysses and the Sirens Waterhouse'
        ]
    },
    # 22. 沃特豪斯 - 回声与水仙花
    {
        'id': 'waterhouse_echo_and_narcissus',
        'title': '回声与水仙花 (1903)',
        'enTitle': 'Echo and Narcissus',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“I paint what I dream, for dreams hold the deepest truths.”',
        'quoteAuthor': '— John William Waterhouse',
        'queries': [
            'John William Waterhouse - Echo and Narcissus - Google Art Project',
            'Waterhouse Echo and Narcissus Walker Art Gallery',
            'Echo and Narcissus Waterhouse'
        ]
    }
]

def search_wikimedia_commons(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=8"
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return [x['title'] for x in data.get('query', {}).get('search', [])]
        except Exception as e:
            time.sleep(1.5)
    return []

def get_image_info(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for pid, pdata in pages.items():
                    if 'imageinfo' in pdata:
                        ii = pdata['imageinfo'][0]
                        u = ii.get('thumburl') if ('thumburl' in ii and ii['width'] > 3840) else ii['url']
                        return u, ii['width'], ii['height']
        except Exception as e:
            time.sleep(1.5)
    return None, 0, 0

def download_and_save(url, target_path, max_dim=3840):
    tmp_path = target_path + ".tmp"
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                with open(tmp_path, 'wb') as f:
                    f.write(resp.read())
            break
        except Exception as e:
            time.sleep(2.0)
    else:
        return False, "Download failed after 3 attempts"

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
        return True, f"Saved ({w}x{h} -> {im.size[0]}x{im.size[1]})"
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False, f"Image processing error: {e}"

def main():
    print(f"==================================================")
    print(f"🎯 开始收集 22 幅传世名画（摩西、拿破仑与20幅希腊神话油画）")
    print(f"==================================================")
    
    harvest_results = []
    
    for idx, t in enumerate(TASKS, 1):
        item_id = t['id']
        title_cn = t['title']
        target_path = os.path.join(images_dir, f"{item_id}.jpg")
        print(f"\n[{idx}/{len(TASKS)}] 正在收集: {item_id} | {title_cn}")
        
        # 如果已经存在且大小合规，可先检查
        if os.path.exists(target_path) and os.path.getsize(target_path) > 100000:
            try:
                with Image.open(target_path) as im:
                    w, h = im.size
                    if max(w, h) >= 1200:
                        print(f"  ⚡ 已存在高质量本地原图: {w}x{h} ({os.path.getsize(target_path)//1024} KB)")
                        t_copy = dict(t)
                        t_copy['file'] = f"{item_id}.jpg"
                        t_copy['src'] = f"assets/images/{item_id}.jpg?v=4.3.0"
                        t_copy['search'] = f"{t['artist']} {t['enTitle']}"
                        harvest_results.append(t_copy)
                        continue
            except Exception:
                pass

        success = False
        for q in t['queries']:
            print(f"  🔍 检索 Commons: '{q}'...")
            titles = search_wikimedia_commons(q)
            for title in titles:
                t_low = title.lower()
                if any(bad in t_low for bad in ['frame', 'gallery', 'room', 'museum photo', '.pdf', 'detail', 'bw.jpg', 'black and white']):
                    continue
                url, w, h = get_image_info(title)
                if url and max(w, h) >= 1200:
                    print(f"    🎯 找到优质母带: {title} ({w}x{h})")
                    ok, msg = download_and_save(url, target_path)
                    if ok:
                        print(f"    ✅ 成功下载并优化: {msg}")
                        success = True
                        t_copy = dict(t)
                        t_copy['file'] = f"{item_id}.jpg"
                        t_copy['src'] = f"assets/images/{item_id}.jpg?v=4.3.0"
                        t_copy['search'] = f"{t['artist']} {t['enTitle']}"
                        harvest_results.append(t_copy)
                        break
                    else:
                        print(f"    ❌ 下载处理失败: {msg}")
            if success:
                break
            time.sleep(1.0)
            
        if not success:
            print(f"  ⚠️ 未能自动获取该画作母带: {item_id}")

    res_path = os.path.join(base_dir, 'scripts', 'harvested_22_results.json')
    with open(res_path, 'w', encoding='utf-8') as f:
        json.dump(harvest_results, f, ensure_ascii=False, indent=2)
    print(f"\n==================================================")
    print(f"🎉 收集完成: 成功 {len(harvest_results)} / {len(TASKS)}")
    print(f"元数据已写入: {res_path}")

if __name__ == '__main__':
    main()
