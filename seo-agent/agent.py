import os
import re
import datetime
import anthropic
from dotenv import load_dotenv
from prompts import PROMPTS
from scraper import fetch_page

load_dotenv()

SYSTEM_PROMPT = (
    "あなたはECモール（楽天・Yahoo・Amazon等）の商品ページ分析・改善の専門コンサルタントです。"
    "各プロンプトに対して、このチャットのここまでの内容を踏まえた上で回答してください。"
    "回答は日本語で、具体的かつ実践的にお願いします。"
)

MODEL = "claude-opus-4-8"


def _ask_star_inputs(text: str) -> str:
    """Replace ★... placeholders with user input interactively."""
    while True:
        match = re.search(r"★[^\n]*", text)
        if not match:
            break
        placeholder = match.group()
        print(f"\n  入力が必要: {placeholder}")
        user_input = input("  > ").strip()
        if not user_input:
            user_input = "（情報なし）"
        text = text.replace(placeholder, user_input, 1)
    return text


def _call_claude(client: anthropic.Anthropic, messages: list) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _save_results(url: str, results: list[dict]) -> str:
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/result_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 商品ページ分析レポート\n\n")
        f.write(f"**URL:** {url}  \n")
        f.write(f"**日時:** {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n\n")
        f.write("---\n\n")
        for item in results:
            f.write(f"## {item['id']}: {item['title']}\n\n")
            f.write(item["response"])
            f.write("\n\n---\n\n")

    return filename


def run_pipeline(url: str) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: .env ファイルに ANTHROPIC_API_KEY を設定してください。")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Scrape page
    print(f"\n商品ページを取得中: {url}")
    page_content = fetch_page(url)
    if "[ページ取得失敗" in page_content:
        print(f"\n警告: {page_content}")
        print("ページ内容を手動で貼り付けてください（空行2回で終了）:")
        lines = []
        empty_count = 0
        while empty_count < 2:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        page_content = "\n".join(lines) if lines else "（ページ内容なし）"
    else:
        print("取得完了。")

    # Ask product type for SEO branch
    print("\n商品タイプを選択してください:")
    print("  1 = 型番商品（メーカー品・ブランド品）")
    print("  2 = オリジナル商品（自社企画・PB商品）")
    while True:
        choice = input("選択 (1 or 2): ").strip()
        if choice in ("1", "2"):
            break
        print("1 または 2 を入力してください。")
    seo_phase = "2S" if choice == "1" else "2O"

    messages: list[dict] = []
    results: list[dict] = []

    print(f"\n{'='*60}")
    print("分析を開始します。")
    print(f"{'='*60}\n")

    for prompt in PROMPTS:
        phase = prompt["phase"]

        # Skip the wrong SEO branch
        if phase in ("2S", "2O") and phase != seo_phase:
            continue

        phase_label = f"フェーズ{phase}" if isinstance(phase, int) else f"フェーズ {phase}"
        print(f"\n{'─'*60}")
        print(f"[{phase_label}] {prompt['id']}: {prompt['title']}")
        print("─" * 60)

        text = prompt["text"]

        # Inject URL and scraped content for prompt 1.0
        if "★ここに商品ページURL" in text:
            text = text.replace("★ここに商品ページURL", url)
        if "★SCRAPED_CONTENT" in text:
            text = text.replace("★SCRAPED_CONTENT", page_content)

        # Handle remaining ★ placeholders interactively
        if "★" in text:
            print("\n  このプロンプトには手動入力が必要です:")
            text = _ask_star_inputs(text)

        # Send to Claude
        messages.append({"role": "user", "content": text})
        print("\n  Claude が分析中...", end="", flush=True)

        response_text = _call_claude(client, messages)
        messages.append({"role": "assistant", "content": response_text})

        print(" 完了")
        print(f"\n{response_text}\n")

        results.append({
            "id": prompt["id"],
            "title": prompt["title"],
            "response": response_text,
        })

    # Save
    filename = _save_results(url, results)
    print(f"\n{'='*60}")
    print(f"分析完了！レポートを保存しました: {filename}")
    print("=" * 60)
