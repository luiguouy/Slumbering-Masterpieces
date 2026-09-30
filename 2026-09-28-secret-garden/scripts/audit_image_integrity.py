import json
import re
import os
from PIL import Image

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    data = json.loads(re.search(r'window\.MASTERPIECES\s*=\s*(\[.*?\]);', f.read(), re.DOTALL).group(1))

print(f"总画作数: {len(data)}")

# 1. 检查是否存在重复的图片文件或哈希
from collections import defaultdict
import hashlib

hash_map = defaultdict(list)
dim_list = []

for d in data:
    path = d.get('src', '').split('?')[0]
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path} (id: {d['id']})")
        continue
    with open(path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    hash_map[file_hash].append((d['id'], d['title'], path))
    try:
        im = Image.open(path)
        dim_list.append((d['id'], d['title'], im.size, im.size[0] / im.size[1]))
    except Exception as e:
        print(f"❌ 无法打开图像: {path}, 错误: {e}")

print("\n=== 重复图片检查 (相同 MD5) ===")
duplicates_found = False
for h, items in hash_map.items():
    if len(items) > 1:
        duplicates_found = True
        print(f"⚠️ 相同图片文件被多个画作使用:")
        for it in items:
            print(f"    - [{it[0]}] 《{it[1]}》 -> {it[2]}")

if not duplicates_found:
    print("未发现完全相同 MD5 的文件。")

# 2. 检查特定名作的宽高比是否符合艺术常识
# 比如《代尔夫特风景》是著名横幅油画，宽远大于高
print("\n=== 检查常识异常（横竖构图错乱） ===")
for aid, title, size, ratio in dim_list:
    if '代尔夫特风景' in title or 'view_of_delft' in aid:
        print(f"代尔夫特风景尺寸: {size}, 宽高比: {ratio:.2f} (如果是竖图说明完全错了！)")
    if '睡莲' in title and 'triptych' in aid:
        print(f"睡莲三联画尺寸: {size}, 宽高比: {ratio:.2f}")
    if '最后的晚餐' in title or 'last_supper' in aid:
        if ratio < 1.0:
            print(f"⚠️ 最后的晚餐异常竖图: {size}")
    if '雅典学院' in title or 'school_of_athens' in aid:
        if ratio < 1.0:
            print(f"⚠️ 雅典学院异常竖图: {size}")
