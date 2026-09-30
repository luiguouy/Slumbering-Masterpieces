import json

candidates_16 = [
    {
        'id': 'raphael_alba_madonna',
        'title': '阿尔巴圣母 (1511)',
        'enTitle': 'The Alba Madonna',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“When one is painting one does not think.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael The Alba Madonna National Gallery of Art'
    },
    {
        'id': 'caravaggio_calling_of_saint_matthew',
        'title': '圣马太的感召 (1600)',
        'enTitle': 'The Calling of Saint Matthew',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“All works, no matter what or by whom painted, are nothing but bagatelles and childish trifles... unless they are made and painted from life.”',
        'quoteAuthor': '— Caravaggio',
        'search': 'Caravaggio The Calling of Saint Matthew San Luigi dei Francesi'
    },
    {
        'id': 'fra_angelico_coronation_of_the_virgin',
        'title': '圣母加冕 (1435)',
        'enTitle': 'Coronation of the Virgin',
        'artist': 'Fra Angelico (安杰利科修士)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who does Christ’s work must always stay with Christ.”',
        'quoteAuthor': '— Fra Angelico',
        'search': 'Fra Angelico Coronation of the Virgin Louvre'
    },
    {
        'id': 'jean_fouquet_melun_diptych_virgin',
        'title': '默伦双联画 · 圣母子与天使 (1452)',
        'enTitle': 'Melun Diptych: Virgin and Child Surrounded by Angels',
        'artist': 'Jean Fouquet (让·富凯)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Form and colour in celestial harmony.”',
        'quoteAuthor': '— Jean Fouquet',
        'search': 'Jean Fouquet Virgin and Child Antwerp'
    },
    {
        'id': 'giotto_lamentation',
        'title': '哀悼基督 (1306)',
        'enTitle': 'Lamentation (The Mourning of Christ)',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Painting is poetry which is seen and not heard.”',
        'quoteAuthor': '— Giotto',
        'search': 'Giotto Lamentation Scrovegni Chapel'
    },
    {
        'id': 'titian_penitent_magdalene',
        'title': '抹大拉的玛利亚 (1533)',
        'enTitle': 'Penitent Magdalene',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“A good painter needs only three colours: black, white, and red.”',
        'quoteAuthor': '— Titian',
        'search': 'Titian Penitent Magdalene Pitti Palace'
    },
    {
        'id': 'bruegel_conversion_of_paul',
        'title': '保罗的皈依 (1567)',
        'enTitle': 'The Conversion of Paul',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature paints the grandest stages of human fate.”',
        'quoteAuthor': '— Pieter Bruegel the Elder',
        'search': 'Pieter Bruegel the Elder The Conversion of Paul Kunsthistorisches Museum'
    },
    {
        'id': 'botticelli_madonna_of_magnificat',
        'title': '尊主颂圣母 (1481)',
        'enTitle': 'Madonna of the Magnificat',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“My soul doth magnify the Lord.”',
        'quoteAuthor': '— Sandro Botticelli',
        'search': 'Botticelli Madonna del Magnificat Uffizi'
    },
    {
        'id': 'giorgione_castelfranco_madonna',
        'title': '卡斯特尔弗兰科圣母 (1504)',
        'enTitle': 'Castelfranco Madonna',
        'artist': 'Giorgione (乔尔乔内)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Light breathes upon the landscape of the soul.”',
        'quoteAuthor': '— Giorgione',
        'search': 'Giorgione Castelfranco Madonna'
    },
    {
        'id': 'veronese_the_wedding_at_cana',
        'title': '迦拿的婚礼 (1563)',
        'enTitle': 'The Wedding at Cana',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“We painters take the same liberties as poets and madmen.”',
        'quoteAuthor': '— Paolo Veronese',
        'search': 'Paolo Veronese The Wedding at Cana Louvre'
    },
    {
        'id': 'rubens_elevation_of_the_cross',
        'title': '上十字架 (1610)',
        'enTitle': 'The Elevation of the Cross',
        'artist': 'Peter Paul Rubens (彼得·保罗·鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no enterprise, however great, has ever surpassed my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Rubens The Elevation of the Cross Antwerp Cathedral'
    },
    {
        'id': 'murillo_soult_immaculate_conception',
        'title': '索尔特无原罪圣母 (1678)',
        'enTitle': 'The Soult Immaculate Conception',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'search': 'Murillo The Immaculate Conception Prado Los Venerables'
    },
    {
        'id': 'tiepolo_adoration_of_the_magi',
        'title': '三博士来朝 (1753)',
        'enTitle': 'The Adoration of the Magi',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Skies without end belong to the painter’s brush.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'search': 'Tiepolo The Adoration of the Magi Alte Pinakothek'
    },
    {
        'id': 'carracci_flight_into_egypt',
        'title': '逃往埃及途中的风景 (1604)',
        'enTitle': 'The Flight into Egypt',
        'artist': 'Annibale Carracci (安尼巴莱·卡拉奇)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature ordered by classical reason becomes eternal beauty.”',
        'quoteAuthor': '— Annibale Carracci',
        'search': 'Annibale Carracci The Flight into Egypt Doria Pamphilj'
    },
    {
        'id': 'bouguereau_song_of_the_angels',
        'title': '天使之歌 (1881)',
        'enTitle': 'Song of the Angels',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Each day I go to my studio full of happiness.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'search': 'William-Adolphe Bouguereau Song of the Angels'
    },
    {
        'id': 'cranach_madonna_under_fir_tree',
        'title': '松树下的圣母 (1530)',
        'enTitle': 'Madonna under the Fir Tree',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Truth and nature abide under the evergreen branch.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'search': 'Lucas Cranach the Elder Madonna under the Fir Tree'
    }
]

with open("data/masterpieces.js", "r", encoding="utf-8") as f:
    js = f.read()

with open("scripts/harvested_50_religious.json", "r", encoding="utf-8") as f:
    harvested = json.load(f)

h_ids = {x['id'] for x in harvested}

collisions = 0
for item in candidates_16:
    if f'"{item["id"]}"' in js or f"'{item['id']}'" in js:
        print(f"COLLISION with masterpieces.js: {item['id']}")
        collisions += 1
    if item['id'] in h_ids:
        print(f"COLLISION with harvested: {item['id']}")
        collisions += 1

print(f"Collisions: {collisions}. Verified unique: {len(candidates_16) - collisions}/16")
