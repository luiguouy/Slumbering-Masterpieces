import urllib.request
import urllib.parse
import json
import time
import os
from PIL import Image

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ArtWebCurator/4.0'
}

Image.MAX_IMAGE_PIXELS = None

EXACT_FILES = {
    'renoir_the_loge': 'File:Pierre-Auguste Renoir, La Loge, Courtauld Gallery.jpg',
    'caillebotte_the_floor_scrapers': 'File:Gustave Caillebotte - The Floor Planers - Google Art Project.jpg',
    'monet_the_magpie': 'File:Claude Monet - The Magpie - Google Art Project.jpg',
    'monet_wheatstacks_snow_morning': 'File:Claude Monet (French - Wheatstacks, Snow Effect, Morning - Google Art Project.jpg',
    'monet_water_lilies_reflections_clouds': 'File:Claude Monet - Reflections of Clouds on the Water-Lily Pond.jpg',
    'monet_water_lilies_evening_effect': 'File:Claude Monet - Nymphéas, effet du soir W1504 - Musée Marmottan-Monet.jpg',
    'monet_water_lilies_weeping_willows': 'File:SAULE PLEUREUR ET BASSIN AUX NYMPHÉAS (1916-1919) Claude Monet - Musée Marmottan Monet (W 1848).jpg',
    'monet_la_japonaise': 'File:Claude Monet - Madame Monet en costume japonais (1876).jpg',
    'monet_water_lily_pond_orsay_1900': 'File:Claude Monet - Le Bassin aux nymphéas, harmonie verte (1899).jpg',
    'degas_racehorses_before_stands': 'File:Edgar Degas - Chevaux de course devant les tribunes.jpg',
    'sisley_canal_saint_martin': 'File:Alfred Sisley - Vue du canal Saint-Martin.jpg',
    'pissarro_great_bridge_rouen': 'File:Camille Pissarro - Le Pont Boieldieu à Rouen, temps mouillé.jpg',
    'pissarro_climbing_path_hermitage': 'File:Camille Pissarro - The Climbing Path at the Hermitage, Pontoise - Brooklyn Museum.jpg',
    'pissarro_peasant_woman_washing': 'File:Camille Pissarro - Femme étendant du linge.jpg',
    'monet_winter_sunlight_giverny': 'File:Claude Monet - Winter Sun, Giverny.jpg',
    'monet_breakup_of_ice': 'File:Claude Monet - The Break-Up of the Ice.jpg',
    'monet_antibes_salis': 'File:Claude Monet - Antibes vue de la Salis.jpg',
    'monet_the_water_lily_pond_1904': 'File:Claude Monet - The Water Lily Pond (1904).jpg',
    'monet_water_lilies_morning_willows': 'File:Claude Monet, Nymphéas, matin aux saules.jpg',
    'monet_water_lilies_morning_marmottan': 'File:Claude Monet - Nymphéas (W 1782) - Musée Marmottan Monet.jpg'
}

def get_wikimedia_image(file_title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=3840&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(1.2)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'imageinfo' in pdata:
                    ii = pdata['imageinfo'][0]
                    target_url = ii.get('thumburl') if ('thumburl' in ii and ii['width'] > 3840) else ii['url']
                    return target_url, ii['width'], ii['height']
    except Exception as e:
        print(f"Error fetching {file_title}: {e}")
    return None, 0, 0

print("Testing exact file matching...")
for k, ft in list(EXACT_FILES.items())[:6]:
    u, w, h = get_wikimedia_image(ft)
    print(f"[{k}] {ft} -> {w}x{h} : {u[:60] if u else 'NOT FOUND'}")
