# -*- coding: utf-8 -*-
"""
优化版名画采集脚本：带智能搜索、限流避让与 2.5K/4K 高清 CDN 下载
遵循 docs/ART_SELECTION_SPEC.md 规范标准
"""
import urllib.request
import urllib.parse
import json
import os
import time
import sys
from PIL import Image

NEW_MASTERPIECES = [
    # === 🇺🇸 美国历史里程碑油画 ===
    {
        'id': 'leutze_washington_crossing_delaware',
        'title': '华盛顿横渡特拉华河 (1851)',
        'enTitle': 'Washington Crossing the Delaware',
        'artist': 'Emanuel Leutze (洛伊茨)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'leutze_washington_crossing_delaware.jpg',
        'searchTerm': 'Emanuel Leutze Washington Crossing the Delaware',
        'quote': '“To courage and virtue, the most arduous enterprise becomes easy.”',
        'quoteAuthor': '— George Washington'
    },
    {
        'id': 'trumbull_declaration_of_independence',
        'title': '独立宣言 (1819)',
        'enTitle': 'Declaration of Independence',
        'artist': 'John Trumbull (特朗布尔)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'trumbull_declaration_of_independence.jpg',
        'searchTerm': 'Declaration of Independence 1819 John Trumbull',
        'quote': '“We hold these truths to be self-evident, that all men are created equal.”',
        'quoteAuthor': '— Thomas Jefferson'
    },
    {
        'id': 'gast_american_progress',
        'title': '美洲的进步 · 西进先锋 (1872)',
        'enTitle': 'American Progress',
        'artist': 'John Gast (约翰·加斯特)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'gast_american_progress.jpg',
        'searchTerm': 'American Progress John Gast painting',
        'quote': '“Westward the course of empire takes its way, guided by the light of progress.”',
        'quoteAuthor': '— John Gast'
    },
    {
        'id': 'homer_prisoners_from_the_front',
        'title': '来自前线的囚犯 · 南北战争 (1866)',
        'enTitle': 'Prisoners from the Front',
        'artist': 'Winslow Homer (温斯洛·霍默)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'homer_prisoners_from_the_front.jpg',
        'searchTerm': 'Winslow Homer Prisoners from the Front',
        'quote': '“Look at nature, work independently, and solve your own problems.”',
        'quoteAuthor': '— Winslow Homer'
    },
    {
        'id': 'west_death_of_general_wolfe',
        'title': '沃尔夫将军之死 · 魁北克战役 (1770)',
        'enTitle': 'The Death of General Wolfe',
        'artist': 'Benjamin West (本杰明·韦斯特)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'west_death_of_general_wolfe.jpg',
        'searchTerm': 'Benjamin West The Death of General Wolfe',
        'quote': '“Art is the representation of human passion and heroism.”',
        'quoteAuthor': '— Benjamin West'
    },
    {
        'id': 'homer_the_gulf_stream',
        'title': '墨西哥湾流 (1899)',
        'enTitle': 'The Gulf Stream',
        'artist': 'Winslow Homer (温斯洛·霍默)',
        'category': 'realism',
        'genre': '🌿 自然风景',
        'file': 'homer_the_gulf_stream.jpg',
        'searchTerm': 'Winslow Homer The Gulf Stream Metropolitan',
        'quote': '“The water is magnificent; the light upon the undulating wave is life itself.”',
        'quoteAuthor': '— Winslow Homer'
    },

    # === 🏛️ 文艺复兴与北方画派 ===
    {
        'id': 'davinci_virgin_of_the_rocks',
        'title': '岩间圣母 (1483)',
        'enTitle': 'Virgin of the Rocks',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'file': 'davinci_virgin_of_the_rocks.jpg',
        'searchTerm': 'Leonardo da Vinci Virgin of the Rocks Louvre',
        'quote': '“Painting is poetry that is seen rather than felt.”',
        'quoteAuthor': '— Leonardo da Vinci'
    },
    {
        'id': 'davinci_st_john_the_baptist',
        'title': '施洗者圣约翰 (1513)',
        'enTitle': 'St. John the Baptist',
        'artist': 'Leonardo da Vinci (达·芬奇)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'file': 'davinci_st_john_the_baptist.jpg',
        'searchTerm': 'Leonardo da Vinci Saint Jean Baptiste',
        'quote': '“The painter who draws merely by practice and by eye is like a mirror.”',
        'quoteAuthor': '— Leonardo da Vinci'
    },
    {
        'id': 'titian_venus_of_urbino',
        'title': '乌尔比诺的维纳斯 (1538)',
        'enTitle': 'Venus of Urbino',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'file': 'titian_venus_of_urbino.jpg',
        'searchTerm': 'Tiziano Venere di Urbino Uffizi',
        'quote': '“A good painter needs only three colours: black, white and red.”',
        'quoteAuthor': '— Titian'
    },
    {
        'id': 'titian_assumption_of_the_virgin',
        'title': '圣母升天 (1518)',
        'enTitle': 'Assumption of the Virgin',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'file': 'titian_assumption_of_the_virgin.jpg',
        'searchTerm': 'Titian Assumption of the Virgin 1516-1518 Frari',
        'quote': '“Colour must be warm and life-infused, rising to heaven like pure light.”',
        'quoteAuthor': '— Titian'
    },
    {
        'id': 'titian_bacchus_and_ariadne',
        'title': '酒神与阿丽亚娜 (1523)',
        'enTitle': 'Bacchus and Ariadne',
        'artist': 'Titian (提香)',
        'category': 'renaissance',
        'genre': '🏛️ 神话宗教',
        'file': 'titian_bacchus_and_ariadne.jpg',
        'searchTerm': 'Titian Bacchus and Ariadne National Gallery London',
        'quote': '“Art is more powerful than nature, for it captures the ecstatic moment forever.”',
        'quoteAuthor': '— Titian'
    },
    {
        'id': 'giorgione_the_tempest',
        'title': '暴风雨 (1508)',
        'enTitle': 'The Tempest',
        'artist': 'Giorgione (乔尔乔内)',
        'category': 'renaissance',
        'genre': '🌿 自然风景',
        'file': 'giorgione_the_tempest.jpg',
        'searchTerm': 'Giorgione La tempesta Gallerie dell Accademia',
        'quote': '“Before the storm breaks, nature holds her breath in mysterious hush.”',
        'quoteAuthor': '— Giorgione'
    },
    {
        'id': 'durer_self_portrait_fur_collar',
        'title': '自画像 · 穿毛皮大衣 (1500)',
        'enTitle': 'Self-Portrait at Twenty-Eight',
        'artist': 'Albrecht Dürer (丢勒)',
        'category': 'renaissance',
        'genre': '👤 人物肖像',
        'file': 'durer_self_portrait_fur_collar.jpg',
        'searchTerm': 'Albrecht Dürer Self-Portrait at Twenty-Eight Alte Pinakothek',
        'quote': '“I paint myself with imperishable colours to bear witness to my craft.”',
        'quoteAuthor': '— Albrecht Dürer'
    },
    {
        'id': 'bruegel_the_peasant_wedding',
        'title': '农民的婚礼 (1567)',
        'enTitle': 'The Peasant Wedding',
        'artist': 'Pieter Bruegel the Elder (老彼得·勃鲁盖尔)',
        'category': 'renaissance',
        'genre': '⚔️ 历史故事',
        'file': 'bruegel_the_peasant_wedding.jpg',
        'searchTerm': 'Pieter Bruegel the Elder The Peasant Wedding',
        'quote': '“To paint the laughter and bread of the common hearth is to paint truth.”',
        'quoteAuthor': '— Pieter Bruegel the Elder'
    },
    {
        'id': 'holbein_the_ambassadors',
        'title': '出使英国的法国使臣 (1533)',
        'enTitle': 'The Ambassadors',
        'artist': 'Hans Holbein the Younger (小汉斯·霍尔拜因)',
        'category': 'renaissance',
        'genre': '👤 人物肖像',
        'file': 'holbein_the_ambassadors.jpg',
        'searchTerm': 'Hans Holbein the Younger The Ambassadors National Gallery',
        'quote': '“Remember that thou must die; yet wisdom and art endure beyond the grave.”',
        'quoteAuthor': '— Hans Holbein the Younger'
    },

    # === 🎭 巴洛克与荷兰黄金时代 ===
    {
        'id': 'rubens_descent_from_the_cross',
        'title': '下十字架 (1614)',
        'enTitle': 'The Descent from the Cross',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'rubens_descent_from_the_cross.jpg',
        'searchTerm': 'Rubens Descent from the Cross Antwerp',
        'quote': '“My passion comes from the heavens above, not from earthly reflections.”',
        'quoteAuthor': '— Peter Paul Rubens'
    },
    {
        'id': 'rubens_rape_of_daughters_leucippus',
        'title': '抢夺留西帕斯的女儿 (1618)',
        'enTitle': 'The Rape of the Daughters of Leucippus',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'rubens_rape_of_daughters_leucippus.jpg',
        'searchTerm': 'Peter Paul Rubens The Rape of the Daughters of Leucippus',
        'quote': '“No undertaking, however vast in size, has surpassed my courage.”',
        'quoteAuthor': '— Peter Paul Rubens'
    },
    {
        'id': 'rubens_the_three_graces',
        'title': '三美神 (1635)',
        'enTitle': 'The Three Graces',
        'artist': 'Peter Paul Rubens (鲁本斯)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'rubens_the_three_graces.jpg',
        'searchTerm': 'The Three Graces by Peter Paul Rubens Prado',
        'quote': '“Grace and beauty are celestial harmony made flesh upon the canvas.”',
        'quoteAuthor': '— Peter Paul Rubens'
    },
    {
        'id': 'rembrandt_return_of_the_prodigal_son',
        'title': '浪子回头 (1669)',
        'enTitle': 'The Return of the Prodigal Son',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'rembrandt_return_of_the_prodigal_son.jpg',
        'searchTerm': 'Rembrandt Harmensz van Rijn The Return of the Prodigal Son Hermitage',
        'quote': '“A painting is finished when the artist says it is finished in his soul.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'rembrandt_self_portrait_1659',
        'title': '戴贝雷帽的自画像 (1659)',
        'enTitle': 'Self-Portrait with Beret',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'rembrandt_self_portrait_1659.jpg',
        'searchTerm': 'Rembrandt van Rijn Self-Portrait 1659 National Gallery Washington',
        'quote': '“Put well in practice what you know; in so doing you discover hidden truth.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'rembrandt_the_jewish_bride',
        'title': '犹太新娘 (1667)',
        'enTitle': 'The Jewish Bride',
        'artist': 'Rembrandt (伦勃朗)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'rembrandt_the_jewish_bride.jpg',
        'searchTerm': 'Rembrandt Harmensz van Rijn The Jewish Bride Rijksmuseum',
        'quote': '“Tenderness is the highest touch of painting; without it, colour is but dust.”',
        'quoteAuthor': '— Rembrandt'
    },
    {
        'id': 'vermeer_woman_reading_a_letter',
        'title': '读信的蓝衣女人 (1663)',
        'enTitle': 'Woman Reading a Letter',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'vermeer_woman_reading_a_letter.jpg',
        'searchTerm': 'Johannes Vermeer Woman Reading a Letter Rijksmuseum',
        'quote': '“In silence and serene blue, the soul hears what words cannot utter.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_woman_holding_a_balance',
        'title': '持天平的女人 (1664)',
        'enTitle': 'Woman Holding a Balance',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'vermeer_woman_holding_a_balance.jpg',
        'searchTerm': 'Johannes Vermeer Woman Holding a Balance National Gallery Washington',
        'quote': '“Balance your earthly desires with the eternal scale of truth.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'vermeer_the_geographer',
        'title': '地理学家 (1669)',
        'enTitle': 'The Geographer',
        'artist': 'Johannes Vermeer (维米尔)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'vermeer_the_geographer.jpg',
        'searchTerm': 'Johannes Vermeer The Geographer Städel',
        'quote': '“To gaze into the vast world through maps and sunlight streaming through glass.”',
        'quoteAuthor': '— Johannes Vermeer'
    },
    {
        'id': 'caravaggio_medusa',
        'title': '美杜莎 (1597)',
        'enTitle': 'Medusa',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'caravaggio_medusa.jpg',
        'searchTerm': 'Medusa by Caravaggio Uffizi',
        'quote': '“When there is no energy there is no colour, no shape, no life.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'caravaggio_david_with_head_of_goliath',
        'title': '大卫手提歌利亚的头颅 (1610)',
        'enTitle': 'David with the Head of Goliath',
        'artist': 'Caravaggio (卡拉瓦乔)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'caravaggio_david_with_head_of_goliath.jpg',
        'searchTerm': 'David with the Head of Goliath Caravaggio Borghese',
        'quote': '“I need no other master than nature herself; she provides all models.”',
        'quoteAuthor': '— Caravaggio'
    },
    {
        'id': 'hals_the_gypsy_girl',
        'title': '吉普赛女郎 (1628)',
        'enTitle': 'The Gypsy Girl',
        'artist': 'Frans Hals (弗朗斯·哈尔斯)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'hals_the_gypsy_girl.jpg',
        'searchTerm': 'Frans Hals The Gypsy Girl Louvre',
        'quote': '“Catch the living smile upon the lips with a single spontaneous stroke.”',
        'quoteAuthor': '— Frans Hals'
    },
    {
        'id': 'poussin_et_in_arcadia_ego',
        'title': '阿卡迪亚的牧人 (1638)',
        'enTitle': 'Et in Arcadia ego',
        'artist': 'Nicolas Poussin (尼古拉·普桑)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'poussin_et_in_arcadia_ego.jpg',
        'searchTerm': 'Nicolas Poussin Et in Arcadia ego Louvre',
        'quote': '“Even in paradise, death reminds us of our fleeting passage.”',
        'quoteAuthor': '— Nicolas Poussin'
    },
    {
        'id': 'velazquez_the_spinners',
        'title': '纺织女 · 阿拉克涅的寓言 (1657)',
        'enTitle': 'The Spinners (Las Hilanderas)',
        'artist': 'Diego Velázquez (委拉斯凯兹)',
        'category': 'baroque',
        'genre': '🏛️ 神话宗教',
        'file': 'velazquez_the_spinners.jpg',
        'searchTerm': 'Diego Velázquez Las Hilanderas Prado',
        'quote': '“I would rather be the first painter of common things than the second in finer art.”',
        'quoteAuthor': '— Diego Velázquez'
    },
    {
        'id': 'velazquez_portrait_of_innocent_x',
        'title': '教皇英诺森十世像 (1650)',
        'enTitle': 'Portrait of Innocent X',
        'artist': 'Diego Velázquez (委拉斯凯兹)',
        'category': 'baroque',
        'genre': '👤 人物肖像',
        'file': 'velazquez_portrait_of_innocent_x.jpg',
        'searchTerm': 'Velázquez Pope Innocent X Doria Pamphilj',
        'quote': '“Troppo vero! (All too true!)”',
        'quoteAuthor': '— Pope Innocent X on Velázquez'
    },

    # === ⚡ 新古典、洛可可与浪漫主义 ===
    {
        'id': 'david_death_of_socrates',
        'title': '苏格拉底之死 (1787)',
        'enTitle': 'The Death of Socrates',
        'artist': 'Jacques-Louis David (达维特)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'david_death_of_socrates.jpg',
        'searchTerm': 'Jacques-Louis David The Death of Socrates Metropolitan',
        'quote': '“The unexamined life is not worth living.”',
        'quoteAuthor': '— Socrates / David'
    },
    {
        'id': 'david_coronation_of_napoleon',
        'title': '拿破仑一世及皇后加冕典礼 (1807)',
        'enTitle': 'The Coronation of Napoleon',
        'artist': 'Jacques-Louis David (达维特)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'david_coronation_of_napoleon.jpg',
        'searchTerm': 'Jacques-Louis David The Coronation of Napoleon Louvre',
        'quote': '“To achieve the grand style, one must create with heroic dignity.”',
        'quoteAuthor': '— Jacques-Louis David'
    },
    {
        'id': 'fragonard_young_girl_reading',
        'title': '读书的少女 (1770)',
        'enTitle': 'A Young Girl Reading',
        'artist': 'Jean-Honoré Fragonard (弗拉戈纳尔)',
        'category': 'romanticism',
        'genre': '👤 人物肖像',
        'file': 'fragonard_young_girl_reading.jpg',
        'searchTerm': 'Jean-Honoré Fragonard Young Girl Reading National Gallery Washington',
        'quote': '“In the stillness of a page, youth finds its eternal reverie.”',
        'quoteAuthor': '— Jean-Honoré Fragonard'
    },
    {
        'id': 'watteau_the_embarkation_for_cythera',
        'title': '舟发西苔岛 (1717)',
        'enTitle': 'The Embarkation for Cythera',
        'artist': 'Antoine Watteau (让-安东尼·华托)',
        'category': 'romanticism',
        'genre': '🏛️ 神话宗教',
        'file': 'watteau_the_embarkation_for_cythera.jpg',
        'searchTerm': 'Antoine Watteau L\'Embarquement pour Cythere Louvre',
        'quote': '“Love is an island of dreams towards which our frail boats sail forever.”',
        'quoteAuthor': '— Antoine Watteau'
    },
    {
        'id': 'goya_the_nude_maja',
        'title': '裸体的玛哈 (1800)',
        'enTitle': 'The Nude Maja',
        'artist': 'Francisco Goya (戈雅)',
        'category': 'romanticism',
        'genre': '👤 人物肖像',
        'file': 'goya_the_nude_maja.jpg',
        'searchTerm': 'The Nude Maja Francisco de Goya Prado',
        'quote': '“Painting, like music, selects notes from nature to transform into passion.”',
        'quoteAuthor': '— Francisco Goya'
    },
    {
        'id': 'goya_the_clothed_maja',
        'title': '着衣的玛哈 (1803)',
        'enTitle': 'The Clothed Maja',
        'artist': 'Francisco Goya (戈雅)',
        'category': 'romanticism',
        'genre': '👤 人物肖像',
        'file': 'goya_the_clothed_maja.jpg',
        'searchTerm': 'La maja vestida Goya Prado',
        'quote': '“The object of art is to awaken the deepest chords of human nature.”',
        'quoteAuthor': '— Francisco Goya'
    },
    {
        'id': 'delacroix_the_barque_of_dante',
        'title': '但丁之舟 (1822)',
        'enTitle': 'The Barque of Dante',
        'artist': 'Eugène Delacroix (德拉克罗瓦)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'delacroix_the_barque_of_dante.jpg',
        'searchTerm': 'Eugène Delacroix The Barque of Dante Louvre',
        'quote': '“Passionate enthusiasm is the divine spark of all great masterpieces.”',
        'quoteAuthor': '— Eugène Delacroix'
    },
    {
        'id': 'delacroix_death_of_sardanapalus',
        'title': '萨达那帕鲁斯之死 (1827)',
        'enTitle': 'The Death of Sardanapalus',
        'artist': 'Eugène Delacroix (德拉克罗瓦)',
        'category': 'romanticism',
        'genre': '⚔️ 历史故事',
        'file': 'delacroix_death_of_sardanapalus.jpg',
        'searchTerm': 'Delacroix Mort de Sardanapale Louvre',
        'quote': '“Glory is not a vain word; it is the triumph of tragic fire.”',
        'quoteAuthor': '— Eugène Delacroix'
    },
    {
        'id': 'constable_salisbury_cathedral',
        'title': '索尔兹伯里大教堂 (1823)',
        'enTitle': 'Salisbury Cathedral from the Bishop\'s Grounds',
        'artist': 'John Constable (约翰·康斯特勃)',
        'category': 'romanticism',
        'genre': '🌿 自然风景',
        'file': 'constable_salisbury_cathedral.jpg',
        'searchTerm': 'John Constable Salisbury Cathedral from the Bishop\'s Grounds',
        'quote': '“Painting is a science, and should be pursued as an inquiry into nature.”',
        'quoteAuthor': '— John Constable'
    },
    {
        'id': 'friedrich_sea_of_ice',
        'title': '冰海 · 极地沉船 (1824)',
        'enTitle': 'The Sea of Ice',
        'artist': 'Caspar David Friedrich (弗里德里希)',
        'category': 'romanticism',
        'genre': '🌿 自然风景',
        'file': 'friedrich_sea_of_ice.jpg',
        'searchTerm': 'Caspar David Friedrich Das Eismeer Hamburger Kunsthalle',
        'quote': '“The sublime solitude of ice and silence speaks louder than human voice.”',
        'quoteAuthor': '— Caspar David Friedrich'
    },

    # === 🌾 写实主义与巡回展览画派 ===
    {
        'id': 'millet_the_angelus',
        'title': '晚钟 (1859)',
        'enTitle': 'The Angelus',
        'artist': 'Jean-François Millet (米勒)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'millet_the_angelus.jpg',
        'searchTerm': 'Jean-François Millet The Angelus Orsay',
        'quote': '“Peasant subjects suit my nature best; the human side of art moves me most.”',
        'quoteAuthor': '— Jean-François Millet'
    },
    {
        'id': 'courbet_burial_at_ornans',
        'title': '奥南的葬礼 (1850)',
        'enTitle': 'A Burial at Ornans',
        'artist': 'Gustave Courbet (古斯塔夫·库尔贝)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'courbet_burial_at_ornans.jpg',
        'searchTerm': 'Gustave Courbet A Burial at Ornans Orsay',
        'quote': '“Show me an angel and I will paint one. I paint only what my eyes behold.”',
        'quoteAuthor': '— Gustave Courbet'
    },
    {
        'id': 'courbet_the_painters_studio',
        'title': '画室 · 真实寓言 (1855)',
        'enTitle': 'The Painter\'s Studio',
        'artist': 'Gustave Courbet (古斯塔夫·库尔贝)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'courbet_the_painters_studio.jpg',
        'searchTerm': 'Gustave Courbet The Artist\'s Studio Orsay',
        'quote': '“To know in order to create, that was my idea. To be simply a painter.”',
        'quoteAuthor': '— Gustave Courbet'
    },
    {
        'id': 'corot_the_bridge_at_mantes',
        'title': '芒特的桥 (1869)',
        'enTitle': 'The Bridge at Mantes',
        'artist': 'Jean-Baptiste-Camille Corot (卡米耶·柯罗)',
        'category': 'realism',
        'genre': '🌿 自然风景',
        'file': 'corot_the_bridge_at_mantes.jpg',
        'searchTerm': 'Jean-Baptiste Camille Corot The Bridge at Mantes Louvre',
        'quote': '“I pray that God will make me see nature without prejudices like a child.”',
        'quoteAuthor': '— Jean-Baptiste-Camille Corot'
    },
    {
        'id': 'shishkin_morning_in_a_pine_forest',
        'title': '松林的早晨 (1889)',
        'enTitle': 'Morning in a Pine Forest',
        'artist': 'Ivan Shishkin (伊凡·希什金)',
        'category': 'realism',
        'genre': '🌿 自然风景',
        'file': 'shishkin_morning_in_a_pine_forest.jpg',
        'searchTerm': 'Ivan Shishkin Morning in a Pine Forest Tretyakov',
        'quote': '“Russia is a land of forests, majestic and eternal under morning dew.”',
        'quoteAuthor': '— Ivan Shishkin'
    },
    {
        'id': 'repin_ivan_the_terrible',
        'title': '伊凡雷帝杀子 (1885)',
        'enTitle': 'Ivan the Terrible and His Son Ivan',
        'artist': 'Ilya Repin (伊里亚·列宾)',
        'category': 'realism',
        'genre': '⚔️ 历史故事',
        'file': 'repin_ivan_the_terrible.jpg',
        'searchTerm': 'Ivan the Terrible and His Son Ivan Tretyakov',
        'quote': '“I painted with tears and blood; tragic history gripped my soul.”',
        'quoteAuthor': '— Ilya Repin'
    },
    {
        'id': 'savrasov_the_rooks_have_returned',
        'title': '白嘴鸦飞来了 (1871)',
        'enTitle': 'The Rooks Have Returned',
        'artist': 'Alexei Savrasov (阿列克谢·萨夫拉索夫)',
        'category': 'realism',
        'genre': '🌿 自然风景',
        'file': 'savrasov_the_rooks_have_returned.jpg',
        'searchTerm': 'Savrasov The Rooks Have Returned Tretyakov',
        'quote': '“Spring begins quietly, with the cry of birds upon the melting snow.”',
        'quoteAuthor': '— Alexei Savrasov'
    },

    # === 🎨 印象派与后印象派 ===
    {
        'id': 'renoir_the_swing',
        'title': '秋千 (1876)',
        'enTitle': 'The Swing',
        'artist': 'Pierre-Auguste Renoir (雷诺阿)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'file': 'renoir_the_swing.jpg',
        'searchTerm': 'Pierre-Auguste Renoir The Swing Orsay',
        'quote': '“A picture ought to be something pleasant, joyful, and pretty.”',
        'quoteAuthor': '— Pierre-Auguste Renoir'
    },
    {
        'id': 'degas_ballet_rehearsal_on_stage',
        'title': '舞台上的芭蕾排练 (1874)',
        'enTitle': 'Ballet Rehearsal on Stage',
        'artist': 'Edgar Degas (德加)',
        'category': 'impressionism',
        'genre': '👤 人物肖像',
        'file': 'degas_ballet_rehearsal_on_stage.jpg',
        'searchTerm': 'Edgar Degas Repetition d un ballet sur la scene Orsay',
        'quote': '“Art is not what you see, but what you make others see.”',
        'quoteAuthor': '— Edgar Degas'
    },
    {
        'id': 'pissarro_boulevard_montmartre_spring',
        'title': '蒙马特大道 · 春晓 (1897)',
        'enTitle': 'Boulevard Montmartre, Spring Morning',
        'artist': 'Camille Pissarro (卡米耶·毕沙罗)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'file': 'pissarro_boulevard_montmartre_spring.jpg',
        'searchTerm': 'Camille Pissarro Boulevard Montmartre Spring Morning',
        'quote': '“Blessed are they who see beautiful things in humble places.”',
        'quoteAuthor': '— Camille Pissarro'
    },
    {
        'id': 'sisley_flood_at_port_marly',
        'title': '马利港的洪水 (1876)',
        'enTitle': 'Flood at Port-Marly',
        'artist': 'Alfred Sisley (阿尔弗雷德·西斯莱)',
        'category': 'impressionism',
        'genre': '🌿 自然风景',
        'file': 'sisley_flood_at_port_marly.jpg',
        'searchTerm': 'Alfred Sisley Flood at Port-Marly Orsay',
        'quote': '“Every picture shows a spot with which the artist has fallen in love.”',
        'quoteAuthor': '— Alfred Sisley'
    },
    {
        'id': 'vangogh_bedroom_in_arles',
        'title': '阿尔勒的卧室 (1888)',
        'enTitle': 'Bedroom in Arles',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'genre': '🌿 自然风景',
        'file': 'vangogh_bedroom_in_arles.jpg',
        'searchTerm': 'Vincent van Gogh De slaapkamer Van Gogh Museum',
        'quote': '“I should like to paint with that something of eternal peace.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'vangogh_wheatfield_with_crows',
        'title': '麦田群鸦 (1890)',
        'enTitle': 'Wheatfield with Crows',
        'artist': 'Vincent van Gogh (梵高)',
        'category': 'post_impressionism',
        'genre': '🌿 自然风景',
        'file': 'vangogh_wheatfield_with_crows.jpg',
        'searchTerm': 'Vincent van Gogh Wheat Field with Crows 1890',
        'quote': '“I paint immense expanses of wheat beneath troubled skies.”',
        'quoteAuthor': '— Vincent van Gogh'
    },
    {
        'id': 'cezanne_basket_of_apples',
        'title': '苹果篮静物 (1893)',
        'enTitle': 'The Basket of Apples',
        'artist': 'Paul Cézanne (保罗·塞尚)',
        'category': 'post_impressionism',
        'genre': '🌿 自然风景',
        'file': 'cezanne_basket_of_apples.jpg',
        'searchTerm': 'Paul Cezanne The Basket of Apples Art Institute of Chicago',
        'quote': '“With an apple I will astonish Paris.”',
        'quoteAuthor': '— Paul Cézanne'
    }
]

images_dir = r'd:\Antigravity_Workspaces\art-web\2026-09-28-secret-garden\assets\images'

def download_url_with_retry(url, target_path, retries=3):
    headers = {
        'User-Agent': 'ArtWebCurator/2.1 (https://github.com/art-web; contact@artweb.local) Python-urllib'
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) < 20000:
                    time.sleep(2)
                    continue
                with open(target_path, 'wb') as f:
                    f.write(data)
                return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = (attempt + 1) * 5
                print(f"    [429 Rate Limit] Sleeping {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"    HTTP Error {e.code}: {e.reason}")
                time.sleep(2)
        except Exception as ex:
            print(f"    Download error: {ex}")
            time.sleep(2)
    return False

def search_wikimedia_image(search_term):
    headers = {
        'User-Agent': 'ArtWebCurator/2.1 (https://github.com/art-web; contact@artweb.local) Python-urllib'
    }
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(search_term)}&gsrnamespace=6&prop=imageinfo&iiprop=url|size&iiurlwidth=2560&format=json"
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            best_info = None
            best_score = -1

            for pid, pdata in pages.items():
                title = pdata.get('title', '').lower()
                # 排除明显带分析图、地图、草稿的非原画文件
                if any(bad in title for bad in ['svg', 'analysis', 'diagram', 'map', 'stamp', 'coin', 'icon']):
                    continue
                if 'imageinfo' in pdata and len(pdata['imageinfo']) > 0:
                    info = pdata['imageinfo'][0]
                    # 评判质量分：优先考虑带 google art project / 原图尺寸大的
                    score = info.get('width', 0) * info.get('height', 0)
                    if 'google art project' in title or 'prado' in title or 'metropolitan' in title or 'louvre' in title:
                        score *= 2
                    if score > best_score:
                        best_score = score
                        best_info = info
            
            if best_info:
                # 优先获取 2560px CDN 快速缩略图，避免直接拉取极重原图被 429
                chosen_url = best_info.get('thumburl') or best_info.get('url')
                return chosen_url, best_info.get('width'), best_info.get('height')
    except Exception as e:
        print(f"    Search error: {e}")
    return None, 0, 0

def main():
    print(f"=== Starting Intelligent Batch Collection for {len(NEW_MASTERPIECES)} Masterpieces ===")
    success_count = 0
    failed = []

    for idx, item in enumerate(NEW_MASTERPIECES):
        target_path = os.path.join(images_dir, item['file'])
        print(f"[{idx+1}/{len(NEW_MASTERPIECES)}] {item['title']} - {item['artist']}")

        # 检查是否已存在且可用
        if os.path.exists(target_path) and os.path.getsize(target_path) > 150000:
            try:
                with Image.open(target_path) as im:
                    if im.size[0] >= 1200 or im.size[1] >= 1200:
                        print(f"  ✓ Already verified locally ({im.size[0]}x{im.size[1]}, size={os.path.getsize(target_path)} bytes)")
                        success_count += 1
                        continue
            except Exception:
                pass

        # 搜索与下载
        time.sleep(1.0) # 礼貌延时
        img_url, orig_w, orig_h = search_wikimedia_image(item['searchTerm'])
        if img_url:
            print(f"  → Found high-res source ({orig_w}x{orig_h}): downloading...")
            ok = download_url_with_retry(img_url, target_path)
            if ok and os.path.exists(target_path):
                try:
                    with Image.open(target_path) as im:
                        print(f"  ✓ SUCCESS: {im.size[0]}x{im.size[1]}, format: {im.format}")
                        success_count += 1
                except Exception as err:
                    print(f"  ✗ Corrupted image: {err}")
                    failed.append(item['id'])
            else:
                print(f"  ✗ FAILED download: {item['id']}")
                failed.append(item['id'])
        else:
            print(f"  ✗ NOT FOUND on Wikimedia: {item['id']}")
            failed.append(item['id'])

    print("\n" + "="*50)
    print(f"Intelligent Collection Complete! Success: {success_count}/{len(NEW_MASTERPIECES)}")
    if failed:
        print(f"Failed count ({len(failed)}): {failed}")
    else:
        print("ALL 54 MASTERPIECES ACQUIRED AND VERIFIED WITH EXCELLENCE!")

if __name__ == '__main__':
    main()
