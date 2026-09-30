import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fast_harvest_engine as fhe

FINAL_4 = [
    {
        'id': 'bruegel_procession_to_calvary',
        'title': '通往各各他之路 · 苦路背负十字架 (1564)',
        'enTitle': 'The Procession to Calvary',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The vastness of earth holds both divine mystery and humble daily toil.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'search': 'Pieter Bruegel the Elder - The Procession to Calvary - Google Art Project'
    },
    {
        'id': 'raphael_small_cowper_madonna',
        'title': '小考珀圣母 (1505)',
        'enTitle': 'The Small Cowper Madonna',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Harmonious grace is the language of angels.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael The Small Cowper Madonna NGA Google Art Project'
    },
    {
        'id': 'michelangelo_the_last_judgment_sistine',
        'title': '最后的审判 · 天国群圣 (1541)',
        'enTitle': 'The Last Judgment (Sistine Chapel)',
        'artist': 'Michelangelo (米开朗基罗)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“My soul can find no staircase to Heaven unless it be through Earth\'s loveliness.”',
        'quoteAuthor': '— Michelangelo',
        'search': 'Last Judgement (Michelangelo)'
    },
    {
        'id': 'cranach_saint_jerome_in_desert',
        'title': '圣哲罗姆在荒野 (1502)',
        'enTitle': 'Saint Jerome in the Wilderness',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“In wild solitude the sacred whisper is heard.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'search': 'Lucas Cranach the Elder Saint Jerome in the Wilderness Google Art Project'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'r', encoding='utf-8') as f:
        existing = json.load(f)

    print(f"Current count: {len(existing)}. Adding final 4 to reach 50...")
    for item in FINAL_4:
        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        c = fhe.find_best_commons_file(item['search'])
        if c:
            fhe.download_and_save(c['url'], save_path)
            ok, msg = fhe.inspect_image(save_path)
            print(f"{item['id']} -> {msg}")
            if ok:
                item['file'] = fn
                item['src'] = f"assets/images/{fn}?v=3.8.0"
                existing.append(item)
        time.sleep(2.0)

    print(f"FINAL TOTAL HARVESTED: {len(existing)}")
    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
