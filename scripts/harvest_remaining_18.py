import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fast_harvest_engine as fhe

REMAINING_18 = [
    {
        'id': 'el_greco_view_of_toledo',
        'title': '托莱多全景 · 暴风雨中的圣城 (1600)',
        'enTitle': 'View of Toledo',
        'artist': 'El Greco (埃尔·格列柯)',
        'category': 'renaissance',
        'genre': '🌊 自然风景',
        'quote': '“The heavens split open in silent storm.”',
        'quoteAuthor': '— El Greco',
        'search': 'El Greco View of Toledo Metropolitan Museum of Art'
    },
    {
        'id': 'rubens_elevation_of_the_cross',
        'title': '上十字架 (1610)',
        'enTitle': 'The Elevation of the Cross',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no enterprise has exceeded my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Peter Paul Rubens Raising of the Cross 1610'
    },
    {
        'id': 'rubens_assumption_of_the_virgin_nga',
        'title': '圣母升天 (1626)',
        'enTitle': 'The Assumption of the Virgin',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Cherubs and golden light bridge the world to heaven.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Peter Paul Rubens The Assumption of the Virgin NGA'
    },
    {
        'id': 'claude_lorrain_embarkation_queen_sheba',
        'title': '示巴女王登舟 · 圣城港湾朝霞 (1648)',
        'enTitle': 'The Embarkation of the Queen of Sheba',
        'artist': 'Claude Lorrain (克劳德·洛兰)',
        'category': 'baroque',
        'genre': '🌊 自然风景',
        'quote': '“The sunrise speaks of kingdoms not yet born.”',
        'quoteAuthor': '— Claude Lorrain',
        'search': 'Claude Lorrain Seaport with the Embarkation of the Queen of Sheba'
    },
    {
        'id': 'murillo_immaculate_conception_los_venerables',
        'title': '无原罪始胎 (1678)',
        'enTitle': 'The Immaculate Conception of Los Venerables',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'search': 'Murillo The Immaculate Conception Prado'
    },
    {
        'id': 'tiepolo_the_immaculate_conception',
        'title': '无玷圣母降临 (1768)',
        'enTitle': 'The Immaculate Conception (Tiepolo)',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Skies without end belong to the painter’s brush.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'search': 'Giovanni Battista Tiepolo The Immaculate Conception Prado'
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
        'search': 'William-Adolphe Bouguereau Song of the Angels'
    },
    {
        'id': 'bouguereau_pieta',
        'title': '哀悼基督 · 圣殇 (1876)',
        'enTitle': 'Pietà (Bouguereau)',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grief consecrated by divine light becomes immortal.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'search': 'William-Adolphe Bouguereau Pietà 1876'
    },
    {
        'id': 'holman_hunt_the_light_of_the_world',
        'title': '世界之光 (1853)',
        'enTitle': 'The Light of the World',
        'artist': 'William Holman Hunt (亨特)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Behold, I stand at the door and knock.”',
        'quoteAuthor': '— William Holman Hunt',
        'search': 'William Holman Hunt The Light of the World'
    },
    {
        'id': 'waterhouse_saint_cecilia',
        'title': '音乐的主保圣人 · 圣塞西莉亚 (1895)',
        'enTitle': 'Saint Cecilia',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“In heavenly melody, the soul finds its wings.”',
        'quoteAuthor': '— John William Waterhouse',
        'search': 'John William Waterhouse Saint Cecilia'
    },
    {
        'id': 'giotto_st_francis_birds',
        'title': '圣方济各向鸟儿布道 (1297)',
        'enTitle': 'Saint Francis Preaching to the Birds',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“All creatures are our sisters and brothers under the sun.”',
        'quoteAuthor': '— Giotto',
        'search': 'Giotto Saint Francis Receiving the Stigmata Louvre'
    },
    {
        'id': 'raphael_madonna_della_seggiola',
        'title': '椅中圣母 (1514)',
        'enTitle': 'Madonna della Seggiola',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“In motherly embrace dwells the quietest kingdom.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Madonna della Seggiola'
    },
    {
        'id': 'poussin_arcadian_shepherds_louvre',
        'title': '圣家族与圣伊丽莎白 (1650)',
        'enTitle': 'The Holy Family (Poussin)',
        'artist': 'Nicolas Poussin (普桑)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Order and light are the eternal guides.”',
        'quoteAuthor': '— Nicolas Poussin',
        'search': 'Nicolas Poussin The Holy Family Louvre'
    },
    {
        'id': 'caravaggio_the_entombment_of_christ',
        'title': '基督下葬 (1603)',
        'enTitle': 'The Entombment of Christ',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“All works are but bagatelles unless painted from nature.”',
        'quoteAuthor': '— Caravaggio',
        'search': 'Caravaggio The Entombment of Christ Vatican Pinacoteca'
    },
    {
        'id': 'rembrandt_simeon_in_the_temple',
        'title': '西面在圣殿中颂赞圣婴 (1631)',
        'enTitle': 'Simeon in the Temple',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Lord, now lettest thou thy servant depart in peace.”',
        'quoteAuthor': '— Rembrandt',
        'search': 'Rembrandt Simeon in the Temple Mauritshuis'
    },
    {
        'id': 'bruegel_adoration_of_the_kings',
        'title': '三王来朝 · 雪景朝圣 (1564)',
        'enTitle': 'The Adoration of the Kings (Bruegel)',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Folk wisdom speaks in the silent falling snow.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'search': 'Pieter Bruegel the Elder The Adoration of the Kings National Gallery'
    },
    {
        'id': 'veronese_the_annunciation',
        'title': '受胎告知 · 天堂之光 (1578)',
        'enTitle': 'The Annunciation (Veronese)',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Venetian skies glow with immortal dawn.”',
        'quoteAuthor': '— Paolo Veronese',
        'search': 'Paolo Veronese The Annunciation Gallerie dell\'Accademia'
    },
    {
        'id': 'zurbaran_the_immaculate_conception',
        'title': '幼年圣母与天使 (1632)',
        'enTitle': 'The Virgin Mary as a Child',
        'artist': 'Francisco de Zurbarán (苏巴朗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“In quiet devotion shines the purest light.”',
        'quoteAuthor': '— Francisco de Zurbarán',
        'search': 'Francisco de Zurbarán The Virgin Mary as a Child Metropolitan'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')

    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'r', encoding='utf-8') as f:
        existing_harvested = json.load(f)

    existing_ids = {x['id'] for x in existing_harvested}
    print(f"Already harvested: {len(existing_harvested)}. Target additional: {len(REMAINING_18)}")

    for i, item in enumerate(REMAINING_18):
        if item['id'] in existing_ids:
            continue
        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"\n[Additional {i+1}/{len(REMAINING_18)}] {item['title']} - {item['artist']}")

        c = fhe.find_best_commons_file(item['search'])
        if not c:
            print(f"  ❌ No file found for {item['search']}")
            time.sleep(2.0)
            continue

        print(f"  🎯 Found: {c['title']} (orig: {c['orig_w']}x{c['orig_h']})")
        # retry logic for 429
        downloaded = False
        for attempt in range(3):
            try:
                fhe.download_and_save(c['url'], save_path)
                downloaded = True
                break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}. Waiting 10s...")
                time.sleep(10.0)

        if downloaded and os.path.exists(save_path):
            ok, msg = fhe.inspect_image(save_path)
            print(f"  🔎 QualityGatekeeper: {msg}")
            if ok:
                item['file'] = fn
                item['src'] = f"assets/images/{fn}?v=3.8.0"
                existing_harvested.append(item)
                existing_ids.add(item['id'])
            else:
                os.remove(save_path)
        time.sleep(3.0)

    print(f"\n==========================================")
    print(f"TOTAL RELIGIOUS MASTERPIECES HARVESTED: {len(existing_harvested)}")
    print(f"==========================================")

    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'w', encoding='utf-8') as f:
        json.dump(existing_harvested, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
