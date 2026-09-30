import json
import re

def update_masterpieces():
    path = "data/masterpieces.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"window\.MASTERPIECES\s*=\s*(\[.*?\]);", content, re.DOTALL)
    if not match:
        print("未找到 window.MASTERPIECES")
        return

    data = json.loads(match.group(1))

    # 精准映射表：将各名作归入符合西方艺术史正统的 6 大画种
    GENRE_MAP = {
        # --- 💐 静物花卉 (Still Life & Floral) ---
        'cezanne_basket_of_apples': '💐 静物花卉',
        'vangogh_sunflowers': '💐 静物花卉',
        'vangogh_irises': '💐 静物花卉',
        'vangogh_almond_blossom': '💐 静物花卉',
        'vangogh_bedroom_in_arles': '💐 静物花卉',       # 阿尔勒卧室（室内陈设与私人物品静物）
        'monet_gladiolus': '💐 静物花卉',             # 剑兰花境
        'monet_yellow_irises': '💐 静物花卉',         # 吉维尼的黄色鸢尾花
        'monet_met_irises': '💐 静物花卉',            # 大都会鸢尾花丛
        'monet_the_rose_arches': '💐 静物花卉',       # 吉维尼玫瑰花园拱门

        # --- 👥 风俗生活 (Daily Life & Genre Scenes) ---
        'bruegel_the_peasant_wedding': '👥 风俗生活',
        'rembrandt_anatomy_lesson': '👥 风俗生活',
        'rembrandt_night_watch': '👥 风俗生活',
        'millet_the_gleaners': '👥 风俗生活',
        'millet_the_angelus': '👥 风俗生活',
        'repin_barge_haulers_on_the_volga': '👥 风俗生活',
        'courbet_the_painters_studio': '👥 风俗生活',
        'bazille_studio_rue_condamine': '👥 风俗生活',
        'degas_cotton_office_new_orleans': '👥 风俗生活',
        'degas_orchestra_of_the_opera': '👥 风俗生活',
        'degas_racehorses_before_stands': '👥 风俗生活',
        'degas_the_dance_class': '👥 风俗生活',
        'degas_ballet_rehearsal_on_stage': '👥 风俗生活',
        'degas_rehearsal_on_stage': '👥 风俗生活',
        'degas_blue_dancers': '👥 风俗生活',
        'degas_dancer_tilting': '👥 风俗生活',
        'degas_dancers_at_the_barre': '👥 风俗生活',
        'degas_l_absinthe': '👥 风俗生活',
        'degas_women_ironing': '👥 风俗生活',
        'degas_the_tub': '👥 风俗生活',
        'vermeer_the_milkmaid': '👥 风俗生活',
        'vermeer_woman_holding_a_balance': '👥 风俗生活',
        'vermeer_woman_reading_a_letter': '👥 风俗生活',
        'vermeer_the_astronomer': '👥 风俗生活',
        'vermeer_the_geographer': '👥 风俗生活',
        'fragonard_the_swing': '👥 风俗生活',
        'fragonard_young_girl_reading': '👥 风俗生活',
        'watteau_the_embarkation_for_cythera': '👥 风俗生活',
        'velazquez_the_spinners': '👥 风俗生活',
        'manet_a_bar_at_the_folies_bergere': '👥 风俗生活',
        'manet_dejeuner_sur_l_herbe': '👥 风俗生活',
        'manet_the_balcony': '👥 风俗生活',
        'manet_the_fifer': '👥 风俗生活',
        'manet_in_the_conservatory': '👥 风俗生活',
        'monet_dejeuner_sur_l_herbe': '👥 风俗生活',
        'monet_women_in_garden': '👥 风俗生活',
        'monet_boulevard_capucines': '👥 风俗生活',
        'monet_rue_saint_denis': '👥 风俗生活',
        'monet_saint_lazare': '👥 风俗生活',
        'caillebotte_the_floor_scrapers': '👥 风俗生活',
        'caillebotte_paris_street_rainy_day': '👥 风俗生活',
        'caillebotte_pont_de_l_europe': '👥 风俗生活',
        'caillebotte_boating_on_yerres': '👥 风俗生活',
        'caillebotte_young_man_at_window': '👥 风俗生活',
        'cassatt_cup_of_tea': '👥 风俗生活',
        'cassatt_the_boating_party': '👥 风俗生活',
        'cassatt_the_childs_bath': '👥 风俗生活',
        'bazille_family_reunion': '👥 风俗生活',
        'pissarro_peasant_woman_washing': '👥 风俗生活',
        'pissarro_apple_picking_eragny': '👥 风俗生活',
        'morisot_reading_green_parasol': '👥 风俗生活',
        'morisot_the_cradle': '👥 风俗生活',
        'morisot_woman_at_toilette': '👥 风俗生活',
        'renoir_bal_du_moulin_de_la_galette': '👥 风俗生活',
        'renoir_luncheon_of_the_boating_party': '👥 风俗生活',
        'renoir_the_swing': '👥 风俗生活',
        'renoir_the_loge': '👥 风俗生活',
        'renoir_girls_at_piano': '👥 风俗生活',
        'renoir_two_sisters_terrace': '👥 风俗生活',
        'renoir_the_skiff': '👥 风俗生活',
        'sorolla_walk_on_the_beach': '👥 风俗生活',
        'hassam_boston_common_twilight': '👥 风俗生活',
        'seurat_sunday_afternoon': '👥 风俗生活',
        'cezanne_card_players': '👥 风俗生活',
        'vangogh_potato_eaters': '👥 风俗生活',
        'vangogh_night_cafe': '👥 风俗生活',
        'sargent_carnation_lily_lily_rose': '👥 风俗生活',
        'hals_the_gypsy_girl': '👥 风俗生活',

        # --- ⚔️ 历史故事 (History & Narrative) ---
        'david_coronation_of_napoleon': '⚔️ 历史故事',
        'david_death_of_marat': '⚔️ 历史故事',
        'david_death_of_socrates': '⚔️ 历史故事',
        'david_napoleon_crossing_the_alps': '⚔️ 历史故事',
        'david_oath_of_the_horatii': '⚔️ 历史故事',
        'delacroix_death_of_sardanapalus': '⚔️ 历史故事',
        'delacroix_liberty_leading_the_people': '⚔️ 历史故事',
        'delacroix_the_barque_of_dante': '⚔️ 历史故事',
        'gericault_raft_of_the_medusa': '⚔️ 历史故事',
        'goya_third_of_may_1808': '⚔️ 历史故事',
        'leutze_washington_crossing_delaware': '⚔️ 历史故事',
        'trumbull_declaration_of_independence': '⚔️ 历史故事',
        'west_death_of_general_wolfe': '⚔️ 历史故事',
        'gast_american_progress': '⚔️ 历史故事',
        'homer_prisoners_from_the_front': '⚔️ 历史故事',
        'repin_ivan_the_terrible': '⚔️ 历史故事',

        # --- 👤 人物肖像 (Portraiture) ---
        'davinci_mona_lisa': '👤 人物肖像',
        'davinci_lady_with_ermine': '👤 人物肖像',
        'holbein_the_ambassadors': '👤 人物肖像',
        'titian_flora': '👤 人物肖像',
        'van_eyck_arnolfini_portrait': '👤 人物肖像',
        'rembrandt_self_portrait_1659': '👤 人物肖像',
        'rembrandt_the_jewish_bride': '👤 人物肖像',
        'velazquez_las_meninas': '👤 人物肖像',
        'velazquez_portrait_of_innocent_x': '👤 人物肖像',
        'vermeer_pearl_earring': '👤 人物肖像',
        'goya_the_clothed_maja': '👤 人物肖像',
        'goya_the_nude_maja': '👤 人物肖像',
        'ingres_la_grande_odalisque': '👤 人物肖像',
        'ingres_the_source': '👤 人物肖像',
        'ingres_the_valpincon_bather': '👤 人物肖像',
        'monet_camille_green_dress': '👤 人物肖像',
        'monet_la_japonaise': '👤 人物肖像',
        'monet_the_red_kerchief': '👤 人物肖像',
        'monet_woman_parasol_left': '👤 人物肖像',
        'monet_woman_parasol_right': '👤 人物肖像',
        'monet_woman_with_parasol': '👤 人物肖像',
        'manet_emile_zola': '👤 人物肖像',
        'manet_olympia': '👤 人物肖像',
        'manet_spring_jeanne': '👤 人物肖像',
        'pissarro_self_portrait': '👤 人物肖像',
        'renoir_jeanne_samary': '👤 人物肖像',
        'renoir_madame_charpentier': '👤 人物肖像',
        'renoir_nude_in_sunlight': '👤 人物肖像',
        'renoir_young_girl_combing_hair': '👤 人物肖像',
        'cezanne_the_large_bathers': '👤 人物肖像',
        'gauguin_tahitian_women_on_beach': '👤 人物肖像',
        'vangogh_self_portrait_bandaged_ear': '👤 人物肖像',
        'klimt_adele_bloch_bauer_i': '👤 人物肖像',
        'klimt_the_kiss': '👤 人物肖像',
        'munch_the_scream': '👤 人物肖像',

        # --- 🌿 自然风景 (Landscape) ---
        'claude_lorrain_embarkation_queen_sheba': '🌿 自然风景',
    }

    modified_count = 0
    title_fixed = 0

    for d in data:
        art_id = d.get('id')

        # 修复莫奈剑兰花名与属性
        if art_id == 'monet_gladiolus':
            d['title'] = '剑兰花境 (1876)'
            d['enTitle'] = 'Gladioli in the Garden'
            title_fixed += 1

        # 修复莫奈吉维尼小径标题与属性
        if art_id == 'monet_giverny_path':
            d['title'] = '吉维尼的花园小径 (1902)'
            d['enTitle'] = 'The Garden Path at Giverny'
            title_fixed += 1

        # 题材修正
        if art_id in GENRE_MAP:
            target_genre = GENRE_MAP[art_id]
            if d.get('genre') != target_genre:
                d['genre'] = target_genre
                modified_count += 1
        else:
            # 统一风景与历史符号
            if d.get('genre') == '🌊 自然风景':
                d['genre'] = '🌿 自然风景'
                modified_count += 1
            elif d.get('genre') == '⚔️ 历史叙事':
                d['genre'] = '👥 风俗生活'
                modified_count += 1

    new_json = json.dumps(data, ensure_ascii=False, indent=4)
    new_content = content[:match.start(1)] + new_json + content[match.end(1):]

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"成功更新 {path}: 修改题材 {modified_count} 处，修正标题 {title_fixed} 处。")

if __name__ == "__main__":
    update_masterpieces()
