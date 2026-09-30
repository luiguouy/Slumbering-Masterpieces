import os
import sys
import time
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

headers = {
    'User-Agent': 'FineArtWorldHeritageBot/1.0 (https://github.com/luiguouy/Slumbering-Masterpieces; contact@worldheritage.org)'
}

dest_dir = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\assets\images'
data_file = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\data\masterpieces.js'
os.makedirs(dest_dir, exist_ok=True)

# 94 幅新增名画定义
NEW_ARTWORKS = [
    # === 1. 🏛️ 文艺复兴与北方画派 ===
    {
        'id': 'davinci_mona_lisa',
        'title': '蒙娜丽莎 (1503)',
        'enTitle': 'Mona Lisa (La Gioconda)',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'file': 'davinci_mona_lisa.jpg',
        'query': 'Leonardo da Vinci Mona Lisa Louvre',
        'quote': '“Simplicity is the ultimate sophistication.”',
        'quoteAuthor': '— Leonardo da Vinci'
    },
    {
        'id': 'davinci_last_supper',
        'title': '最后的晚餐 (1498)',
        'enTitle': 'The Last Supper',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'file': 'davinci_last_supper.jpg',
        'query': 'Leonardo da Vinci The Last Supper',
        'quote': '“The painter has the Universe in his mind and hands.”',
        'quoteAuthor': '— Leonardo da Vinci'
    },
    {
        'id': 'michelangelo_creation_of_adam',
        'title': '创世纪 · 创造亚当 (1512)',
        'enTitle': 'The Creation of Adam',
        'artist': 'Michelangelo (米开朗基罗)',
        'category': 'renaissance',
        'file': 'michelangelo_creation_of_adam.jpg',
        'query': 'Michelangelo Creation of Adam cropped',
        'quote': '“I saw the angel in the marble and carved until I set him free.”',
        'quoteAuthor': '— Michelangelo'
    },
    {
        'id': 'botticelli_birth_of_venus',
        'title': '维纳斯的诞生 (1485)',
        'enTitle': 'The Birth of Venus',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'file': 'botticelli_birth_of_venus.jpg',
        'query': 'Sandro Botticelli La nascita di Venere Google Art Project',
        'quote': '“Beauty is the harmony of celestial proportions.”',
        'quoteAuthor': '— Sandro Botticelli'
    },
    {
        'id': 'botticelli_primavera',
        'title': '春 · 普里马韦拉 (1482)',
        'enTitle': 'Primavera (Spring)',
        'artist': 'Sandro Botticelli (波提切利)',
        'category': 'renaissance',
        'file': 'botticelli_primavera.jpg',
        'query': 'Botticelli Primavera Uffizi',
        'quote': '“Where spring blossoms, the grace of heaven descends upon the earth.”',
        'quoteAuthor': '— Sandro Botticelli'
    },
    {
        'id': 'raphael_school_of_athens',
        'title': '雅典学院 (1511)',
        'enTitle': 'The School of Athens',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'file': 'raphael_school_of_athens.jpg',
        'query': 'Raphael School of Athens Vatican',
        'quote': '“Time is a vindictive bandit to steal the beauty of our former selves.”',
        'quoteAuthor': '— Raphael'
    },
    {
        'id': 'raphael_sistine_madonna',
        'title': '西斯廷圣母 (1512)',
        'enTitle': 'Sistine Madonna',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'file': 'raphael_sistine_madonna.jpg',
        'query': 'Raphael Sistine Madonna Dresden',
        'quote': '“When one is painting one does not think; one simply adores.”',
        'quoteAuthor': '— Raphael'
    },
    {
        'id': 'raphael_madonna_of_the_meadow',
        'title': '草地上的圣母 (1506)',
        'enTitle': 'Madonna of the Meadow',
        'artist': 'Raphael (拉斐尔)',
        'category': 'renaissance',
        'file': 'raphael_madonna_of_the_meadow.jpg',
        'query': 'Raffaello Sanzio Madonna del Prato',
        'quote': '“To paint is to reveal the divine tenderness hidden in the grass.”',
        'quoteAuthor': '— Raphael'
    },
    {
        'id': 'davinci_lady_with_ermine',
        'title': '抱银貂的女子 (1490)',
        'enTitle': 'Lady with an Ermine',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'file': 'davinci_lady_with_ermine.jpg',
        'query': 'Lady with an Ermine Leonardo da Vinci Czartoryski',
        'quote': '“Movement is the cause of all life.”',
        'quoteAuthor': '— Leonardo da Vinci'
    },
    {
        'id': 'van_eyck_arnolfini_portrait',
        'title': '阿诺菲尼夫妇像 (1434)',
        'enTitle': 'The Arnolfini Portrait',
        'artist': 'Jan van Eyck (扬·凡·艾克)',
        'category': 'renaissance',
        'file': 'van_eyck_arnolfini_portrait.jpg',
        'query': 'Jan van Eyck The Arnolfini Portrait National Gallery',
        'quote': '“As I can, not as I would.” (Als ich kan)',
        'quoteAuthor': '— Jan van Eyck'
    },
    {
        'id': 'bosch_garden_of_earthly_delights',
        'title': '人间乐园 (1500)',
        'enTitle': 'The Garden of Earthly Delights',
        'artist': 'Hieronymus Bosch (博斯)',
        'category': 'renaissance',
        'file': 'bosch_garden_of_earthly_delights.jpg',
        'query': 'The Garden of Earthly Delights by Bosch Prado',
        'quote': '“Poor is the mind that always uses the inventions of others and invents nothing itself.”',
        'quoteAuthor': '— Hieronymus Bosch'
    },
    {
        'id': 'bruegel_tower_of_babel',
        'title': '巴别塔 (1563)',
        'enTitle': 'The Tower of Babel',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'file': 'bruegel_tower_of_babel.jpg',
        'query': 'Pieter Bruegel the Elder The Tower of Babel Vienna',
        'quote': '“Human ambition climbs to heaven, yet earth remains beneath our feet.”',
        'quoteAuthor': '— Pieter Bruegel the Elder'
    },
    {
        'id': 'bruegel_the_hunters_in_the_snow',
        'title': '雪中猎人 (1565)',
        'enTitle': 'The Hunters in the Snow',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'file': 'bruegel_the_hunters_in_the_snow.jpg',
        'query': 'Pieter Bruegel the Elder Hunters in the Snow Vienna',
        'quote': '“In the silence of winter snow, human resilience burns like a quiet ember.”',
        'quoteAuthor': '— Pieter Bruegel the Elder'
    },
    {
        'id': 'bruegel_triumph_of_death',
        'title': '死神的胜利 (1562)',
        'enTitle': 'The Triumph of Death',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'file': 'bruegel_triumph_of_death.jpg',
        'query': 'The Triumph of Death by Pieter Bruegel the Elder Prado',
        'quote': '“All worldly glory fades before the great equalizer.”',
        'quoteAuthor': '— Pieter Bruegel the Elder'
    },
    {
        'id': 'bruegel_parable_of_the_blind',
        'title': '盲人的寓言 (1568)',
        'enTitle': 'The Parable of the Blind',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'file': 'bruegel_parable_of_the_blind.jpg',
        'query': 'The Blind Leading the Blind Pieter Bruegel the Elder Naples',
        'quote': '“If the blind lead the blind, both shall fall into the ditch.”',
        'quoteAuthor': '— Pieter Bruegel the Elder'
    },

    # === 2. 🎭 巴洛克与荷兰黄金时代 ===
    {
        'id': 'caravaggio_calling_of_saint_matthew',
        'title': '圣马太蒙召 (1600)',
        'enTitle': 'The Calling of Saint Matthew',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'file': 'caravaggio_calling_of_saint_matthew.jpg',
        'query': 'Caravaggio The Calling of Saint Matthew Contarelli',
        'quote': '“When there is no light, everything is darkness; but when a single beam enters, all truth is illuminated.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'caravaggio_judith_beheading_holofernes',
        'title': '朱迪斯斩杀霍洛芬斯 (1599)',
        'enTitle': 'Judith Beheading Holofernes',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'file': 'caravaggio_judith_beheading_holofernes.jpg',
        'query': 'Judith Beheading Holofernes Caravaggio Barberini',
        'quote': '“Nature has supplied me with plenty of masters, and none greater than reality.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'caravaggio_bacchus',
        'title': '酒神巴克斯 (1595)',
        'enTitle': 'Bacchus',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'file': 'caravaggio_bacchus.jpg',
        'query': 'Bacchus by Caravaggio Uffizi',
        'quote': '“All works are nothing but bagatelles unless they are made from life.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'caravaggio_supper_at_emmaus',
        'title': '以马忤斯的晚餐 (1601)',
        'enTitle': 'Supper at Emmaus',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'file': 'caravaggio_supper_at_emmaus.jpg',
        'query': 'Supper at Emmaus Caravaggio London',
        'quote': '“In the dramatic clash of shadow and glare lies the beating heart of faith.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'rembrandt_night_watch',
        'title': '夜巡 (1642)',
        'enTitle': 'The Night Watch',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'file': 'rembrandt_night_watch.jpg',
        'query': 'Rembrandt The Night Watch Rijksmuseum',
        'quote': '“A painting is finished when the artist says it is finished.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'rembrandt_anatomy_lesson',
        'title': '杜尔普医生的解剖课 (1632)',
        'enTitle': 'The Anatomy Lesson of Dr. Nicolaes Tulp',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'file': 'rembrandt_anatomy_lesson.jpg',
        'query': 'The Anatomy Lesson of Dr Nicolaes Tulp Mauritshuis',
        'quote': '“Practise what you know, and it will help to make clear what now you do not know.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'rembrandt_storm_on_sea_of_galilee',
        'title': '加利利海风暴 (1633)',
        'enTitle': 'The Storm on the Sea of Galilee',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'file': 'rembrandt_storm_on_sea_of_galilee.jpg',
        'query': 'Rembrandt Christ in the Storm on the Lake of Galilee',
        'quote': '“Choose only one master: Nature.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'velazquez_las_meninas',
        'title': '宫娥 (1656)',
        'enTitle': 'Las Meninas',
        'artist': 'Diego Velázquez (委拉斯凯兹)',
        'category': 'baroque',
        'file': 'velazquez_las_meninas.jpg',
        'query': 'Diego Velázquez Las Meninas Prado',
        'quote': '“I would rather be the first painter of common things than the second in higher art.”',
        'quoteAuthor': '— Diego Velázquez'
    },
    {
        'id': 'vermeer_pearl_earring',
        'title': '戴珍珠耳环的少女 (1665)',
        'enTitle': 'Girl with a Pearl Earring',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'file': 'vermeer_pearl_earring.jpg',
        'query': 'Johannes Vermeer Girl With The Pearl Earring Mauritshuis',
        'quote': '“Silence is the most profound harmony in light.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_the_milkmaid',
        'title': '倒牛奶的女仆 (1658)',
        'enTitle': 'The Milkmaid',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'file': 'vermeer_the_milkmaid.jpg',
        'query': 'Johannes Vermeer Het melkmeisje Rijksmuseum',
        'quote': '“In the everyday pouring of milk, eternity quietly resides.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_the_little_street',
        'title': '小街 (1658)',
        'enTitle': 'The Little Street',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'file': 'vermeer_the_little_street.jpg',
        'query': 'Johannes Vermeer The Little Street Rijksmuseum',
        'quote': '“Bricks and cobblestones bathed in afternoon sun speak of home.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_view_of_delft',
        'title': '代尔夫特风景 (1661)',
        'enTitle': 'View of Delft',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'file': 'vermeer_view_of_delft.jpg',
        'query': 'Johannes Vermeer View of Delft Mauritshuis',
        'quote': '“The clouds drift over Delft, painting the rooftops in gold and shadow.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_the_astronomer',
        'title': '天文学家 (1668)',
        'enTitle': 'The Astronomer',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'file': 'vermeer_the_astronomer.jpg',
        'query': 'Johannes Vermeer The Astronomer Louvre',
        'quote': '“By touching the celestial globe, man touches the hem of infinity.”',
        'quoteAuthor': '— Johannes Vermeer'
    },

    # === 3. ⚡ 新古典、洛可可与浪漫主义 ===
    {
        'id': 'fragonard_the_swing',
        'title': '秋千 (1767)',
        'enTitle': 'The Swing',
        'artist': 'Jean-Honoré Fragonard (弗拉戈纳尔)',
        'category': 'romanticism',
        'file': 'fragonard_the_swing.jpg',
        'query': 'Jean-Honoré Fragonard The Swing Wallace Collection',
        'quote': '“Let pleasure and grace dance through the enchanted rose garden.”',
        'quoteAuthor': '— Jean-Honoré Fragonard'
    },
    {
        'id': 'david_oath_of_the_horatii',
        'title': '荷拉斯兄弟之誓 (1784)',
        'enTitle': 'Oath of the Horatii',
        'artist': 'Jacques-Louis David (达维特)',
        'category': 'romanticism',
        'file': 'david_oath_of_the_horatii.jpg',
        'query': 'Jacques-Louis David Oath of the Horatii Louvre',
        'quote': '“To achieve the true sublime, one must capture the unyielding spirit of civic virtue.”',
        'quoteAuthor': '— Jacques-Louis David'
    },
    {
        'id': 'david_death_of_marat',
        'title': '马拉之死 (1793)',
        'enTitle': 'The Death of Marat',
        'artist': 'Jacques-Louis David (达维特)',
        'category': 'romanticism',
        'file': 'david_death_of_marat.jpg',
        'query': 'Jacques-Louis David Death of Marat Brussels',
        'quote': '“The brush must serve the sacred memory of devotion.”',
        'quoteAuthor': '— Jacques-Louis David'
    },
    {
        'id': 'david_napoleon_crossing_the_alps',
        'title': '跨越阿尔卑斯山圣伯纳隘道的拿破仑 (1801)',
        'enTitle': 'Napoleon Crossing the Alps',
        'artist': 'Jacques-Louis David (达维特)',
        'category': 'romanticism',
        'file': 'david_napoleon_crossing_the_alps.jpg',
        'query': 'Jacques-Louis David Bonaparte franchissant le Grand-Saint-Bernard',
        'quote': '“Calm on a fiery steed.”',
        'quoteAuthor': '— Jacques-Louis David'
    },
    {
        'id': 'ingres_the_valpincon_bather',
        'title': '瓦平松的浴女 (1808)',
        'enTitle': 'The Valpinçon Bather',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'file': 'ingres_the_valpincon_bather.jpg',
        'query': 'La baigneuse Valpinçon Jean-Auguste-Dominique Ingres Louvre',
        'quote': '“Drawing is the probity of art.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres'
    },
    {
        'id': 'ingres_la_grande_odalisque',
        'title': '大宫女 (1814)',
        'enTitle': 'Grande Odalisque',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'file': 'ingres_la_grande_odalisque.jpg',
        'query': 'Jean Auguste Dominique Ingres Une Odalisque Louvre',
        'quote': '“Form is not in the contour, it is in the curves and harmony of pure line.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres'
    },
    {
        'id': 'ingres_the_source',
        'title': '泉 (1856)',
        'enTitle': 'The Source (La Source)',
        'artist': 'Jean-Auguste-Dominique Ingres (安格尔)',
        'category': 'romanticism',
        'file': 'ingres_the_source.jpg',
        'query': 'Ingres La Source 1856 Orsay',
        'quote': '“Grace and purity flow from the spring of classical ideals.”',
        'quoteAuthor': '— Jean-Auguste-Dominique Ingres'
    },
    {
        'id': 'goya_third_of_may_1808',
        'title': '1808年5月3日夜间起义枪杀 (1814)',
        'enTitle': 'The Third of May 1808',
        'artist': 'Francisco Goya (戈雅)',
        'category': 'romanticism',
        'file': 'goya_third_of_may_1808.jpg',
        'query': 'El Tres de Mayo Francisco de Goya Prado',
        'quote': '“The sleep of reason produces monsters.”',
        'quoteAuthor': '— Francisco Goya'
    },
    {
        'id': 'goya_saturn_devouring_his_son',
        'title': '农神吞噬其子 (1823)',
        'enTitle': 'Saturn Devouring His Son',
        'artist': 'Francisco Goya (戈雅)',
        'category': 'romanticism',
        'file': 'goya_saturn_devouring_his_son.jpg',
        'query': 'Francisco de Goya Saturno devorando a su hijo',
        'quote': '“In art, there is no need for colour; there is only light and shade.”',
        'quoteAuthor': '— Francisco Goya'
    },
    {
        'id': 'gericault_raft_of_the_medusa',
        'title': '梅杜萨之筏 (1819)',
        'enTitle': 'The Raft of the Medusa',
        'artist': 'Théodore Géricault (席里柯)',
        'category': 'romanticism',
        'file': 'gericault_raft_of_the_medusa.jpg',
        'query': 'Le Radeau de la Méduse Théodore Géricault Louvre',
        'quote': '“Neither the masters nor the school can give what passion alone creates.”',
        'quoteAuthor': '— Théodore Géricault'
    },
    {
        'id': 'delacroix_liberty_leading_the_people',
        'title': '自由引导人民 (1830)',
        'enTitle': 'Liberty Leading the People',
        'artist': 'Eugène Delacroix (德拉克罗瓦)',
        'category': 'romanticism',
        'file': 'delacroix_liberty_leading_the_people.jpg',
        'query': 'Eugène Delacroix La Liberté guidant le peuple Louvre',
        'quote': '“Colour in a picture is like enthusiasm in life.”',
        'quoteAuthor': '— Eugène Delacroix'
    },
    {
        'id': 'friedrich_wanderer_above_sea_of_fog',
        'title': '雾海上的旅人 (1818)',
        'enTitle': 'Wanderer above the Sea of Fog',
        'artist': 'Caspar David Friedrich (弗里德里希)',
        'category': 'romanticism',
        'file': 'friedrich_wanderer_above_sea_of_fog.jpg',
        'query': 'Caspar David Friedrich Wanderer above the sea of fog Hamburg',
        'quote': '“The artist should paint not only what he sees before him, but also what he sees within himself.”',
        'quoteAuthor': '— Caspar David Friedrich'
    },
    {
        'id': 'constable_the_hay_wain',
        'title': '干草车 (1821)',
        'enTitle': 'The Hay Wain',
        'artist': 'John Constable (约翰·康斯特勃)',
        'category': 'romanticism',
        'file': 'constable_the_hay_wain.jpg',
        'query': 'John Constable The Hay Wain National Gallery',
        'quote': '“Painting is with me but another word for feeling.”',
        'quoteAuthor': '— John Constable'
    },
    {
        'id': 'turner_the_fighting_temeraire',
        'title': '被拖去解体的战舰无畏号 (1839)',
        'enTitle': 'The Fighting Temeraire',
        'artist': 'J. M. W. Turner (透纳)',
        'category': 'romanticism',
        'file': 'turner_the_fighting_temeraire.jpg',
        'query': 'The Fighting Temeraire JMW Turner National Gallery',
        'quote': '“The sun is God.”',
        'quoteAuthor': '— J. M. W. Turner'
    },
    {
        'id': 'turner_rain_steam_and_speed',
        'title': '雨、蒸汽和速度——西部大铁路 (1844)',
        'enTitle': 'Rain, Steam and Speed - The Great Western Railway',
        'artist': 'J. M. W. Turner (透纳)',
        'category': 'romanticism',
        'file': 'turner_rain_steam_and_speed.jpg',
        'query': 'Rain Steam and Speed the Great Western Railway Turner',
        'quote': '“I did not paint it to be understood, but I wished to show what such a scene was like.”',
        'quoteAuthor': '— J. M. W. Turner'
    },

    # === 4. 🌾 写实主义与巡回展览画派 ===
    {
        'id': 'millet_the_gleaners',
        'title': '拾穗者 (1857)',
        'enTitle': 'The Gleaners',
        'artist': 'Jean-François Millet (米勒)',
        'category': 'realism',
        'file': 'millet_the_gleaners.jpg',
        'query': 'Jean-François Millet Des glaneuses Orsay',
        'quote': '“It is the treat of my life to see the sun rise and the flowers bloom with peasant devotion.”',
        'quoteAuthor': '— Jean-François Millet'
    },
    {
        'id': 'repin_barge_haulers_on_the_volga',
        'title': '伏尔加河上的纤夫 (1873)',
        'enTitle': 'Barge Haulers on the Volga',
        'artist': 'Ilya Repin (列宾)',
        'category': 'realism',
        'file': 'repin_barge_haulers_on_the_volga.jpg',
        'query': 'Ilya Repin Barge Haulers on the Volga State Russian Museum',
        'quote': '“Art is the breath of the people; it must reflect their toil, their strength, their unyielding soul.”',
        'quoteAuthor': '— Ilya Repin'
    },
    {
        'id': 'whistler_mothers_portrait',
        'title': '惠斯勒的母亲 · 灰与黑的协奏 (1871)',
        'enTitle': "Whistler's Mother (Arrangement in Grey and Black No. 1)",
        'artist': 'James McNeill Whistler (惠斯勒)',
        'category': 'realism',
        'file': 'whistler_mothers_portrait.jpg',
        'query': 'Whistlers Mother high res Orsay',
        'quote': '“As music is the poetry of sound, so is painting the poetry of sight.”',
        'quoteAuthor': '— James McNeill Whistler'
    },

    # === 6. 🎨 印象派巅峰盛宴 ===
    {
        'id': 'manet_dejeuner_sur_l_herbe',
        'title': '草地上的午餐 (1863)',
        'enTitle': "Le Déjeuner sur l'herbe",
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'file': 'manet_dejeuner_sur_l_herbe.jpg',
        'query': 'Édouard Manet Le Déjeuner sur l herbe Orsay',
        'quote': '“I paint what I see, and not what it pleases others to see.”',
        'quoteAuthor': '— Édouard Manet'
    },
    {
        'id': 'manet_olympia',
        'title': '奥林匹亚 (1863)',
        'enTitle': 'Olympia',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'file': 'manet_olympia.jpg',
        'query': 'Edouard Manet Olympia Orsay',
        'quote': '“Conciseness in art is a necessity and an elegance.”',
        'quoteAuthor': '— Édouard Manet'
    },
    {
        'id': 'manet_a_bar_at_the_folies_bergere',
        'title': '女神游乐厅的吧台 (1882)',
        'enTitle': 'A Bar at the Folies-Bergère',
        'artist': 'Édouard Manet (马奈)',
        'category': 'impressionism',
        'file': 'manet_a_bar_at_the_folies_bergere.jpg',
        'query': 'Edouard Manet A Bar at the Folies-Bergère Courtauld',
        'quote': '“There is only one true thing: instantly paint what you see.”',
        'quoteAuthor': '— Édouard Manet'
    },
    {
        'id': 'renoir_bal_du_moulin_de_la_galette',
        'title': '红磨坊街的舞会 (1876)',
        'enTitle': 'Bal du moulin de la Galette',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'file': 'renoir_bal_du_moulin_de_la_galette.jpg',
        'query': 'Pierre-Auguste Renoir Le Moulin de la Galette Orsay',
        'quote': '“A picture must be an amiable thing, joyous and pretty — yes, pretty!”',
        'quoteAuthor': '— Pierre-Auguste Renoir'
    },
    {
        'id': 'renoir_luncheon_of_the_boating_party',
        'title': '游艇上的午餐 (1881)',
        'enTitle': 'Luncheon of the Boating Party',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'file': 'renoir_luncheon_of_the_boating_party.jpg',
        'query': 'Pierre-Auguste Renoir Luncheon of the Boating Party Phillips Collection',
        'quote': '“Why shouldn\'t art be pretty? There are enough unpleasant things in the world.”',
        'quoteAuthor': '— Pierre-Auguste Renoir'
    },
    {
        'id': 'degas_the_dance_class',
        'title': '舞蹈课 (1874)',
        'enTitle': 'The Dance Class',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'file': 'degas_the_dance_class.jpg',
        'query': 'Edgar Degas The Dance Class Orsay',
        'quote': '“Art is not what you see, but what you make others see.”',
        'quoteAuthor': '— Edgar Degas'
    },
    {
        'id': 'degas_dancer_tilting',
        'title': '舞台上的舞女 · 绿衣舞者 (1878)',
        'enTitle': 'Dancer on Stage (Swaying Dancer)',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'file': 'degas_dancer_tilting.jpg',
        'query': 'Edgar Degas Danseuse sur la scene Orsay',
        'quote': '“They call me the painter of dancers; they don\'t understand that for me, the dancer is a pretext for painting beautiful fabrics and rendering movement.”',
        'quoteAuthor': '— Edgar Degas'
    },
    {
        'id': 'degas_l_absinthe',
        'title': '苦艾酒 (1876)',
        'enTitle': 'L\'Absinthe',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'file': 'degas_l_absinthe.jpg',
        'query': 'Edgar Degas In a Café Absinthe Orsay',
        'quote': '“A picture is something which requires as much knavery, trickery, and deceit as the perpetration of a crime.”',
        'quoteAuthor': '— Edgar Degas'
    },
    {
        'id': 'caillebotte_paris_street_rainy_day',
        'title': '下雨天的巴黎街道 (1877)',
        'enTitle': 'Paris Street; Rainy Day',
        'artist': 'Gustave Caillebotte (卡耶博特)',
        'category': 'impressionism',
        'file': 'caillebotte_paris_street_rainy_day.jpg',
        'query': 'Gustave Caillebotte Paris Street Rainy Day Art Institute of Chicago',
        'quote': '“Rain glistens on Parisian stones like mirrors of modern life.”',
        'quoteAuthor': '— Gustave Caillebotte'
    },

    # === 7. 🌻 后印象派三杰与现代先驱 ===
    {
        'id': 'vangogh_starry_night',
        'title': '星夜 (1889)',
        'enTitle': 'The Starry Night',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_starry_night.jpg',
        'query': 'Van Gogh Starry Night MoMA Google Art Project',
        'quote': '“I don\'t know anything with certainty, but seeing the stars makes me dream.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_sunflowers',
        'title': '向日葵 · 十五朵向日葵 (1888)',
        'enTitle': 'Sunflowers',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_sunflowers.jpg',
        'query': 'Vincent van Gogh Sunflowers National Gallery London',
        'quote': '“The sunflower is mine, in a way.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_starry_night_over_the_rhone',
        'title': '罗讷河上的星夜 (1888)',
        'enTitle': 'Starry Night Over the Rhône',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_starry_night_over_the_rhone.jpg',
        'query': 'Vincent van Gogh Starry Night over the Rhone Orsay',
        'quote': '“Often it seems to me that the night is much more alive and richly coloured than the day.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_almond_blossom',
        'title': '盛开的杏花 (1890)',
        'enTitle': 'Almond Blossoms',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_almond_blossom.jpg',
        'query': 'Vincent van Gogh Almond blossom Van Gogh Museum',
        'quote': '“Great things are not done by impulse, but by a series of small things brought together.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_irises',
        'title': '鸢尾花 (1889)',
        'enTitle': 'Irises',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_irises.jpg',
        'query': 'Vincent van Gogh Irises Getty',
        'quote': '“If you truly love nature, you will find beauty everywhere.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_night_cafe',
        'title': '夜间咖啡馆 (1888)',
        'enTitle': 'The Night Café',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_night_cafe.jpg',
        'query': 'Vincent Willem van Gogh The Night Café Yale',
        'quote': '“I have tried to express the terrible passions of humanity by means of red and green.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_potato_eaters',
        'title': '吃土豆的人 (1885)',
        'enTitle': 'The Potato Eaters',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_potato_eaters.jpg',
        'query': 'Vincent van Gogh The Potato Eaters Van Gogh Museum',
        'quote': '“They have tilled the earth themselves with the same hands they now put in the dish.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_self_portrait_bandaged_ear',
        'title': '自画像 · 包扎耳朵的自画像 (1889)',
        'enTitle': 'Self-Portrait with Bandaged Ear',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'file': 'vangogh_self_portrait_bandaged_ear.jpg',
        'query': 'Vincent van Gogh Self-Portrait with Bandaged Ear Courtauld',
        'quote': '“I put my heart and my soul into my work, and have lost my mind in the process.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'seurat_sunday_afternoon',
        'title': '大碗岛的星期天下午 (1886)',
        'enTitle': 'A Sunday on La Grande Jatte',
        'artist': 'Georges Seurat (修拉)',
        'category': 'post_impressionism',
        'file': 'seurat_sunday_afternoon.jpg',
        'query': 'A Sunday on La Grande Jatte Georges Seurat Art Institute of Chicago',
        'quote': '“They see poetry in what I have done. No, I apply my method and that is all there is to it.”',
        'quoteAuthor': '— Georges Seurat'
    },
    {
        'id': 'cezanne_mont_sainte_victoire',
        'title': '圣维克多山系列 (1904)',
        'enTitle': 'Mont Sainte-Victoire',
        'artist': 'Paul Cézanne (塞尚)',
        'category': 'post_impressionism',
        'file': 'cezanne_mont_sainte_victoire.jpg',
        'query': 'Paul Cézanne Mont Sainte-Victoire Philadelphia',
        'quote': '“Treat nature by means of the cylinder, the sphere, the cone.”',
        'quoteAuthor': '— Paul Cézanne'
    },
    {
        'id': 'cezanne_card_players',
        'title': '玩纸牌的人 (1895)',
        'enTitle': 'The Card Players',
        'artist': 'Paul Cézanne (塞尚)',
        'category': 'post_impressionism',
        'file': 'cezanne_card_players.jpg',
        'query': 'Les Joueurs de carte Paul Cézanne Orsay',
        'quote': '“A work of art which did not begin in emotion is not art.”',
        'quoteAuthor': '— Paul Cézanne'
    },
    {
        'id': 'cezanne_the_large_bathers',
        'title': '大浴女 (1906)',
        'enTitle': 'The Large Bathers',
        'artist': 'Paul Cézanne (塞尚)',
        'category': 'post_impressionism',
        'file': 'cezanne_the_large_bathers.jpg',
        'query': 'Les Grandes Baigneuses Paul Cézanne Philadelphia Museum of Art',
        'quote': '“The day is coming when a single carrot, freshly observed, will set off a revolution.”',
        'quoteAuthor': '— Paul Cézanne'
    },
    {
        'id': 'gauguin_where_do_we_come_from',
        'title': '我们从何处来？我们是谁？我们向何处去？ (1897)',
        'enTitle': 'Where Do We Come From? What Are We? Where Are We Going?',
        'artist': 'Paul Gauguin (高更)',
        'category': 'post_impressionism',
        'file': 'gauguin_where_do_we_come_from.jpg',
        'query': 'Paul Gauguin D ou venons-nous Que sommes-nous Ou allons-nous Boston',
        'quote': '“I shut my eyes in order to see.”',
        'quoteAuthor': '— Paul Gauguin'
    },
    {
        'id': 'gauguin_vision_after_the_sermon',
        'title': '布道后的幻象 · 雅各与天使搏斗 (1888)',
        'enTitle': 'Vision after the Sermon',
        'artist': 'Paul Gauguin (高更)',
        'category': 'post_impressionism',
        'file': 'gauguin_vision_after_the_sermon.jpg',
        'query': 'Vision after the Sermon Paul Gauguin National Galleries of Scotland',
        'quote': '“Art is an abstraction; derive this abstraction from nature while dreaming before it.”',
        'quoteAuthor': '— Paul Gauguin'
    },
    {
        'id': 'gauguin_tahitian_women_on_beach',
        'title': '塔希提少女 · 沙滩上的大溪地女人 (1891)',
        'enTitle': 'Tahitian Women on the Beach',
        'artist': 'Paul Gauguin (高更)',
        'category': 'post_impressionism',
        'file': 'gauguin_tahitian_women_on_beach.jpg',
        'query': 'Femmes de Tahiti Paul Gauguin Musée d Orsay',
        'quote': '“Colour is the language of the listening eye.”',
        'quoteAuthor': '— Paul Gauguin'
    },
    {
        'id': 'rousseau_the_sleeping_gypsy',
        'title': '沉睡的吉普赛人 (1897)',
        'enTitle': 'The Sleeping Gypsy',
        'artist': 'Henri Rousseau (亨利·卢梭)',
        'category': 'post_impressionism',
        'file': 'rousseau_the_sleeping_gypsy.jpg',
        'query': 'Henri Rousseau The Sleeping Gypsy MoMA',
        'quote': '“Nothing makes me so happy as to observe nature and to paint what I see.”',
        'quoteAuthor': '— Henri Rousseau'
    },
    {
        'id': 'rousseau_the_dream',
        'title': '梦境 (1910)',
        'enTitle': 'The Dream',
        'artist': 'Henri Rousseau (亨利·卢梭)',
        'category': 'post_impressionism',
        'file': 'rousseau_the_dream.jpg',
        'query': 'The Dream Henri Rousseau MoMA',
        'quote': '“When I go into the glasshouses and see the strange plants of exotic lands, it seems to me that I enter into a dream.”',
        'quoteAuthor': '— Henri Rousseau'
    },

    # === 8. 🌌 象征主义与表现主义 ===
    {
        'id': 'munch_the_scream',
        'title': '呐喊 (1893)',
        'enTitle': 'The Scream',
        'artist': 'Edvard Munch (蒙克)',
        'category': 'expressionism',
        'file': 'munch_the_scream.jpg',
        'query': 'Edvard Munch The Scream National Gallery of Norway',
        'quote': '“I sensed an infinite scream passing through nature.”',
        'quoteAuthor': '— Edvard Munch'
    },
    {
        'id': 'klimt_the_kiss',
        'title': '吻 (1908)',
        'enTitle': 'The Kiss (Der Kuss)',
        'artist': 'Gustav Klimt (克里姆特)',
        'category': 'expressionism',
        'file': 'klimt_the_kiss.jpg',
        'query': 'Gustav Klimt Der Kuss Belvedere Vienna',
        'quote': '“All art is erotic.”',
        'quoteAuthor': '— Gustav Klimt'
    },
    {
        'id': 'klimt_adele_bloch_bauer_i',
        'title': '金衣女人 · 阿黛尔·布洛赫-鲍尔像一号 (1907)',
        'enTitle': 'Portrait of Adele Bloch-Bauer I',
        'artist': 'Gustav Klimt (克里姆特)',
        'category': 'expressionism',
        'file': 'klimt_adele_bloch_bauer_i.jpg',
        'query': 'Gustav Klimt Adele Bloch-Bauer I Neue Galerie',
        'quote': '“Truth is like fire; to tell the truth means to glow and burn in gold.”',
        'quoteAuthor': '— Gustav Klimt'
    },
    {
        'id': 'waterhouse_the_lady_of_shalott',
        'title': '沙洛特女郎 (1888)',
        'enTitle': 'The Lady of Shalott',
        'artist': 'John William Waterhouse (沃特豪斯)',
        'category': 'expressionism',
        'file': 'waterhouse_the_lady_of_shalott.jpg',
        'query': 'John William Waterhouse The Lady of Shalott Tate Britain',
        'quote': '“She loosed the chain, and down she lay; The broad stream bore her far away.”',
        'quoteAuthor': '— John William Waterhouse'
    },

    # === 9. 🔷 现代主义、立体派与超现实主义 ===
    {
        'id': 'picasso_les_demoiselles_davignon',
        'title': '亚威农的少女 (1907)',
        'enTitle': 'Les Demoiselles d\'Avignon',
        'artist': 'Pablo Picasso (毕加索)',
        'category': 'modernism',
        'file': 'picasso_les_demoiselles_davignon.jpg',
        'query': 'Pablo Picasso Les Demoiselles d Avignon MoMA',
        'quote': '“Art washes away from the soul the dust of everyday life.”',
        'quoteAuthor': '— Pablo Picasso'
    },
    {
        'id': 'picasso_old_guitarist',
        'title': '老吉他手 (1903)',
        'enTitle': 'The Old Guitarist',
        'artist': 'Pablo Picasso (毕加索)',
        'category': 'modernism',
        'file': 'picasso_old_guitarist.jpg',
        'query': 'Pablo Picasso The Old Guitarist Art Institute of Chicago',
        'quote': '“Colors, like features, follow the changes of the emotions.”',
        'quoteAuthor': '— Pablo Picasso'
    },
    {
        'id': 'picasso_guernica',
        'title': '格尔尼卡 (1937)',
        'enTitle': 'Guernica',
        'artist': 'Pablo Picasso (毕加索)',
        'category': 'modernism',
        'file': 'picasso_guernica.jpg',
        'query': 'Pablo Picasso Guernica Reina Sofia',
        'quote': '“Painting is not made to decorate apartments. It\'s an offensive and defensive weapon against the enemy.”',
        'quoteAuthor': '— Pablo Picasso'
    },
    {
        'id': 'picasso_weeping_woman',
        'title': '哭泣的女人 (1937)',
        'enTitle': 'The Weeping Woman',
        'artist': 'Pablo Picasso (毕加索)',
        'category': 'modernism',
        'file': 'picasso_weeping_woman.jpg',
        'query': 'Pablo Picasso The Weeping Woman Tate',
        'quote': '“Every act of creation is first an act of destruction.”',
        'quoteAuthor': '— Pablo Picasso'
    },
    {
        'id': 'matisse_dance',
        'title': '舞蹈 (1910)',
        'enTitle': 'Dance (La Danse)',
        'artist': 'Henri Matisse (马蒂斯)',
        'category': 'modernism',
        'file': 'matisse_dance.jpg',
        'query': 'Henri Matisse La danse Hermitage',
        'quote': '“Creativity takes courage.”',
        'quoteAuthor': '— Henri Matisse'
    },
    {
        'id': 'matisse_the_dessert_harmony_in_red',
        'title': '红色的和谐 (1908)',
        'enTitle': 'The Dessert: Harmony in Red',
        'artist': 'Henri Matisse (马蒂斯)',
        'category': 'modernism',
        'file': 'matisse_the_dessert_harmony_in_red.jpg',
        'query': 'Henri Matisse Le Dessert Harmonie en rouge Hermitage',
        'quote': '“What I dream of is an art of balance, of purity and serenity.”',
        'quoteAuthor': '— Henri Matisse'
    },
    {
        'id': 'duchamp_nude_descending_a_staircase',
        'title': '下楼的裸女二号 (1912)',
        'enTitle': 'Nude Descending a Staircase, No. 2',
        'artist': 'Marcel Duchamp (杜尚)',
        'category': 'modernism',
        'file': 'duchamp_nude_descending_a_staircase.jpg',
        'query': 'Marcel Duchamp Nude Descending a Staircase No. 2 Philadelphia',
        'quote': '“Art is not about itself, but the attention we bring to it.”',
        'quoteAuthor': '— Marcel Duchamp'
    },
    {
        'id': 'dali_persistence_of_memory',
        'title': '记忆的永恒 (1931)',
        'enTitle': 'The Persistence of Memory',
        'artist': 'Salvador Dalí (达利)',
        'category': 'modernism',
        'file': 'dali_persistence_of_memory.jpg',
        'query': 'Salvador Dali The Persistence of Memory MoMA',
        'quote': '“Intelligence without ambition is a bird without wings... Time is fluid like melting camembert.”',
        'quoteAuthor': '— Salvador Dalí'
    },
    {
        'id': 'magritte_son_of_man',
        'title': '人类之子 (1964)',
        'enTitle': 'The Son of Man',
        'artist': 'René Magritte (马格利特)',
        'category': 'modernism',
        'file': 'magritte_son_of_man.jpg',
        'query': 'René Magritte The Son of Man',
        'quote': '“Everything we see hides another thing, we always want to see what is hidden by what we see.”',
        'quoteAuthor': '— René Magritte'
    },
    {
        'id': 'wood_american_gothic',
        'title': '美国哥特式 (1930)',
        'enTitle': 'American Gothic',
        'artist': 'Grant Wood (格兰特·伍德)',
        'category': 'modernism',
        'file': 'wood_american_gothic.jpg',
        'query': 'Grant Wood American Gothic Art Institute of Chicago',
        'quote': '“All the good ideas I\'ve ever had came to me while I was milking a cow.”',
        'quoteAuthor': '— Grant Wood'
    },
    {
        'id': 'hopper_nighthawks',
        'title': '夜游者 (1942)',
        'enTitle': 'Nighthawks',
        'artist': 'Edward Hopper (爱德华·霍珀)',
        'category': 'modernism',
        'file': 'hopper_nighthawks.jpg',
        'query': 'Edward Hopper Nighthawks Art Institute of Chicago',
        'quote': '“Unconsciously, probably, I was painting the loneliness of a large city.”',
        'quoteAuthor': '— Edward Hopper'
    },
    {
        'id': 'mondrian_composition_with_red_blue_yellow',
        'title': '红黄蓝黑的构成 (1930)',
        'enTitle': 'Composition with Red, Blue and Yellow',
        'artist': 'Piet Mondrian (蒙德里安)',
        'category': 'modernism',
        'file': 'mondrian_composition_with_red_blue_yellow.jpg',
        'query': 'Piet Mondrian Composition with Red Blue and Yellow',
        'quote': '“Art should be above reality, having no direct relation to life... Pure plastic art.”',
        'quoteAuthor': '— Piet Mondrian'
    },
    {
        'id': 'kandinsky_composition_viii',
        'title': '第八号构图 (1923)',
        'enTitle': 'Composition VIII',
        'artist': 'Wassily Kandinsky (康定斯基)',
        'category': 'modernism',
        'file': 'kandinsky_composition_viii.jpg',
        'query': 'Vassily Kandinsky Composition 8 Guggenheim',
        'quote': '“Colour is the keyboard, the eyes are the harmonies, the soul is the piano with many strings.”',
        'quoteAuthor': '— Wassily Kandinsky'
    },
    {
        'id': 'pollock_autumn_rhythm',
        'title': '秋水仙 · 秋天的韵律 (第30号) (1950)',
        'enTitle': 'Autumn Rhythm (Number 30)',
        'artist': 'Jackson Pollock (杰克逊·波洛克)',
        'category': 'modernism',
        'file': 'pollock_autumn_rhythm.jpg',
        'query': 'Jackson Pollock Autumn Rhythm Number 30 Metropolitan Museum of Art',
        'quote': '“Painting is a state of being... Painting is self-discovery. Every good artist paints what he is.”',
        'quoteAuthor': '— Jackson Pollock'
    },
    {
        'id': 'warhol_campbells_soup_cans',
        'title': '金宝汤罐头 (1962)',
        'enTitle': 'Campbell\'s Soup Cans',
        'artist': 'Andy Warhol (安迪·沃霍尔)',
        'category': 'modernism',
        'file': 'warhol_campbells_soup_cans.jpg',
        'query': 'Andy Warhol Campbells Soup Cans MoMA',
        'quote': '“Pop art is about liking things... Everything has its beauty, but not everyone sees it.”',
        'quoteAuthor': '— Andy Warhol'
    },
    {
        'id': 'warhol_marilyn_diptych',
        'title': '玛丽莲·双联画 (1962)',
        'enTitle': 'Marilyn Diptych',
        'artist': 'Andy Warhol (安迪·沃霍尔)',
        'category': 'modernism',
        'file': 'warhol_marilyn_diptych.jpg',
        'query': 'Andy Warhol Marilyn Diptych Tate',
        'quote': '“Don\'t pay any attention to what they write about you. Just measure it in inches.”',
        'quoteAuthor': '— Andy Warhol'
    },
    {
        'id': 'kahlo_the_two_fridas',
        'title': '两朵芙烈达 (1939)',
        'enTitle': 'The Two Fridas (Las dos Fridas)',
        'artist': 'Frida Kahlo (弗里达·卡罗)',
        'category': 'modernism',
        'file': 'kahlo_the_two_fridas.jpg',
        'query': 'Frida Kahlo The Two Fridas Museo de Arte Moderno',
        'quote': '“I paint flowers so they will not die... I never paint dreams or nightmares. I paint my own reality.”',
        'quoteAuthor': '— Frida Kahlo'
    },

    # === 10. 🌊 东方瑰宝与世界名作 ===
    {
        'id': 'hokusai_great_wave',
        'title': '神奈川冲浪里 (1831)',
        'enTitle': 'The Great Wave off Kanagawa',
        'artist': 'Katsushika Hokusai (葛饰北斋)',
        'category': 'world_treasures',
        'file': 'hokusai_great_wave.jpg',
        'query': 'Great Wave off Kanagawa Hokusai Met',
        'quote': '“From the age of six, I had a passion for copying the form of things... at ninety I shall penetrate their essential nature.”',
        'quoteAuthor': '— Katsushika Hokusai'
    }
]

print(f"Total defined new paintings: {len(NEW_ARTWORKS)}")

def fetch_thumb_url(query):
    # Search Wikimedia Commons with 1800px thumburl
    for attempt in range(3):
        try:
            params = {
                'action': 'query',
                'generator': 'search',
                'gsrsearch': query,
                'gsrnamespace': '6',
                'gsrlimit': '3',
                'prop': 'imageinfo',
                'iiprop': 'url|size',
                'iiurlwidth': '1800',
                'format': 'json'
            }
            url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode('utf-8'))
                for pid, p in d.get('query', {}).get('pages', {}).items():
                    info = p.get('imageinfo', [{}])[0]
                    # thumburl is highly efficient
                    return info.get('thumburl') or info.get('url')
            return None
        except Exception as e:
            time.sleep(1.2)
    return None

def download_and_optimize(item):
    target_path = os.path.join(dest_dir, item['file'])
    if os.path.exists(target_path) and os.path.getsize(target_path) > 30000:
        return 'EXISTS'

    img_url = fetch_thumb_url(item['query'])
    if not img_url:
        # Fallback query with simple title + artist
        simple_q = item['title'].split('(')[0] + ' ' + item['artist'].split('(')[0]
        img_url = fetch_thumb_url(simple_q)

    if not img_url:
        return 'NO_URL'

    temp_path = os.path.join(dest_dir, 'tmp_' + item['file'])
    for dl_attempt in range(3):
        try:
            time.sleep(0.8)
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp, open(temp_path, 'wb') as f:
                f.write(resp.read())

            im = Image.open(temp_path)
            if im.mode != 'RGB':
                im = im.convert('RGB')
            im.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            im.save(target_path, 'JPEG', quality=92)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return f"OK({im.size})"
        except Exception as e:
            time.sleep(1.5)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if dl_attempt == 2:
                return f"ERR({e})"

if __name__ == '__main__':
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(NEW_ARTWORKS)
    print(f"Processing {limit} paintings...")
    success = 0
    skipped = 0
    failed = []

    for idx, item in enumerate(NEW_ARTWORKS[:limit]):
        print(f"[{idx+1}/{limit}] {item['title']} ...", end=' ', flush=True)
        res = download_and_optimize(item)
        print(res)
        if 'OK' in res:
            success += 1
        elif 'EXISTS' in res:
            skipped += 1
        else:
            failed.append((item['id'], item['title'], res))

    print(f"\nDone: {success} downloaded, {skipped} existing, {len(failed)} failed.")
    if failed:
        print("Failed list:", failed)
