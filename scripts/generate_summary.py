import os
import sys
from pathlib import Path

from google import genai
from google.genai import types

MODEL = os.environ.get(
"GEMINI_MODEL",
"gemini-3.5-flash"
)

OUTPUT_DIR = Path(
"data/summaries"
)

PROMPT = """
You are a knowledge-management analyst.

Read the supplied daily knowledge report.

Generate a concise but information-dense Markdown summary.

Requirements:

Do not invent facts.

Preserve important numbers, names, dates and sources.

Clearly distinguish facts from interpretation.

If information is missing, say so.

Prefer bullet points and short paragraphs.

Write in Traditional Chinese.

Keep the report suitable for an executive reader.

Use exactly this structure:

Daily Knowledge Summary
Executive Summary
Key Findings
Important Changes
Trends
Risks and Uncertainties
Follow-up
Sources

"""

def read_report(path):
return path.read_text(
encoding="utf-8"
)

def generate_summary(client, report):
response = client.models.generate_content(
model=MODEL,
contents=[
types.Content(
role="user",
parts=[
types.Part.from_text(
text=PROMPT
),
types.Part.from_text(
text="\n\nSOURCE REPORT:\n"
+ report
),
],
)
],
)

if not response.text:
    raise RuntimeError(
        "Gemini returned an empty response."
    )

return response.text.strip()


def main():
if len(sys.argv) < 2:
print(
"Usage: "
"python scripts/generate_summary.py "
"<report.md>"
)
sys.exit(1)

report_path = Path(
    sys.argv[1]
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

client = genai.Client()

report = read_report(
    report_path
)

summary = generate_summary(
    client,
    report
)

date = report_path.stem

output = (
    OUTPUT_DIR
    / f"{date}-summary.md"
)

output.write_text(
    summary,
    encoding="utf-8"
)

print(
    f"Generated summary: {output}"
)


if name == "main":
main()
