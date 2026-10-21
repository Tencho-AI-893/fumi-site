"""ワンアクション・セットアップ。質問は2つだけ（Notionの鍵・親ページのURL）。残りは自動。"""
import getpass
import os
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
    print("=== 第二の脳 セットアップ（質問は1つだけです）===\n")
    if ENV_PATH.exists():
        raise SystemExit("ℹ️ すでにセットアップ済みです（.env があります）。普段は『起動.bat』を使ってください。"
                         "\n   やり直したい時は .env の名前を変えてからもう一度実行してください。（既存ファイルは上書きしません）")
    check_ollama()

    print("\n【質問】Notionの鍵（シークレット）を貼ってEnter。※貼っても画面には何も出ません。それで正常です")
    token = getpass.getpass("> ").strip()
    os.environ["NOTION_TOKEN"] = token
    try:
        notion.request("GET", "/users/me")
    except net.NetError as e:
        raise SystemExit(f"❌ 鍵が正しくないようです（{e.status}）。コピーし直してやり直してください。")
    print("✅ Notionの鍵を確認")

    target = notion.find_target()
    if not target:
        raise SystemExit("❌ 連携に共有されたページが見つかりません。Notionで空のページを1つ作り、右上『…』→『接続』→『第二の脳』を追加して、もう一度ダブルクリックしてください。")
    kind, target_id = target
    if kind == "database":
        db_id = target_id
        print("✅ 共有されていた『第二の脳』データベースを使います")
    else:
        try:
            db_id = notion.create_database(target_id, "第二の脳")
        except net.NetError as e:
            raise SystemExit(f"❌ データベースを作れませんでした（{e.status}）。連携の権限に『コンテンツを挿入』が入っているか確認してください。")
        print("✅ Notionに『第二の脳』データベースを自動作成")

    ENV_PATH.write_text(render_env(token, db_id), encoding="utf-8")
    config.load_env()
    print("✅ 設定ファイル(.env)を作成")

    con = db.connect()
    entry, _ = pipeline.submit(con, "これは第二の脳のテストメモです。セットアップ成功の確認用。消してOKです。", "メモ")
    if entry["status"] == "saved":
        print("✅ テスト保存に成功！ Notionを開いて確認してください:", entry["notion_url"])
    else:
        print("⚠️ テスト保存は未完了:", entry["error"], "\n   原文はPC内に残っています。画面の『再送』で再実行できます。")
    if os.name == "nt" and input("\nパソコン起動時に自動で裏で動かし、デスクトップにアイコンを作ってええですか？（Enter＝はい / n＝いいえ）> ").strip().lower() != "n":
        install_windows_shortcuts()
        print("✅ 自動起動とデスクトップアイコンを設定（やめたい時は スタートアップ の second-brain.vbs を消すだけ）")
        os.startfile(startup_vbs_path())  # いま裏で起動
        import time
        time.sleep(2)
        webbrowser.open(URL)
        print("完了！ ブラウザに入力画面が開きました。この黒い画面は閉じてOKです。")
        return
    print("\n入力画面を開きます（止める時はこの黒い画面を閉じる）")
    webbrowser.open(URL)
    server.serve()


URL = "http://127.0.0.1:8765"


def vbs_content(root: Path) -> str:
    """黒い画面を出さずに裏でサーバーを動かす小さな起動スクリプト。"""
    return ('CreateObject("Wscript.Shell").Run "cmd /c cd /d ""%s"" && set PYTHONUTF8=1 && python -m app serve", 0\r\n' % root)


def startup_vbs_path() -> Path:
    return Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs/Startup/second-brain.vbs"


def install_windows_shortcuts() -> None:
    startup_vbs_path().write_text(vbs_content(config.ROOT), encoding="utf-8")
    desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
    if desktop.exists():
        (desktop / "第二の脳.url").write_text(f"[InternetShortcut]\r\nURL={URL}\r\n", encoding="utf-8")
