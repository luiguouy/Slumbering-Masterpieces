import urllib.request
import urllib.parse
import json

HEADERS = {'User-Agent': 'ArtWebHarvester/4.0'}

queries = {
    'renoir_the_loge': 'Pierre-Auguste Renoir La Loge',
    'caillebotte_the_floor_scrapers': 'Gustave Caillebotte The Floor Planers',
    'monet_the_magpie': 'Claude Monet The Magpie',
    'monet_the_water_lily_pond_1904': 'Claude Monet The Water Lily Pond 1904',
    'monet_water_lilies_reflections_clouds': 'Claude Monet Reflections of Clouds on the Water-Lily Pond',
    'monet_breakup_of_ice': 'Claude Monet The Breakup of the Ice',
    'monet_wheatstacks_snow_morning': 'Claude Monet Wheatstacks, Snow Effect, Morning',
    'monet_antibes_salis': 'Claude Monet Antibes Seen from the Salis Gardens',
    'monet_water_lilies_evening_effect': 'Claude Monet Nymphéas effet du soir',
    'monet_water_lilies_weeping_willows': 'Claude Monet Nymphéas et saule pleureur',
    'monet_water_lilies_morning_willows': 'Claude Monet Water Lilies Morning with Willows',
    'monet_water_lilies_morning_marmottan': 'Claude Monet Nymphéas matin Marmottan',
    'sisley_canal_saint_martin': 'Alfred Sisley Vue du canal Saint-Martin',
    'pissarro_great_bridge_rouen': 'Camille Pissarro Le Pont Boieldieu à Rouen',
    'pissarro_climbing_path_hermitage': 'Camille Pissarro The Climbing Path at the Hermitage',
    'pissarro_peasant_woman_washing': 'Camille Pissarro Femme étendant du linge',
    'degas_racehorses_before_stands': 'Edgar Degas Chevaux de course devant les tribunes',
    'monet_winter_sunlight_giverny': 'Claude Monet Winter Sun Giverny',
    'monet_la_japonaise': 'Claude Monet La Japonaise Madame Monet en costume japonais',
    'monet_water_lily_pond_orsay_1900': 'Claude Monet Le Bassin aux nymphéas, harmonie verte'
}

for k, q in queries.items():
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=3"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = [x['title'] for x in data.get('query', {}).get('search', [])]
            print(f"[{k}] -> {results}")
    except Exception as e:
        print(f"[{k}] -> Error: {e}")
