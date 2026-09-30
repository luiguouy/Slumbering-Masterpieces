import urllib.request
import urllib.parse
import json

import time

HEADERS = {
    'User-Agent': 'ArtWebCuratorBot/2.1 (https://artweb.local; contact: curator@artweb.local) Python-urllib/3.12'
}

def safe_request(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 3
                print(f"Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"HTTP error {e.code}: {e}")
                time.sleep(2)
        except Exception as e:
            print(f"Network error: {e}")
            time.sleep(2)
    return None

def search(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=6"
    data = safe_request(url)
    time.sleep(1.2)
    if data and 'query' in data and 'search' in data['query']:
        return [r['title'] for r in data['query']['search']]
    return []

def info(title):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size|mime&format=json"
    data = safe_request(url)
    time.sleep(1.2)
    if data and 'query' in data and 'pages' in data['query']:
        for pid in data['query']['pages']:
            if 'imageinfo' in data['query']['pages'][pid]:
                return data['query']['pages'][pid]['imageinfo'][0]
    return None

queries = {
    'Odalisque': 'Jean Auguste Dominique Ingres Grande Odalisque Louvre',
    'Astronomer': 'Johannes Vermeer The Astronomer Louvre'
}

for k, q in queries.items():
    print(f"\n--- {k} ---")
    titles = search(q)
    for t in titles[:3]:
        inf = info(t)
        if inf:
            print(f"  {t} ({inf['width']}x{inf['height']}, {inf['size']//1024}KB)")
