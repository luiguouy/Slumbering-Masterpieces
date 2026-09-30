import json

def finalize_masterpieces():
    js_path = 'data/masterpieces.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start = content.find('window.MASTERPIECES =')
    start_bracket = content.find('[', start)
    end_bracket = content.rfind('];')
    arts = json.loads(content[start_bracket:end_bracket+1])

    # Check if veronese_wedding_at_cana is already in
    has_veronese = any(a['id'] == 'veronese_wedding_at_cana' for a in arts)
    if not has_veronese:
        veronese_item = {
            "id": "veronese_wedding_at_cana",
            "title": "迦拿的婚礼 (1563)",
            "enTitle": "The Wedding at Cana",
            "artist": "Paolo Veronese (保罗·委罗内塞)",
            "category": "renaissance",
            "file": "veronese_wedding_at_cana.jpg",
            "query": "Paolo Veronese The Wedding at Cana Louvre",
            "quote": "“We painters take the same license the poets and the fools take.”",
            "quoteAuthor": "— Paolo Veronese",
            "src": "assets/images/veronese_wedding_at_cana.jpg?v=3.8.0",
            "genre": "🏛️ 神话宗教"
        }
        # Insert into renaissance section (e.g. after raphael)
        arts.append(veronese_item)

    # Deduplicate by ID just in case
    clean_arts = []
    seen = set()
    for a in arts:
        if a['id'] not in seen:
            clean_arts.append(a)
            seen.add(a['id'])

    # Category counts
    cat_counts = {}
    for a in clean_arts:
        cat_counts[a['category']] = cat_counts.get(a['category'], 0) + 1

    cat_start = content.find('window.ART_CATEGORIES =')
    cat_start_bracket = content.find('[', cat_start)
    cat_end_bracket = content.find('];', cat_start)
    cats = json.loads(content[cat_start_bracket:cat_end_bracket+1])
    for c in cats:
        c['count'] = cat_counts.get(c['id'], 0)

    header = content[:cat_start]
    new_cats_json = json.dumps(cats, ensure_ascii=False, indent=4)
    new_arts_json = json.dumps(clean_arts, ensure_ascii=False, indent=4)
    new_content = f"{header}window.ART_CATEGORIES = {new_cats_json};\n\nwindow.MASTERPIECES = {new_arts_json};\n"

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Final masterpieces count: {len(clean_arts)}")
    print(f"Categories breakdown: {cat_counts}")

if __name__ == '__main__':
    finalize_masterpieces()
