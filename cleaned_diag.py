import json
from collections import Counter

with open("data/cleaned/terraria_wiki_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

total_sections = 0
for page in data:
    total_sections += len(page["sections"])

print(f"Total pages: {len(data)}")
print(f"Total sections: {total_sections}")
print(f"Average sections per page: {total_sections / len(data):.1f}")

headings = Counter()
for page in data:
    for section in page["sections"]:
        headings[section["heading"].lower()] += 1

print("\nTop 30 section headings:")
for heading, count in headings.most_common(30):
    print(f"  {heading}: {count}")