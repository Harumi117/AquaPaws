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

# ★プレースホルダーの自動置換マップ
_STAR_MAP = [
    ("★ここにレビューを貼り付け",
     "（レビューデータなし。ページ内容・商品特性・フェーズ1の分析から推定して分析してください）"),
    ("★ここに実流入キーワードデータを貼り付け（なければ「データなし」と入力）",
     "データなし"),
    ("★ここに検索結果の情報を貼り付け（競合商品名・価格・訴求内容など。なければ「情報なし」と入力）",
     "情報なし"),
    ("★ここに競合商品URLを1行ずつ貼り付け",
     "（競合URL情報なし。ここまでの市場分析をもとに一般的な競合傾向で分析してください）"),
    ("★ここに商品名・型番を入力",
     "（フェーズ1の分析結果から商品名・型番を特定してください）"),
    ("★S3で選択した候補を記入（未記入の場合は推奨候補を使用）",
     "（推奨候補を使用）"),
    ("★O3で選択した候補を記入（未記入の場合は推奨候補を使用）",
     "（推奨候補を使用）"),
    ("★実績・強み・利便性・ストーリーをここに記載",
     "（フェーズ1〜5の分析結果から自社商品の強みを推定して整理してください）"),
    # スタッフ情報（該当なし扱い）
    ("★店主・スタッフ名:", "該当なし:"),
    ("★その人の経歴・業界年数:", "該当なし:"),
    ("★この商品カテゴリでの専門性（資格・経験・実績）:", "該当なし:"),
    ("★この商品を選んだ理由・選定基準:", "該当なし:"),
    ("★他の類似商品ではなくこれを扱う理由:", "該当なし:"),
    ("★顧客から実際にもらった印象的な質問・相談:", "該当なし:"),
    # ページ設計
    ("★対象モール（楽天 / Yahoo / Amazon など）:", "楽天市場:"),
    ("★想定画像枚数:", "15枚:"),
    # O3ポジショニング項目（フェーズ1分析から推定）
    ("★ブランド名: [あり / なし]", "（フェーズ1の分析から推定）:"),
    ("★ブランド名（ありの場合）:", "（フェーズ1の分析から推定）:"),
    ("★ショップ名:", "（フェーズ1の分析から推定）:"),
    ("★商品の正式名称または仮名:", "（フェーズ1の分析から推定）:"),
    ("★商品カテゴリ（一般名詞）:", "（フェーズ1の分析から推定）:"),
    ("★商品の主な用途:", "（フェーズ1の分析から推定）:"),
    ("★想定する主なターゲット:", "（フェーズ1の分析から推定）:"),
    ("★商品の主要スペック:", "（フェーズ1の分析から推定）:"),
    ("★商品の差別化ポイント（3つ以上）:", "（フェーズ1〜2の分析から推定）:"),
    ("★商品が生まれた背景:", "（ページ内容から推定）:"),
    ("★商品名の由来（決まっている場合）:", "（ページ内容から推定）:"),
]


def _auto_fill_stars(text: str) -> str:
    """Replace all ★ placeholders automatically without user input."""
    for placeholder, value in _STAR_MAP:
        text = text.replace(placeholder, value)
    # 残った★があれば汎用フォールバック
    remaining = re.findall(r"★[^\n]*", text)
    for ph in remaining:
        text = text.replace(ph, "（ここまでの分析から推定・補完してください）", 1)
    return text


def _call_claude(client: anthropic.Anthropic, messages: list) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _detect_branch(client: anthropic.Anthropic, messages: list) -> str:
    """Ask Claude to determine S (型番) or O (オリジナル) branch."""
    detect_prompt = (
        "この商品は「型番商品（メーカー品・ブランド品で型番がある）」と"
        "「オリジナル商品（自社企画・PB商品）」のどちらですか？"
        "「S」または「O」の1文字だけで答えてください。"
    )
    msgs = messages + [{"role": "user", "content": detect_prompt}]
    response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        system=SYSTEM_PROMPT,
        messages=msgs,
    )
    answer = response.content[0].text.strip().upper()
    return "2S" if "S" in answer else "2O"


def _save_results(url: str, results: list[dict]) -> str:
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/result_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 商品ページ分析レポート\n\n")
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

    # ページ取得（失敗してもそのまま続行）
    print(f"\n商品ページを取得中: {url}")
    page_content = fetch_page(url)
    if "[ページ取得失敗" in page_content:
        print(f"警告: {page_content}")
        print("ページ内容を取得できませんでしたが、URLの情報をもとに分析を続けます。")
        page_content = f"（ページ自動取得失敗。URL: {url} の情報をもとに分析してください）"
    else:
        print("取得完了。")

    messages: list[dict] = []
    results: list[dict] = []
    seo_phase: str | None = None

    print(f"\n{'='*60}")
    print("分析を開始します（全自動モード）")
    print(f"{'='*60}\n")

    for prompt in PROMPTS:
        phase = prompt["phase"]

        # フェーズ1完了後にS/O自動判定
        if seo_phase is None and phase in ("2S", "2O"):
            print("\n  商品タイプを自動判定中...", end="", flush=True)
            seo_phase = _detect_branch(client, messages)
            branch_name = "型番商品" if seo_phase == "2S" else "オリジナル商品"
            print(f" {branch_name} と判定")

        # 対象外ブランチをスキップ
        if phase in ("2S", "2O") and phase != seo_phase:
            continue

        phase_label = f"フェーズ{phase}" if isinstance(phase, int) else f"フェーズ {phase}"
        print(f"\n{'─'*60}")
        print(f"[{phase_label}] {prompt['id']}: {prompt['title']}")
        print("─" * 60)

        text = prompt["text"]

        # URL・ページ内容を注入
        if "★ここに商品ページURL" in text:
            text = text.replace("★ここに商品ページURL", url)
        if "★SCRAPED_CONTENT" in text:
            text = text.replace("★SCRAPED_CONTENT", page_content)

        # 残り★を全自動補完
        text = _auto_fill_stars(text)

        # Claudeに送信
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

    filename = _save_results(url, results)
    print(f"\n{'='*60}")
    print(f"分析完了！レポートを保存しました: {filename}")
    print("=" * 60)
