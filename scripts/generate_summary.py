import os
import sys
from pathlib import Path

from google import genai


MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def generate_summary(input_file, output_file):
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

    source_text = input_path.read_text(
        encoding="utf-8"
    )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
你是一個知識庫摘要助手。

請將以下 Markdown 文件整理成繁體中文摘要。

要求：

1. 列出 5～10 個重要重點
2. 保留重要數字、日期、名稱
3. 不要捏造原文沒有的資訊
4. 不確定的資訊標示「待確認」
5. 找出值得注意的變化
6. 最後提供簡報架構

輸出格式：

# 摘要

## 重點

- 

## 重要資訊

- 

## 值得注意的變化

- 

## 待確認

- 

## 簡報架構

1.
2.
3.

---

原始資料：

{source_text}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        response.text,
        encoding="utf-8"
    )

    print(
        f"Summary generated: {output_path}"
    )


def main():
    if len(sys.argv) != 3:
        print(
            "Usage:"
            " python scripts/generate_summary.py"
            " <input.md> <output.md>"
        )
        sys.exit(1)

    generate_summary(
        sys.argv[1],
        sys.argv[2],
    )


if __name__ == "__main__":
    main()
