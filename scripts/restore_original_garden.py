import json

def restore_garden():
    js_path = 'data/masterpieces.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start = content.find('window.MASTERPIECES =')
    start_bracket = content.find('[', start)
    end_bracket = content.rfind('];')
    arts = json.loads(content[start_bracket:end_bracket+1])

    # Check if already present
    arts = [a for a in arts if a['id'] != 'garden_monet_sanctuary']

    # Insert at the very beginning (Index 0)
    garden_entry = {
        "id": "garden_monet_sanctuary",
        "title": "莫奈的秘密花园 · 沉睡花境 (创世典藏)",
        "enTitle": "The Slumbering Garden (Monet's Sanctuary)",
        "artist": "Claude Monet (莫奈风格 · 创世特辑)",
        "category": "monet",
        "file": "garden.jpg",
        "query": "Claude Monet Secret Garden Sanctuary",
        "quote": "“I must have flowers, always, and always.”",
        "quoteAuthor": "— Claude Monet",
        "src": "assets/images/garden.jpg?v=3.8.0",
        "genre": "🌸 秘境序曲"
    }
    arts.insert(0, garden_entry)

    # Recalculate categories
    cat_counts = {}
    for a in arts:
        cat_counts[a['category']] = cat_counts.get(a['category'], 0) + 1

    cat_start = content.find('window.ART_CATEGORIES =')
    cat_start_bracket = content.find('[', cat_start)
    cat_end_bracket = content.find('];', cat_start)
    cats = json.loads(content[cat_start_bracket:cat_end_bracket+1])
    for c in cats:
        c['count'] = cat_counts.get(c['id'], 0)

    header = content[:cat_start]
    new_cats_json = json.dumps(cats, ensure_ascii=False, indent=4)
    new_arts_json = json.dumps(arts, ensure_ascii=False, indent=4)
    new_content = f"{header}window.ART_CATEGORIES = {new_cats_json};\n\nwindow.MASTERPIECES = {new_arts_json};\n"

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully restored garden.jpg as the #1 opening masterpiece! Total: {len(arts)}")
    print(f"Monet category count now: {cat_counts.get('monet')}")

if __name__ == '__main__':
    restore_garden()
