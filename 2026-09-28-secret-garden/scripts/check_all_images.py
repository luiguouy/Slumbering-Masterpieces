import json

with open('scripts/deep_audit_result.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

print("=== ALL ARTWORKS WITH RESOLUTION < 1800 MAX OR < 900 MIN ===")
for r in results:
    w, h = r['w'], r['h']
    if max(w, h) < 1800 or min(w, h) < 900:
        a = r['art']
        print(f"{a['id']}: {w}x{h} (color: {r['colorfulness']}) 《{a['title']}》 - {a['artist']}")

print("\n=== ALL ARTWORKS WITH COLORFULNESS < 23 ===")
for r in results:
    if r['colorfulness'] < 23:
        a = r['art']
        print(f"{a['id']}: {r['w']}x{r['h']} (color: {r['colorfulness']:.1f}, sat: {r['mean_s']:.2f}, val: {r['mean_v']:.2f}) 《{a['title']}》 - {a['artist']}")
