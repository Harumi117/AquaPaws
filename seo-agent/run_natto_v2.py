"""納豆おやつ 再分析（実流入キーワードデータ追加版）"""
import os
import re
import datetime
import anthropic
from dotenv import load_dotenv
from prompts import PROMPTS

load_dotenv()

URL = "https://item.rakuten.co.jp/dogcat-shop/watashiinu286/"

PAGE_CONTENT = """
フリーズ ドライ 納豆 犬 ひきわり納豆 (50g/150g/500g)
商品番号： watashiinu286
価格: 810円〜7,690円
評価：5.0（3件）

【主な特徴】
・無添加: 甘味料、香料、着色料不使用
・栄養: 高タンパク・低カロリー
・原材料: 国産大豆を使用
・製法: フリーズドライ加工でより栄養価を保持
・用途: おやつ、ドッグフードのトッピング、トレーニング用ご褒美

【どんなワンちゃんに？】
超小型犬、小型犬、中型犬、大型犬
全年齢対応（成犬、シニア犬、老犬）

成分値: 粗蛋白 41.5%以上 粗脂肪 23%以上 カロリー415kcal/100g

ヒューマングレードの安心安全な犬用おやつ。国産納豆をフリーズドライ製法で仕上げた、栄養満点の一品。
無添加・自然食にこだわった製法。愛犬の健康と幸せを第一に。
"""

REVIEWS = """
レビュー1（2026年03月10日）:
愛犬に納豆をあげたくてこちらのフリーズドライがとても便利です。ご飯にふりかけられるのでとても助かっています。

レビュー2（2025年11月17日・ori28さん・50代男性）:
うちのワンコは、大好きで毎日フードに少し混ぜて食べてます。

レビュー3（2025年09月16日・あーちゃんホイホイさん・50代男性）:
わんこが納豆好きとは思いませんでしたが、これをかけると、あっという間にご飯完食です！健康にも良さそう。

総合評価：5.0（3件）
"""

# ★ 実流入キーワードデータ（楽天RMS）
KEYWORD_DATA = """
【楽天RMS 実流入キーワードデータ】
キーワード          | アクセス数 | 転換率  | 順位
犬 納豆             | 2         | 0.00%  | 61位
納豆フリーズドライ 犬| 1         | 0.00%  | 1位
納豆 フリーズドライ  | 1         | 0.00%  | 101位以下
犬用納豆            | 1         | 0.00%  | 3位
犬用フリーズドライ納豆| 1        | 0.00%  | （データなし）

【考察メモ】
・「納豆フリーズドライ 犬」で1位を取れているが転換率0%
・「犬 納豆」で61位と低順位のためアクセスが少ない
・全体的に転換率0%で購入に至っていない
"""

SYSTEM = (
    "あなたはECモール（楽天・Yahoo・Amazon等）の商品ページ分析・改善の専門コンサルタントです。"
    "各プロンプトに対して、このチャットのここまでの内容を踏まえた上で回答してください。"
    "回答は日本語で、具体的かつ実践的にお願いします。"
)

MODEL = "claude-opus-4-8"

_STAR_MAP = [
    ("★ここにレビューを貼り付け", REVIEWS),
    ("★ここに実流入キーワードデータを貼り付け（なければ「データなし」と入力）", KEYWORD_DATA),
    ("★ここに検索結果の情報を貼り付け（競合商品名・価格・訴求内容など。なければ「情報なし」と入力）", "情報なし"),
    ("★ここに競合商品URLを1行ずつ貼り付け", "（競合URL情報なし。ここまでの市場分析をもとに分析してください）"),
    ("★ここに商品名・型番を入力", "フリーズドライひきわり納豆（わたしいぬ わたしねこライフ / watashiinu286）"),
    ("★S3で選択した候補を記入（未記入の場合は推奨候補を使用）", "（推奨候補を使用）"),
    ("★O3で選択した候補を記入（未記入の場合は推奨候補を使用）", "（推奨候補を使用）"),
    ("★実績・強み・利便性・ストーリーをここに記載", "（フェーズ1〜5の分析から推定してください）"),
    ("★店主・スタッフ名:", "該当なし:"),
    ("★その人の経歴・業界年数:", "該当なし:"),
    ("★この商品カテゴリでの専門性（資格・経験・実績）:", "該当なし:"),
    ("★この商品を選んだ理由・選定基準:", "該当なし:"),
    ("★他の類似商品ではなくこれを扱う理由:", "該当なし:"),
    ("★顧客から実際にもらった印象的な質問・相談:", "該当なし:"),
    ("★対象モール（楽天 / Yahoo / Amazon など）:", "楽天市場:"),
    ("★想定画像枚数:", "15枚:"),
    ("★ブランド名: [あり / なし]", "あり:"),
    ("★ブランド名（ありの場合）:", "わたしいぬ わたしねこライフ:"),
    ("★ショップ名:", "わたしいぬ わたしねこライフ（dogcat-shop）:"),
    ("★商品の正式名称または仮名:", "フリーズドライ ひきわり納豆:"),
    ("★商品カテゴリ（一般名詞）:", "犬用おやつ（フリーズドライ・トッピング）:"),
    ("★商品の主な用途:", "フードトッピング・おやつ・トレーニングご褒美:"),
    ("★想定する主なターゲット:", "無添加・国産にこだわる愛犬家（40〜60代）:"),
    ("★商品の主要スペック:", "粗蛋白41.5%以上、カロリー415kcal/100g、国産大豆、フリーズドライ:"),
    ("★商品の差別化ポイント（3つ以上）:", "①納豆という唯一無二の素材 ②フリーズドライで手軽にふりかけ ③無添加・国産・ヒューマングレード:"),
    ("★商品が生まれた背景:", "（ページ内容から推定）:"),
    ("★商品名の由来（決まっている場合）:", "（ページ内容から推定）:"),
]

def auto_fill(text):
    for ph, val in _STAR_MAP:
        text = text.replace(ph, val)
    for ph in re.findall(r"★[^\n]*", text):
        text = text.replace(ph, "（ここまでの分析から推定してください）", 1)
    return text

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
messages = []
results = []
SEO_PHASE = "2O"

print("=" * 60)
print("Sera が分析を開始します...（実流入KWデータ追加版）")
print("=" * 60)

for prompt in PROMPTS:
    phase = prompt["phase"]
    if phase in ("2S", "2O") and phase != SEO_PHASE:
        continue

    print(f"\n[{prompt['id']}] {prompt['title']} ...", end="", flush=True)

    text = prompt["text"]
    text = text.replace("★ここに商品ページURL", URL)
    text = text.replace("★SCRAPED_CONTENT", PAGE_CONTENT)
    text = auto_fill(text)

    messages.append({"role": "user", "content": text})
    resp = client.messages.create(model=MODEL, max_tokens=4096, system=SYSTEM, messages=messages)
    response_text = resp.content[0].text
    messages.append({"role": "assistant", "content": response_text})
    results.append({"id": prompt["id"], "title": prompt["title"], "response": response_text})
    print(" 完了")

os.makedirs("output", exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = f"output/natto_report_v2_{ts}.md"
with open(outfile, "w", encoding="utf-8") as f:
    f.write("# フリーズドライひきわり納豆 商品ページ分析レポート（実流入KW版）\n\n")
    f.write(f"**URL:** {URL}  \n")
    f.write(f"**日時:** {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n\n---\n\n")
    for item in results:
        f.write(f"## {item['id']}: {item['title']}\n\n{item['response']}\n\n---\n\n")

print(f"\nSera の分析完了！ファイル: {outfile}")
