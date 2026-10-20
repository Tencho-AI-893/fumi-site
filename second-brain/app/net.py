"""外部通信の共通部品（標準ライブラリだけ。429/5xxは待って再試行）。"""
import json
import time
import urllib.error
import urllib.request


class NetError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status


def http_json(url, method="POST", headers=None, body=None, timeout=60, retries=3):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:200]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = float(e.headers.get("Retry-After") or 2 ** attempt)
                time.sleep(min(wait, 30))
                continue
            raise NetError(e.code, msg) from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise NetError(0, f"接続できません: {getattr(e, 'reason', e)}") from None
