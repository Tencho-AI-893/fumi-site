import json
import os
import tempfile
import unittest
from unittest import mock

os.environ["SB_DATA_DIR"] = tempfile.mkdtemp()
os.environ["NOTION_DATABASE_ID"] = "dbid"
os.environ["NOTION_TOKEN"] = "x"

from app import classify, db, notion, pipeline, safety  # noqa: E402


def fake_ai(conf=0.9, cat="SM.カルマ経営"):
    return {"title": "求人サイト構想", "summary": "要約", "category": cat, "tags": ["求人", "a,b"],
            "project": "", "confidence": conf}


class Base(unittest.TestCase):
    def setUp(self):
        self.con = db.connect()
        self.con.execute("DELETE FROM entries")
        self.con.commit()
        self.pages = []

        def fake_request(method, path, body=None):
            if path == "/pages":
                self.pages.append(body)
                return {"id": f"p{len(self.pages)}", "url": "https://notion.so/p"}
            return {}
        self.p1 = mock.patch.object(notion, "request", fake_request)
        self.p1.start()
        self.addCleanup(self.p1.stop)


class Tests(Base):
    def test_happy_path_keeps_raw_and_saves(self):
        raw = "求人サイトを作りたい。" * 500  # 長文 → 複数ブロック
        with mock.patch("app.llm.complete_json", return_value=fake_ai()):
            e, new = pipeline.submit(self.con, raw)
        self.assertTrue(new)
        self.assertEqual(e["status"], "saved")
        body = self.pages[0]
        text = "".join(b["paragraph"]["rich_text"][0]["text"]["content"] for b in body["children"][1:])
        self.assertEqual(text, raw)  # 原文が欠けない
        self.assertEqual(body["properties"]["カテゴリー"]["select"]["name"], "SM.カルマ経営")
        self.assertEqual(body["properties"]["タグ"]["multi_select"][1]["name"], "a、b")  # カンマ除去

    def test_low_confidence_goes_to_review(self):
        with mock.patch("app.llm.complete_json", return_value=fake_ai(conf=0.3)):
            pipeline.submit(self.con, "なんかよく分からないメモ")
        props = self.pages[0]["properties"]
        self.assertEqual(props["カテゴリー"]["select"]["name"], "要確認")
        self.assertTrue(props["要確認"]["checkbox"])
        self.assertEqual(props["AI推定"]["rich_text"][0]["text"]["content"], "SM.カルマ経営")

    def test_unknown_category_is_review(self):
        c = classify.normalize({"category": "でたらめ", "confidence": 0.99}, ["A"], "x")
        self.assertTrue(c["needs_review"])

    def test_duplicate_not_registered_twice(self):
        with mock.patch("app.llm.complete_json", return_value=fake_ai()):
            pipeline.submit(self.con, "同じ メモ")
            _, new = pipeline.submit(self.con, "同じ  メモ")
        self.assertFalse(new)
        self.assertEqual(len(self.pages), 1)

    def test_notion_failure_keeps_raw_and_retry_skips_ai(self):
        calls = {"ai": 0}

        def ai(*a):
            calls["ai"] += 1
            return fake_ai()
        good = notion.request
        notion.request = mock.Mock(side_effect=RuntimeError("down"))
        with mock.patch("app.llm.complete_json", ai):
            e, _ = pipeline.submit(self.con, "大事なメモ")
            self.assertEqual(e["status"], "failed")
            self.assertEqual(e["raw"], "大事なメモ")
            notion.request = good
            res = pipeline.retry_all(self.con)
        self.assertEqual(res[0]["status"], "saved")
        self.assertEqual(calls["ai"], 1)  # AIは1回だけ（課金の二重払いなし）
        self.assertEqual(len(self.pages), 1)

    def test_retry_is_idempotent(self):
        with mock.patch("app.llm.complete_json", return_value=fake_ai()):
            e, _ = pipeline.submit(self.con, "メモ")
        pipeline.process(self.con, e["id"])
        self.assertEqual(len(self.pages), 1)

    def test_sensitive_never_sent_to_ai_and_held(self):
        with mock.patch("app.llm.complete_json", side_effect=AssertionError("AIに送った!")):
            e, _ = pipeline.submit(self.con, "Aさんの電話 090-1234-5678")
        self.assertEqual(e["status"], "held")
        self.assertEqual(self.pages, [])

    def test_sensitive_goes_to_separate_db_without_ai(self):
        with mock.patch.dict(os.environ, {"NOTION_SENSITIVE_DATABASE_ID": "secretdb"}), \
                mock.patch("app.llm.complete_json", side_effect=AssertionError("AIに送った!")):
            e, _ = pipeline.submit(self.con, "口座番号は1234567")
        self.assertEqual(e["status"], "saved")
        self.assertEqual(self.pages[0]["parent"], {"database_id": "secretdb"})
        self.assertNotIn("口座", self.pages[0]["properties"]["タイトル"]["title"][0]["text"]["content"])

    def test_approved_sensitive_can_use_ai(self):
        with mock.patch("app.llm.complete_json", return_value=fake_ai()):
            e, _ = pipeline.submit(self.con, "パスワード運用ルールを決めたい")
            self.assertEqual(e["status"], "held")
            e = pipeline.process(self.con, e["id"], approve_ai=True)
        self.assertEqual(e["status"], "saved")

    def test_no_ai_checkbox(self):
        with mock.patch("app.llm.complete_json", side_effect=AssertionError("AIに送った!")):
            e, _ = pipeline.submit(self.con, "ふつうの文章", no_ai=True)
        self.assertEqual(e["status"], "held")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            pipeline.submit(self.con, "   ")

    def test_safety_detects(self):
        self.assertTrue(safety.detect_sensitive("a@b.com"))
        self.assertFalse(safety.detect_sensitive("来月の売上目標を考える"))


class ServerTests(Base):
    def test_http_rules(self):
        import threading
        import urllib.error
        import urllib.request
        from http.server import ThreadingHTTPServer
        from app.server import Handler
        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        base = f"http://127.0.0.1:{srv.server_port}"

        def post(h):
            r = urllib.request.Request(base + "/api/add", json.dumps({"text": "テスト"}).encode(), h, method="POST")
            return urllib.request.urlopen(r)
        with self.assertRaises(urllib.error.HTTPError) as cm:
            post({"Content-Type": "application/json"})  # X-SB無し = 拒否
        self.assertEqual(cm.exception.code, 403)
        with mock.patch("app.llm.complete_json", return_value=fake_ai()):
            out = json.load(post({"Content-Type": "application/json", "X-SB": "1"}))
        self.assertEqual(out["entry"]["status"], "saved")
        self.assertIn("第二の脳", urllib.request.urlopen(base + "/").read().decode())


if __name__ == "__main__":
    unittest.main()
