"""Local Ollama adapter (localhost only): chat, token logprobs (naturalness floor) and embeddings (semantic fit).

Plan 4.4: control plane never imports torch, so embeddings go through Ollama's HTTP endpoint. `keep_alive: 0` unloads the
model after each call so Whisper/demucs can use the GPU between stages. Logprobs need Ollama >= 0.12.11 (installed 0.15.6);
the shape of the response is verified by `python -m ww.cli ollama-smoke`, not assumed.
"""
from __future__ import annotations

from typing import Optional

from .client import Raw, Request

BASE = "http://127.0.0.1:11434"


class OllamaBackend:
    def __init__(self, base: str = BASE, keep_alive=0, timeout: float = 300.0):
        self.base, self.keep_alive, self.timeout = base, keep_alive, timeout

    def _post(self, path: str, body: dict) -> dict:
        import requests
        r = requests.post(self.base + path, json=body, timeout=self.timeout)
        if r.status_code >= 400:
            e = RuntimeError(f"ollama {path} -> {r.status_code}: {r.text[:200]}")
            e.status_code = r.status_code
            raise e
        return r.json()

    def call(self, req: Request) -> Raw:
        msgs = ([{"role": "system", "content": req.system}] if req.system else []) + list(req.messages)
        body: dict = {"model": req.model, "messages": msgs, "stream": False, "keep_alive": self.keep_alive,
                      "options": {"num_predict": req.max_tokens}}
        if req.temperature is not None:
            body["options"]["temperature"] = req.temperature
        if req.schema:
            body["format"] = req.schema
        d = self._post("/api/chat", body)
        return Raw(text=d.get("message", {}).get("content", ""), in_tokens=d.get("prompt_eval_count", 0) or 0,
                   out_tokens=d.get("eval_count", 0) or 0)

    def token_logprobs(self, model: str, prompt: str, max_tokens: int = 1) -> list[dict]:
        """[{token, logprob}] for the generated tokens; used on candidate bars as a naturalness floor only."""
        d = self._post("/api/generate", {"model": model, "prompt": prompt, "stream": False, "logprobs": True,
                                          "top_logprobs": 5, "keep_alive": self.keep_alive,
                                          "options": {"num_predict": max_tokens}})
        return d.get("logprobs") or d.get("response_logprobs") or []

    def embed(self, model: str, texts: list[str]) -> list[list[float]]:
        d = self._post("/api/embed", {"model": model, "input": texts, "keep_alive": self.keep_alive})
        return d.get("embeddings", [])


def available(base: str = BASE) -> Optional[list[str]]:
    """names of installed models, or None when Ollama is not running."""
    try:
        import requests
        r = requests.get(base + "/api/tags", timeout=3)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:  # noqa: BLE001
        return None
