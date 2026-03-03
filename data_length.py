import json

with open("data/raw/terraria_wiki_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total pages scraped: {len(data)}")