import json
import re

path = "data/masterpieces.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"window\.MASTERPIECES\s*=\s*(\[.*?\]);", content, re.DOTALL)
data = json.loads(match.group(1))

for d in data:
    aid = d.get('id')
    # 更新特定作品元数据
    if aid == 'monet_water_lilies_1906':
        d['title'] = "睡莲系列 · 碧水浮萍 (1905)"
        d['enTitle'] = "Water Lilies (1905)"

    # 给所有图片强制刷新版本号，确保浏览器彻底清空旧图片缓存
    base_src = d['src'].split('?')[0]
    d['src'] = f"{base_src}?v=4.2.0"

new_json = json.dumps(data, ensure_ascii=False, indent=4)
new_content = content[:match.start(1)] + new_json + content[match.end(1):]

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("成功刷新版本号至 v=4.2.0 并更新睡莲元数据！")
