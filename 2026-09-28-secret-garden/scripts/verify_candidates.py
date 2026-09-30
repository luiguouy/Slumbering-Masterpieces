import json
import re

CANDIDATES = [
    {"id": "raphael_sistine_madonna", "title": "西斯廷圣母 (1512)", "artist": "Raphael (拉斐尔)", "query": "File:RAFAEL - Madonna Sixtina (Gemäldegalerie Alter Meister, Dresden, 1513-14. Öl auf Leinwand, 265 x 196 cm).jpg"},
    {"id": "michelangelo_creation_of_adam", "title": "创造亚当 (1512)", "artist": "Michelangelo (米开朗基罗)", "query": "Michelangelo Creation of Adam Sistine Chapel Ceiling"},
    {"id": "bruegel_tower_of_babel", "title": "通天塔 · 巴别塔 (1563)", "artist": "Pieter Bruegel the Elder (老彼得·勃鲁盖尔)", "query": "Pieter Bruegel the Elder The Tower of Babel Kunsthistorisches Museum"},
    {"id": "botticelli_madonna_of_magnificat", "title": "尊主颂圣母 (1481)", "artist": "Sandro Botticelli (波提切利)", "query": "Botticelli Madonna del Magnificato Uffizi"},
    {"id": "raphael_madonna_in_the_meadow", "title": "草地上的圣母 (1506)", "artist": "Raphael (拉斐尔)", "query": "Raphael Madonna del Prato Kunsthistorisches Museum"},
    {"id": "titian_assumption_of_the_virgin", "title": "圣母升天 (1518)", "artist": "Titian (提香)", "query": "Titian Assumption of the Virgin Santa Maria Gloriosa dei Frari"},
    {"id": "giorgione_castelfranco_madonna", "title": "卡斯特尔弗兰科圣母 (1504)", "artist": "Giorgione (乔尔乔内)", "query": "Giorgione Castelfranco Madonna Duomo di Castelfranco Veneto"},
    {"id": "veronese_the_wedding_at_cana", "title": "迦拿的婚礼 (1563)", "artist": "Paolo Veronese (保罗·委罗内塞)", "query": "Paolo Veronese The Wedding at Cana Louvre"},
    {"id": "rubens_the_elevation_of_the_cross", "title": "上十字架 (1610)", "artist": "Peter Paul Rubens (彼得·保罗·鲁本斯)", "query": "Rubens The Elevation of the Cross Cathedral of Our Lady Antwerp"},
    {"id": "murillo_immaculate_conception_soult", "title": "索尔特无原罪圣母 (1678)", "artist": "Bartolomé Esteban Murillo (穆里略)", "query": "Murillo The Immaculate Conception of Los Venerables Prado"},
    {"id": "caravaggio_supper_at_emmaus", "title": "以马忤斯的晚餐 (1601)", "artist": "Caravaggio (卡拉瓦乔)", "query": "Caravaggio Supper at Emmaus National Gallery London"},
    {"id": "davinci_virgin_of_the_rocks_louvre", "title": "岩间圣母 (1486)", "artist": "Leonardo da Vinci (达·芬奇)", "query": "Leonardo da Vinci Virgin of the Rocks Louvre"},
    {"id": "cranach_madonna_under_fir_tree", "title": "松树下的圣母 (1530)", "artist": "Lucas Cranach the Elder (老卢卡斯·克拉纳赫)", "query": "Lucas Cranach the Elder Madonna under the Fir Tree Wroclaw"},
    {"id": "bouguereau_song_of_the_angels", "title": "天使之歌 (1881)", "artist": "William-Adolphe Bouguereau (布格罗)", "query": "William-Adolphe Bouguereau Song of the Angels Forest Lawn"},
    {"id": "bouguereau_the_annunciation", "title": "受胎告知 (1888)", "artist": "William-Adolphe Bouguereau (布格罗)", "query": "William-Adolphe Bouguereau The Annunciation"},
    {"id": "tiepolo_the_annunciation", "title": "受胎告知 (1757)", "artist": "Giovanni Battista Tiepolo (提埃坡罗)", "query": "Giovanni Battista Tiepolo The Annunciation"}
]

with open("data/masterpieces.js", "r", encoding="utf-8") as f:
    js = f.read()

for c in CANDIDATES:
    if c['id'] in js:
        print(f"COLLISION with masterpieces.js: {c['id']}")
    title_key = c['title'].split(' ')[0]
    if f'"{title_key}"' in js or f"'{title_key}'" in js:
        print(f"Possible title collision: {c['title']}")

with open("scripts/harvested_50_religious.json", "r", encoding="utf-8") as f:
    h = json.load(f)
h_ids = {x['id'] for x in h}

for c in CANDIDATES:
    if c['id'] in h_ids:
        print(f"COLLISION with harvested: {c['id']}")

print("Candidate verification done. Total candidates:", len(CANDIDATES))
