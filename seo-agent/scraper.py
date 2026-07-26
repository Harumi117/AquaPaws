import requests
from bs4 import BeautifulSoup


def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line for line in text.splitlines() if len(line.strip()) > 5]
        content = "\n".join(lines)

        # Limit to avoid exceeding token limits
        if len(content) > 8000:
            content = content[:8000] + "\n...[省略]"

        return content
    except Exception as e:
        return f"[ページ取得失敗: {e}]\nURLを確認するか、内容を手動で入力してください。"
