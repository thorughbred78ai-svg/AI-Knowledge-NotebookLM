- name: Check Gemini configuration
  run: |
    if [ -z "$GEMINI_API_KEY" ]; then
      echo "ERROR: GEMINI_API_KEY is missing"
      exit 1
    fi

    echo "GEMINI_API_KEY is configured"
    echo "GEMINI_MODEL=$GEMINI_MODEL"


import os
import sys
from pathlib import Path

from google import genai


# ============================================================
# Configuration
# ============================================================

MODEL = os.environ.get(
    "GEMINI_MODEL",
    "gemini-3.8-flash",
)


# ============================================================
# Generate Summary
# ============================================================

def generate_summary(input_file: str, output_file: str) -> None:
    """
    使用 Gemini 將 Markdown 文件整理成繁體中文摘要。

    Args:
        input_file: 原始 Markdown 檔案
        output_file: 摘要輸出檔案
    """

    # --------------------------------------------------------
    # Check API Key
    # --------------------------------------------------------

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    # --------------------------------------------------------
    # Prepare paths
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Read source Markdown
    # --------------------------------------------------------

    source_text = input_path.read_text(
        encoding="utf-8"
    )

    if not source_text.strip():
        raise RuntimeError(
            f"Input file is empty: {input_path}"
        )

    print(
        f"Input file : {input_path}"
    )

    print(
        f"Output file: {output_path}"
    )

    print(
        f"Gemini model: {MODEL}"
    )

    # --------------------------------------------------------
    # Create Gemini client
    # --------------------------------------------------------

    client = genai.Client(
        api_key=api_key
    )

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
你是一個企業知識庫摘要助手。

請將以下 Markdown 文件整理成「繁體中文」的高品質摘要，
供後續自動產生 PowerPoint 簡報使用。

請嚴格遵守以下規則：

1. 只根據原始資料回答。
2. 不要自行捏造不存在的資訊。
3. 保留重要的人名、組織名稱、產品名稱。
4. 保留重要日期、數字、百分比與統計資料。
5. 如果原始資料不足以確認某件事情，請標示「待確認」。
6. 不要把推測寫成事實。
7. 移除與內容無關的重複資訊。
8. 摘要應該簡潔、容易閱讀。
9. 使用繁體中文。
10. 摘要內容要適合直接交給 PowerPoint 產生程式使用。

請按照以下格式輸出：

# 摘要

用 2～4 段文字說明這份資料的主要內容。

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

如果某項沒有資料，請寫「無」。

## 值得注意的變化

- 變化 1
- 變化 2
- 變化 3

如果沒有明確變化，請寫：

- 原始資料未提供明確的變化資訊。

## 待確認

列出原始資料中無法確認、資訊不足或需要進一步查證的內容。

如果沒有，請寫：

- 無。

## 簡報建議

提供 5～8 頁 PowerPoint 的建議架構。

格式：

1. 標題頁
2. 核心摘要
3. 重要發現
4. 數據與趨勢
5. 值得注意的變化
6. 待確認事項
7. 結論

請依照實際資料調整，不要硬套上述標題。

---

# 原始 Markdown

{source_text}
"""

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    print(
        "Sending request to Gemini..."
    )

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
    )

    # --------------------------------------------------------
    # Get response
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

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


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Command line entry point.
    """

    if len(sys.argv) != 3:
        print(
            "Usage:"
        )

        print(
            "  python scripts/generate_summary.py "
            "<input.md> <output.md>"
        )

        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        generate_summary(
            input_file,
            output_file,
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

