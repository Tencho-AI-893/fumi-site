"""1件の処理の流れ：金庫(SQLite)へ保存 → 機微チェック → AI分類 → Notion保存。どこで失敗しても原文は残る。"""
import json

from . import classify, config, db, notion, safety


def submit(con, text, source_type="メモ", no_ai=False):
    """入口。返り値: (entry, is_new)。"""
    text = text.strip()
    if not text:
        raise ValueError("空のメモは保存できません")
    reasons = safety.detect_sensitive(text)
    entry, is_new = db.add(con, text, source_type, no_ai, reasons)
    if is_new:
        entry = process(con, entry["id"])
    return entry, is_new


def process(con, entry_id, approve_ai=False):
    """再実行しても安全（Notion保存済みなら何もしない・AI結果は再利用）。"""
    e = db.get(con, entry_id)
    if e["notion_page_id"]:
        return e
    reasons = json.loads(e["sensitive_reasons"])
    sensitive_db = config.get("NOTION_SENSITIVE_DATABASE_ID")
    held_from_ai = bool(e["no_ai"]) or (bool(reasons) and not approve_ai)
    db.update(con, entry_id, attempts=e["attempts"] + 1)
    try:
        if held_from_ai:
            if not sensitive_db:
                db.update(con, entry_id, status="held",
                          error="機微情報の可能性があるため保留中（AIにも通常DBにも送っていません）")
                return db.get(con, entry_id)
            page_id, url = notion.create_sensitive_page(sensitive_db, e)
        else:
            if e["classified"]:
                c = json.loads(e["classified"])
            else:
                c = classify.classify(e["raw"], e["source_type"])
                db.update(con, entry_id, classified=json.dumps(c, ensure_ascii=False))
            page_id, url = notion.create_page(config.get("NOTION_DATABASE_ID"), e, c)
        db.update(con, entry_id, status="saved", notion_page_id=page_id, notion_url=url, error=None)
    except Exception as ex:  # 原文は金庫にあるので失わない。理由だけ記録（本文は出さない）
        db.update(con, entry_id, status="failed", error=f"{type(ex).__name__}: {str(ex)[:200]}")
    return db.get(con, entry_id)


def retry_all(con):
    return [process(con, r["id"]) for r in db.retryable(con)]
