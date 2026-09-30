import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'}

queries = {
    'vermeer_view_of_delft': 'Johannes Vermeer View of Delft Mauritshuis',
    'bellini_madonna_of_the_meadow': 'Giovanni Bellini Madonna of the Meadow London',
    'monet_antibes_salis': 'Monet Antibes Seen from the Salis Gardens Toledo',
    'monet_breakup_of_ice': 'Monet The Breakup of the Ice Vetheuil',
    'monet_water_lilies_weeping_willows': 'Claude Monet Water Lilies Weeping Willows'
}

for k, q in queries.items():
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=3&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        print(f"\n=== {k} ===")
        for p in data.get('query', {}).get('pages', {}).values():
            if 'imageinfo' in p:
                info = p['imageinfo'][0]
                print(f"  {p['title']} ({info['width']}x{info['height']}) -> {info['url']}")
    except Exception as e:
        print(f"Error {k}: {e}")
