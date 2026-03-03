import requests
import json
import os
import time

API_URL = "https://terraria.wiki.gg/api.php"
WIKI_BASE = "https://terraria.wiki.gg/wiki/"

HEADERS = {
    "User-Agent": "TerrariaGuideBot/1.0 (educational project)"
}


def fetch_recipes_batch(offset=0, limit=500):
    """Fetch a batch of recipes from the Cargo database."""
    params = {
        "action": "cargoquery",
        "tables": "Recipes",
        "fields": "Recipes.result,Recipes.amount,Recipes.station,Recipes.ings",
        "limit": limit,
        "offset": offset,
        "format": "json",
    }
    response = requests.get(API_URL, params=params, headers=HEADERS)
    data = response.json()
    return data.get("cargoquery", [])


def fetch_all_recipes():
    """Fetch all recipes from the Cargo database in batches."""
    all_recipes = []
    offset = 0
    limit = 500

    while True:
        print(f"  Fetching recipes {offset} to {offset + limit}...")
        batch = fetch_recipes_batch(offset, limit)

        if not batch:
            break

        all_recipes.extend(batch)
        print(f"  Got {len(batch)} recipes (total: {len(all_recipes)})")

        if len(batch) < limit:
            break

        offset += limit
        time.sleep(0.3)

    return all_recipes


def parse_ingredients(ings_str):
    """Parse the ings string into a readable list with amounts."""
    if not ings_str:
        return []

    # Format is ¦Item¦Amount^¦Item¦Amount
    # First split on ^ to get individual ingredient pairs
    ingredient_pairs = ings_str.split("^")

    ingredients = []
    for pair in ingredient_pairs:
        # Each pair is ¦Item¦Amount or just ¦Item
        parts = [p.strip() for p in pair.split("\u00a6") if p.strip()]
        if len(parts) == 2:
            item, amount = parts
            ingredients.append(f"{amount}x {item}")
        elif len(parts) == 1:
            ingredients.append(parts[0])

    return ingredients


def build_recipe_text(recipe):
    """Convert a recipe dict into readable training text."""
    fields = recipe.get("title", {})
    result = fields.get("result", "").strip()
    amount = fields.get("amount", "1").strip()
    station = fields.get("station", "").strip()
    ings_raw = fields.get("ings", "").strip()

    if not result:
        return None, None

    ingredients = parse_ingredients(ings_raw)

    if not ingredients:
        return None, None

    amount_str = f"{amount}x " if amount and amount != "1" else ""
    lines = [f"To craft {amount_str}{result} you need:"]
    for ing in ingredients:
        lines.append(f"- {ing}")
    if station:
        lines.append(f"Crafted at: {station}")

    return result, "\n".join(lines)


def generate_crafting_pairs(recipes, output_path):
    """Generate training pairs from recipe data."""
    by_result = {}
    for recipe in recipes:
        result, text = build_recipe_text(recipe)
        if not result or not text:
            continue
        if result not in by_result:
            by_result[result] = []
        by_result[result].append(text)

    pairs = []
    for result, recipe_texts in by_result.items():
        if len(recipe_texts) == 1:
            combined = recipe_texts[0]
        else:
            # Multiple recipes exist — likely version differences
            combined = f"{result} has {len(recipe_texts)} known recipes (may vary by version or platform):\n\n"
            combined += "\n\n".join(recipe_texts)

        wiki_url = WIKI_BASE + result.replace(" ", "_")
        wiki_link = f"\n\nFor more information, see: {wiki_url}"

        pairs.extend([
            {
                "instruction": f"How do I craft {result} in Terraria?",
                "input": "",
                "output": combined + wiki_link
            },
            {
                "instruction": f"What are the ingredients for {result} in Terraria?",
                "input": "",
                "output": combined + wiki_link
            },
            {
                "instruction": f"What do I need to make {result} in Terraria?",
                "input": "",
                "output": combined + wiki_link
            },
        ])

    with open(output_path, 'a', encoding='utf-8') as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')

    print(f"Generated {len(pairs)} crafting pairs from {len(by_result)} unique items.")
    print(f"Appended to {output_path}")
    return pairs


def main():
    print("Fetching all recipes from Terraria wiki Cargo database...")
    recipes = fetch_all_recipes()
    print(f"\nTotal recipes fetched: {len(recipes)}")

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/terraria_recipes_raw.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)
    print("Saved raw recipes to data/raw/terraria_recipes_raw.json")

    print("\nGenerating crafting training pairs...")
    generate_crafting_pairs(
        recipes,
        "data/training/terraria_training_pairs.jsonl"
    )


if __name__ == "__main__":
    main()