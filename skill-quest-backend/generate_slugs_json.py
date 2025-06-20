import csv
import json
import os

def title_to_slug(title):
    return title.strip().lower().replace(" ", "-").replace("'", "").replace(",", "").replace(".", "")

difficulties = ["easy", "medium", "hard"]
slugs_by_difficulty = {}

for level in difficulties:
    filename = f"leetcode_{level}_questions.csv"  # Update if your filenames differ
    slugs = []

    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        continue

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row.get("title") or row.get("Title")
            if title:
                slug = title_to_slug(title)
                slugs.append(slug)

    slugs_by_difficulty[level] = slugs

with open("slugs_by_difficulty.json", "w", encoding="utf-8") as f:
    json.dump(slugs_by_difficulty, f, indent=2)

print("✅ Generated slugs_by_difficulty.json")
