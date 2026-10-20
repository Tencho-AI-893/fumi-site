"""SQLite：原文の金庫・処理履歴・重複判定・再送管理。ここに原文が必ず残る。"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_hash TEXT NOT NULL,
  raw TEXT NOT NULL,
  source_type TEXT NOT NULL DEFAULT 'メモ',
  no_ai INTEGER NOT NULL DEFAULT 0,
  sensitive_reasons TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'pending',  -- pending/saved/failed/held
  classified TEXT,                          -- AI結果(JSON)。再送時にAIを呼び直さない
  notion_page_id TEXT,
  notion_url TEXT,
  attempts INTEGER NOT NULL DEFAULT 0,
  error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_hash ON entries(content_hash);
CREATE INDEX IF NOT EXISTS idx_status ON entries(status);
"""


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(config.data_dir() / "secondbrain.sqlite")
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def content_hash(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def add(con, raw, source_type="メモ", no_ai=False, reasons=None):
    """追加。同じ内容が保存済みなら (既存行, False) を返す＝重複防止。"""
    h = content_hash(raw)
    dup = con.execute(
        "SELECT * FROM entries WHERE content_hash=? AND status IN ('saved','pending','failed','held') "
        "ORDER BY id LIMIT 1", (h,)).fetchone()
    if dup:
        return dup, False
    t = now()
    cur = con.execute(
        "INSERT INTO entries(content_hash,raw,source_type,no_ai,sensitive_reasons,created_at,updated_at)"
        " VALUES(?,?,?,?,?,?,?)",
        (h, raw, source_type, int(no_ai), json.dumps(reasons or [], ensure_ascii=False), t, t))
    con.commit()
    return get(con, cur.lastrowid), True


def get(con, entry_id):
    return con.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()


def update(con, entry_id, **fields):
    fields["updated_at"] = now()
    cols = ", ".join(f"{k}=?" for k in fields)
    con.execute(f"UPDATE entries SET {cols} WHERE id=?", (*fields.values(), entry_id))
    con.commit()


def recent(con, limit=20):
    return con.execute("SELECT * FROM entries ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def retryable(con):
    return con.execute("SELECT * FROM entries WHERE status IN ('failed','pending') ORDER BY id").fetchall()
