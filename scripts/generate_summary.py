import os
import sys
from pathlib import Path

from google import genai


MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


def generate_summary(input_file: str, output_file: str):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set."
        )

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    text = input_path.read_text(
        encoding="utf-8"
    )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
請將以下知識庫內容整理成繁體中文摘要。

要求：

1. 提供 5～10 個重點
2. 找出重要事實
3. 找出值得注意的變化
4. 如果內容包含數字，保留原始數字
5. 不要自行捏造資料
6. 不確定的內容請標示「待確認」
7. 最後提供「簡報建議架構」

輸出格式：

# 摘要

## 重點
- ...

## 重要資訊
- ...

## 待確認
- ...

## 簡報建議
1. ...
2. ...
3. ...

原始內容：

{text}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
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
            "Usage: "
            "python generate_summary.py "
            "<input.md> <output.md>"
        )
        sys.exit(1)

    generate_summary(
        sys.argv[1],
        sys.argv[2],
    )


if __name__ == "__main__":
    main()

