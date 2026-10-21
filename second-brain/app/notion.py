"""Notion API。原文はページ本文に丸ごと入れ、AIの要約で上書きしない。"""
from . import config
from .net import http_json

BASE = "https://api.notion.com/v1"
CHUNK = 1900  # Notionは1つの文字ブロック2000字まで


def _headers():
    token = config.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN が未設定です（.env を確認）")
    return {"Authorization": f"Bearer {token}",
            "Notion-Version": config.get("NOTION_VERSION", "2022-06-28")}


def request(method, path, body=None):
    return http_json(BASE + path, method=method, headers=_headers(), body=body)


def _text(s):
    return [{"type": "text", "text": {"content": s[:2000]}}] if s else []


def _paragraphs(raw):
    return [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": _text(raw[i:i + CHUNK])}}
            for i in range(0, len(raw), CHUNK)] or []


def build_properties(entry, c, hash_):
    p = {
        "タイトル": {"title": _text(c["title"])},
        "要約": {"rich_text": _text(c["summary"])},
        "カテゴリー": {"select": {"name": c["category"]}},
        "タグ": {"multi_select": [{"name": t} for t in c["tags"]]},
        "登録日時": {"date": {"start": entry["created_at"]}},
        "元情報": {"select": {"name": entry["source_type"]}},
        "関連プロジェクト": {"rich_text": _text(c["project"])},
        "信頼度": {"number": c["confidence"]},
        "要確認": {"checkbox": bool(c["needs_review"])},
        "AI推定": {"rich_text": _text(c["suggested_category"])},
        "原文ハッシュ": {"rich_text": _text(hash_)},
    }
    return p


def create_page(database_id, entry, classified):
    """ページ作成。本文が100ブロックを超えたら追記で続ける。返り値: (page_id, url)"""
    blocks = [{"object": "block", "type": "heading_2",
               "heading_2": {"rich_text": _text("原文（AIは書き換えません）")}}] + _paragraphs(entry["raw"])
    version = config.get("NOTION_VERSION", "2022-06-28")
    ds = config.get("NOTION_DATA_SOURCE_ID")
    parent = {"type": "data_source_id", "data_source_id": ds} if ds else {"database_id": database_id}
    page = request("POST", "/pages", {
        "parent": parent,
        "properties": build_properties(entry, classified, entry["content_hash"]),
        "children": blocks[:100]})
    for i in range(100, len(blocks), 100):
        request("PATCH", f"/blocks/{page['id']}/children", {"children": blocks[i:i + 100]})
    return page["id"], page.get("url", "")


def create_sensitive_page(database_id, entry):
    """機微メモ：AIを通さず、原文だけを別DBへ。タイトルに本文は出さない。"""
    c = {"title": f"機微メモ {entry['created_at'][:16].replace('T', ' ')}", "summary": "", "category": "機微",
         "tags": [], "project": "", "confidence": 1.0, "needs_review": False, "suggested_category": ""}
    return create_page(database_id, entry, c)


DB_SCHEMA = {
    "タイトル": {"title": {}},
    "要約": {"rich_text": {}},
    "カテゴリー": {"select": {"options": [{"name": c["name"]} for c in config.categories()] +
                              [{"name": config.REVIEW_CATEGORY}]}},
    "タグ": {"multi_select": {}},
    "登録日時": {"date": {}},
    "元情報": {"select": {}},
    "関連プロジェクト": {"rich_text": {}},
    "信頼度": {"number": {"format": "number"}},
    "要確認": {"checkbox": {}},
    "AI推定": {"rich_text": {}},
    "原文ハッシュ": {"rich_text": {}},
}


def create_database(parent_page_id, title):
    """店長が共有した親ページの『中』に新しいDBを作る。既存データには触れない。"""
    r = request("POST", "/databases", {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": _text(title), "properties": DB_SCHEMA})
    return r["id"]


def _title_of(obj):
    if obj.get("object") == "database":
        parts = obj.get("title", [])
    else:
        t = next((v for v in obj.get("properties", {}).values() if v.get("type") == "title"), {})
        parts = t.get("title", [])
    return "".join(x.get("plain_text", "") for x in parts)


def find_target(name="第二の脳"):
    """連携に共有されたものから保存先を自動で探す。返り値: ("database"|"page", id)。無ければ None。
    優先順位: 同名のデータベース → 共有された最初のページ（その中にDBを作る）。"""
    def search(kind):
        r = request("POST", "/search", {"filter": {"property": "object", "value": kind}, "page_size": 20})
        return r.get("results", [])
    for d in search("database"):
        if _title_of(d) == name:
            return "database", d["id"]
    pages = [p for p in search("page") if p.get("parent", {}).get("type") != "database_id"]
    return ("page", pages[0]["id"]) if pages else None
