import sys

from . import config, db, notion, pipeline, server

config.load_env()
HELP = """使い方:
  python -m app serve            入力画面を起動
  python -m app check            設定が足りているか確認（キーは表示しません）
  python -m app setup <親ページID>  Notionに「第二の脳」DBを新規作成
  python -m app retry            失敗したものを全部再送
"""


def check():
    ok = True
    for name, why in [("NOTION_TOKEN", "Notionへ保存する鍵"), ("NOTION_DATABASE_ID", "保存先データベース")]:
        has = bool(config.get(name))
        ok &= has
        print(("✅" if has else "❌"), name, "-", why)
    prov = config.get("LLM_PROVIDER", "openai")
    if prov == "openai":
        has = bool(config.get("OPENAI_API_KEY"))
        ok &= has
        print(("✅" if has else "❌"), "OPENAI_API_KEY - AI分類の鍵")
    else:
        print("✅ ローカルAI(Ollama)を使用:", config.get("OLLAMA_URL", "http://127.0.0.1:11434"))
    print("ℹ️ 機微メモ用DB:", "あり" if config.get("NOTION_SENSITIVE_DATABASE_ID") else "なし（機微メモはPC内で保留）")
    return ok


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "serve":
        server.serve()
    elif cmd == "check":
        sys.exit(0 if check() else 1)
    elif cmd == "setup" and len(argv) > 1:
        print("作成しました。次の行を .env の NOTION_DATABASE_ID= に貼ってください:\n" + notion.create_database(argv[1], "第二の脳"))
    elif cmd == "retry":
        res = pipeline.retry_all(db.connect())
        print(f"{len(res)}件を処理: 成功 {sum(r['status'] == 'saved' for r in res)} / 未完了 {sum(r['status'] != 'saved' for r in res)}")
    else:
        print(HELP)


main(sys.argv[1:])
