import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'}

def search(q):
    api_url = f'https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=5&prop=imageinfo&iiprop=url|size&format=json'
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    for p in data.get('query', {}).get('pages', {}).values():
        if 'imageinfo' in p:
            info = p['imageinfo'][0]
            print(p['title'], f"{info['width']}x{info['height']}", info['url'])

print("=== 昂蒂布海景 ===")
search("Monet Antibes Seen from the Salis Gardens")

print("\n=== 普林斯顿日本桥 ===")
search("Monet Japanese Footbridge Princeton")
