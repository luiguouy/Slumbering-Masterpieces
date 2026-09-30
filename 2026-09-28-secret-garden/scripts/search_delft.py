import urllib.request
import urllib.parse
import json
import os
from PIL import Image

headers = {
    'User-Agent': 'FineArtRestorerBot/1.0 (contact@artweb.org)'
}

def search_wikimedia(query):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=5&prop=imageinfo&iiprop=url|size|extmetadata&format=json"
    req = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    pages = data.get('query', {}).get('pages', {})
    results = []
    for pid, p in pages.items():
        if 'imageinfo' in p and p['imageinfo']:
            info = p['imageinfo'][0]
            title = p.get('title', '')
            results.append({
                'title': title,
                'url': info.get('url'),
                'width': info.get('width', 0),
                'height': info.get('height', 0),
                'size': info.get('size', 0)
            })
    return results

print("=== 搜索维米尔代尔夫特风景 ===")
res = search_wikimedia("Johannes Vermeer View of Delft Google Art Project")
for r in res:
    print(r['title'], r['width'], r['height'], r['url'])
