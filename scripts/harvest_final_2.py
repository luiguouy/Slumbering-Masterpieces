import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fast_harvest_engine as fhe

FINAL_2 = [
    {
        'id': 'botticelli_cestello_annunciation',
        'title': '切斯特洛圣母领报 (1489)',
        'enTitle': 'Cestello Annunciation',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The grace of Heaven descends on silent wings.”',
        'quoteAuthor': '— Sandro Botticelli',
        'search': 'Botticelli Cestello Annunciation Uffizi Google Art Project'
    },
    {
        'id': 'vandyck_susanna_and_the_elders',
        'title': '苏珊娜与二长老 (1622)',
        'enTitle': 'Susanna and the Elders',
        'artist': 'Anthony van Dyck (凡·戴克)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Purity withstands the shadows of deceit.”',
        'quoteAuthor': '— Anthony van Dyck',
        'search': 'Anthony van Dyck Susanna and the Elders Alte Pinakothek'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'r', encoding='utf-8') as f:
        existing = json.load(f)

    for item in FINAL_2:
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
        time.sleep(1.5)

    print(f"FINAL 50 COMPLETE COUNT: {len(existing)}")
    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
