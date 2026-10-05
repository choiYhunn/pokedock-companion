from pathlib import Path
import urllib.request, json

OUT=Path("sdcard/pokemon/full")
OUT.mkdir(parents=True,exist_ok=True)
CAT=json.loads(Path("config/pokemon_catalog.json").read_text(encoding="utf-8"))
items=CAT["favorites"]+CAT["extended"]
for p in items:
    url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p['id']}.png"
    dst=OUT/f"{p['id']}_{p['name']}.png"
    print("GET",url)
    urllib.request.urlretrieve(url,dst)
print("Downloaded for private personal prototype use.")