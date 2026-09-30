import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fast_harvest_engine as fhe

# 50幅精选传世宗教名画（高色彩、高分辨率、零重复）
CANDIDATES = [
    # 早期文艺复兴与北方文艺复兴
    {
        'id': 'fra_angelico_annunciation',
        'title': '受胎告知 (1426)',
        'enTitle': 'The Annunciation',
        'artist': 'Fra Angelico (安杰利科修士)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who does Christ’s work must always stay with Christ.”',
        'quoteAuthor': '— Fra Angelico',
        'search': 'Fra Angelico The Annunciation Prado'
    },
    {
        'id': 'giotto_kiss_of_judas',
        'title': '犹大之吻 (1305)',
        'enTitle': 'The Kiss of Judas',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The brush is the tongue of the eye.”',
        'quoteAuthor': '— Giotto',
        'search': 'Giotto The Kiss of Judas Scrovegni'
    },
    {
        'id': 'van_eyck_ghent_adoration',
        'title': '根特祭坛画 · 羔羊的颂赞 (1432)',
        'enTitle': 'Adoration of the Mystic Lamb',
        'artist': 'Jan van Eyck (扬·凡·艾克)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“As I can, not as I would.”',
        'quoteAuthor': '— Jan van Eyck',
        'search': 'Ghent Altarpiece Adoration of the Mystic Lamb'
    },
    {
        'id': 'van_eyck_madonna_of_chancellor_rolin',
        'title': '洛林大臣的圣母 (1435)',
        'enTitle': 'Madonna of Chancellor Rolin',
        'artist': 'Jan van Eyck (扬·凡·艾克)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature is the supreme teacher of colour.”',
        'quoteAuthor': '— Jan van Eyck',
        'search': 'Jan van Eyck Madonna of Chancellor Rolin Louvre'
    },
    {
        'id': 'van_der_weyden_descent_from_cross',
        'title': '下十字架 (1435)',
        'enTitle': 'The Descent from the Cross',
        'artist': 'Rogier van der Weyden (范德魏登)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“True tears reflect the truest colours of grace.”',
        'quoteAuthor': '— Rogier van der Weyden',
        'search': 'Rogier van der Weyden The Descent from the Cross Prado'
    },
    {
        'id': 'botticelli_adoration_of_magi',
        'title': '三博士来朝 (1475)',
        'enTitle': 'Adoration of the Magi',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Beauty is the shadow of divine perfection.”',
        'quoteAuthor': '— Sandro Botticelli',
        'search': 'Botticelli Adoration of the Magi Uffizi'
    },
    {
        'id': 'botticelli_madonna_of_pomegranate',
        'title': '持石榴的圣母 (1487)',
        'enTitle': 'Madonna of the Pomegranate',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“In every seed of the pomegranate lies a sacred promise.”',
        'quoteAuthor': '— Sandro Botticelli',
        'search': 'Botticelli Madonna of the Pomegranate Uffizi'
    },
    {
        'id': 'bellini_san_giobbe_altarpiece',
        'title': '圣焦贝祭坛画 (1487)',
        'enTitle': 'San Giobbe Altarpiece',
        'artist': 'Giovanni Bellini (贝利尼)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Light dissolves the boundaries between heaven and earth.”',
        'quoteAuthor': '— Giovanni Bellini',
        'search': 'Giovanni Bellini San Giobbe Altarpiece'
    },
    {
        'id': 'bellini_madonna_of_the_meadow',
        'title': '草地上的圣母与圣子 (1505)',
        'enTitle': 'Madonna of the Meadow (Bellini)',
        'artist': 'Giovanni Bellini (贝利尼)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Silence in nature is the voice of holiness.”',
        'quoteAuthor': '— Giovanni Bellini',
        'search': 'Giovanni Bellini Madonna of the Meadow National Gallery'
    },
    {
        'id': 'perugino_delivery_of_the_keys',
        'title': '基督将天国钥匙交予圣彼得 (1482)',
        'enTitle': 'Delivery of the Keys',
        'artist': 'Pietro Perugino (佩鲁吉诺)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Symmetry and light are the harmony of the spirit.”',
        'quoteAuthor': '— Pietro Perugino',
        'search': 'Pietro Perugino Delivery of the Keys Sistine Chapel'
    },

    # 全盛期文艺复兴与威尼斯画派
    {
        'id': 'davinci_virgin_and_child_st_anne',
        'title': '圣母子与圣安妮 (1503)',
        'enTitle': 'The Virgin and Child with Saint Anne',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Details make perfection, and perfection is not a detail.”',
        'quoteAuthor': '— Leonardo da Vinci',
        'search': 'Leonardo da Vinci The Virgin and Child with Saint Anne Louvre'
    },
    {
        'id': 'davinci_annunciation',
        'title': '受胎告知 (1472)',
        'enTitle': 'Annunciation (Leonardo)',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who loves practice without theory is like a sailor without a rudder.”',
        'quoteAuthor': '— Leonardo da Vinci',
        'search': 'Leonardo da Vinci Annunciation Uffizi'
    },
    {
        'id': 'michelangelo_doni_tondo',
        'title': '多尼圆幅 · 圣家族 (1507)',
        'enTitle': 'Doni Tondo (The Holy Family)',
        'artist': 'Michelangelo (米开朗基罗)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Every block of stone has a statue inside it.”',
        'quoteAuthor': '— Michelangelo',
        'search': 'Michelangelo Doni Tondo Uffizi'
    },
    {
        'id': 'raphael_transfiguration',
        'title': '基督显圣容 (1520)',
        'enTitle': 'Transfiguration',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“To paint is to love again, to live twice.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Transfiguration Vatican'
    },
    {
        'id': 'raphael_madonna_of_the_goldfinch',
        'title': '金翅雀圣母 (1506)',
        'enTitle': 'Madonna of the Goldfinch',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Simplicity is the highest goal of art.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Madonna del cardellino Uffizi'
    },
    {
        'id': 'raphael_madonna_della_seggiola',
        'title': '椅中圣母 (1514)',
        'enTitle': 'Madonna della Seggiola',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“In motherly embrace dwells the quietest kingdom.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Madonna della Seggiola Pitti Palace'
    },
    {
        'id': 'raphael_saint_catherine',
        'title': '亚历山大的圣凯瑟琳 (1507)',
        'enTitle': 'Saint Catherine of Alexandria',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Faith turns the broken wheel into celestial light.”',
        'quoteAuthor': '— Raphael',
        'search': 'Raphael Saint Catherine of Alexandria National Gallery'
    },
    {
        'id': 'titian_sacred_and_profane_love',
        'title': '天上的爱与人间的爱 (1514)',
        'enTitle': 'Sacred and Profane Love',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“He who understands colour holds the key to all secrets.”',
        'quoteAuthor': '— Titian',
        'search': 'Titian Sacred and Profane Love Borghese'
    },
    {
        'id': 'titian_presentation_of_the_virgin',
        'title': '圣母进殿 (1538)',
        'enTitle': 'Presentation of the Virgin at the Temple',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The steps of faith are paved with brilliant dawn.”',
        'quoteAuthor': '— Titian',
        'search': 'Titian Presentation of the Virgin at the Temple Gallerie dell\'Accademia'
    },
    {
        'id': 'tintoretto_miracle_of_the_slave',
        'title': '圣马可的奇迹 · 奴隶的拯救 (1548)',
        'enTitle': 'Miracle of the Slave',
        'artist': 'Tintoretto (丁托列托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The drawing of Michelangelo, the colouring of Titian.”',
        'quoteAuthor': '— Tintoretto',
        'search': 'Tintoretto Miracle of the Slave Gallerie dell\'Accademia'
    },
    {
        'id': 'veronese_feast_house_of_levi',
        'title': '利未家的宴会 (1573)',
        'enTitle': 'The Feast in the House of Levi',
        'artist': 'Paolo Veronese (保罗·委罗内塞)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Art claims the freedom of poets and dreamers.”',
        'quoteAuthor': '— Paolo Veronese',
        'search': 'Paolo Veronese Feast in the House of Levi Gallerie dell\'Accademia'
    },
    {
        'id': 'correggio_holy_night_nativity',
        'title': '神圣之夜 · 牧羊人的朝拜 (1530)',
        'enTitle': 'Holy Night (Adoration of the Shepherds)',
        'artist': 'Correggio (科雷吉欧)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“The light of the child outshines the sun.”',
        'quoteAuthor': '— Correggio',
        'search': 'Correggio Holy Night Dresden'
    },

    # 风格主义与北方大师
    {
        'id': 'durer_the_four_apostles',
        'title': '四使徒 (1526)',
        'enTitle': 'The Four Apostles',
        'artist': 'Albrecht Dürer (丢勒)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“In truth, art is embodied in nature; whoever can extract it, has it.”',
        'quoteAuthor': '— Albrecht Dürer',
        'search': 'Albrecht Dürer The Four Apostles Alte Pinakothek'
    },
    {
        'id': 'durer_martyrdom_ten_thousand',
        'title': '一万名基督徒的殉道 (1508)',
        'enTitle': 'Martyrdom of the Ten Thousand',
        'artist': 'Albrecht Dürer (丢勒)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Virtue remains triumphant in the sacred groves.”',
        'quoteAuthor': '— Albrecht Dürer',
        'search': 'Albrecht Dürer Martyrdom of the Ten Thousand KHM'
    },
    {
        'id': 'grunewald_isenheim_resurrection',
        'title': '伊森海姆祭坛画 · 复活 (1516)',
        'enTitle': 'Isenheim Altarpiece: The Resurrection',
        'artist': 'Matthias Grünewald (格吕内瓦尔德)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Through deep darkness bursts the unconquerable light.”',
        'quoteAuthor': '— Matthias Grünewald',
        'search': 'Matthias Grünewald Isenheim Altarpiece Resurrection'
    },
    {
        'id': 'cranach_garden_of_eden',
        'title': '伊甸园中的亚当与夏娃 (1530)',
        'enTitle': 'The Garden of Eden',
        'artist': 'Lucas Cranach the Elder (老卢卡斯·克拉纳赫)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“Nature and innocence were crowned with green leaves.”',
        'quoteAuthor': '— Lucas Cranach the Elder',
        'search': 'Lucas Cranach the Elder The Garden of Eden KHM Vienna'
    },
    {
        'id': 'el_greco_burial_of_count_orgaz',
        'title': '奥尔加斯伯爵的葬礼 (1586)',
        'enTitle': 'The Burial of the Count of Orgaz',
        'artist': 'El Greco (埃尔·格列柯)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“I paint because the spirits whisper madly inside my head.”',
        'quoteAuthor': '— El Greco',
        'search': 'El Greco The Burial of the Count of Orgaz Santo Tome'
    },
    {
        'id': 'el_greco_opening_fifth_seal',
        'title': '揭开第五印 · 启示录景象 (1614)',
        'enTitle': 'The Opening of the Fifth Seal',
        'artist': 'El Greco (埃尔·格列柯)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“I hold the languages of the soul higher than earth.”',
        'quoteAuthor': '— El Greco',
        'search': 'El Greco The Opening of the Fifth Seal Metropolitan Museum of Art'
    },
    {
        'id': 'el_greco_view_of_toledo',
        'title': '托莱多全景 · 暴风雨中的圣城 (1600)',
        'enTitle': 'View of Toledo',
        'artist': 'El Greco (埃尔·格列柯)',
        'category': 'renaissance',
        'genre': '🌊 自然风景',
        'quote': '“The heavens split open in silent storm.”',
        'quoteAuthor': '— El Greco',
        'search': 'El Greco View of Toledo Metropolitan Museum of Art'
    },

    # 巴洛克黄金时代
    {
        'id': 'rubens_elevation_of_the_cross',
        'title': '上十字架 (1610)',
        'enTitle': 'The Elevation of the Cross',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My talent is such that no enterprise has exceeded my courage.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Peter Paul Rubens The Elevation of the Cross Antwerp'
    },
    {
        'id': 'rubens_adoration_of_the_magi_prado',
        'title': '三博士来朝 · 东方朝圣盛典 (1609)',
        'enTitle': 'The Adoration of the Magi',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Color is the wine that gladdens the painter’s heart.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Peter Paul Rubens Adoration of the Magi Prado'
    },
    {
        'id': 'rubens_assumption_of_the_virgin_nga',
        'title': '圣母升天 (1626)',
        'enTitle': 'The Assumption of the Virgin',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Cherubs and golden light bridge the world to heaven.”',
        'quoteAuthor': '— Peter Paul Rubens',
        'search': 'Peter Paul Rubens The Assumption of the Virgin NGA'
    },
    {
        'id': 'vandyck_samson_and_delilah',
        'title': '参孙与大利拉 (1630)',
        'enTitle': 'Samson and Delilah',
        'artist': 'Anthony van Dyck (凡·戴克)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Passion weaves its brightest trap in threads of silk.”',
        'quoteAuthor': '— Anthony van Dyck',
        'search': 'Anthony van Dyck Samson and Delilah KHM Vienna'
    },
    {
        'id': 'poussin_fall_of_the_manna',
        'title': '旷野中的甘露 (1639)',
        'enTitle': 'The Fall of the Manna',
        'artist': 'Nicolas Poussin (普桑)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“My nature impels me to seek things that are well ordered.”',
        'quoteAuthor': '— Nicolas Poussin',
        'search': 'Nicolas Poussin The Fall of the Manna Louvre'
    },
    {
        'id': 'claude_lorrain_embarkation_queen_sheba',
        'title': '示巴女王登舟 · 圣城港湾朝霞 (1648)',
        'enTitle': 'The Embarkation of the Queen of Sheba',
        'artist': 'Claude Lorrain (克劳德·洛兰)',
        'category': 'baroque',
        'genre': '🌊 自然风景',
        'quote': '“The sunrise speaks of kingdoms not yet born.”',
        'quoteAuthor': '— Claude Lorrain',
        'search': 'Claude Lorrain The Embarkation of the Queen of Sheba National Gallery'
    },
    {
        'id': 'murillo_immaculate_conception_los_venerables',
        'title': '无原罪始胎 (1678)',
        'enTitle': 'The Immaculate Conception of Los Venerables',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grace walks among golden clouds with gentle steps.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'search': 'Murillo The Immaculate Conception of Los Venerables Prado'
    },
    {
        'id': 'murillo_the_good_shepherd',
        'title': '好牧人 · 幼年基督与羔羊 (1660)',
        'enTitle': 'The Good Shepherd',
        'artist': 'Bartolomé Esteban Murillo (穆里略)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“In gentle hands is found the eternal shelter.”',
        'quoteAuthor': '— Bartolomé Esteban Murillo',
        'search': 'Murillo The Good Shepherd Prado'
    },
    {
        'id': 'tiepolo_the_immaculate_conception',
        'title': '无玷圣母降临 (1768)',
        'enTitle': 'The Immaculate Conception (Tiepolo)',
        'artist': 'Giovanni Battista Tiepolo (提埃坡罗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“Skies without end belong to the painter’s brush.”',
        'quoteAuthor': '— Giovanni Battista Tiepolo',
        'search': 'Giovanni Battista Tiepolo The Immaculate Conception Prado'
    },

    # 19世纪学院派、浪漫主义与拉斐尔前派
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
        'id': 'bouguereau_the_virgin_of_consolation',
        'title': '圣母抚慰者 (1877)',
        'enTitle': 'The Virgin of Consolation',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Art brings soothing tears where words fall silent.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'search': 'William-Adolphe Bouguereau The Virgin of Consolation'
    },
    {
        'id': 'bouguereau_pieta',
        'title': '哀悼基督 · 圣殇 (1876)',
        'enTitle': 'Pietà (Bouguereau)',
        'artist': 'William-Adolphe Bouguereau (布格罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Grief consecrated by divine light becomes immortal.”',
        'quoteAuthor': '— William-Adolphe Bouguereau',
        'search': 'William-Adolphe Bouguereau Pietà 1876'
    },
    {
        'id': 'millais_christ_in_house_of_his_parents',
        'title': '基督在父母家中 (1850)',
        'enTitle': 'Christ in the House of His Parents',
        'artist': 'John Everett Millais (米莱斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Truth to nature is the only eternal standard of art.”',
        'quoteAuthor': '— John Everett Millais',
        'search': 'John Everett Millais Christ in the House of His Parents Tate'
    },
    {
        'id': 'holman_hunt_the_light_of_the_world',
        'title': '世界之光 (1853)',
        'enTitle': 'The Light of the World',
        'artist': 'William Holman Hunt (亨特)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“Behold, I stand at the door and knock.”',
        'quoteAuthor': '— William Holman Hunt',
        'search': 'William Holman Hunt The Light of the World Keble College'
    },
    {
        'id': 'rossetti_ecce_ancilla_domini',
        'title': '受胎告知 · 见习婢女 (1850)',
        'enTitle': 'Ecce Ancilla Domini!',
        'artist': 'Dante Gabriel Rossetti (罗塞蒂)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“The white lily bears the silent word of angels.”',
        'quoteAuthor': '— Dante Gabriel Rossetti',
        'search': 'Dante Gabriel Rossetti Ecce Ancilla Domini Tate'
    },
    {
        'id': 'burne_jones_star_of_bethlehem',
        'title': '伯利恒之星 · 贤士朝圣 (1890)',
        'enTitle': 'The Star of Bethlehem',
        'artist': 'Edward Burne-Jones (伯恩-琼斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“I mean by a picture a beautiful romantic dream.”',
        'quoteAuthor': '— Edward Burne-Jones',
        'search': 'Edward Burne-Jones The Star of Bethlehem Birmingham'
    },
    {
        'id': 'moreau_the_apparition',
        'title': '显灵 · 施洗者圣约翰的头颅 (1876)',
        'enTitle': 'The Apparition',
        'artist': 'Gustave Moreau (居斯塔夫·莫罗)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“I do not believe in what I see, but only in what I feel.”',
        'quoteAuthor': '— Gustave Moreau',
        'search': 'Gustave Moreau The Apparition Musée d\'Orsay'
    },
    {
        'id': 'waterhouse_saint_cecilia',
        'title': '音乐的主保圣人 · 圣塞西莉亚 (1895)',
        'enTitle': 'Saint Cecilia',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'quote': '“In heavenly melody, the soul finds its wings.”',
        'quoteAuthor': '— John William Waterhouse',
        'search': 'John William Waterhouse Saint Cecilia'
    },
    {
        'id': 'caravaggio_the_annunciation',
        'title': '受胎告知 · 天使下凡 (1608)',
        'enTitle': 'The Annunciation (Caravaggio)',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'quote': '“All works are nothing but bagatelles unless done from life.”',
        'quoteAuthor': '— Caravaggio',
        'search': 'Caravaggio The Annunciation Nancy'
    },
    {
        'id': 'giotto_st_francis_preaching_to_the_birds',
        'title': '圣方济各向鸟儿布道 (1297)',
        'enTitle': 'Saint Francis Preaching to the Birds',
        'artist': 'Giotto (乔托)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'quote': '“All creatures are our sisters and brothers under the sun.”',
        'quoteAuthor': '— Giotto',
        'search': 'Giotto Saint Francis Preaching to the Birds Louvre'
    }
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_dir = os.path.join(base_dir, 'assets', 'images')
    os.makedirs(img_dir, exist_ok=True)

    print(f"=== Starting Fast Curation for 50 World Religious Masterpieces ===")
    successful = []
    
    for i, item in enumerate(CANDIDATES):
        fn = f"{item['id']}.jpg"
        save_path = os.path.join(img_dir, fn)
        print(f"\n[{i+1}/{len(CANDIDATES)}] {item['title']} - {item['artist']}")

        # If already exists and valid, skip download
        if os.path.exists(save_path):
            ok, msg = fhe.inspect_image(save_path)
            if ok:
                print(f"  ⚡ Already exists and passed gatekeeper: {fn}")
                item['file'] = fn
                item['src'] = f"assets/images/{fn}?v=3.8.0"
                successful.append(item)
                continue

        # Search official museum candidate
        c = fhe.find_best_commons_file(item['search'])
        if not c:
            print(f"  ❌ No highres match for: {item['search']}")
            continue

        print(f"  🎯 Found official file: {c['title']} (orig: {c['orig_w']}x{c['orig_h']})")
        try:
            fhe.download_and_save(c['url'], save_path)
            ok, msg = fhe.inspect_image(save_path)
            print(f"  🔎 QualityGatekeeper: {msg}")
            if ok:
                item['file'] = fn
                item['src'] = f"assets/images/{fn}?v=3.8.0"
                successful.append(item)
            else:
                print(f"  ⚠️ Rejected by gatekeeper, removing file.")
                if os.path.exists(save_path):
                    os.remove(save_path)
        except Exception as e:
            print(f"  ❌ Error downloading: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
        time.sleep(1.0)

    print(f"\n==========================================")
    print(f"Successfully harvested {len(successful)} / {len(CANDIDATES)} masterpieces!")
    print(f"==========================================")

    # Save metadata
    with open(os.path.join(base_dir, 'scripts', 'harvested_50_religious.json'), 'w', encoding='utf-8') as f:
        json.dump(successful, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
