"""AIへの問い合わせ。OpenAI と Ollama（店内ローカルAI）を環境変数で切り替える。"""
import json

from . import config
from .net import http_json


def complete_json(system: str, user: str) -> dict:
    provider = config.get("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        base = config.get("OLLAMA_URL", "http://127.0.0.1:11434")
        out = http_json(f"{base}/api/chat", body={
            "model": config.get("OLLAMA_MODEL", "llama3.1"), "stream": False, "format": "json",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            timeout=300)
        return json.loads(out["message"]["content"])
    key = config.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY が未設定です（.env を確認）")
    out = http_json("https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"}, body={
        "model": config.get("OPENAI_MODEL", "gpt-4o-mini"), "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    return json.loads(out["choices"][0]["message"]["content"])
