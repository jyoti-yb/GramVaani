import os
import json
import re

INPUT_DIR = "rag/knowledge_base"
OUTPUT_FILE = "rag/knowledge_base/chunks.json"

SECTION_HEADERS = [
    "General Information",
    "Climate",
    "Soil",
    "Popular Varieties",
    "Land Preparation",
    "Sowing",
    "Seed",
    "Fertilizer",
    "Weed Control",
    "Irrigation",
    "Plant protection",
    "Harvesting",
    "Post-Harvest",
]


def split_into_sections(text):
    sections = {}
    current_section = "General"

    for line in text.split("\n"):
        line = line.strip()

        if line in SECTION_HEADERS:
            current_section = line
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(line)

    return sections


def build_chunks():
    all_chunks = []

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".txt"):
            continue

        crop_name = filename.replace(".txt", "").replace("_", " ")

        with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
            text = f.read()

        sections = split_into_sections(text)

        for section, content_lines in sections.items():
            content = "\n".join(content_lines).strip()

            if len(content) < 50:
                continue

            chunk = {
                "crop": crop_name,
                "section": section,
                "content": content
            }

            all_chunks.append(chunk)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Created {len(all_chunks)} chunks.")


if __name__ == "__main__":
    build_chunks()