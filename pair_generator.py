import json
import os
import random

BOSS_SPAWN_MESSAGES = {
    "Eye of Cthulhu": "You feel an evil presence watching you...",
    "The Destroyer": "You feel vibrations from deep below...",
    "The Twins": "This is going to be a terrible night...",
    "Skeletron Prime": "The air is getting colder around you...",
    "Skeletron": "The air is getting colder around you...",
    "Eater of Worlds": "You feel vibrations from deep below...",
    "Brain of Cthulhu": "Screams echo around you...",
    "Queen Bee": "The jungle grows restless...",
    "Wall of Flesh": "Impending doom approaches...",
    "Queen Slime": "The sound of Queen Slime's laughter echoes around you...",
    "Plantera": "The jungle grows restless...",
    "Duke Fishron": "The water is churning...",
    "Empress of Light": "The Empress of Light has awoken!",
    "Moon Lord": "Impending doom approaches...",
    "Mechdusa": "What a horrible night to have a curse.",
}

SKIP_HEADINGS = {
    "interaction quotes",
    "happiness quotes",
    "advice",
    "names",
    "living preferences",
    "shimmered form",
    "achievements",
    "references",
    "see also",
    "external links",
    "gallery",
    "set",
}


def generate_training_pairs(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        cleaned_data = json.load(f)

    training_pairs = []

    for page in cleaned_data:
        title = page["title"]
        url = page["url"]
        wiki_link = f"\n\nFor more information, see: {url}"

        for section in page["sections"]:
            content = section["content"]
            heading = section["heading"]
            versions = section["versions"]

            # Skip unhelpful headings
            if heading.lower() in SKIP_HEADINGS:
                continue

            h = heading.lower()

            # Build version context string
            if "all_versions" in versions:
                version_note = ""
            else:
                version_map = {
                    "desktop": "PC/Desktop",
                    "mobile": "Mobile",
                    "console": "Console",
                    "legacy_3ds": "3DS (legacy)",
                }
                version_names = [version_map.get(v, v) for v in versions]
                version_note = f" (applies to: {', '.join(version_names)})"

            # Don't add version notes to history sections
            if h == "history":
                version_note = ""

            # Skip very short content
            if len(content) < 30:
                continue

            # INTRODUCTION
            if h == "introduction":
                pairs = [
                    {
                        "instruction": f"What is {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Tell me about {title} in Terraria.",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Give me an overview of {title} in Terraria.",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # HISTORY
            elif h == "history":
                pairs = [
                    {
                        "instruction": f"What changes have been made to {title} across Terraria updates?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What version was {title} introduced in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Has {title} changed in recent Terraria updates?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # TIPS
            elif h == "tips":
                pairs = [
                    {
                        "instruction": f"What are some tips for using {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"How do I use {title} effectively in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Any advice for {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # NOTES
            elif h == "notes":
                pairs = [
                    {
                        "instruction": f"What should I know about {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Are there any important notes about {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # TRIVIA
            elif h == "trivia":
                pairs = [
                    {
                        "instruction": f"What are some interesting facts about {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Tell me something interesting about {title} in Terraria.",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # DROPS / LOOT
            elif h in ["drops", "loot"]:
                pairs = [
                    {
                        "instruction": f"What does {title} drop in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What loot can I get from {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What items does {title} drop in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # BEHAVIOR
            elif h == "behavior":
                pairs = [
                    {
                        "instruction": f"How does {title} behave in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What are {title}'s attack patterns in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # SUMMONING / SUMMONING AND SPAWNING
            elif h in ["summoning", "summoning and spawning"]:
                pairs = [
                    {
                        "instruction": f"How do I summon {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What do I need to spawn {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"Where and how does {title} spawn in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # AFTERMATH
            elif h == "aftermath":
                pairs = [
                    {
                        "instruction": f"What happens after defeating {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What does defeating {title} unlock in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # FIRST PHASE / SECOND PHASE
            elif h in ["first phase", "second phase"]:
                pairs = [
                    {
                        "instruction": f"What happens during {title}'s {heading} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"How do I deal with {title}'s {heading} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # EXPERT MODE
            elif h == "expert mode":
                pairs = [
                    {
                        "instruction": f"How does {title} differ in Expert Mode in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What changes about {title} in Expert Mode?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # HARDMODE
            elif h == "hardmode":
                pairs = [
                    {
                        "instruction": f"How does {title} change in Hardmode in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What is the Hardmode version of {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # TYPES
            elif h == "types":
                pairs = [
                    {
                        "instruction": f"What are the different types of {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"How many variants of {title} are there in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # RECIPES / CRAFTING / USED TO CRAFT / USED IN
            elif h in ["recipes", "crafting", "used to craft", "used in"]:
                pairs = [
                    {
                        "instruction": f"How do I craft {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What are the crafting ingredients for {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What can I craft with {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # SHIMMER TRANSMUTATION
            elif h == "shimmer transmutation":
                pairs = [
                    {
                        "instruction": f"Can I shimmer {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What does {title} turn into when shimmered in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # SPREAD / CONVERSIONS
            elif h in ["spread", "conversions"]:
                pairs = [
                    {
                        "instruction": f"How does {title} spread in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What blocks does {title} convert in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # ENEMIES
            elif h == "enemies":
                pairs = [
                    {
                        "instruction": f"What enemies are found in {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What monsters spawn in {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # COMPLETING
            elif h == "completing":
                pairs = [
                    {
                        "instruction": f"How do I complete {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                    {
                        "instruction": f"What are the steps to complete {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # SEGMENTS
            elif h == "segments":
                pairs = [
                    {
                        "instruction": f"What segments make up {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # BOOST GEAR
            elif h == "boost gear":
                pairs = [
                    {
                        "instruction": f"What gear should I use to boost {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # CONSUMABLES
            elif h == "consumables":
                pairs = [
                    {
                        "instruction": f"What consumables are related to {title} in Terraria?",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            # DEFAULT
            else:
                pairs = [
                    {
                        "instruction": f"Tell me about the {heading} of {title} in Terraria.",
                        "input": "",
                        "output": content + version_note + wiki_link
                    },
                ]

            training_pairs.extend(pairs)

        # Add boss spawn message pairs after processing all sections
        if title in BOSS_SPAWN_MESSAGES and BOSS_SPAWN_MESSAGES[title]:
            msg = BOSS_SPAWN_MESSAGES[title]
            training_pairs.extend([
                {
                    "instruction": f"What does the message '{msg}' mean in Terraria?",
                    "input": "",
                    "output": f"The message \"{msg}\" is the spawn announcement for {title}. This means {title} has spawned or will spawn very soon. Prepare yourself!" + wiki_link
                },
                {
                    "instruction": f"What spawns when I see '{msg}' in Terraria?",
                    "input": "",
                    "output": f"\"{msg}\" is the status message that appears when {title} spawns. Get ready to fight!" + wiki_link
                },
            ])

    # Shuffle for better training
    random.shuffle(training_pairs)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for pair in training_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')

    print(f"Generated {len(training_pairs)} training pairs.")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    generate_training_pairs(
        "data/cleaned/terraria_wiki_cleaned.json",
        "data/training/terraria_training_pairs.jsonl"
    )