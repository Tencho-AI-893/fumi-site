"""機微情報の検出。引っかかったメモはAIへ送らず、別扱いにする（店長の承認があれば送る）。"""
import re

PATTERNS = {
    "電話番号": re.compile(r"(?<!\d)0\d{1,4}[-ー ]?\d{1,4}[-ー ]?\d{3,4}(?!\d)"),
    "メールアドレス": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "カード/口座番号らしき数字": re.compile(r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)"),
    "APIキー/秘密鍵らしき文字列": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|ntn_[A-Za-z0-9]{16,}|secret_[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,})"),
}
KEYWORDS = ["パスワード", "暗証番号", "口座番号", "マイナンバー", "身分証", "秘密鍵", "キャスト名簿", "本名"]


def detect_sensitive(text: str) -> list[str]:
    reasons = [name for name, pat in PATTERNS.items() if pat.search(text)]
    reasons += [f"キーワード「{k}」" for k in KEYWORDS if k in text]
    return reasons
