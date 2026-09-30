import urllib.request
import urllib.parse
import json

HEADERS = {'User-Agent': 'ArtWebCuratorBot/2.1 (contact: curator@artweb.local) Python-urllib/3.12'}
def search(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&srnamespace=6&format=json&srlimit=5"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return [r['title'] for r in json.loads(resp.read().decode())['query']['search']]

print("Giverny Garden Orsay:", search("Le jardin de Claude Monet a Giverny"))
print("Monet Gladioli DIA:", search("Gladioli Monet Detroit"))
print("Monet Water Lilies Chicago:", search("Water Lilies Monet Art Institute of Chicago"))
