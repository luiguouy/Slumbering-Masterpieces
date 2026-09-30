import os
import json
import re
from PIL import Image

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')
masterpieces_js_path = os.path.join(data_dir, 'masterpieces.js')
images_dir = os.path.join(base_dir, 'assets', 'images')
index_html_path = os.path.join(base_dir, 'index.html')

NEW_22_ARTWORKS = [
    # 1. 摩西在西奈山领受律法
    {
        "id": "gerome_moses_mount_sinai",
        "title": "摩西在西奈山领受律法 (1895)",
        "enTitle": "Moses on Mount Sinai",
        "artist": "Jean-Léon Gérôme (让-莱昂·热罗姆)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“Art is a severe mistress, who demands all of one’s mind and soul.”",
        "quoteAuthor": "— Jean-Léon Gérôme",
        "search": "Jean-Léon Gérôme Moses on Mount Sinai",
        "file": "gerome_moses_mount_sinai.jpg",
        "src": "assets/images/gerome_moses_mount_sinai.jpg?v=4.3.0"
    },
    # 2. 王座上的拿破仑一世
    {
        "id": "ingres_napoleon_on_his_imperial_throne",
        "title": "王座上的拿破仑一世 (1806)",
        "enTitle": "Napoleon I on His Imperial Throne",
        "artist": "Jean-Auguste-Dominique Ingres (安格尔)",
        "category": "romanticism",
        "genre": "⚔️ 历史故事",
        "quote": "“Drawing includes everything except the tint.”",
        "quoteAuthor": "— Jean-Auguste-Dominique Ingres",
        "search": "Jean-Auguste-Dominique Ingres Napoleon I on His Imperial Throne",
        "file": "ingres_napoleon_on_his_imperial_throne.jpg",
        "src": "assets/images/ingres_napoleon_on_his_imperial_throne.jpg?v=4.3.0"
    },
    # 3. 提香 - 劫夺欧罗巴
    {
        "id": "titian_rape_of_europa",
        "title": "劫夺欧罗巴 (1562)",
        "enTitle": "The Rape of Europa",
        "artist": "Titian (提香)",
        "category": "renaissance",
        "genre": "🏛️ 神话宗教",
        "quote": "“Color does not make a picture; it gives it breath.”",
        "quoteAuthor": "— Titian",
        "search": "Titian The Rape of Europa Isabella Stewart Gardner Museum",
        "file": "titian_rape_of_europa.jpg",
        "src": "assets/images/titian_rape_of_europa.jpg?v=4.3.0"
    },
    # 4. 提香 - 维纳斯与阿多尼斯
    {
        "id": "titian_venus_and_adonis",
        "title": "维纳斯与阿多尼斯 (1554)",
        "enTitle": "Venus and Adonis",
        "artist": "Titian (提香)",
        "category": "renaissance",
        "genre": "🏛️ 神话宗教",
        "quote": "“A good painter needs only three colors: black, white and red.”",
        "quoteAuthor": "— Titian",
        "search": "Titian Venus and Adonis Prado Museum",
        "file": "titian_venus_and_adonis.jpg",
        "src": "assets/images/titian_venus_and_adonis.jpg?v=4.3.0"
    },
    # 5. 波提切利 - 战神与维纳斯
    {
        "id": "botticelli_venus_and_mars",
        "title": "战神与维纳斯 (1485)",
        "enTitle": "Venus and Mars",
        "artist": "Sandro Botticelli (波提切利)",
        "category": "renaissance",
        "genre": "🏛️ 神话宗教",
        "quote": "“Painting is poetry that is seen rather than felt.”",
        "quoteAuthor": "— Sandro Botticelli",
        "search": "Sandro Botticelli Venus and Mars National Gallery London",
        "file": "botticelli_venus_and_mars.jpg",
        "src": "assets/images/botticelli_venus_and_mars.jpg?v=4.3.0"
    },
    # 6. 老彼得·勃鲁盖尔 - 伊卡洛斯的坠落
    {
        "id": "bruegel_fall_of_icarus",
        "title": "伊卡洛斯的坠落 (1560)",
        "enTitle": "Landscape with the Fall of Icarus",
        "artist": "Pieter Bruegel the Elder (老彼得·勃鲁盖尔)",
        "category": "renaissance",
        "genre": "🏛️ 神话宗教",
        "quote": "“Nature herself is the greatest book of divine wonders.”",
        "quoteAuthor": "— Pieter Bruegel the Elder",
        "search": "Pieter Bruegel Landscape with the Fall of Icarus",
        "file": "bruegel_fall_of_icarus.jpg",
        "src": "assets/images/bruegel_fall_of_icarus.jpg?v=4.3.0"
    },
    # 7. 科雷吉欧 - 勒达与天鹅
    {
        "id": "correggio_leda_and_the_swan",
        "title": "勒达与天鹅 (1532)",
        "enTitle": "Leda and the Swan",
        "artist": "Correggio (科雷吉欧)",
        "category": "renaissance",
        "genre": "🏛️ 神话宗教",
        "quote": "“Light and shadow are the soul of all living art.”",
        "quoteAuthor": "— Correggio",
        "search": "Correggio Leda and the Swan Gemäldegalerie Berlin",
        "file": "correggio_leda_and_the_swan.jpg",
        "src": "assets/images/correggio_leda_and_the_swan.jpg?v=4.3.0"
    },
    # 8. 卡拉瓦乔 - 水仙少年纳喀索斯
    {
        "id": "caravaggio_narcissus",
        "title": "水仙少年纳喀索斯 (1599)",
        "enTitle": "Narcissus",
        "artist": "Caravaggio (卡拉瓦乔)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“All works are nothing but childish trifles unless painted from life.”",
        "quoteAuthor": "— Caravaggio",
        "search": "Caravaggio Narcissus Palazzo Barberini Rome",
        "file": "caravaggio_narcissus.jpg",
        "src": "assets/images/caravaggio_narcissus.jpg?v=4.3.0"
    },
    # 9. 伦勃朗 - 达那厄
    {
        "id": "rembrandt_danae",
        "title": "达那厄 (1636)",
        "enTitle": "Danaë",
        "artist": "Rembrandt (伦勃朗)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“Painting is the grandchild of nature; it is related to the divine.”",
        "quoteAuthor": "— Rembrandt",
        "search": "Rembrandt Danae Hermitage Museum",
        "file": "rembrandt_danae.jpg",
        "src": "assets/images/rembrandt_danae.jpg?v=4.3.0"
    },
    # 10. 鲁本斯 - 帕里斯的裁判
    {
        "id": "rubens_judgement_of_paris",
        "title": "帕里斯的裁判 (1636)",
        "enTitle": "The Judgement of Paris",
        "artist": "Peter Paul Rubens (鲁本斯)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“My talent is such that no undertaking has ever surpassed my courage.”",
        "quoteAuthor": "— Peter Paul Rubens",
        "search": "Peter Paul Rubens The Judgement of Paris National Gallery London",
        "file": "rubens_judgement_of_paris.jpg",
        "src": "assets/images/rubens_judgement_of_paris.jpg?v=4.3.0"
    },
    # 11. 鲁本斯 - 被缚的普罗米修斯
    {
        "id": "rubens_prometheus_bound",
        "title": "被缚的普罗米修斯 (1612)",
        "enTitle": "Prometheus Bound",
        "artist": "Peter Paul Rubens (鲁本斯)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“Every impression of color is an illusion created by light.”",
        "quoteAuthor": "— Peter Paul Rubens",
        "search": "Peter Paul Rubens Prometheus Bound Philadelphia Museum of Art",
        "file": "rubens_prometheus_bound.jpg",
        "src": "assets/images/rubens_prometheus_bound.jpg?v=4.3.0"
    },
    # 12. 鲁本斯 - 珀耳修斯拯救安德洛墨达
    {
        "id": "rubens_perseus_and_andromeda",
        "title": "珀耳修斯拯救安德洛墨达 (1622)",
        "enTitle": "Perseus Freeing Andromeda",
        "artist": "Peter Paul Rubens (鲁本斯)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“I confess that I am by natural instinct better fitted to execute very large works.”",
        "quoteAuthor": "— Peter Paul Rubens",
        "search": "Peter Paul Rubens Perseus and Andromeda Hermitage Museum",
        "file": "rubens_perseus_and_andromeda.jpg",
        "src": "assets/images/rubens_perseus_and_andromeda.jpg?v=4.3.0"
    },
    # 13. 委拉斯凯兹 - 火神的锻造厂
    {
        "id": "velazquez_apollo_forge_of_vulcan",
        "title": "火神的锻造厂 (1630)",
        "enTitle": "Apollo in the Forge of Vulcan",
        "artist": "Diego Velázquez (委拉斯凯兹)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“I would rather be the first painter of common things than the second in higher art.”",
        "quoteAuthor": "— Diego Velázquez",
        "search": "Diego Velázquez Apollo in the Forge of Vulcan Prado Museum",
        "file": "velazquez_apollo_forge_of_vulcan.jpg",
        "src": "assets/images/velazquez_apollo_forge_of_vulcan.jpg?v=4.3.0"
    },
    # 14. 普桑 - 阿波罗与达芙妮
    {
        "id": "poussin_apollo_and_daphne",
        "title": "阿波罗与达芙妮 (1664)",
        "enTitle": "Apollo and Daphne",
        "artist": "Nicolas Poussin (普桑)",
        "category": "baroque",
        "genre": "🏛️ 神话宗教",
        "quote": "“Painting is nothing but the imitation of human actions.”",
        "quoteAuthor": "— Nicolas Poussin",
        "search": "Nicolas Poussin Apollo and Daphne Louvre Museum",
        "file": "poussin_apollo_and_daphne.jpg",
        "src": "assets/images/poussin_apollo_and_daphne.jpg?v=4.3.0"
    },
    # 15. 布歇 - 狄安娜出浴
    {
        "id": "boucher_diana_leaving_her_bath",
        "title": "狄安娜出浴 (1742)",
        "enTitle": "Diana Leaving Her Bath",
        "artist": "François Boucher (布歇)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“Art breathes life into graceful moments that time cannot erase.”",
        "quoteAuthor": "— François Boucher",
        "search": "François Boucher Diana Leaving Her Bath Louvre Museum",
        "file": "boucher_diana_leaving_her_bath.jpg",
        "src": "assets/images/boucher_diana_leaving_her_bath.jpg?v=4.3.0"
    },
    # 16. 热拉尔 - 丘比特与普赛克
    {
        "id": "gerard_cupid_and_psyche",
        "title": "丘比特与普赛克 (1798)",
        "enTitle": "Cupid and Psyche",
        "artist": "François Gérard (弗朗索瓦·热拉尔)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“Beauty is the harmony of reason, passion and grace.”",
        "quoteAuthor": "— François Gérard",
        "search": "François Gérard Cupid and Psyche Louvre Museum",
        "file": "gerard_cupid_and_psyche.jpg",
        "src": "assets/images/gerard_cupid_and_psyche.jpg?v=4.3.0"
    },
    # 17. 安格尔 - 俄狄浦斯与斯芬克斯
    {
        "id": "ingres_oedipus_and_sphinx",
        "title": "俄狄浦斯与斯芬克斯 (1808)",
        "enTitle": "Oedipus and the Sphinx",
        "artist": "Jean-Auguste-Dominique Ingres (安格尔)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“To draw does not simply mean to reproduce contours; drawing does not consist merely of lines.”",
        "quoteAuthor": "— Jean-Auguste-Dominique Ingres",
        "search": "Jean-Auguste-Dominique Ingres Oedipus and the Sphinx Louvre",
        "file": "ingres_oedipus_and_sphinx.jpg",
        "src": "assets/images/ingres_oedipus_and_sphinx.jpg?v=4.3.0"
    },
    # 18. 安格尔 - 朱庇特与忒提斯
    {
        "id": "ingres_jupiter_and_thetis",
        "title": "朱庇特与忒提斯 (1811)",
        "enTitle": "Jupiter and Thetis",
        "artist": "Jean-Auguste-Dominique Ingres (安格尔)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“There is no grace without strength.”",
        "quoteAuthor": "— Jean-Auguste-Dominique Ingres",
        "search": "Jean-Auguste-Dominique Ingres Jupiter and Thetis Granet Museum",
        "file": "ingres_jupiter_and_thetis.jpg",
        "src": "assets/images/ingres_jupiter_and_thetis.jpg?v=4.3.0"
    },
    # 19. 柯罗 - 俄耳甫斯引领欧律狄刻走出冥界
    {
        "id": "corot_orpheus_leading_eurydice",
        "title": "俄耳甫斯引领欧律狄刻走出冥界 (1861)",
        "enTitle": "Orpheus Leading Eurydice from the Underworld",
        "artist": "Jean-Baptiste-Camille Corot (柯罗)",
        "category": "realism",
        "genre": "🏛️ 神话宗教",
        "quote": "“Beauty in art is truth bathed in an impression received from nature.”",
        "quoteAuthor": "— Jean-Baptiste-Camille Corot",
        "search": "Jean-Baptiste-Camille Corot Orpheus Leading Eurydice Metropolitan Museum",
        "file": "corot_orpheus_leading_eurydice.jpg",
        "src": "assets/images/corot_orpheus_leading_eurydice.jpg?v=4.3.0"
    },
    # 20. 布格罗 - 维纳斯的诞生
    {
        "id": "bouguereau_birth_of_venus",
        "title": "维纳斯的诞生 (1879)",
        "enTitle": "The Birth of Venus",
        "artist": "William-Adolphe Bouguereau (布格罗)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“There is only one art: it is that of showing the ideal.”",
        "quoteAuthor": "— William-Adolphe Bouguereau",
        "search": "William-Adolphe Bouguereau The Birth of Venus Musée d'Orsay",
        "file": "bouguereau_birth_of_venus.jpg",
        "src": "assets/images/bouguereau_birth_of_venus.jpg?v=4.3.0"
    },
    # 21. 沃特豪斯 - 奥德修斯与塞壬
    {
        "id": "waterhouse_ulysses_and_the_sirens",
        "title": "奥德修斯与塞壬 (1891)",
        "enTitle": "Ulysses and the Sirens",
        "artist": "John William Waterhouse (沃特豪斯)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“Mythology is poetry dressed in the living colors of the soul.”",
        "quoteAuthor": "— John William Waterhouse",
        "search": "John William Waterhouse Ulysses and the Sirens NGV Melbourne",
        "file": "waterhouse_ulysses_and_the_sirens.jpg",
        "src": "assets/images/waterhouse_ulysses_and_the_sirens.jpg?v=4.3.0"
    },
    # 22. 沃特豪斯 - 回声与水仙花
    {
        "id": "waterhouse_echo_and_narcissus",
        "title": "回声与水仙花 (1903)",
        "enTitle": "Echo and Narcissus",
        "artist": "John William Waterhouse (沃特豪斯)",
        "category": "romanticism",
        "genre": "🏛️ 神话宗教",
        "quote": "“I paint what I dream, for dreams hold the deepest truths.”",
        "quoteAuthor": "— John William Waterhouse",
        "search": "John William Waterhouse Echo and Narcissus Walker Art Gallery",
        "file": "waterhouse_echo_and_narcissus.jpg",
        "src": "assets/images/waterhouse_echo_and_narcissus.jpg?v=4.3.0"
    }
]

def main():
    print("Reading masterpieces.js...", flush=True)
    with open(masterpieces_js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract window.MASTERPIECES
    m = re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', content, re.DOTALL)
    if not m:
        raise Exception("Could not find window.MASTERPIECES in masterpieces.js")

    current_masterpieces = json.loads(m.group(1))
    print(f"Current count: {len(current_masterpieces)}", flush=True)

    existing_ids = {x['id'] for x in current_masterpieces}
    
    # 过滤与校验新画作
    to_add = []
    for it in NEW_22_ARTWORKS:
        if it['id'] in existing_ids:
            print(f"  Warning: ID {it['id']} already exists, skipping.", flush=True)
            continue
        # 验证图片文件是否存在且有效
        img_p = os.path.join(images_dir, it['file'])
        if not os.path.exists(img_p):
            raise Exception(f"Missing image file: {img_p}")
        try:
            with Image.open(img_p) as im:
                w, h = im.size
                if max(w, h) < 1000:
                    print(f"  Warning: resolution {w}x{h} might be small for {it['id']}", flush=True)
        except Exception as e:
            raise Exception(f"Corrupt image file {img_p}: {e}")
        to_add.append(it)

    print(f"Adding {len(to_add)} new masterpieces...", flush=True)
    
    # 将画作按 category 分组插入
    categories_order = [
        "renaissance",
        "baroque",
        "romanticism",
        "realism",
        "monet",
        "impressionism",
        "post_impressionism",
        "expressionism"
    ]

    grouped_artworks = {c: [] for c in categories_order}
    for item in current_masterpieces:
        c = item.get('category', 'renaissance')
        if c in grouped_artworks:
            grouped_artworks[c].append(item)
        else:
            grouped_artworks['renaissance'].append(item)

    for item in to_add:
        c = item.get('category', 'romanticism')
        if c in grouped_artworks:
            grouped_artworks[c].append(item)
        else:
            grouped_artworks['romanticism'].append(item)

    final_masterpieces = []
    category_counts = {}
    for c in categories_order:
        items = grouped_artworks[c]
        # 按标题排序保持整洁
        items.sort(key=lambda x: x.get('artist', '') + x.get('title', ''))
        category_counts[c] = len(items)
        final_masterpieces.extend(items)

    total_count = len(final_masterpieces)
    print(f"New total count: {total_count}", flush=True)
    for c, cnt in category_counts.items():
        print(f"  Category '{c}': {cnt} artworks", flush=True)

    # 重构 ART_CATEGORIES
    categories_meta = [
        {"id": "renaissance", "name": "🏛️ 文艺复兴与北方画派 (Renaissance & Northern Masters)", "count": category_counts['renaissance']},
        {"id": "baroque", "name": "🎭 巴洛克与荷兰黄金时代 (Baroque & Dutch Golden Age)", "count": category_counts['baroque']},
        {"id": "romanticism", "name": "⚡ 新古典、洛可可与浪漫主义 (Neoclassicism & Romanticism)", "count": category_counts['romanticism']},
        {"id": "realism", "name": "🌾 写实主义与巡回展览画派 (Realism & Wanderers)", "count": category_counts['realism']},
        {"id": "monet", "name": "🌟 克劳德·莫奈专题特辑 (Claude Monet Collection)", "count": category_counts['monet']},
        {"id": "impressionism", "name": "🎨 印象派巅峰盛宴 (Impressionism Masters)", "count": category_counts['impressionism']},
        {"id": "post_impressionism", "name": "🌻 后印象派三杰与现代先驱 (Post-Impressionism)", "count": category_counts['post_impressionism']},
        {"id": "expressionism", "name": "🌌 象征主义与表现主义 (Symbolism & Expressionism)", "count": category_counts['expressionism']}
    ]

    # 生成规范美观的 masterpieces.js
    header = f"""/**
 * Slumbering Masterpieces · World Fine Art Collection
 * 全球世界级传世名画博览馆数据库（共 {total_count} 幅殿堂级油画旷世杰作）
 */

window.ART_CATEGORIES = {json.dumps(categories_meta, ensure_ascii=False, indent=4)};

window.MASTERPIECES = {json.dumps(final_masterpieces, ensure_ascii=False, indent=4)};
"""
    with open(masterpieces_js_path, 'w', encoding='utf-8') as f:
        f.write(header)
    print(f"Updated {masterpieces_js_path} successfully!", flush=True)

    # 更新 index.html 中的数量
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = re.sub(r'1\s*/\s*\d+', f'1 / {total_count}', html)
    html = re.sub(r'World Masterpieces · \d+ 幅传世杰作', f'World Masterpieces · {total_count} 幅传世杰作', html)

    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {index_html_path} successfully!", flush=True)

    # 输出清单文件以备审计
    audit_file = os.path.join(base_dir, 'scripts', 'all_artworks_list.txt')
    with open(audit_file, 'w', encoding='utf-8') as f:
        f.write(f"Total: {total_count}\n")
        for i, item in enumerate(final_masterpieces, 1):
            f.write(f"{i:03d} | {item['id']:<40} | 《{item['title']}》 | {item['genre']} | {item['category']}\n")
    print(f"Updated {audit_file} successfully!", flush=True)

if __name__ == '__main__':
    main()
