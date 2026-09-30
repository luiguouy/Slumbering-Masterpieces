import urllib.request
import urllib.parse
import json
import os
import time

def search_gap(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=5"
    req = urllib.request.Request(url, headers={'User-Agent': 'ArtWebHighResGallery/4.0 (contact: admin@artweb.local)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return [r['title'] for r in data['query']['search']]
    except Exception as e:
        print(f"Search error for {query}: {e}")
        return []

def get_image_info(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'ArtWebHighResGallery/4.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        pages = data['query']['pages']
        for pid in pages:
            if 'imageinfo' in pages[pid]:
                ii = pages[pid]['imageinfo'][0]
                return {
                    'url': ii['url'],
                    'width': ii['width'],
                    'height': ii['height'],
                    'size': ii['size']
                }
    except Exception as e:
        print(f"Info error for {title}: {e}")
    return None

targets = [
    # 1. In-place high-res upgrades
    {
        'id': 'ingres_the_source',
        'type': 'upgrade',
        'file': 'ingres_the_source.jpg',
        'search': 'Jean Auguste Dominique Ingres - The Spring - Google Art Project 2.jpg'
    },
    {
        'id': 'ingres_la_grande_odalisque',
        'type': 'upgrade',
        'file': 'ingres_la_grande_odalisque.jpg',
        'search': 'Grande Odalisque Google Art Project'
    },
    {
        'id': 'raphael_sistine_madonna',
        'type': 'upgrade',
        'file': 'raphael_sistine_madonna.jpg',
        'search': 'Raphael - The Sistine Madonna - Google Arts & Culture.jpg'
    },
    {
        'id': 'degas_dancer_tilting',
        'type': 'upgrade',
        'file': 'degas_dancer_tilting.jpg',
        'search': 'Edgar Degas Swaying Dancer Dancer in Green Google Art Project'
    },
    {
        'id': 'monet_argenteuil',
        'type': 'upgrade',
        'file': 'monet_argenteuil.jpg',
        'search': 'Monet Artist Garden at Argenteuil Google Art Project'
    },
    {
        'id': 'monet_gladiolus',
        'type': 'upgrade',
        'file': 'monet_gladiolus.jpg',
        'search': 'Monet Gladioli Google Art Project'
    },
    {
        'id': 'monet_giverny_path',
        'type': 'upgrade',
        'file': 'monet_giverny_path.jpg',
        'search': 'Claude Monet - The Garden Path at Giverny'
    },
    {
        'id': 'monet_sainte_adresse',
        'type': 'upgrade',
        'file': 'monet_sainte_adresse.jpg',
        'search': 'Claude Monet Garden at Sainte-Adresse Google Art Project'
    },
    {
        'id': 'monet_argenteuil_basin',
        'type': 'upgrade',
        'file': 'monet_argenteuil_basin.jpg',
        'search': 'Claude Monet The Basin at Argenteuil Google Art Project'
    },
    {
        'id': 'vermeer_the_astronomer',
        'type': 'upgrade',
        'file': 'vermeer_the_astronomer.jpg',
        'search': 'Johannes Vermeer The Astronomer Google Art Project'
    },
    {
        'id': 'bruegel_tower_of_babel',
        'type': 'upgrade',
        'file': 'bruegel_tower_of_babel.jpg',
        'search': 'Pieter Bruegel the Elder The Tower of Babel Vienna Google Art Project'
    },

    # 2. Replacements for dull / colorless / dark artworks
    {
        'id': 'turner_the_grand_canal_venice',
        'replaces': 'turner_rain_steam_and_speed',
        'type': 'replace',
        'file': 'turner_the_grand_canal_venice.jpg',
        'title': '威尼斯大运河 (1835)',
        'enTitle': 'The Grand Canal, Venice',
        'artist': 'J. M. W. Turner (透纳)',
        'category': 'romanticism',
        'genre': '🌊 自然风景',
        'quote': '“Light is therefore colour.”',
        'quoteAuthor': '— J. M. W. Turner',
        'search': 'Turner The Grand Canal Venice Google Art Project'
    },
    {
        'id': 'sargent_carnation_lily_lily_rose',
        'replaces': 'whistler_mothers_portrait',
        'type': 'replace',
        'file': 'sargent_carnation_lily_lily_rose.jpg',
        'title': '康乃馨、百合与玫瑰 (1886)',
        'enTitle': 'Carnation, Lily, Lily, Rose',
        'artist': 'John Singer Sargent (约翰·辛格·萨金特)',
        'category': 'realism',
        'genre': '👤 人物肖像',
        'quote': '“You can’t do a sketch in enough color.”',
        'quoteAuthor': '— John Singer Sargent',
        'search': 'John Singer Sargent Carnation Lily Lily Rose Google Art Project'
    },
    {
        'id': 'monet_bouquet_of_sunflowers',
        'replaces': 'courbet_burial_at_ornans',
        'type': 'replace',
        'file': 'monet_bouquet_of_sunflowers.jpg',
        'title': '向日葵花束 (1881)',
        'enTitle': 'Bouquet of Sunflowers',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '💐 静物花卉',
        'quote': '“Color is my day-long obsession, joy and torment.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet - Bouquet of Sunflowers - Google Art Project.jpg'
    },
    {
        'id': 'pissarro_apple_picking_eragny',
        'replaces': 'corot_the_bridge_at_mantes',
        'type': 'replace',
        'file': 'pissarro_apple_picking_eragny.jpg',
        'title': '厄拉尼采苹果 (1888)',
        'enTitle': 'Apple Picking at Éragny',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌾 田园风光',
        'quote': '“Blessed are they who see beautiful things in humble places where other people see nothing.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro Apple Picking at Eragny Google Art Project'
    },
    {
        'id': 'titian_flora',
        'replaces': 'davinci_st_john_the_baptist',
        'type': 'replace',
        'file': 'titian_flora.jpg',
        'title': '花神弗洛拉 (1515)',
        'enTitle': 'Flora',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '👤 人物肖像',
        'quote': '“A good painter needs only three colours: black, white and red.”',
        'quoteAuthor': '— Titian',
        'search': 'Titian - Flora - Google Art Project.jpg'
    },
    {
        'id': 'raphael_madonna_of_the_meadow',
        'replaces': 'durer_self_portrait_fur_collar',
        'type': 'replace',
        'file': 'raphael_madonna_of_the_meadow.jpg',
        'title': '草地上的圣母 (1506)',
        'enTitle': 'Madonna of the Meadow (Madonna del Prato)',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Time is a versatile performer. It flies, marches on, heals all wounds.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Madonna of the Meadow Google Art Project'
    }
]

print(f"Starting discovery for {len(targets)} artworks...")
results = []
for item in targets:
    q = item['search']
    res = search_gap(q)
    best_file = None
    best_info = None
    if res:
        for title in res:
            info = get_image_info(title)
            if info and info['width'] >= 1500 and info['height'] >= 1500:
                best_file = title
                best_info = info
                break
            elif info and not best_info:
                best_file = title
                best_info = info
    
    if best_file and best_info:
        print(f"[FOUND] {item['id']}: {best_file} ({best_info['width']}x{best_info['height']}, {best_info['size']//1024}KB)")
        item['selected_file'] = best_file
        item['info'] = best_info
        results.append(item)
    else:
        print(f"[MISSING/LOWRES] {item['id']} for search '{q}'")
    time.sleep(0.5)

with open('scripts/highres_gap_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone! Successfully matched {len(results)}/{len(targets)} artworks.")
