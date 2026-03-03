# import json
#
# with open("data/training/terraria_training_pairs.jsonl", "r", encoding="utf-8") as f:
#     pairs = [json.loads(line) for line in f if line.strip()]
#
# # Check if any crafting pairs have amounts
# crafting_pairs = [p for p in pairs if "How do I craft" in p["instruction"]]
# print(f"Total pairs: {len(pairs)}")
# print(f"Crafting pairs: {len(crafting_pairs)}")
# print("\nSample crafting pair:")
# if crafting_pairs:
#     print(json.dumps(crafting_pairs[0], indent=2))


# import json
#
# with open("data/training/terraria_training_pairs.jsonl", "r", encoding="utf-8") as f:
#     pairs = [json.loads(line) for line in f if line.strip()]
#
# for p in pairs:
#     if "Crimtane Candelabra" in p["instruction"]:
#         print(json.dumps(p, indent=2))
#         break

#
# import json
# import re
#
# with open("data/raw/terraria_wiki_raw.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# # Find Eye of Cthulhu page
# for page in data:
#     if page["title"] == "Eye of Cthulhu":
#         for section in page["sections"]:
#             print(f"\n=== {section['heading']} ===")
#             print(section["content"][:800])

# import json
# import re
#
# with open("data/raw/terraria_wiki_raw.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# # Find pages with sell templates, chance templates, duration templates
# targets = ["sell", "chance", "duration", "defense", "wikipedia"]
# found = 0
#
# for page in data:
#     for section in page["sections"]:
#         content = section["content"]
#         for target in targets:
#             if f"{{{{{target}|" in content.lower() and found < 10:
#                 print(f"\n=== {page['title']} - {section['heading']} ===")
#                 # Show just the lines containing the template
#                 for line in content.split('\n'):
#                     if target in line.lower():
#                         print(line[:200])
#                 found += 1

# import json
#
# with open("data/raw/terraria_wiki_raw.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# targets = ["sell|", "wikipedia|", "pink dye", "koala", "shark"]
# found = 0
#
# for page in data:
#     for section in page["sections"]:
#         content = section["content"]
#         for target in targets:
#             if target in content.lower() and found < 10:
#                 print(f"\n=== {page['title']} - {section['heading']} ===")
#                 for line in content.split('\n'):
#                     if target in line.lower():
#                         print(line[:200])
#                 found += 1

import json, re

with open("data/raw/terraria_wiki_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Search for pages where sell price appears in non-infobox content
found = 0
for page in data:
    for section in page["sections"]:
        content = section["content"]
        # Look for coin/price related patterns
        if re.search(r'\{\{(coin|price|sell|buy|value)', content, re.IGNORECASE) and found < 8:
            print(f"\n=== {page['title']} - {section['heading']} ===")
            for line in content.split('\n'):
                if re.search(r'\{\{(coin|price|sell|buy|value)', line, re.IGNORECASE):
                    print(line[:200])
            found += 1