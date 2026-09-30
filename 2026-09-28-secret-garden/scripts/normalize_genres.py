import json
import re

def main():
    path = "data/masterpieces.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"window\.MASTERPIECES\s*=\s*(\[.*?\]);", content, re.DOTALL)
    if not match:
        print("Could not find window.MASTERPIECES")
        return

    data = json.loads(match.group(1))

    fixes = {
        'garden_monet_sanctuary': '🌿 自然风景',
        'turner_the_grand_canal_venice': '🌿 自然风景',
        'pissarro_apple_picking_eragny': '🌿 自然风景',
        'monet_giverny_path': '🌿 自然风景',
        'monet_gladiolus': '💐 静物花卉',
        'cezanne_basket_of_apples': '💐 静物花卉',
        'vangogh_sunflowers': '💐 静物花卉',
        'vangogh_irises': '💐 静物花卉',
        'vangogh_almond_blossom': '💐 静物花卉'
    }

    modified_count = 0
    for d in data:
        art_id = d.get('id')
        if art_id in fixes:
            old = d.get('genre')
            new = fixes[art_id]
            if old != new:
                d['genre'] = new
                modified_count += 1
                print(f"Updated {art_id}: {old} -> {new}")

    new_masterpieces_json = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content[:match.start(1)] + new_masterpieces_json + content[match.end(1):]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully normalized {modified_count} genres in {path}")

if __name__ == "__main__":
    main()
