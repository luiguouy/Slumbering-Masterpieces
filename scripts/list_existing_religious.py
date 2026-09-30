import json

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    c = f.read()
start = c.find('window.MASTERPIECES =')
arts = json.loads(c[start+len('window.MASTERPIECES ='):c.rfind('];')+1])

print(f"Total existing artworks: {len(arts)}")
religious_existing = []
for a in arts:
    title_lower = (a['title'] + ' ' + a['enTitle']).lower()
    if a.get('genre') == '🏛️ 神话宗教' or any(k in title_lower for k in ['圣', '基督', '创世', '晚餐', '亚当', '天使', 'madonna', 'supper', 'christ', 'adam', 'virgin', 'cana', 'god', 'jesus', 'apocalypse', 'judgment']):
        religious_existing.append(f"{a['id']}: 《{a['title']}》 ({a['enTitle']}) - {a['artist']}")

print(f"Existing religious artworks ({len(religious_existing)}):")
for r in religious_existing:
    print(" ", r)
