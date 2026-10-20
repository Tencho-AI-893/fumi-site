"""設定の読み込み。APIキーなどの秘密は .env（環境変数）からだけ読む。コードには書かない。"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CATEGORIES = [
    {"name": "SM.カルマ経営", "hint": "店の売上・会員・運営・集客・料金など経営判断"},
    {"name": "キャスト・採用・人材管理", "hint": "キャスト/スタッフの採用・育成・シフト・面談"},
    {"name": "AI開発・自動化", "hint": "TENCHO-AI, VAULT, プロンプト, 自動化, プログラム開発"},
    {"name": "投資・資産形成", "hint": "TRADER-AI, BTC, FX, 積立, 資産管理"},
    {"name": "ブログ・コンテンツ制作", "hint": "記事・SNS・LP・文章のネタや下書き"},
    {"name": "PC・IT・設備", "hint": "PC, ネットワーク, 機材, ソフトの設定や購入"},
    {"name": "自己成長・習慣", "hint": "健康, 学び, 習慣, 考え方"},
    {"name": "アイデア・未分類", "hint": "どれにも当てはまらない思いつき"},
]
REVIEW_CATEGORY = "要確認"


def load_env(path: Path | None = None) -> None:
    """.env を読んで環境変数に入れる（すでにある環境変数は上書きしない）。"""
    path = path or ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def data_dir() -> Path:
    d = Path(get("SB_DATA_DIR") or ROOT / "data")
    d.mkdir(parents=True, exist_ok=True)
    return d


def categories() -> list[dict]:
    """categories.json があればそれを使う。無ければ初期カテゴリー。"""
    f = ROOT / "categories.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return DEFAULT_CATEGORIES


def confidence_threshold() -> float:
    return float(get("CONFIDENCE_THRESHOLD", "0.6"))
