import os
import sys
from pathlib import Path

from google import genai


MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.8-flash",
)


def generate_summary(input_file: str, output_file: str) -> None:
    """Generate a Traditional Chinese summary using Gemini."""

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    if not input_path.is_file():
        raise ValueError(
            f"Input path is not a file: {input_path}"
        )

    source_text = input_path.read_text(
        encoding="utf-8"
    )

    if not source_text.strip():
        raise RuntimeError(
            f"Input file is empty: {input_path}"
        )

    print(f"Input file : {input_path}")
    print(f"Output file: {output_path}")
    print(f"Gemini model: {MODEL}")

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
你是一個企業知識庫摘要助手。

請將以下 Markdown 文件整理成繁體中文摘要，
供後續自動產生 PowerPoint 簡報使用。

請嚴格遵守：

1. 只根據原始資料回答。
2. 不要捏造原始資料沒有的資訊。
3. 保留重要的人名、組織名稱與產品名稱。
4. 保留重要日期、數字、百分比與統計資料。
5. 資訊不足時標示「待確認」。
6. 不要把推測寫成事實。
7. 移除無關的重複資訊。
8. 使用繁體中文。
9. 摘要要適合後續製作 PowerPoint。

請使用以下格式：

# 摘要

用 2～4 段文字說明主要內容。

## 重點

- 重點 1
- 重點 2
- 重點 3
- 重點 4
- 重點 5

## 重要資訊

- 日期：
- 人物／組織：
- 產品／服務：
- 數字／統計：
- 其他重要資訊：

沒有資料的項目請寫「無」。

## 值得注意的變化

- 變化 1
- 變化 2
- 變化 3

如果沒有明確變化，請寫：

- 原始資料未提供明確的變化資訊。

## 待確認

列出需要進一步查證的內容。

如果沒有，請寫：

- 無。

## 簡報建議

提供 5～8 頁 PowerPoint 的建議架構。

請依照實際資料調整，不要硬套固定標題。

---

# 原始 Markdown

{source_text}
"""

    print("Sending request to Gemini...")

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
    )

    summary = interaction.output_text

    if not summary:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    summary = summary.strip()

    if not summary:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        summary,
        encoding="utf-8",
    )

    print(
        f"Summary generated successfully: {output_path}"
    )


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage:"
        )
        print(
            "  python scripts/generate_summary.py "
            "<input.md> <output.md>"
        )
        sys.exit(1)

    try:
        generate_summary(
            sys.argv[1],
            sys.argv[2],
        )

    except Exception as error:
        print()
        print(
            "ERROR: Failed to generate summary."
        )
        print(
            f"  {error}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

