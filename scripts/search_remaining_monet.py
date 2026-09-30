import urllib.request
import urllib.parse
import json
import time

HEADERS = {
    'User-Agent': 'ArtWebCuratorBot/2.1 (https://artweb.local; contact: curator@artweb.local) Python-urllib/3.12'
}

def search(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=5"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return [r['title'] for r in json.loads(resp.read().decode())['query']['search']]

def info(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    for pid in data['query']['pages']:
        if 'imageinfo' in data['query']['pages'][pid]:
            return data['query']['pages'][pid]['imageinfo'][0]
    return None

queries = {
    'monet_argenteuil': 'Claude Monet The Artists Garden at Argenteuil NGA',
    'monet_gladioli': 'Claude Monet Gladioli Detroit',
    'monet_giverny': 'Claude Monet The Garden Path at Giverny Orsay',
    'monet_sainte_adresse': 'Claude Monet Garden at Sainte-Adresse Met',
    'monet_basin': 'Claude Monet The Basin at Argenteuil Orsay',
    'bruegel_babel': 'Pieter Bruegel the Elder The Tower of Babel Vienna'
}

for k, q in queries.items():
    print(f"\n--- {k} ---")
    titles = search(q)
    for t in titles[:3]:
        inf = info(t)
        if inf:
            print(f"  {t} ({inf['width']}x{inf['height']}, {inf['size']//1024}KB)")
    time.sleep(1.2)
