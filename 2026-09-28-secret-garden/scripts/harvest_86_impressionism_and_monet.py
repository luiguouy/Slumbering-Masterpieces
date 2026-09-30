import os
import sys
import json
import time
import urllib.request
import urllib.parse
from PIL import Image

# 引入博物馆采集团队引擎
from museum_harvester import MuseumHarvester, QualityGatekeeper

TARGET_86_ARTWORKS = [
    # ========================================================
    # 板块一：印象派群星名家杰作 (50幅)
    # ========================================================
    # --- 1. 皮埃尔-奥古斯特·雷诺阿 (8幅) ---
    {
        'id': 'renoir_two_sisters_terrace',
        'title': '两姐妹 · 露台 (1881)',
        'enTitle': 'Two Sisters (On the Terrace)',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1881',
        'quote': '“The pain passes, but the beauty remains.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Pierre-Auguste Renoir Two Sisters On the Terrace'
    },
    {
        'id': 'renoir_the_loge',
        'title': '包厢 (1874)',
        'enTitle': 'La Loge (The Theatre Box)',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1874',
        'quote': '“Why shouldn’t art be pretty? There are enough unpleasant things in the world.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Pierre-Auguste Renoir La Loge Courtauld'
    },
    {
        'id': 'renoir_girls_at_piano',
        'title': '弹钢琴的少女 (1892)',
        'enTitle': 'Girls at the Piano',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1892',
        'quote': '“One must from time to time attempt things that are beyond one\'s capacity.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Pierre-Auguste Renoir Girls at the Piano d\'Orsay'
    },
    {
        'id': 'renoir_madame_charpentier',
        'title': '夏庞蒂埃夫人及子女像 (1878)',
        'enTitle': 'Madame Georges Charpentier and Her Children',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1878',
        'quote': '“A picture must be an amiable thing, joyous and pretty.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Renoir Madame Georges Charpentier and Her Children Met'
    },
    {
        'id': 'renoir_nude_in_sunlight',
        'title': '阳光下的裸女 (1875)',
        'enTitle': 'Nude in the Sunlight (Torso, sun effect)',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1875',
        'quote': '“I arrange my subject as I like, and then I begin to paint.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Pierre-Auguste Renoir Torso, sun effect d\'Orsay'
    },
    {
        'id': 'renoir_young_girl_combing_hair',
        'title': '梳头的少女 (1894)',
        'enTitle': 'Young Girl Combing Her Hair',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1894',
        'quote': '“The work of art must seize upon you, wrap you up in itself.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Renoir Young Girl Combing Her Hair'
    },
    {
        'id': 'renoir_jeanne_samary',
        'title': '女演员让娜·萨马里像 (1877)',
        'enTitle': 'Portrait of the Actress Jeanne Samary',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1877',
        'quote': '“Colour is the fruit of life.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Renoir Portrait of Jeanne Samary Pushkin'
    },
    {
        'id': 'renoir_the_skiff',
        'title': '塞纳河上的小艇 (1875)',
        'enTitle': 'The Skiff (La Yole)',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1875',
        'quote': '“You come to nature with all your theories, and she knocks them all flat.”',
        'quoteAuthor': '— Pierre-Auguste Renoir',
        'search': 'Pierre-Auguste Renoir The Skiff La Yole National Gallery'
    },

    # --- 2. 爱德华·马奈 (6幅) ---
    {
        'id': 'manet_the_fifer',
        'title': '吹短笛的男孩 (1866)',
        'enTitle': 'The Fifer (Le Fifre)',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1866',
        'quote': '“There is only one true thing: instantly paint what you see.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Édouard Manet The Fifer Le Fifre d\'Orsay'
    },
    {
        'id': 'manet_the_balcony',
        'title': '阳台 (1868)',
        'enTitle': 'The Balcony (Le Balcon)',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1868',
        'quote': '“Color is a matter of taste and of sensibility.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Édouard Manet The Balcony Le Balcon d\'Orsay'
    },
    {
        'id': 'manet_emile_zola',
        'title': '埃米尔·左拉像 (1868)',
        'enTitle': 'Portrait of Émile Zola',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1868',
        'quote': '“I paint what I see, and not what it pleases others to see.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Portrait of Émile Zola by Édouard Manet Orsay'
    },
    {
        'id': 'manet_grand_canal_venice',
        'title': '威尼斯大运河 (1875)',
        'enTitle': 'The Grand Canal of Venice (Blue Venice)',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1875',
        'quote': '“You must always remain master of yourself and do what you please.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Édouard Manet The Grand Canal of Venice Shelburne'
    },
    {
        'id': 'manet_in_the_conservatory',
        'title': '温室里 (1879)',
        'enTitle': 'In the Conservatory',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1879',
        'quote': '“No one can be a painter unless he cares for painting above all else.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Édouard Manet In the Conservatory Alte Nationalgalerie'
    },
    {
        'id': 'manet_spring_jeanne',
        'title': '春 · 雅娜·德马西 (1881)',
        'enTitle': 'Spring (Jeanne Demarsy)',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1881',
        'quote': '“Concision in art is a necessity and an elegance.”',
        'quoteAuthor': '— Édouard Manet',
        'search': 'Édouard Manet Spring Jeanne Getty'
    },

    # --- 3. 埃德加·德加 (8幅) ---
    {
        'id': 'degas_dancers_at_the_barre',
        'title': '把杆上的舞者 (1888)',
        'enTitle': 'Dancers at the Barre',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1888',
        'quote': '“Art is not what you see, but what you make others see.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas Dancers at the Barre Phillips'
    },
    {
        'id': 'degas_orchestra_of_the_opera',
        'title': '歌剧院管弦乐团 (1870)',
        'enTitle': 'The Orchestra of the Opera',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '⚔️ 历史叙事',
        'year': '1870',
        'quote': '“Painting is easy when you don\'t know how, but very difficult when you do.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas The Orchestra of the Opera d\'Orsay'
    },
    {
        'id': 'degas_cotton_office_new_orleans',
        'title': '新奥尔良棉花交易所 (1873)',
        'enTitle': 'A Cotton Office in New Orleans',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '⚔️ 历史叙事',
        'year': '1873',
        'quote': '“Daylight is too easy. What I want is difficult: the atmosphere of lamps and gas.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas A Cotton Office in New Orleans Pau'
    },
    {
        'id': 'degas_rehearsal_on_stage',
        'title': '舞台上的芭蕾排练 (1874)',
        'enTitle': 'Rehearsal on Stage',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1874',
        'quote': '“Make a drawing, begin it again, trace it; begin it again, and trace it again.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas Rehearsal on Stage Met'
    },
    {
        'id': 'degas_the_tub',
        'title': '盆浴 (1886)',
        'enTitle': 'The Tub (Le Tub)',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1886',
        'quote': '“A picture is something which requires as much knavery, trickery, and deceit as the perpetration of a crime.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas The Tub Le Tub d\'Orsay'
    },
    {
        'id': 'degas_racehorses_before_stands',
        'title': '看台前的赛马 (1868)',
        'enTitle': 'Racehorses before the Stands',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1868',
        'quote': '“The secret is to follow the advice the masters gave: draw lines, many lines.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas Racehorses before the Stands d\'Orsay'
    },
    {
        'id': 'degas_women_ironing',
        'title': '熨衣妇 (1884)',
        'enTitle': 'Women Ironing (Repasseuses)',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1884',
        'quote': '“One gives idea of truth with the aid of the artificial.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas Women Ironing d\'Orsay'
    },
    {
        'id': 'degas_blue_dancers',
        'title': '蓝衣舞者 (1897)',
        'enTitle': 'Blue Dancers (Danseuses bleues)',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1897',
        'quote': '“I am a colorist with line.”',
        'quoteAuthor': '— Edgar Degas',
        'search': 'Edgar Degas Blue Dancers Danseuses bleues'
    },

    # --- 4. 卡米耶·毕沙罗 (8幅) ---
    {
        'id': 'pissarro_the_red_roofs',
        'title': '蓬图瓦兹的红屋顶 (1877)',
        'enTitle': 'The Red Roofs (Les toits rouges)',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1877',
        'quote': '“Blessed are they who see beautiful things in humble places where other people see nothing.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro The Red Roofs Les toits rouges d\'Orsay'
    },
    {
        'id': 'pissarro_boulevard_montmartre_night',
        'title': '夜幕下的蒙马特大道 (1897)',
        'enTitle': 'The Boulevard Montmartre at Night',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1897',
        'quote': '“Work at the same time on sky, water, branches, ground, keeping everything going on an equal basis.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro The Boulevard Montmartre at Night National Gallery'
    },
    {
        'id': 'pissarro_boulevard_montmartre_winter',
        'title': '冬日晨曦中的蒙马特大道 (1897)',
        'enTitle': 'Boulevard Montmartre, Winter Morning',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1897',
        'quote': '“Everything is beautiful, the whole secret is in knowing how to interpret it.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro Boulevard Montmartre, Winter Morning Met'
    },
    {
        'id': 'pissarro_garden_hermitage_pontoise',
        'title': '蓬图瓦兹赫米塔日花园 (1877)',
        'enTitle': 'The Garden of the Hermitage, Pontoise',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1877',
        'quote': '“Paint the essential character of things.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro The Garden of the Hermitage, Pontoise'
    },
    {
        'id': 'pissarro_self_portrait',
        'title': '自画像 (1903)',
        'enTitle': 'Self-Portrait',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1903',
        'quote': '“I will only stop working when I stop breathing.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro Self-Portrait 1903 Tate'
    },
    {
        'id': 'pissarro_great_bridge_rouen',
        'title': '鲁昂的大桥 (1896)',
        'enTitle': 'The Great Bridge at Rouen',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1896',
        'quote': '“It is only by drawing often, drawing everything, drawing incessantly, that you find rhythm.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro The Great Bridge at Rouen Carnegie'
    },
    {
        'id': 'pissarro_climbing_path_hermitage',
        'title': '通往赫米塔日的小径 (1875)',
        'enTitle': 'The Climbing Path at the Hermitage',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1875',
        'quote': '“Do not define too closely the outlines of things; it is the brush stroke of the right value and color which should produce the drawing.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro The Climbing Path at the Hermitage Brooklyn'
    },
    {
        'id': 'pissarro_peasant_woman_washing',
        'title': '洗晒衣物的农妇 (1887)',
        'enTitle': 'Peasant Woman Hanging Washing',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1887',
        'quote': '“I am only happy when I work.”',
        'quoteAuthor': '— Camille Pissarro',
        'search': 'Camille Pissarro Peasant Woman Hanging Washing d\'Orsay'
    },

    # --- 5. 阿尔弗雷德·西斯莱 (6幅) ---
    {
        'id': 'sisley_bridge_at_moret',
        'title': '莫雷桥 · 夏日晴空 (1893)',
        'enTitle': 'The Bridge at Moret',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1893',
        'quote': '“Every picture shows a spot with which the artist has fallen in love.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley The Bridge at Moret d\'Orsay'
    },
    {
        'id': 'sisley_snow_at_louveciennes',
        'title': '鲁沃谢讷的雪景 (1878)',
        'enTitle': 'Snow at Louveciennes',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1878',
        'quote': '“The sky cannot be only a background... it gives movement.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley Snow at Louveciennes d\'Orsay'
    },
    {
        'id': 'sisley_canal_saint_martin',
        'title': '圣马丁运河景致 (1870)',
        'enTitle': 'View of the Canal Saint-Martin',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1870',
        'quote': '“The animation of the canvas is one of the greatest difficulties of painting.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley View of the Canal Saint-Martin d\'Orsay'
    },
    {
        'id': 'sisley_road_to_louveciennes',
        'title': '通往鲁沃谢讷的道路 (1879)',
        'enTitle': 'The Road from Versailles to Louveciennes',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1879',
        'quote': '“I always begin by painting the sky.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley The Road from Versailles to Louveciennes'
    },
    {
        'id': 'sisley_bridge_at_argenteuil',
        'title': '阿让特伊的小桥 (1872)',
        'enTitle': 'The Bridge at Argenteuil',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1872',
        'quote': '“To give life to the work of art is certainly one of the most arduous tasks of the painter.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley Bridge at Argenteuil 1872'
    },
    {
        'id': 'sisley_meadow_spring',
        'title': '春日的草甸 (1880)',
        'enTitle': 'The Small Meadows in Spring',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1880',
        'quote': '“Sun and water are the soul of landscape.”',
        'quoteAuthor': '— Alfred Sisley',
        'search': 'Alfred Sisley The Small Meadows in Spring National Gallery'
    },

    # --- 6. 居斯塔夫·卡耶博特 (4幅) ---
    {
        'id': 'caillebotte_the_floor_scrapers',
        'title': '刨地板工人 (1875)',
        'enTitle': 'The Floor Scrapers (Les raboteurs de parquet)',
        'artist': 'Gustave Caillebotte (居斯塔夫·卡耶博特)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1875',
        'quote': '“Art is modern life seen with modern eyes.”',
        'quoteAuthor': '— Gustave Caillebotte',
        'search': 'Gustave Caillebotte The Floor Scrapers Les raboteurs de parquet'
    },
    {
        'id': 'caillebotte_pont_de_l_europe',
        'title': '欧洲桥 (1876)',
        'enTitle': 'Le Pont de l\'Europe',
        'artist': 'Gustave Caillebotte (居斯塔夫·卡耶博特)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1876',
        'quote': '“The iron and stone of Paris hold their own poetry.”',
        'quoteAuthor': '— Gustave Caillebotte',
        'search': 'Gustave Caillebotte Le Pont de l\'Europe'
    },
    {
        'id': 'caillebotte_young_man_at_window',
        'title': '窗前的年轻男子 (1876)',
        'enTitle': 'Young Man at His Window',
        'artist': 'Gustave Caillebotte (居斯塔夫·卡耶博特)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1876',
        'quote': '“A quiet glance can hold the entire city.”',
        'quoteAuthor': '— Gustave Caillebotte',
        'search': 'Gustave Caillebotte Young Man at His Window Getty'
    },
    {
        'id': 'caillebotte_boating_on_yerres',
        'title': '耶尔河上的泛舟者 (1877)',
        'enTitle': 'Boating on the Yerres (Skiffs)',
        'artist': 'Gustave Caillebotte (居斯塔夫·卡耶博特)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1877',
        'quote': '“The water is alive with every dip of the oar.”',
        'quoteAuthor': '— Gustave Caillebotte',
        'search': 'Gustave Caillebotte Boating on the Yerres Skiffs'
    },

    # --- 7. 莫里索 & 卡萨特 (女性印象派双璧 · 6幅) ---
    {
        'id': 'morisot_the_cradle',
        'title': '摇篮 (1872)',
        'enTitle': 'The Cradle (Le Berceau)',
        'artist': 'Berthe Morisot (贝尔特·莫里索)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1872',
        'quote': '“It is important to express oneself... Provided the feelings are real and taken from your own experience.”',
        'quoteAuthor': '— Berthe Morisot',
        'search': 'Berthe Morisot The Cradle Le Berceau d\'Orsay'
    },
    {
        'id': 'morisot_reading_green_parasol',
        'title': '阅读 · 绿荫下的女子 (1873)',
        'enTitle': 'Reading (The Green Parasol)',
        'artist': 'Berthe Morisot (贝尔特·莫里索)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1873',
        'quote': '“Real painters understand with a brush in their hand.”',
        'quoteAuthor': '— Berthe Morisot',
        'search': 'Berthe Morisot Reading Cleveland'
    },
    {
        'id': 'morisot_woman_at_toilette',
        'title': '梳妆台前的女人 (1875)',
        'enTitle': 'Woman at Her Toilette',
        'artist': 'Berthe Morisot (贝尔特·莫里索)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1875',
        'quote': '“My ambition is limited to capturing something fleeting.”',
        'quoteAuthor': '— Berthe Morisot',
        'search': 'Berthe Morisot Woman at Her Toilette Art Institute of Chicago'
    },
    {
        'id': 'cassatt_the_boating_party',
        'title': '划船派对 (1893)',
        'enTitle': 'The Boating Party',
        'artist': 'Mary Cassatt (玛丽·卡萨特)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1893',
        'quote': '“I have touched with a sense of art some people — they felt the love and the life.”',
        'quoteAuthor': '— Mary Cassatt',
        'search': 'Mary Cassatt The Boating Party National Gallery of Art'
    },
    {
        'id': 'cassatt_the_childs_bath',
        'title': '浴室 / 孩童的足浴 (1893)',
        'enTitle': 'The Child\'s Bath',
        'artist': 'Mary Cassatt (玛丽·卡萨特)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1893',
        'quote': '“There are two ways of painting: one is for the eye, the other is for the mind.”',
        'quoteAuthor': '— Mary Cassatt',
        'search': 'Mary Cassatt The Child\'s Bath Art Institute of Chicago'
    },
    {
        'id': 'cassatt_cup_of_tea',
        'title': '茶会 (1880)',
        'enTitle': 'The Cup of Tea',
        'artist': 'Mary Cassatt (玛丽·卡萨特)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1880',
        'quote': '“I hated conventional art. I began to live when I first saw Degas\' pastels.”',
        'quoteAuthor': '— Mary Cassatt',
        'search': 'Mary Cassatt The Cup of Tea Met'
    },

    # --- 8. 巴齐耶、索罗拉、哈萨姆 (4幅) ---
    {
        'id': 'bazille_studio_rue_condamine',
        'title': '孔达米纳街的画室 (1870)',
        'enTitle': 'Bazille\'s Studio',
        'artist': 'Frédéric Bazille (弗雷德里克·巴齐耶)',
        'category': 'impressionism',
        'genre': '⚔️ 历史叙事',
        'year': '1870',
        'quote': '“For me, painting is a passion that devours everything else.”',
        'quoteAuthor': '— Frédéric Bazille',
        'search': 'Frédéric Bazille Bazille\'s Studio d\'Orsay'
    },
    {
        'id': 'bazille_family_reunion',
        'title': '家庭重聚 (1867)',
        'enTitle': 'The Family Reunion',
        'artist': 'Frédéric Bazille (弗雷德里克·巴齐耶)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1867',
        'quote': '“The sunlight on the terrace makes every face a portrait of eternity.”',
        'quoteAuthor': '— Frédéric Bazille',
        'search': 'Frédéric Bazille The Family Reunion d\'Orsay'
    },
    {
        'id': 'sorolla_walk_on_the_beach',
        'title': '海滩漫步 (1909)',
        'enTitle': 'Walk on the Beach (Paseo a orillas del mar)',
        'artist': 'Joaquín Sorolla (华金·索罗拉)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'year': '1909',
        'quote': '“I could not paint at all if I had to paint slowly... Light changes every second.”',
        'quoteAuthor': '— Joaquín Sorolla',
        'search': 'Joaquín Sorolla Paseo a orillas del mar'
    },
    {
        'id': 'hassam_boston_common_twilight',
        'title': '雨中的波士顿公地 (1886)',
        'enTitle': 'Boston Common at Twilight',
        'artist': 'Childe Hassam (柴尔德·哈萨姆)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'year': '1886',
        'quote': '“The man who will go down to posterity is the man who paints his own time.”',
        'quoteAuthor': '— Childe Hassam',
        'search': 'Childe Hassam Boston Common at Twilight'
    },

    # ========================================================
    # 板块二：莫奈经典风光、人物与旅途系列 (24幅)
    # ========================================================
    {
        'id': 'monet_the_magpie',
        'title': '喜鹊 (1869)',
        'enTitle': 'The Magpie (La Pie)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1869',
        'quote': '“Colour is my day-long obsession, joy and torment.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Magpie La Pie d\'Orsay'
    },
    {
        'id': 'monet_breakup_of_ice',
        'title': '塞纳河破冰 (1880)',
        'enTitle': 'The Breakup of the Ice, Vétheuil',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1880',
        'quote': '“I want to paint the air in which the bridge, the house, and the boat exist.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Breakup of the Ice Vétheuil'
    },
    {
        'id': 'monet_wheatstacks_snow_morning',
        'title': '吉维尼雪中的干草堆 (1891)',
        'enTitle': 'Wheatstacks, Snow Effect, Morning',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1891',
        'quote': '“For me, a landscape hardly exists at all in its own right; its appearance changes at every moment.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Wheatstacks, Snow Effect, Morning Art Institute of Chicago'
    },
    {
        'id': 'monet_winter_sunlight_giverny',
        'title': '冬日的吉维尼小径 (1885)',
        'enTitle': 'Winter Sunlight, Giverny',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1885',
        'quote': '“Every moment is a new dawn of light.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Winter Sunlight, Giverny'
    },
    {
        'id': 'monet_cliff_etretat_sunset',
        'title': '象鼻山 · 埃特尔塔悬崖与海门 (1883)',
        'enTitle': 'The Cliff, Étretat, Sunset',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1883',
        'quote': '“I am chasing after a ray of light, even the slightest gleam.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Cliff, Étretat, Sunset'
    },
    {
        'id': 'monet_needle_rock_belle_ile',
        'title': '贝利尔岛狂风巨浪 · 针岩 (1886)',
        'enTitle': 'The Needle Rock at Port-Coton, Belle-Île',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1886',
        'quote': '“The sea is terrifyingly grand, and the rocks are sinister and savage.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Needle Rock at Port-Coton Belle-Île'
    },
    {
        'id': 'monet_antibes_salis',
        'title': '昂蒂布海景 · 从萨利花园眺望 (1888)',
        'enTitle': 'Antibes Seen from the Salis Gardens',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1888',
        'quote': '“Here you swim in blue air, and the sea is pure gold.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Antibes Seen from the Salis Gardens Toledo'
    },
    {
        'id': 'monet_villas_at_bordighera',
        'title': '博尔迪盖拉的别墅 (1884)',
        'enTitle': 'Villas at Bordighera',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1884',
        'quote': '“I am in a fairy wonderland, I don’t know where to look first.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Villas at Bordighera'
    },
    {
        'id': 'monet_low_tide_pourville',
        'title': '普尔维尔低潮时的海滩 (1882)',
        'enTitle': 'Low Tide at Pourville',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1882',
        'quote': '“The richness I achieve comes from nature, the source of my inspiration.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Low Tide at Pourville Cleveland'
    },
    {
        'id': 'monet_rough_sea_etretat',
        'title': '埃特尔塔的风暴海浪 (1883)',
        'enTitle': 'Rough Sea at Étretat',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1883',
        'quote': '“I want to seize the impossible: the spray of crashing waves.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Rough Sea at Étretat Lyon'
    },
    {
        'id': 'monet_la_japonaise',
        'title': '穿日本和服的卡米尔 (1876)',
        'enTitle': 'Madame Monet in a Japanese Kimono (La Japonaise)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '👤 人物肖像',
        'year': '1876',
        'quote': '“The eye should learn to see before the hand learns to trace.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Madame Monet in a Japanese Kimono La Japonaise'
    },
    {
        'id': 'monet_the_red_kerchief',
        'title': '红围巾 · 莫奈夫人画像 (1873)',
        'enTitle': 'The Red Kerchief: Portrait of Camille Monet',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '👤 人物肖像',
        'year': '1873',
        'quote': '“Love and light are the identical flame in my brush.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Red Kerchief Portrait of Camille Monet Cleveland'
    },
    {
        'id': 'monet_woman_parasol_left',
        'title': '撑阳伞的女人 · 面向左方 (1886)',
        'enTitle': 'Woman with a Parasol, Facing Left',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '👤 人物肖像',
        'year': '1886',
        'quote': '“I paint as a bird sings.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Woman with a Parasol, Facing Left d\'Orsay'
    },
    {
        'id': 'monet_woman_parasol_right',
        'title': '撑阳伞的女人 · 面向右方 (1886)',
        'enTitle': 'Woman with a Parasol, Facing Right',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '👤 人物肖像',
        'year': '1886',
        'quote': '“Light is the true actor on my canvas.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Woman with a Parasol, Facing Right d\'Orsay'
    },
    {
        'id': 'monet_san_giorgio_maggiore_dusk',
        'title': '威尼斯圣乔治马焦雷教堂黄昏 (1908)',
        'enTitle': 'San Giorgio Maggiore at Dusk',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1908',
        'quote': '“Venice is too beautiful to paint; it is a miracle of light.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet San Giorgio Maggiore at Dusk'
    },
    {
        'id': 'monet_doges_palace',
        'title': '威尼斯总督宫 (1908)',
        'enTitle': 'The Doge\'s Palace',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1908',
        'quote': '“The water trembles with the reflection of marble palaces.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Doge\'s Palace Brooklyn'
    },
    {
        'id': 'monet_charing_cross_bridge',
        'title': '伦敦查令十字桥 (1899)',
        'enTitle': 'Charing Cross Bridge',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1899',
        'quote': '“Without the fog, London would not be a beautiful city.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Charing Cross Bridge Thyssen'
    },
    {
        'id': 'monet_houses_of_parliament_seagulls',
        'title': '伦敦国会大厦 · 海鸥与波光 (1904)',
        'enTitle': 'The Houses of Parliament, Seagulls',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1904',
        'quote': '“It’s the fog that gives it its magnificent breadth.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Houses of Parliament, Seagulls'
    },
    {
        'id': 'monet_the_water_lily_pond_1904',
        'title': '吉维尼的睡莲池 (1904)',
        'enTitle': 'The Water Lily Pond, Giverny',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1904',
        'quote': '“One instant, one aspect of nature contains it all.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Water Lily Pond 1904 Denver'
    },
    {
        'id': 'monet_water_lilies_evening_effect',
        'title': '睡莲与倒影 · 暮色效应 (1897)',
        'enTitle': 'Water Lilies, Evening Effect',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1897',
        'quote': '“The water plants are an extension of the sky.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Evening Effect Marmottan'
    },
    {
        'id': 'monet_poppy_field_vetheuil',
        'title': '维特伊附近的野罂粟花田 (1879)',
        'enTitle': 'Poppy Field near Vétheuil',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1879',
        'quote': '“A sea of vermilion blossoms rolling over green slopes.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Poppy Field near Vétheuil'
    },
    {
        'id': 'monet_yellow_irises',
        'title': '吉维尼的黄色鸢尾花 (1914)',
        'enTitle': 'Yellow Irises with Pink Cloud',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“My garden is my most beautiful masterpiece.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Yellow Irises Marmottan'
    },
    {
        'id': 'monet_the_rose_arches',
        'title': '吉维尼玫瑰花园拱门 (1913)',
        'enTitle': 'The Rose Arches, Giverny',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1913',
        'quote': '“All my money goes into my garden, but I am in raptures.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Rose Arches, Giverny Marmottan'
    },
    {
        'id': 'monet_water_lilies_weeping_willows',
        'title': '睡莲与垂柳 (1916)',
        'enTitle': 'Water Lilies and Weeping Willows',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1916',
        'quote': '“The willows weep over water that holds the secrets of stars.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies and Weeping Willows Marmottan'
    },

    # ========================================================
    # 板块三：莫奈《睡莲 / 荷花水景》殿堂特辑 (12幅)
    # ========================================================
    {
        'id': 'monet_water_lilies_green_reflections',
        'title': '睡莲 · 绿色倒影 (1914)',
        'enTitle': 'Water Lilies: Green Reflections',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“Water and reflection have become an obsession for me.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Green Reflections Orangerie'
    },
    {
        'id': 'monet_water_lilies_london_national',
        'title': '睡莲 · 湛蓝幽潭 (1916)',
        'enTitle': 'Water Lilies (Nymphéas)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1916',
        'quote': '“These landscapes of water and reflection have taken over my soul.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies 1916 National Gallery'
    },
    {
        'id': 'monet_water_lilies_artic_1906',
        'title': '睡莲池 · 水映浮云 (1906)',
        'enTitle': 'Water Lilies',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1906',
        'quote': '“The illusion of an endless whole, of water without horizon.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies 1906 Art Institute of Chicago'
    },
    {
        'id': 'monet_water_lilies_sunset_orangerie',
        'title': '睡莲 · 晚霞与日落 (1914)',
        'enTitle': 'Water Lilies, Sunset',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“I must have flowers, always, and always.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Sunset Orangerie'
    },
    {
        'id': 'monet_water_lilies_moma_triptych',
        'title': '睡莲巨幕长卷 (1914)',
        'enTitle': 'Water Lilies (Triptych)',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“My life has been nothing but a failure to capture what cannot be painted: light.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies MoMA'
    },
    {
        'id': 'monet_the_japanese_bridge_blaze',
        'title': '日本桥 · 烈焰与紫藤绝唱 (1920)',
        'enTitle': 'The Japanese Bridge',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1920',
        'quote': '“I paint what I feel, beyond what my weakened eyes can behold.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Japanese Bridge Marmottan'
    },
    {
        'id': 'monet_water_lilies_morning_willows',
        'title': '睡莲池 · 晨光与垂柳 (1914)',
        'enTitle': 'Water Lilies, Morning with Willows',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“Peace is born from the surface of clear water.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Morning with Willows Orangerie'
    },
    {
        'id': 'monet_water_lily_pond_orsay_1900',
        'title': '睡莲与日本桥水景 (1900)',
        'enTitle': 'Water Lily Pond and Path by the Water',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1900',
        'quote': '“I took time to understand my water-lilies... I cultivated them without thinking of painting them.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Le Bassin aux nymphéas, harmonie verte d\'Orsay'
    },
    {
        'id': 'monet_water_lilies_morning_marmottan',
        'title': '睡莲 · 清晨初绽 (1914)',
        'enTitle': 'Water Lilies, Morning',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1914',
        'quote': '“The morning light opens petals that the night had held silent.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Morning Marmottan'
    },
    {
        'id': 'monet_water_lilies_reflections_clouds',
        'title': '睡莲池 · 柳树倒影 (1920)',
        'enTitle': 'Reflections of Clouds on the Water-Lily Pond',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1920',
        'quote': '“The sky is deep inside the water.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Reflections of Clouds on the Water-Lily Pond MoMA'
    },
    {
        'id': 'monet_water_lilies_honolulu',
        'title': '睡莲与水草丛 (1917)',
        'enTitle': 'Water Lilies',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1917',
        'quote': '“Every brush stroke breathes the life of summer.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet Water Lilies Honolulu'
    },
    {
        'id': 'monet_japanese_bridge_irises_princeton',
        'title': '日本桥与紫藤花架 (1899)',
        'enTitle': 'The Japanese Bridge with Irises',
        'artist': 'Claude Monet (莫奈)',
        'category': 'monet',
        'genre': '🌿 自然风景',
        'year': '1899',
        'quote': '“My heart is forever tied to this bridge and these flowers.”',
        'quoteAuthor': '— Claude Monet',
        'search': 'Claude Monet The Japanese Bridge Princeton'
    }
]

def main():
    print(f"================================================================")
    print(f"🚀 启动 86 幅印象派与莫奈典藏名画全自动多源采集流水线")
    print(f"   - 印象派群星杰作: 50 幅")
    print(f"   - 莫奈经典风光肖像: 24 幅")
    print(f"   - 莫奈睡莲荷花殿堂: 12 幅")
    print(f"================================================================")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, 'assets', 'images')
    harvester = MuseumHarvester(output_dir=images_dir)

    success_list = []
    failed_list = []

    for idx, item in enumerate(TARGET_86_ARTWORKS, 1):
        filename = f"{item['id']}.jpg"
        filepath = os.path.join(images_dir, filename)

        print(f"\n[{idx}/86] 正在处理: 《{item['title']}》 - {item['artist']}")

        # 检查是否已有且合格
        if os.path.exists(filepath):
            passed, msg = QualityGatekeeper.inspect(filepath)
            if passed:
                print(f"  ⚡ 已存在且通过质检: {filename} ({msg}) -> 跳过下载")
                success_list.append(item)
                continue
            else:
                print(f"  ⚠️ 现有文件未达标 ({msg})，重新采集...")

        # 执行官方多源智能采集
        ok, meta = harvester.harvest(item['search'], filename)
        if ok:
            item['image'] = f"assets/images/{filename}"
            item['verified'] = True
            success_list.append(item)
        else:
            # 尝试精简搜索词二次重试
            simplified = ' '.join(item['search'].split()[:4])
            print(f"  🔄 尝试精简搜索重试: '{simplified}'...")
            ok2, meta2 = harvester.harvest(simplified, filename)
            if ok2:
                item['image'] = f"assets/images/{filename}"
                item['verified'] = True
                success_list.append(item)
            else:
                failed_list.append(item)
                print(f"  ❌ 最终未能捕获: {item['title']}")

        # 防过载保护
        time.sleep(0.5)

    print(f"\n================================================================")
    print(f"🎉 采集流水线完成统计:")
    print(f"   ✅ 成功入库并完成 4K 质检: {len(success_list)} / 86 幅")
    print(f"   ❌ 待处理/补漏: {len(failed_list)} 幅")
    print(f"================================================================")

    # 导出采集结果
    output_result_path = os.path.join(base_dir, 'scripts', 'harvest_86_result.json')
    with open(output_result_path, 'w', encoding='utf-8') as f:
        json.dump({
            'success_count': len(success_list),
            'failed_count': len(failed_list),
            'artworks': success_list,
            'failed': failed_list
        }, f, ensure_ascii=False, indent=2)
    print(f"元数据清单已暂存至: {output_result_path}")

if __name__ == '__main__':
    main()
