import urllib.request, json 
with urllib.request.urlopen("https://world.openfoodfacts.org/ingredients.json") as url:
    data = json.loads(url.read().decode())
    print(data['name'])