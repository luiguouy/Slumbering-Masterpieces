import json

with open('scripts/deep_audit_result.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Criteria for substandard:
# 1. Low resolution: min(w, h) < 700 or max(w, h) < 1200
# 2. Too dark/dull/colorless: colorfulness < 16 or (colorfulness < 22 and s < 0.25 and v < 0.3)
substandard = []
for r in results:
    w, h = r['w'], r['h']
    c = r['colorfulness']
    s = r['mean_s']
    v = r['mean_v']
    reasons = []
    
    # Check low resolution
    if min(w, h) < 700:
        reasons.append(f"超低分辨率 ({w}x{h})，糊成一团")
    elif max(w, h) < 1200:
        reasons.append(f"中低分辨率 ({w}x{h})")
        
    # Check colorless / dark / gloomy
    if c < 12:
        reasons.append(f"严重褪色或近乎黑白素描/严重缺乏色彩 (色彩分: {c})")
    elif v < 0.15:
        reasons.append(f"画面死黑一片/暗沉看不清细节 (亮度: {v})")
    elif c < 21 and s < 0.22 and v < 0.35:
        reasons.append(f"色彩极其寡淡灰暗/单调沉闷 (色彩分: {c}, 饱和度: {s})")
    
    if reasons:
        substandard.append({
            'id': r['art']['id'],
            'title': r['art']['title'],
            'artist': r['art']['artist'],
            'category': r['art']['category'],
            'reasons': reasons,
            'w': w, 'h': h, 'c': c, 's': s, 'v': v
        })

print(f"Total problematic artworks found: {len(substandard)}\n")
for item in substandard:
    print(f"- [{item['category']}] {item['id']}: 《{item['title']}》 - {item['artist']}")
    for reas in item['reasons']:
        print(f"    * {reas}")
