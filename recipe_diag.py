import json

with open("data/raw/terraria_recipes_raw.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

# Find the Crimtane Candelabra recipe specifically
for r in recipes:
    if "Candelabra" in r["title"].get("result", ""):
        print(json.dumps(r, indent=2))