import requests
import json
import os
import time

API_URL = "https://terraria.wiki.gg/api.php"
WIKI_BASE = "https://terraria.wiki.gg/wiki/"

HEADERS = {
    "User-Agent": "TerrariaGuideBot/1.0 (educational project)"
}

CATEGORIES = [
    # Enemies & Bosses
    "Boss NPCs",
    "Forest NPCs",
    "Underground NPCs",
    "Cavern NPCs",
    "Desert NPCs",
    "Ocean NPCs",
    "Snow NPCs",
    "Jungle NPCs",
    "Dungeon NPCs",
    "Corruption NPCs",
    "Crimson NPCs",
    "Hallow NPCs",
    "Underworld NPCs",
    "Space NPCs",
    "Mushroom NPCs",
    "Event NPCs",

    # Weapons
    "Melee weapons",
    "Ranged weapons",
    "Magic weapons",
    "Summon weapons",
    "Yoyos",
    "Flails",
    "Bows",
    "Guns",
    "Launchers",

    # Armor
    "Armor items",
    "Armor sets",

    # Items
    "Accessory items",
    "Tool items",
    "Potion items",
    "Ore items",
    "Bar items",
    "Crafting station items",
    "Mount summon items",
    "Ammunition items",
    "Consumable items",

    # Status effects
    "Buffs",
    "Debuffs",

    # Events
    "Events",
]

HARDCODED_PAGES = [
    "Bosses",
    "NPCs",
    "Tools",
    "Weapons",
    "Armor",
    "Accessories",
    "Wings",
    "Mounts",
    "Hooks",
    "Biomes",
    "Events",
    "Fishing",
    "Crafting",
    "Hardmode",
    "King Slime",
    "Eye of Cthulhu",
    "Eater of Worlds",
    "Brain of Cthulhu",
    "Queen Bee",
    "Skeletron",
    "Wall of Flesh",
    "Queen Slime",
    "The Twins",
    "The Destroyer",
    "Skeletron Prime",
    "Plantera",
    "Golem",
    "Duke Fishron",
    "Empress of Light",
    "Lunatic Cultist",
    "Moon Lord",
    "Forest",
    "Underground layer",
    "Cavern layer",
    "The Underworld",
    "Ocean",
    "Desert",
    "Snow biome",
    "Jungle",
    "Dungeon",
    "The Corruption",
    "The Crimson",
    "The Hallow",
    "Space",
    "Mushroom biome",
    "Goblin Army",
    "Blood Moon",
    "Frost Legion",
    "Pirate Invasion",
    "Martian Madness",
    "Pumpkin Moon",
    "Frost Moon",
    "Solar Eclipse",
    "Lunar Events",
]

VERSION_KEYWORDS = {
    "desktop": ["desktop", "pc", "1.4", "1.3", "journey's end", "labor of love"],
    "mobile": ["mobile", "ios", "android"],
    "console": ["console", "xbox", "playstation", "switch"],
    "legacy_3ds": ["3ds", "old-gen", "legacy"],
}


def get_category_members(category, limit=500):
    """Get all page titles in a category."""
    pages = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": limit,
        "cmtype": "page",
        "format": "json",
    }

    while True:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        data = response.json()

        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            if m["ns"] == 0:
                pages.append(m["title"])

        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break

        time.sleep(0.2)

    return pages


def get_page_content(title):
    """Fetch raw wikitext for a page."""
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext|sections",
        "format": "json",
    }

    response = requests.get(API_URL, params=params, headers=HEADERS)
    data = response.json()

    if "error" in data:
        return None, None

    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
    sections = data.get("parse", {}).get("sections", [])

    return wikitext, sections


def detect_versions(text):
    """Detect which game versions content applies to."""
    text_lower = text.lower()
    found = []
    for version, keywords in VERSION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(version)
                break
    return found if found else ["all_versions"]


def split_into_sections(wikitext, page_title):
    """Split wikitext into sections by heading."""
    import re
    sections = []

    pattern = r'(={2,4})\s*([^=]+?)\s*\1'
    parts = re.split(pattern, wikitext)

    if parts[0].strip():
        sections.append({
            "heading": "Introduction",
            "content": parts[0].strip(),
            "versions": detect_versions(parts[0])
        })

    i = 1
    while i < len(parts) - 2:
        heading = parts[i + 1].strip()
        content = parts[i + 2].strip() if i + 2 < len(parts) else ""
        if heading and content:
            sections.append({
                "heading": heading,
                "content": content,
                "versions": detect_versions(content)
            })
        i += 3

    return sections


def scrape_all():
    os.makedirs("data/raw", exist_ok=True)
    output_path = "data/raw/terraria_wiki_raw.json"

    # Load existing data to avoid re-scraping
    existing = {}
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for page in json.load(f):
                existing[page["title"]] = page
        print(f"Loaded {len(existing)} existing pages")

    # Collect all unique page titles from categories
    all_titles = set()
    print("Collecting page titles from categories...")
    for category in CATEGORIES:
        print(f"  Category: {category}")
        members = get_category_members(category)
        all_titles.update(members)
        print(f"    -> {len(members)} pages")
        time.sleep(0.3)

    # Add hardcoded pages after the loop
    print("\nAdding hardcoded pages...")
    all_titles.update(HARDCODED_PAGES)

    # Filter out already scraped
    new_titles = [t for t in all_titles if t not in existing]
    print(f"\nTotal unique pages: {len(all_titles)}")
    print(f"Already scraped: {len(existing)}")
    print(f"New pages to scrape: {len(new_titles)}\n")

    all_data = list(existing.values())

    for i, title in enumerate(new_titles):
        print(f"Scraping ({i+1}/{len(new_titles)}): {title}")
        wikitext, _ = get_page_content(title)

        if not wikitext:
            print(f"  -> Failed or not found")
            continue

        sections = split_into_sections(wikitext, title)

        page_data = {
            "title": title,
            "url": WIKI_BASE + title.replace(" ", "_"),
            "sections": sections
        }

        all_data.append(page_data)
        print(f"  -> Got {len(sections)} sections")

        # Save incrementally every 50 pages
        if (i + 1) % 50 == 0:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            print(f"  [Saved checkpoint: {len(all_data)} pages]")

        time.sleep(0.3)

    # Final save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Scraped {len(all_data)} total pages.")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    scrape_all()