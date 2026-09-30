import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0 FineArtCurator/1.0'}

# Test Met API for El Greco or Rubens or Bouguereau
url = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=Annunciation&hasImages=true"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        print("Met total IDs found:", data.get('total'))
        if data.get('objectIDs'):
            obj_id = data['objectIDs'][0]
            obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
            with urllib.request.urlopen(urllib.request.Request(obj_url, headers=headers), timeout=10) as obj_r:
                obj_data = json.loads(obj_r.read().decode())
                print("Met object 1:", obj_data.get('title'), obj_data.get('artistDisplayName'), obj_data.get('primaryImage')[:60] if obj_data.get('primaryImage') else "no image")
except Exception as e:
    print("Met error:", e)

# Test AIC API
aic_url = "https://api.artic.edu/api/v1/artworks/search?q=Madonna&query[term][is_public_domain]=true&fields=id,title,artist_title,image_id,artwork_type_title&limit=3"
req = urllib.request.Request(aic_url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        print("AIC total:", data['pagination']['total'])
        for it in data['data']:
            print("AIC artwork:", it['title'], "-", it.get('artist_title'), "image_id:", it.get('image_id'))
except Exception as e:
    print("AIC error:", e)
