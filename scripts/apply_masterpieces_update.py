import json
import re

def update_masterpieces():
    js_path = 'data/masterpieces.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements map
    # id -> new object
    replacements = {
        'turner_rain_steam_and_speed': {
            "id": "turner_the_grand_canal_venice",
            "title": "威尼斯大运河 (1835)",
            "enTitle": "The Grand Canal, Venice",
            "artist": "J. M. W. Turner (透纳)",
            "category": "romanticism",
            "file": "turner_the_grand_canal_venice.jpg",
            "query": "Turner The Grand Canal Venice Google Art Project",
            "quote": "“Light is therefore colour.”",
            "quoteAuthor": "— J. M. W. Turner",
            "src": "assets/images/turner_the_grand_canal_venice.jpg?v=3.8.0",
            "genre": "🌊 自然风景"
        },
        'whistler_mothers_portrait': {
            "id": "sargent_carnation_lily_lily_rose",
            "title": "康乃馨、百合与玫瑰 (1886)",
            "enTitle": "Carnation, Lily, Lily, Rose",
            "artist": "John Singer Sargent (约翰·辛格·萨金特)",
            "category": "realism",
            "file": "sargent_carnation_lily_lily_rose.jpg",
            "query": "John Singer Sargent Carnation Lily Lily Rose Google Art Project",
            "quote": "“You can’t do a sketch in enough color.”",
            "quoteAuthor": "— John Singer Sargent",
            "src": "assets/images/sargent_carnation_lily_lily_rose.jpg?v=3.8.0",
            "genre": "👤 人物肖像"
        },
        'courbet_burial_at_ornans': {
            "id": "pissarro_apple_picking_eragny",
            "title": "厄拉尼采苹果 (1888)",
            "enTitle": "Apple Picking at Éragny",
            "artist": "Camille Pissarro (卡米耶·毕沙罗)",
            "category": "realism",
            "file": "pissarro_apple_picking_eragny.jpg",
            "query": "Camille Pissarro Apple Picking Google Art Project",
            "quote": "“Blessed are they who see beautiful things in humble places where other people see nothing.”",
            "quoteAuthor": "— Camille Pissarro",
            "src": "assets/images/pissarro_apple_picking_eragny.jpg?v=3.8.0",
            "genre": "🌾 田园风光"
        },
        'davinci_st_john_the_baptist': {
            "id": "titian_flora",
            "title": "花神弗洛拉 (1515)",
            "enTitle": "Flora",
            "artist": "Titian (提香)",
            "category": "renaissance",
            "file": "titian_flora.jpg",
            "query": "Titian Flora Google Art Project",
            "quote": "“A good painter needs only three colours: black, white and red.”",
            "quoteAuthor": "— Titian",
            "src": "assets/images/titian_flora.jpg?v=3.8.0",
            "genre": "👤 人物肖像"
        },
        'durer_self_portrait_fur_collar': {
            "id": "raphael_madonna_of_the_meadow",
            "title": "草地上的圣母 (1506)",
            "enTitle": "Madonna of the Meadow (Madonna del Prato)",
            "artist": "Raphael (拉斐尔)",
            "category": "renaissance",
            "file": "raphael_madonna_of_the_meadow.jpg",
            "query": "Raphael Madonna of the Meadow Google Art Project",
            "quote": "“Time is a versatile performer. It flies, marches on, heals all wounds.”",
            "quoteAuthor": "— Raphael",
            "src": "assets/images/raphael_madonna_of_the_meadow.jpg?v=3.8.0",
            "genre": "🏛️ 神话宗教"
        }
    }

    # Extract JSON
    start = content.find('window.MASTERPIECES =')
    start_bracket = content.find('[', start)
    end_bracket = content.rfind('];')
    json_text = content[start_bracket:end_bracket+1]
    artworks = json.loads(json_text)

    new_list = []
    seen_ids = set()
    for art in artworks:
        art_id = art['id']
        # Bump version query param
        art['src'] = art['src'].split('?')[0] + '?v=3.8.0'
        
        # In-place title tune for Monet if needed
        if art_id == 'monet_gladiolus':
            art['title'] = "睡莲池景 (1900)"
            art['enTitle'] = "Water Lily Pond"
            art['genre'] = "💐 静物花卉"
        elif art_id == 'monet_giverny_path':
            art['title'] = "日本桥与睡莲 (1899)"
            art['enTitle'] = "The Japanese Footbridge"
            art['genre'] = "🌿 自然风光"

        if art_id in replacements:
            rep = replacements[art_id]
            if rep['id'] not in seen_ids:
                new_list.append(rep)
                seen_ids.add(rep['id'])
        else:
            if art_id not in seen_ids:
                new_list.append(art)
                seen_ids.add(art_id)

    print(f"Total updated artworks: {len(new_list)} (unique IDs: {len(seen_ids)})")

    # Update categories count
    cat_counts = {}
    for art in new_list:
        cat = art['category']
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    cat_start = content.find('window.ART_CATEGORIES =')
    cat_start_bracket = content.find('[', cat_start)
    cat_end_bracket = content.find('];', cat_start)
    cats = json.loads(content[cat_start_bracket:cat_end_bracket+1])
    for c in cats:
        c['count'] = cat_counts.get(c['id'], 0)

    # Reconstruct file
    new_cats_json = json.dumps(cats, ensure_ascii=False, indent=4)
    new_art_json = json.dumps(new_list, ensure_ascii=False, indent=4)

    header = content[:cat_start]
    middle = f"window.ART_CATEGORIES = {new_cats_json};\n\nwindow.MASTERPIECES = {new_art_json};\n"
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(header + middle)
    print("Successfully written updated masterpieces.js with ?v=3.8.0!")

if __name__ == '__main__':
    update_masterpieces()
