"""入力画面（自分のPC内だけで動く。外部公開しない）。"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import db, pipeline

SOURCES = ["メモ", "アイデア", "会議メモ", "URL", "ブログ下書き", "AI会話ログ", "投資記録", "業務改善"]
MAX_BODY = 2_000_000
ALLOWED_HOSTS = ("127.0.0.1", "localhost")

PAGE = """<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>第二の脳</title><style>
body{font-family:system-ui,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#222}
textarea{width:100%;height:220px;font-size:16px;padding:10px;box-sizing:border-box}
button{font-size:16px;padding:10px 20px;cursor:pointer} .row{display:flex;gap:12px;align-items:center;margin:10px 0;flex-wrap:wrap}
#msg{margin:12px 0;padding:10px;border-radius:6px;display:none} .ok{background:#e6f6e6}.ng{background:#fde8e8}.wait{background:#fff6dd}
li{margin:6px 0} small{color:#666}</style>
<h1>🧠 第二の脳</h1>
<textarea id="t" placeholder="ここに思いついたことを貼るだけ。分類はAIがやります。（Ctrl+Enterで保存）" autofocus></textarea>
<div class="row"><select id="s">__OPTS__</select>
<label><input type="checkbox" id="n"> AIに送らない（機微メモ）</label>
<button id="b">保存する</button></div>
<div id="msg"></div><h3>最近の登録</h3><ul id="l"></ul>
<script>
const $=id=>document.getElementById(id), H={'Content-Type':'application/json','X-SB':'1'};
const L={saved:'✅保存済み',failed:'⚠️失敗（再送できます）',held:'🔒保留',pending:'⏳処理中'};
function show(c,t){const m=$('msg');m.className=c;m.textContent=t;m.style.display='block'}
async function post(p,b){const r=await fetch(p,{method:'POST',headers:H,body:JSON.stringify(b||{})});return r.json()}
async function load(){const d=await (await fetch('/api/entries')).json();const ul=$('l');ul.textContent='';
 for(const e of d.entries){const li=document.createElement('li');
  li.append(L[e.status]+' ');
  if(e.notion_url){const a=document.createElement('a');a.href=e.notion_url;a.target='_blank';a.textContent=e.title||'(開く)';li.append(a)}else li.append(e.title||e.preview);
  if(e.category){const s=document.createElement('small');s.textContent=' ['+e.category+(e.needs_review?'・要確認':'')+']';li.append(s)}
  if(e.error){const s=document.createElement('small');s.textContent=' '+e.error;li.append(s)}
  if(e.status=='failed'){const b=document.createElement('button');b.textContent='再送';b.onclick=async()=>{await post('/api/retry',{id:e.id});load()};li.append(' ',b)}
  if(e.status=='held'&&e.sensitive.length){const b=document.createElement('button');b.textContent='承認してAIに送る';b.onclick=async()=>{if(confirm('理由: '+e.sensitive.join('、')+'\\nこの内容をAIに送ります。よいですか？')){await post('/api/approve',{id:e.id});load()}};li.append(' ',b)}
  ul.append(li)}}
async function save(){const t=$('t').value;if(!t.trim())return;$('b').disabled=true;show('wait','保存中…');
 try{const d=await post('/api/add',{text:t,source_type:$('s').value,no_ai:$('n').checked});
  if(d.error)show('ng',d.error);else if(!d.is_new)show('wait','同じ内容がすでに登録済みです（重複は作りません）');
  else if(d.entry.status=='saved'){show('ok','保存しました：'+(d.entry.title||'')+(d.entry.needs_review?'（分類に自信がないので「要確認」にしました）':''));$('t').value=''}
  else {show('ng',(L[d.entry.status]||'')+' '+(d.entry.error||'')+' ※原文はこのPCに安全に残っています');$('t').value=''}
 }catch(e){show('ng','通信エラー。原文は消さずに残しています')}
 $('b').disabled=false;load()}
$('b').onclick=save;$('t').addEventListener('keydown',e=>{if(e.ctrlKey&&e.key=='Enter')save()});load();
</script></html>"""


def view(e):
    c = json.loads(e["classified"]) if e["classified"] else {}
    return {"id": e["id"], "status": e["status"], "title": c.get("title", ""), "preview": e["raw"][:30],
            "category": c.get("category", ""), "needs_review": c.get("needs_review", False),
            "notion_url": e["notion_url"], "error": e["error"],
            "sensitive": json.loads(e["sensitive_reasons"])}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # 本文を含み得るのでアクセスログは出さない
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        return self.headers.get("Host", "").split(":")[0] in ALLOWED_HOSTS  # DNS rebinding対策

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, "{}")
        if self.path == "/":
            opts = "".join(f"<option>{s}</option>" for s in SOURCES)
            return self._send(200, PAGE.replace("__OPTS__", opts), "text/html; charset=utf-8")
        if self.path == "/api/entries":
            con = db.connect()
            return self._send(200, json.dumps({"entries": [view(e) for e in db.recent(con)]}, ensure_ascii=False))
        self._send(404, "{}")

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-SB") != "1":  # 他サイトからの勝手な送信を拒否
            return self._send(403, "{}")
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return self._send(413, json.dumps({"error": "長すぎます（2MBまで）"}))
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
            con = db.connect()
            if self.path == "/api/add":
                entry, is_new = pipeline.submit(con, body.get("text", ""), body.get("source_type", "メモ"),
                                                bool(body.get("no_ai")))
                out = {"is_new": is_new, "entry": view(entry)}
            elif self.path == "/api/retry":
                if body.get("id"):
                    pipeline.process(con, int(body["id"]))
                else:
                    pipeline.retry_all(con)
                out = {"ok": True}
            elif self.path == "/api/approve":
                pipeline.process(con, int(body["id"]), approve_ai=True)
                out = {"ok": True}
            else:
                return self._send(404, "{}")
            self._send(200, json.dumps(out, ensure_ascii=False))
        except ValueError as e:
            self._send(400, json.dumps({"error": str(e)}, ensure_ascii=False))
        except Exception as e:
            self._send(500, json.dumps({"error": f"{type(e).__name__}"}, ensure_ascii=False))


def serve(port=8765):
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)  # 127.0.0.1 = このPCからしか見えない
    print(f"起動しました → ブラウザで http://127.0.0.1:{port} を開いてください（止める時は Ctrl+C）")
    srv.serve_forever()
