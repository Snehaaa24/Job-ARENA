import sys
import requests
import json
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    print(json.dumps({ "error": "Slug not provided" }))
    sys.exit(1)

slug = sys.argv[1]

url = "https://leetcode.com/graphql"
headers = {
    "Content-Type": "application/json",
    "Referer": f"https://leetcode.com/problems/{slug}/",
    "User-Agent": "Mozilla/5.0",
}

query = """
query getQuestionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    difficulty
    content
    exampleTestcases
  }
}
"""

variables = {
    "titleSlug": slug
}

try:
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()

    q = data["data"]["question"]
    title = q["title"]
    difficulty = q["difficulty"]
    description = q["content"]
    example_raw = q["exampleTestcases"] or ""

    # Parse the HTML description
    soup = BeautifulSoup(description, "html.parser")

    # Extract constraints from <ul><li>...</li></ul>
    constraint_list = soup.find("ul")
    constraints = []
    if constraint_list:
        for li in constraint_list.find_all("li"):
            constraints.append(li.get_text().strip())
    if not constraints:
        constraints = ["Default constraint 1", "Default constraint 2"]

    # Parse examples from <pre> blocks
    example_blocks = soup.find_all("pre")
    examples = []
    for block in example_blocks:
        raw_text = block.get_text()
        parts = raw_text.split("Output:")
        if len(parts) == 2:
            input_part = parts[0].replace("Input:", "").strip()
            output_part = parts[1].split("Explanation:")[0].strip() if "Explanation:" in parts[1] else parts[1].strip()
            explanation = parts[1].split("Explanation:")[1].strip() if "Explanation:" in parts[1] else ""
            examples.append({
                "input": input_part,
                "output": output_part,
                "explanation": explanation or "Explanation not found"
            })
    if not examples:
        examples = [{
            "input": example_raw,
            "output": "Expected output here",
            "explanation": "Explanation placeholder"
        }]

    result = {
        "title": title,
        "difficulty": difficulty,
        "description": description,
        "examples": examples,
        "constraints": constraints
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({ "error": str(e) }))
    sys.exit(1)
