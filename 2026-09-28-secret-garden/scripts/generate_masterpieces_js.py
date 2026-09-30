import os
import json
import re

app_js_path = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\app.js'
data_js_path = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\data\masterpieces.js'
collect_py_path = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\scripts\collect_artworks.py'

# 从 collect_artworks.py 读取 NEW_ARTWORKS
with open(collect_py_path, 'r', encoding='utf-8') as f:
    collect_code = f.read()

# 提取 NEW_ARTWORKS 数组定义
start_idx = collect_code.find('NEW_ARTWORKS = [')
end_idx = collect_code.find('\nprint(f"Total defined new paintings:')
new_artworks_code = collect_code[start_idx:end_idx].strip()

# 执行代码片段获取 new_artworks 对象
local_scope = {}
exec(new_artworks_code, {}, local_scope)
new_artworks = local_scope['NEW_ARTWORKS']

# 现有的 33 幅画作定义与归类
EXISTING_ARTWORKS = [
    # 莫奈专栏 (26幅真实传世油画名作)
    {
        'id': 'monet_giverny_path',
        'title': '吉维尼的花园小径 (1902)',
        'enTitle': 'The Garden Path at Giverny',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'thumb_monet_giverny.jpg',
        'src': 'assets/images/thumb_monet_giverny.jpg?v=3.6.1',
        'quote': '“Perhaps I owe having become a painter to flowers.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_argenteuil',
        'title': '阿让特伊的艺术家花园 (1873)',
        'enTitle': "The Artist's Garden at Argenteuil",
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'thumb_monet_argenteuil.jpg',
        'src': 'assets/images/thumb_monet_argenteuil.jpg?v=3.6.1',
        'quote': '“My garden is my most beautiful masterpiece.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_met_irises',
        'title': '大都会的鸢尾花丛 (1890)',
        'enTitle': 'Irises in the Garden',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_met_irises.jpg',
        'src': 'assets/images/monet_met_irises.jpg?v=3.6.1',
        'quote': '“Colour is my day-long obsession, joy and torment.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_vetheuil',
        'title': '维特伊的艺术家花园 (1880)',
        'enTitle': "The Artist's Garden at Vétheuil",
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_nga_vetheuil.jpg',
        'src': 'assets/images/monet_nga_vetheuil.jpg?v=3.6.1',
        'quote': '“The richness I achieve comes from nature, the source of my inspiration.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_sainte_adresse',
        'title': '圣阿德雷斯的露台花园 (1867)',
        'enTitle': 'Garden at Sainte-Adresse',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'preview_sainte_adresse.jpg',
        'src': 'assets/images/preview_sainte_adresse.jpg?v=3.6.1',
        'quote': '“Everyone discusses my art and pretends to understand, when it is simply necessary to love.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_gladiolus',
        'title': '剑兰花境 (1876)',
        'enTitle': 'Gladioli in the Garden',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'thumb_monet_gladiolus.jpg',
        'src': 'assets/images/thumb_monet_gladiolus.jpg?v=3.6.1',
        'quote': '“I would like to paint the way a bird sings.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_water_lilies_bridge',
        'title': '睡莲池与日本桥 (1899)',
        'enTitle': 'Water Lilies and Japanese Bridge',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_japanese_bridge.jpg',
        'src': 'assets/images/monet_japanese_bridge.jpg?v=3.6.1',
        'quote': '“It took me time to understand my water lilies... I planted them without thinking of painting them.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_poppy_field',
        'title': '阿让特伊的虞美人花田 (1873)',
        'enTitle': 'Poppy Field at Argenteuil',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_poppy_field.jpg',
        'src': 'assets/images/monet_poppy_field.jpg?v=3.6.1',
        'quote': '“Every day I discover even more beautiful things. It is intoxicating me, and I want to paint it all.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_impression_sunrise',
        'title': '日出·印象 (1872)',
        'enTitle': 'Impression, Sunrise',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_impression_sunrise.jpg',
        'src': 'assets/images/monet_impression_sunrise.jpg?v=3.6.1',
        'quote': '“A landscape is only an impression, instantaneous, hence the label they\'ve given us.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_woman_with_parasol',
        'title': '撑阳伞的女人 · 散步 (1875)',
        'enTitle': 'Woman with a Parasol - Madame Monet and Her Son',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_woman_with_parasol.jpg',
        'src': 'assets/images/monet_woman_with_parasol.jpg?v=3.6.1',
        'quote': '“I am working on figures outdoors as I want, done like landscapes... It is an old dream that always torments me.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_water_lilies_1906',
        'title': '睡莲系列 · 碧波浮萍 (1906)',
        'enTitle': 'Water Lilies (Nymphéas)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_water_lilies_1906.jpg',
        'src': 'assets/images/monet_water_lilies_1906.jpg?v=3.6.1',
        'quote': '“These water landscapes have become an obsession. They are beyond my powers as an old man, and yet I want to succeed in expressing what I feel.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_haystacks_snow',
        'title': '干草堆系列 · 雪景晨光 (1891)',
        'enTitle': 'Wheatstacks (Snow Effect, Morning)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_haystacks_snow.jpg',
        'src': 'assets/images/monet_haystacks_snow.jpg?v=3.6.1',
        'quote': '“The further I go, the more I see that a lot of work is needed to succeed in rendering what I want to render: \'instantaneity\'.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_rouen_cathedral',
        'title': '鲁昂大教堂系列 · 阳光下的西正面 (1894)',
        'enTitle': 'Rouen Cathedral, West Façade, Sunlight',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_rouen_cathedral.jpg',
        'src': 'assets/images/monet_rouen_cathedral.jpg?v=3.6.1',
        'quote': '“Everything changes, even stone... Colour is vibration just like music.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_saint_lazare',
        'title': '圣拉扎尔火车站 (1877)',
        'enTitle': 'Gare Saint-Lazare, Arrival of a Train',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_saint_lazare.jpg',
        'src': 'assets/images/monet_saint_lazare.jpg?v=3.6.1',
        'quote': '“I am following nature without being able to grasp her... and then there is the light that refuses to stay still.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_camille_green_dress',
        'title': '绿衣女子 · 卡米尔 (1866)',
        'enTitle': 'The Woman in the Green Dress (Camille)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_camille_green_dress.jpg',
        'src': 'assets/images/monet_camille_green_dress.jpg?v=3.6.1',
        'quote': '“My heart goes out to the light and the beauty that walks among us.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_dejeuner_sur_l_herbe',
        'title': '草地上的午餐 (1866)',
        'enTitle': 'Le Déjeuner sur l\'herbe',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_dejeuner_sur_l_herbe.jpg',
        'src': 'assets/images/monet_dejeuner_sur_l_herbe.jpg?v=3.6.1',
        'quote': '“I want to paint the air in which the bridge, the house, and the boat are situated, the beauty of the air around them.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_women_in_garden',
        'title': '花园里的女人 (1866)',
        'enTitle': 'Women in the Garden (Femmes au jardin)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_women_in_garden.jpg',
        'src': 'assets/images/monet_women_in_garden.jpg?v=3.6.1',
        'quote': '“I paint directly from nature, outdoors, trying to catch the freshness of sunlight on the flowers and fabrics.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_la_grenouillere',
        'title': '蛙塘岛水上浴场 (1869)',
        'enTitle': 'Bathers at La Grenouillère',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_la_grenouillere.jpg',
        'src': 'assets/images/monet_la_grenouillere.jpg?v=3.6.1',
        'quote': '“I have a dream of a picture of the waters of La Grenouillère... sparkling with life and ripples.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_argenteuil_basin',
        'title': '阿让特伊盆地帆船 (1872)',
        'enTitle': 'The Basin at Argenteuil',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_argenteuil_basin.jpg',
        'src': 'assets/images/monet_argenteuil_basin.jpg?v=3.6.1',
        'quote': '“Water is the mirror of the sky, reflecting every fleeting cloud and beam of shimmer.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_boulevard_capucines',
        'title': '卡普辛大道 · 冬日熙攘 (1873)',
        'enTitle': 'Boulevard des Capucines',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_boulevard_capucines.jpg',
        'src': 'assets/images/monet_boulevard_capucines.jpg?v=3.6.1',
        'quote': '“To capture the pulse of the boulevard, the bustle of carriages and pedestrians disappearing into winter haze.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_rue_saint_denis',
        'title': '圣丹尼斯街的节日 (1878)',
        'enTitle': 'Rue Saint-Denis, Celebration of June 30, 1878',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_rue_saint_denis.jpg',
        'src': 'assets/images/monet_rue_saint_denis.jpg?v=3.6.1',
        'quote': '“I was enchanted by the flags... thousands of banners billowing in the Parisian breeze like fields of flowers.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_poplars',
        'title': '埃普特河畔的白杨树系列 (1891)',
        'enTitle': 'Poplars on the Epte',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_poplars.jpg',
        'src': 'assets/images/monet_poplars.jpg?v=3.6.1',
        'quote': '“Nature does not stand still. Every hour brings a new vibration through the slender poplars against the sky.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_etretat_cliff',
        'title': '普尔维尔峭壁漫步 (1882)',
        'enTitle': 'The Cliff Walk at Pourville',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_etretat_cliff.jpg',
        'src': 'assets/images/monet_etretat_cliff.jpg?v=3.6.1',
        'quote': '“The sea is an incredible spectacle, changing colour and grandeur with every passing hour.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_parliament',
        'title': '伦敦国会大厦系列 · 雾中夕阳 (1903)',
        'enTitle': 'The Houses of Parliament, Sunset',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_parliament.jpg',
        'src': 'assets/images/monet_parliament.jpg?v=3.6.1',
        'quote': '“Without the fog, London would not be a beautiful city. It is the fog that gives it its magnificent amplitude.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_waterloo_bridge',
        'title': '滑铁卢桥系列 · 晨曦日光效应 (1903)',
        'enTitle': 'Waterloo Bridge, Sunlight Effect',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_waterloo_bridge.jpg',
        'src': 'assets/images/monet_waterloo_bridge.jpg?v=3.6.1',
        'quote': '“I cannot paint the bridge, I paint only the atmosphere, the light, the fleeting mist upon the Thames.”',
        'quoteAuthor': '— Claude Monet'
    },
    {
        'id': 'monet_venice_grand_canal',
        'title': '威尼斯大运河与安康圣母圣殿 (1908)',
        'enTitle': 'The Grand Canal, Venice',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'file': 'monet_venice_grand_canal.jpg',
        'src': 'assets/images/monet_venice_grand_canal.jpg?v=3.6.1',
        'quote': '“The light of Venice is so exquisite, like molten jewels floating upon the undulating waves.”',
        'quoteAuthor': '— Claude Monet'
    },
]

# 组装 8 大传世出名油画流派展厅 (剔除现代主义与非油画内容)
CATEGORIES = [
    ('renaissance', '🏛️ 文艺复兴与北方画派 (Renaissance & Northern Masters)'),
    ('baroque', '🎭 巴洛克与荷兰黄金时代 (Baroque & Dutch Golden Age)'),
    ('romanticism', '⚡ 新古典、洛可可与浪漫主义 (Neoclassicism & Romanticism)'),
    ('realism', '🌾 写实主义与巡回展览画派 (Realism & Wanderers)'),
    ('monet', '🌟 克劳德·莫奈专题特辑 (Claude Monet Collection)'),
    ('impressionism', '🎨 印象派巅峰盛宴 (Impressionism Masters)'),
    ('post_impressionism', '🌻 后印象派三杰与现代先驱 (Post-Impressionism)'),
    ('expressionism', '🌌 象征主义与表现主义 (Symbolism & Expressionism)')
]

# 合并全部名画列表并按分类排序组织
combined = []
for p in EXISTING_ARTWORKS:
    combined.append(p)

for p in new_artworks:
    # 避免 id 重复
    if not any(x['id'] == p['id'] for x in combined):
        p_copy = dict(p)
        p_copy['src'] = f"assets/images/{p['file']}?v=3.6.1"
        combined.append(p_copy)

# 按类别组织
sorted_artworks = []
for cat_id, cat_name in CATEGORIES:
    cat_items = [p for p in combined if p.get('category') == cat_id]
    sorted_artworks.extend(cat_items)

print(f"Total master gallery count: {len(sorted_artworks)}")

# 生成 JS 文件
js_content = "/**\n * Slumbering Masterpieces · World Fine Art Collection\n"
js_content += f" * 全球世界级传世名画博览馆数据库（共 {len(sorted_artworks)} 幅殿堂级杰作）\n"
js_content += " */\n\n"

js_content += "window.ART_CATEGORIES = [\n"
for cat_id, cat_name in CATEGORIES:
    cnt = len([p for p in sorted_artworks if p.get('category') == cat_id])
    js_content += f"    {{ id: '{cat_id}', name: '{cat_name}', count: {cnt} }},\n"
js_content += "];\n\n"

js_content += "window.MASTERPIECES = " + json.dumps(sorted_artworks, ensure_ascii=False, indent=4) + ";\n"

with open(data_js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully generated {data_js_path}!")
