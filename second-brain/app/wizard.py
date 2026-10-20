"""ワンアクション・セットアップ。質問は2つだけ（Notionの鍵・親ページのURL）。残りは自動。"""
import getpass
import re
import webbrowser
from pathlib import Path

from . import config, db, net, notion, pipeline, server

ENV_PATH = config.ROOT / ".env"
OLLAMA = "http://127.0.0.1:11434"
MODEL = "gemma2:9b"


def extract_page_id(text: str) -> str | None:
    """NotionのURL（またはID）から32桁のIDを取り出す。ページ名の文字を巻き込まないよう境界を厳密に見る。"""
    hexd = r"[0-9a-fA-F]"
    plain = re.findall(rf"(?<!{hexd})({hexd}{{32}})(?!{hexd})", text)
    if plain:
        return plain[-1].lower()
    dashed = re.findall(rf"(?<!{hexd})({hexd}{{8}}-{hexd}{{4}}-{hexd}{{4}}-{hexd}{{4}}-{hexd}{{12}})(?!{hexd})", text)
    return dashed[-1].replace("-", "").lower() if dashed else None


def render_env(token: str, db_id: str, existing: dict | None = None) -> str:
    return "\n".join([
        "# 第二の脳の設定。このファイルは絶対にGitHubへ上げない",
        f"NOTION_TOKEN={token}", f"NOTION_DATABASE_ID={db_id}", "NOTION_SENSITIVE_DATABASE_ID=",
        "LLM_PROVIDER=ollama", f"OLLAMA_MODEL={MODEL}", f"OLLAMA_URL={OLLAMA}",
        "CONFIDENCE_THRESHOLD=0.6", ""])


def check_ollama() -> None:
    try:
        tags = net.http_json(f"{OLLAMA}/api/tags", method="GET", timeout=5, retries=0)
    except net.NetError:
        raise SystemExit("❌ Ollamaが起動していません。スタートメニューから Ollama を起動して、もう一度ダブルクリックしてください。")
    names = [m.get("name", "") for m in tags.get("models", [])]
    if not any(n.startswith(MODEL.split(":")[0]) for n in names):
        raise SystemExit(f"❌ AIモデルが見つかりません。コマンドプロンプトで  ollama pull {MODEL}  を実行してください。")
    print(f"✅ ローカルAI（{MODEL}）を確認")


def main() -> None:
    print("=== 第二の脳 セットアップ（質問は2つだけです）===\n")
    if ENV_PATH.exists():
        raise SystemExit("ℹ️ すでにセットアップ済みです（.env があります）。普段は『起動.bat』を使ってください。"
                         "\n   やり直したい時は .env の名前を変えてからもう一度実行してください。（既存ファイルは上書きしません）")
    check_ollama()

    print("\n【質問1】Notionの鍵（シークレット）を貼ってEnter。※貼っても画面には何も出ません。それで正常です")
    token = getpass.getpass("> ").strip()
    import os
    os.environ["NOTION_TOKEN"] = token
    try:
        notion.request("GET", "/users/me")
    except net.NetError as e:
        raise SystemExit(f"❌ 鍵が正しくないようです（{e.status}）。コピーし直してやり直してください。")
    print("✅ Notionの鍵を確認")

    print("\n【質問2】Notionで作った親ページのURLを貼ってEnter（ページ右上『…』→リンクをコピー）")
    page_id = extract_page_id(input("> "))
    if not page_id:
        raise SystemExit("❌ URLからページIDが読み取れませんでした。ページのリンクを貼り直してください。")
    try:
        db_id = notion.create_database(page_id, "第二の脳")
    except net.NetError as e:
        hint = ("そのページに『第二の脳』の連携が共有されていません。ページ右上『…』→『接続』→『第二の脳』を追加してください。"
                if e.status in (403, 404) else "")
        raise SystemExit(f"❌ データベースを作れませんでした（{e.status}）。{hint}")
    print("✅ Notionに『第二の脳』データベースを作成")

    ENV_PATH.write_text(render_env(token, db_id), encoding="utf-8")
    config.load_env()
    print("✅ 設定ファイル(.env)を作成")

    con = db.connect()
    entry, _ = pipeline.submit(con, "これは第二の脳のテストメモです。セットアップ成功の確認用。消してOKです。", "メモ")
    if entry["status"] == "saved":
        print("✅ テスト保存に成功！ Notionを開いて確認してください:", entry["notion_url"])
    else:
        print("⚠️ テスト保存は未完了:", entry["error"], "\n   原文はPC内に残っています。画面の『再送』で再実行できます。")
    print("\n入力画面を開きます（止める時はこの黒い画面を閉じる）")
    webbrowser.open("http://127.0.0.1:8765")
    server.serve()
