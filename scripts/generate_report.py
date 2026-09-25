from datetime import datetime, timezone
from pathlib import Path


OUTPUT_DIR = Path("data/reports")


def generate_report():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output_file = OUTPUT_DIR / f"{date}.md"

    content = f"""# Daily Report {date}

Generated automatically by GitHub Actions.

## Repository

{__import__("os").environ.get("GITHUB_REPOSITORY", "unknown")}

## Workflow

{__import__("os").environ.get("GITHUB_WORKFLOW", "unknown")}

## Run

{__import__("os").environ.get("GITHUB_RUN_ID", "unknown")}

## Generated At

{datetime.now(timezone.utc).isoformat()}
"""

    output_file.write_text(
        content,
        encoding="utf-8",
    )

    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    generate_report()

