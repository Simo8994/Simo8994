"""Prova ogni modello esposto dal proxy LiteLLM e stampa quali rispondono.

Uso:  python test_providers.py [filtro]   es. python test_providers.py groq
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("LITELLM_URL", "http://localhost:4000")
KEY = os.environ.get("LITELLM_MASTER_KEY", "")


def call(path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    flt = sys.argv[1] if len(sys.argv) > 1 else ""
    models = sorted({m["id"] for m in call("/v1/models")["data"]})
    for name in (m for m in models if flt in m):
        t = time.time()
        try:
            out = call("/v1/chat/completions", {
                "model": name,
                "messages": [{"role": "user", "content": "Rispondi solo: ok"}],
                "max_tokens": 50,
            })
            text = (out["choices"][0]["message"].get("content") or "").strip()
            print(f"OK   {name:32} {time.time() - t:5.1f}s  {text[:40]!r}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace").replace("\n", " ")
            print(f"FAIL {name:32} HTTP {e.code}  {msg[:90]}")
        except Exception as e:
            print(f"FAIL {name:32} {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
