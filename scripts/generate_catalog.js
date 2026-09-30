/**
 * 生成传世油画名作台账总览表 (docs/COLLECTED_ARTWORKS.md)
 */
const fs = require('fs');
const path = require('path');

const GENRE_MAP = {
    // 文艺复兴
    'davinci_mona_lisa': '👤 人物肖像',
    'davinci_last_supper': '🏛️ 神话宗教',
    'michelangelo_creation_of_adam': '🏛️ 神话宗教',
    'botticelli_birth_of_venus': '🏛️ 神话宗教',
    'botticelli_primavera': '🏛️ 神话宗教',
    'raphael_school_of_athens': '🏛️ 神话宗教',
    'raphael_sistine_madonna': '🏛️ 神话宗教',
    'raphael_madonna_of_the_meadow': '🏛️ 神话宗教',
    'davinci_lady_with_ermine': '👤 人物肖像',
    'van_eyck_arnolfini_portrait': '👤 人物肖像',
    'bosch_garden_of_earthly_delights': '🏛️ 神话宗教',
    'bruegel_tower_of_babel': '🏛️ 神话宗教',
    'bruegel_the_hunters_in_the_snow': '🌿 自然风景',
    'bruegel_triumph_of_death': '🏛️ 神话宗教',
    'bruegel_parable_of_the_blind': '🏛️ 神话宗教',

    // 巴洛克
    'caravaggio_calling_of_saint_matthew': '🏛️ 神话宗教',
    'caravaggio_judith_beheading_holofernes': '🏛️ 神话宗教',
    'caravaggio_bacchus': '🏛️ 神话宗教',
    'caravaggio_supper_at_emmaus': '🏛️ 神话宗教',
    'rembrandt_night_watch': '⚔️ 历史故事',
    'rembrandt_anatomy_lesson': '⚔️ 历史故事',
    'rembrandt_storm_on_sea_of_galilee': '🏛️ 神话宗教',
    'velazquez_las_meninas': '👤 人物肖像',
    'vermeer_pearl_earring': '👤 人物肖像',
    'vermeer_the_milkmaid': '👤 人物肖像',
    'vermeer_the_little_street': '🌿 自然风景',
    'vermeer_view_of_delft': '🌿 自然风景',
    'vermeer_the_astronomer': '👤 人物肖像',

    // 浪漫主义与新古典
    'fragonard_the_swing': '👤 人物肖像',
    'david_oath_of_the_horatii': '⚔️ 历史故事',
    'david_death_of_marat': '⚔️ 历史故事',
    'david_napoleon_crossing_the_alps': '⚔️ 历史故事',
    'ingres_the_valpincon_bather': '👤 人物肖像',
    'ingres_la_grande_odalisque': '👤 人物肖像',
    'ingres_the_source': '👤 人物肖像',
    'goya_third_of_may_1808': '⚔️ 历史故事',
    'goya_saturn_devouring_his_son': '🏛️ 神话宗教',
    'gericault_raft_of_the_medusa': '⚔️ 历史故事',
    'delacroix_liberty_leading_the_people': '⚔️ 历史故事',
    'friedrich_wanderer_above_sea_of_fog': '🌿 自然风景',
    'constable_the_hay_wain': '🌿 自然风景',
    'turner_the_fighting_temeraire': '🌿 自然风景',
    'turner_rain_steam_and_speed': '🌿 自然风景',

    // 写实主义
    'millet_the_gleaners': '⚔️ 历史故事',
    'repin_barge_haulers_on_the_volga': '⚔️ 历史故事',
    'whistler_mothers_portrait': '👤 人物肖像',

    // 莫奈
    'monet_giverny_path': '🌿 自然风景',
    'monet_argenteuil': '🌿 自然风景',
    'monet_met_irises': '🌿 自然风景',
    'monet_vetheuil': '🌿 自然风景',
    'monet_sainte_adresse': '🌿 自然风景',
    'monet_gladiolus': '🌿 自然风景',
    'monet_water_lilies_bridge': '🌿 自然风景',
    'monet_poppy_field': '🌿 自然风景',
    'monet_impression_sunrise': '🌿 自然风景',
    'monet_woman_with_parasol': '👤 人物肖像',
    'monet_water_lilies_1906': '🌿 自然风景',
    'monet_haystacks_snow': '🌿 自然风景',
    'monet_rouen_cathedral': '🌿 自然风景',
    'monet_saint_lazare': '🌿 自然风景',
    'monet_camille_green_dress': '👤 人物肖像',
    'monet_dejeuner_sur_l_herbe': '👤 人物肖像',
    'monet_women_in_garden': '👤 人物肖像',
    'monet_la_grenouillere': '🌿 自然风景',
    'monet_argenteuil_basin': '🌿 自然风景',
    'monet_boulevard_capucines': '🌿 自然风景',
    'monet_rue_saint_denis': '🌿 自然风景',
    'monet_poplars': '🌿 自然风景',
    'monet_etretat_cliff': '🌿 自然风景',
    'monet_parliament': '🌿 自然风景',
    'monet_waterloo_bridge': '🌿 自然风景',
    'monet_venice_grand_canal': '🌿 自然风景',

    // 印象派
    'manet_dejeuner_sur_l_herbe': '👤 人物肖像',
    'manet_olympia': '👤 人物肖像',
    'manet_a_bar_at_the_folies_bergere': '👤 人物肖像',
    'renoir_bal_du_moulin_de_la_galette': '👤 人物肖像',
    'renoir_luncheon_of_the_boating_party': '👤 人物肖像',
    'degas_the_dance_class': '👤 人物肖像',
    'degas_dancer_tilting': '👤 人物肖像',
    'degas_l_absinthe': '👤 人物肖像',
    'caillebotte_paris_street_rainy_day': '🌿 自然风景',

    // 后印象派
    'vangogh_starry_night': '🌿 自然风景',
    'vangogh_sunflowers': '🌿 自然风景',
    'vangogh_starry_night_over_the_rhone': '🌿 自然风景',
    'vangogh_almond_blossom': '🌿 自然风景',
    'vangogh_irises': '🌿 自然风景',
    'vangogh_night_cafe': '🌿 自然风景',
    'vangogh_potato_eaters': '👤 人物肖像',
    'vangogh_self_portrait_bandaged_ear': '👤 人物肖像',
    'seurat_sunday_afternoon': '🌿 自然风景',
    'cezanne_mont_sainte_victoire': '🌿 自然风景',
    'cezanne_card_players': '👤 人物肖像',
    'cezanne_the_large_bathers': '👤 人物肖像',
    'gauguin_where_do_we_come_from': '🏛️ 神话宗教',
    'gauguin_vision_after_the_sermon': '🏛️ 神话宗教',
    'gauguin_tahitian_women_on_beach': '👤 人物肖像',
    'rousseau_the_sleeping_gypsy': '🏛️ 神话宗教',
    'rousseau_the_dream': '🏛️ 神话宗教',

    // 表现主义
    'munch_the_scream': '👤 人物肖像',
    'klimt_the_kiss': '👤 人物肖像',
    'klimt_adele_bloch_bauer_i': '👤 人物肖像',
    'waterhouse_the_lady_of_shalott': '🏛️ 神话宗教'
};

const dataJsPath = path.join(__dirname, '../data/masterpieces.js');
const outputMdPath = path.join(__dirname, '../../docs/COLLECTED_ARTWORKS.md');

const content = fs.readFileSync(dataJsPath, 'utf8');
eval(content.replace(/window\./g, 'global.'));

const paintings = global.MASTERPIECES;
const catsData = global.ART_CATEGORIES;

// 题材统计
const genreCounts = {};
paintings.forEach(p => {
    const g = p.genre || GENRE_MAP[p.id] || '🌿 自然风景';
    p.genre = g;
    genreCounts[g] = (genreCounts[g] || 0) + 1;
});

// 生成 Markdown
const md = [];
md.push('# 📋 传世著名油画已收录台账总览表 (Collected Masterpieces Catalog)\n');
md.push('> **统计基准**：2026-09-29  ');
md.push(`> **已收录总量**：**${paintings.length} 幅** 世界殿堂级油画旷世杰作  `);
md.push(`> **展厅流派数**：**${catsData.length} 大历史时代展厅**  `);
md.push('> **准入标准**：完全遵照 [`docs/ART_SELECTION_SPEC.md`](ART_SELECTION_SPEC.md) 执行三重认证与纯净度质检\n');
md.push('---\n');

md.push('## 📊 题材与展厅全景统计 (Overview)\n');
md.push('### 1. 四大核心题材分布\n');
md.push('| 核心题材 | 收录画作数量 | 占比 | 代表作品范例 |');
md.push('| :--- | :---: | :---: | :--- |');

const sortedGenres = Object.entries(genreCounts).sort((a, b) => b[1] - a[1]);
sortedGenres.forEach(([g, cnt]) => {
    const pct = ((cnt / paintings.length) * 100).toFixed(1) + '%';
    const examples = paintings.filter(p => p.genre === g).slice(0, 3).map(p => p.title).join('、');
    md.push(`| **${g}** | **${cnt} 幅** | ${pct} | ${examples} 等 |`);
});

md.push('\n### 2. 八大流派展厅分布\n');
md.push('| 序号 | 展厅流派名称 | 收录作品数 | 重点大师阵容 |');
md.push('| :---: | :--- | :---: | :--- |');

catsData.forEach((cat, idx) => {
    const catItems = paintings.filter(p => p.category === cat.id);
    const artists = [...new Set(catItems.map(p => {
        const match = p.artist.match(/\((.*?)\)/);
        return match ? match[1] : p.artist;
    }))];
    md.push(`| ${idx + 1} | ${cat.name} | **${cat.count} 幅** | ${artists.slice(0, 5).join('、')} |`);
});

md.push('\n---\n');
md.push('## 🏛️ 全部已收录传世油画名作台账明细 (Detailed Catalog)\n');
md.push('| 编号 | 中文题名 (年份) | 外文题名 | 创作者 (Artist) | 流派展厅 | 核心题材 | 资产文件名 | 质检状态 |');
md.push('| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: |');

paintings.forEach((p, i) => {
    const catObj = catsData.find(c => c.id === p.category);
    const catName = catObj ? catObj.name.split(' ')[1] : p.category;
    const g = p.genre;
    const num = String(i + 1).padStart(3, '0');
    md.push(`| **${num}** | **${p.title}** | *${p.enTitle}* | ${p.artist} | ${catName} | ${g} | \`${p.file}\` | ✅ 纯净原版 |`);
});

md.push('\n---\n');
md.push('## 🔍 题材分类索引速查 (Quick Genre Index)\n');

['🌿 自然风景', '👤 人物肖像', '⚔️ 历史故事', '🏛️ 神话宗教'].forEach(g => {
    const subItems = paintings.filter(p => p.genre === g);
    md.push(`### ${g} (${subItems.length} 幅)\n`);
    const lines = subItems.map(item => `- **${item.title}** —— ${item.artist} (*${item.enTitle}*)`);
    md.push(lines.join('\n'));
    md.push('\n');
});

const mdContent = md.join('\n');
fs.writeFileSync(outputMdPath, mdContent, 'utf8');

console.log(`Successfully generated ${outputMdPath} with ${paintings.length} artworks cataloged!`);
