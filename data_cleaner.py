import json
import re
import os

SKIP_HEADINGS = {
    "references",
    "see also",
    "external links",
    "gallery",
    "set",
}

SKIP_PAGE_PATTERNS = [
    r"^#REDIRECT",
    r"^List of ",
    r"/id$",
    r"/cs$",
    r"/da$",
    r"/es$",
    r"/fi$",
    r"/it$",
    r"/ja$",
    r"/lt$",
    r"/nl$",
    r"/no$",
    r"/tr$",
    r"/vi$",
    r"/yue$",
]


def should_skip_page(title, first_content):
    if first_content.strip().startswith("#REDIRECT"):
        return True
    for pattern in SKIP_PAGE_PATTERNS:
        if re.search(pattern, title):
            return True
    return False


def clean_history(text):
    def replace_history(match):
        content = match.group(1)
        parts = content.split("|", 1)
        if len(parts) == 2:
            version = parts[0].strip()
            desc = parts[1].strip()
            desc = re.sub(r'\{\{[^{}]*\}\}', '', desc)
            desc = re.sub(r'Old sprite was\s*\.?', '', desc)
            desc = re.sub(r'[Oo]ld sprite[^.]*\.', '', desc)
            desc = desc.strip("*").strip()
            if desc:
                return f"- {version}: {desc}"
        return ""

    text = re.sub(r'\{\{history\|([^{}]*(?:\{\{[^{}]*\}\}[^{}]*)*)\}\}',
                  replace_history, text, flags=re.DOTALL)
    return text


def replace_coin(m):
    inner = m.group(1).strip()
    if inner.isdigit():
        val = int(inner)
        gold = val // 10000
        silver = (val % 10000) // 100
        copper = val % 100
        parts = []
        if gold: parts.append(f"{gold} gold")
        if silver: parts.append(f"{silver} silver")
        if copper: parts.append(f"{copper} copper")
        return ' '.join(parts) if parts else inner
    result = inner
    result = re.sub(r'(\d+)gc', r'\1 gold', result)
    result = re.sub(r'(\d+)sc', r'\1 silver', result)
    result = re.sub(r'(\d+)cc', r'\1 copper', result)
    return result.strip()


def clean_text(text):
    if text.strip().startswith("#REDIRECT"):
        return ""

    # Extract version exclusivity — only keep real version numbers
    exclusive_match = re.search(r'\{\{exclusive\|([^}]+)\}\}', text)
    exclusive_note = ""
    if exclusive_match:
        val = exclusive_match.group(1).strip()
        if re.match(r'^[\d.]+$', val):
            exclusive_note = f"[Available from version {val}] "

    # ----------------------------------------------------------------
    # EXTRACT useful content from templates BEFORE stripping them
    # ----------------------------------------------------------------

    # {{wikipedia|Display Text|Link}} or {{wikipedia|Term}} → extract text
    text = re.sub(r'\{\{wikipedia\|[^|{}]*\|([^|{}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{wikipedia\|([^|{}]+)\}\}', r'\1', text)

    # {{iwlink|game|file|Display Text}} → extract display text
    text = re.sub(r'\{\{iwlink\|[^|{}]*\|[^|{}]*\|([^|{}]+)\}\}', r'\1', text)

    # {{item|Name|...}} → extract item name
    text = re.sub(r'\{\{item\|([^|{}]+?)(?:\|[^{}]*)?\}\}', r'\1', text)

    # {{npc|Name|...}} → extract NPC name
    text = re.sub(r'\{\{npc\|([^|{}]+?)(?:\|[^{}]*)?\}\}', r'\1', text)

    # {{eil|Name|...}} → extract name
    text = re.sub(r'\{\{eil\|([^|{}]+?)(?:\|[^{}]*)?\}\}', r'\1', text)

    # {{nslink|page|display}} → extract display text
    text = re.sub(r'\{\{nslink\|[^|{}]+\|([^|{}]+)\}\}', r'\1', text)

    # {{chance|1/150}} → extract fraction
    text = re.sub(r'\{\{chance\|([^|{}]+?)(?:\|[^{}]*)?\}\}', r'\1', text)

    # {{duration|30 ticks}} → "30 ticks"
    # {{duration|rawseconds=2-6}} → "2-6 seconds"
    def replace_duration(m):
        inner = m.group(1).strip()
        if inner.startswith("rawseconds="):
            val = inner.replace("rawseconds=", "").strip()
            return f"{val} seconds"
        if any(c in inner for c in ['*', '/', '+', '(', ')']):
            return ""
        return inner
    text = re.sub(r'\{\{duration\|([^{}]+)\}\}', replace_duration, text)

    # {{coin|4gc 50sc}} → "4 gold 50 silver"
    text = re.sub(r'\{\{coin\|([^{}]+)\}\}', replace_coin, text)

    # {{sc|20}} → "20 silver", {{gc|...}} → gold, {{cc|...}} → copper
    text = re.sub(r'\{\{sc\|(\d+)\}\}', r'\1 silver', text)
    text = re.sub(r'\{\{gc\|(\d+)\}\}', r'\1 gold', text)
    text = re.sub(r'\{\{cc\|(\d+)\}\}', r'\1 copper', text)

    # {{mph|N pixels}} → strip
    text = re.sub(r'\{\{mph\|[^{}]+\}\}', '', text)

    # Clean history sections
    text = clean_history(text)

    # ----------------------------------------------------------------
    # STRIP templates that have no useful text content
    # ----------------------------------------------------------------

    # Strip complex price expression templates
    text = re.sub(r'\{\{sell expr\|[^{}]+\}\}', '', text)
    text = re.sub(r'\{\{buy expr\|[^{}]+\}\}', '', text)

    # Strip source code refs
    text = re.sub(r'\{\{source code ref\|.*?\}\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\{\{[^{}]*\n[^{}]*\}\}', '', text)

    # Strip footnote templates
    text = re.sub(r'\{\{footnote\|[^{}]*\}\}', '', text)

    # Strip gameText templates (unresolvable)
    text = re.sub(r'\{\{gameText\|[^{}]*\}\}', '', text)

    # Strip wall/tile ID templates
    text = re.sub(r'\{\{wall\|[^{}]*\}\}', '', text)

    # Strip icon templates
    text = re.sub(r'\{\{icon[^{}]*\}\}', '', text)

    # Strip table include templates
    text = re.sub(r'\{\{:[^{}]*\}\}', '', text)

    # Strip remaining templates iteratively
    for _ in range(8):
        text = re.sub(r'\{\{[^{}]*\}\}', '', text)

    # Strip remaining nested templates
    for _ in range(3):
        text = re.sub(r'\{\{.*?\}\}', '', text, flags=re.DOTALL)

    # ----------------------------------------------------------------
    # Standard cleanup
    # ----------------------------------------------------------------

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)

    # Remove file/image links
    text = re.sub(r'\[\[File:.*?\]\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[Image:.*?\]\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[Media:.*?\]\]', '', text, flags=re.DOTALL)

    text = re.sub(r'\[\[File:.*?\]\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[Image:.*?\]\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\[\[Media:.*?\]\]', '', text, flags=re.DOTALL)

    # Convert [[link|display]] to display text
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)

    # Convert [[link]] to link text
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)

    # Remove external links
    text = re.sub(r'\[https?://[^\s\]]+\s([^\]]+)\]', r'\1', text)
    text = re.sub(r'\[https?://[^\]]+\]', '', text)

    # Remove table markup
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    text = re.sub(r'^\s*[|!].*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\|-', '', text)

    # Remove wiki formatting
    text = re.sub(r"'{2,3}", '', text)
    text = re.sub(r'={2,6}[^=]+=+', '', text)

    # Remove category links
    text = re.sub(r'\[\[Category:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[[a-z\-]+:[^\]]*\]\]', '', text)

    # Remove image filename patterns
    text = re.sub(r'\S+\.(png|gif|jpg|wav)\S*', '', text)
    text = re.sub(r'\S*\.png\|link=\]\]', '', text)
    text = re.sub(r'\S*\.png\|[^\]]*\]\]', '', text)

    # Remove __NOTOC__ and similar magic words
    text = re.sub(r'__[A-Z]+__', '', text)

    # Clean up bullet asterisks
    text = re.sub(r'^\s*\*+\s*', '- ', text, flags=re.MULTILINE)

    # Remove lines that are clearly just leftover markup artifacts
    text = re.sub(r'^\s*\[\]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.\]\]\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.\s*$', '', text, flags=re.MULTILINE)

    # Remove spurious version tags
    text = re.sub(r'\s*\(applies to:[^)]+\)', '', text)

    # Remove empty parentheses
    text = re.sub(r'\(\s*\)', '', text)

    # Add exclusive note back if found
    if exclusive_note:
        text = exclusive_note + text.lstrip('\n')

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()

    return text


def clean_data(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    cleaned_data = []
    skipped_redirects = 0
    skipped_empty = 0

    for page in raw_data:
        title = page["title"]
        url = page["url"]
        sections = page["sections"]

        first_content = sections[0]["content"] if sections else ""
        if should_skip_page(title, first_content):
            skipped_redirects += 1
            continue

        cleaned_page = {
            "title": title,
            "url": url,
            "sections": []
        }

        for section in sections:
            heading = section["heading"]
            content = section["content"]
            versions = section["versions"]

            if heading.lower() in SKIP_HEADINGS:
                continue

            cleaned_content = clean_text(content)

            if len(cleaned_content) < 20:
                continue

            cleaned_page["sections"].append({
                "heading": heading,
                "content": cleaned_content,
                "versions": versions
            })

        total_content = " ".join(s["content"] for s in cleaned_page["sections"])
        if len(total_content) < 50:
            skipped_empty += 1
            continue

        if cleaned_page["sections"]:
            cleaned_data.append(cleaned_page)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Total pages in:      {len(raw_data)}")
    print(f"Skipped (redirects): {skipped_redirects}")
    print(f"Skipped (empty):     {skipped_empty}")
    print(f"Pages out:           {len(cleaned_data)}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    clean_data(
        "data/raw/terraria_wiki_raw.json",
        "data/cleaned/terraria_wiki_cleaned.json"
    )