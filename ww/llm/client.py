"""The only way ww talks to a model (R12). Routes by model name, enforces budgets, retries, caches, validates, ledgers.

  deepseek-flash / deepseek-v4-pro (ds-flash, ds-pro) -> DeepSeek API  (needs DEEPSEEK_API_KEY; uses `requests`)
  claude-* (haiku, sonnet, opus, fable)               -> Anthropic API when ANTHROPIC_API_KEY is set, else the logged-in
                                                         `claude` CLI headless (no key; WW_CLAUDE_VIA=api|cli forces one)
  stub*                                               -> deterministic offline backend for tests
  anything else                                       -> local Ollama (ww.llm.local)

`private=True` is the calibration mode: no response cache, no bodies stored anywhere, hashes only in the ledger, and ONLY
providers Joe has approved for the original's lines (anthropic and deepseek, approved 13 Oct 2026; narrow with
WW_PRIVATE_ALLOW=...). Only ww.calib may construct a private client.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from .. import config
from . import pricing
from .ledger import Ledger
from .limiter import AdaptiveLimiter
from .schema import validate

RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}
# Joe, 13 Oct 2026 (chat): "Allow DeepSeek for calibration" - the original's lines may go to Anthropic OR DeepSeek in private
# (calibration) mode only; never into writer prompts, never cached, never logged beyond hashes. ollama never leaves the machine.
PRIVATE_ALLOW_DEFAULT = ("anthropic", "deepseek", "ollama", "stub")


@dataclass
class Request:
    model: str
    messages: list
    system: str = ""
    max_tokens: int = 2000
    effort: Optional[str] = None       # None/none = no thinking; low | medium | high | max
    schema: Optional[dict] = None      # JSON schema: JSON mode + local validation + one repair re-ask
    temperature: Optional[float] = None
    cache_system: bool = False         # Anthropic only; DeepSeek caches prefixes automatically
    stage: str = "adhoc"
    scope: str = "run"

    def key(self) -> str:
        body = {"m": pricing.resolve(self.model), "s": self.system, "msg": self.messages, "mt": self.max_tokens,
                "e": self.effort, "sc": self.schema, "t": self.temperature}
        return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass
class Raw:
    text: str
    in_tokens: int = 0       # prompt tokens NOT served from cache
    out_tokens: int = 0
    cache_read: int = 0      # prompt tokens served from cache
    cache_write: int = 0


@dataclass
class Result:
    text: str
    parsed: Any = None
    model: str = ""
    in_tokens: int = 0
    out_tokens: int = 0
    cache_read: int = 0
    usd: float = 0.0
    cached_hit: bool = False
    schema_errors: list = field(default_factory=list)


def extract_json(text: str) -> Any:
    """first complete JSON object/array in text (tolerates code fences and chatter); None if there is none."""
    t = re.sub(r"```(?:json)?", "", text)
    for opener, closer in (("{", "}"), ("[", "]")):
        start = t.find(opener)
        while start != -1:
            depth, in_str, esc = 0, False, False
            for i in range(start, len(t)):
                ch = t[i]
                if in_str:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        in_str = False
                elif ch == '"':
                    in_str = True
                elif ch == opener:
                    depth += 1
                elif ch == closer:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(t[start:i + 1])
                        except json.JSONDecodeError:
                            break
            start = t.find(opener, start + 1)
    return None


class StubBackend:
    """offline, deterministic. handlers: stage -> fn(Request) -> str. Default returns '{}'."""
    def __init__(self, handlers: Optional[dict] = None):
        self.handlers = handlers or {}
        self.calls: list[Request] = []

    def call(self, req: Request) -> Raw:
        self.calls.append(req)
        fn = self.handlers.get(req.stage)
        text = fn(req) if fn else "{}"
        n_in = sum(len(m["content"]) for m in req.messages) // 4 + len(req.system) // 4
        return Raw(text=text, in_tokens=n_in, out_tokens=max(1, len(text) // 4))


class TransientAPIError(RuntimeError):
    def __init__(self, msg: str, status_code: int = 503):
        super().__init__(msg)
        self.status_code = status_code


def parse_sse(lines) -> tuple[str, dict]:
    """accumulate content and the final usage object from an SSE chat-completions stream (keep-alive comments ignored).
    The last finish_reason is exposed as usage['_finish_reason']."""
    text, usage, finish = [], {}, None
    for raw in lines:
        if not raw:
            continue
        line = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            ch = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if ch.get("usage"):
            usage = ch["usage"]
        for c in ch.get("choices") or []:
            piece = (c.get("delta") or {}).get("content")
            if piece:
                text.append(piece)
            if c.get("finish_reason"):
                finish = c["finish_reason"]
    usage = dict(usage)
    usage["_finish_reason"] = finish
    return "".join(text), usage


class DeepSeekBackend:
    """OpenAI-style chat completions at https://api.deepseek.com (verified against api-docs.deepseek.com, 12 Oct 2026).

    thinking: Request.effort None/'none' -> {"thinking":{"type":"disabled"}} (cheap reader/seed calls, temperature honoured);
    low -> enabled/low; medium|high -> enabled/high; max -> enabled/max (temperature is IGNORED in thinking mode).
    Structured output: response_format json_object (valid JSON, NOT schema-enforced) + the schema pasted into the system
    prompt; ww.llm validates and re-asks once. JSON mode can return empty content -> treated as transient and retried."""
    BASE = "https://api.deepseek.com"
    EFFORT = {"low": "low", "medium": "high", "high": "high", "max": "max"}

    def __init__(self, api_key: Optional[str] = None, base: Optional[str] = None, post: Optional[Callable] = None,
                 timeout: float = 620.0):
        self.key = api_key or config.secret("DEEPSEEK_API_KEY")
        self.base = (base or self.BASE).rstrip("/")
        self.timeout = timeout
        self._post = post

    def body(self, req: Request) -> dict:
        system = req.system
        if req.schema:
            system = (system + "\n\n" if system else "") + (
                "Respond with ONE JSON object only (valid json, no prose, no code fences) matching this JSON schema:\n"
                + json.dumps(req.schema, ensure_ascii=False))
        msgs = ([{"role": "system", "content": system}] if system else []) + list(req.messages)
        b: dict = {"model": pricing.resolve(req.model), "messages": msgs, "max_tokens": req.max_tokens, "stream": False}
        if req.effort not in (None, "none"):  # long silent thinking calls get cut by intermediaries; stream them
            b["stream"] = True
            b["stream_options"] = {"include_usage": True}
        if req.effort not in (None, "none"):
            # reasoning tokens are billed AND counted against max_tokens: a 6k cap let the model think its way to an empty reply (13 Oct)
            b["max_tokens"] = req.max_tokens + {"low": 6000, "medium": 12000, "high": 20000, "max": 40000}.get(req.effort, 20000)
        if req.effort in (None, "none"):
            b["thinking"] = {"type": "disabled"}
            if req.temperature is not None:
                b["temperature"] = req.temperature
        else:
            b["thinking"] = {"type": "enabled"}
            b["reasoning_effort"] = self.EFFORT.get(req.effort, "high")
        if req.schema:
            b["response_format"] = {"type": "json_object"}
        return b

    def call(self, req: Request) -> Raw:
        if not self.key and self._post is None:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")
        body = self.body(req)
        if body.get("stream") and self._post is None:
            import requests
            r = requests.post(self.base + "/chat/completions", json=body, timeout=self.timeout, stream=True,
                              headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
            if r.status_code >= 400:
                e = RuntimeError(f"deepseek {r.status_code}: {r.text[:200]}")
                e.status_code = r.status_code
                raise e
            text, u = parse_sse(r.iter_lines())
            d = {"usage": u}
            msg = {"content": text}
        else:
            if self._post is not None:
                r = self._post(self.base + "/chat/completions", body)
            else:
                import requests
                r = requests.post(self.base + "/chat/completions", json=body, timeout=self.timeout,
                                  headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
            if r.status_code >= 400:
                e = RuntimeError(f"deepseek {r.status_code}: {str(getattr(r, 'text', ''))[:200]}")
                e.status_code = r.status_code
                raise e
            d = r.json()
            msg = (d.get("choices") or [{}])[0].get("message", {})
        text = msg.get("content") or ""
        u = d.get("usage", {}) or {}
        raw = Raw(text=text, in_tokens=u.get("prompt_cache_miss_tokens", u.get("prompt_tokens", 0)) or 0,
                  out_tokens=u.get("completion_tokens", 0) or 0, cache_read=u.get("prompt_cache_hit_tokens", 0) or 0)
        if req.schema and not text.strip():
            fr = u.get("_finish_reason")
            e = TransientAPIError(f"deepseek returned empty content in JSON mode (finish_reason={fr}, out_tokens={raw.out_tokens}): "
                                  f"{'raise max_tokens/lower effort' if fr == 'length' else 'retry once'}")
            e.usage = raw          # the tokens were billed even though the reply was empty
            e.retry_once = True
            raise e
        return raw


class AnthropicBackend:
    """optional. Structured-output / effort shapes follow the research run's reading of the docs (output_config via
    extra_body) and are VERIFIED ONLY by a live call (`python -m ww.cli llm-smoke`)."""
    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("pip install anthropic") from e
        key = api_key or config.secret("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic(api_key=key)

    def call(self, req: Request) -> Raw:
        kwargs: dict = {"model": pricing.resolve(req.model), "max_tokens": req.max_tokens, "messages": req.messages}
        if req.system:
            kwargs["system"] = ([{"type": "text", "text": req.system, "cache_control": {"type": "ephemeral"}}]
                                if req.cache_system else req.system)
        if req.temperature is not None:
            kwargs["temperature"] = req.temperature
        oc: dict = {}
        if req.effort and req.effort != "none":
            oc["effort"] = req.effort
        if req.schema:
            oc["format"] = {"type": "json_schema", "schema": req.schema}
        if oc:
            kwargs["extra_body"] = {"output_config": oc}
        resp = self.client.messages.create(**kwargs)
        text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
        u = resp.usage
        return Raw(text=text, in_tokens=getattr(u, "input_tokens", 0) or 0, out_tokens=getattr(u, "output_tokens", 0) or 0,
                   cache_read=getattr(u, "cache_read_input_tokens", 0) or 0,
                   cache_write=getattr(u, "cache_creation_input_tokens", 0) or 0)


class ClaudeCLIBackend:
    """Claude through the logged-in `claude` CLI in headless mode (`claude -p`): no API key needed. Joe, 15 Oct 2026: "Why do I
    need an API key? I should be able to use claude too". Used for claude-* models when ANTHROPIC_API_KEY is unset.
    Tools, MCP servers, settings, hooks and session files are all off, and it runs in an empty temp dir, so the reader never
    sees this repo's CLAUDE.md or knows who wrote the bars. Schema -> --json-schema (validated by the CLI, returned as
    structured_output). Probe 15 Oct: ~5 s and ~$0.0004 per small Haiku call (total_cost_usd is notional on a subscription)."""
    EFFORT = {"low": "low", "medium": "medium", "high": "high", "max": "max"}

    def __init__(self, exe: Optional[str] = None, run: Optional[Callable] = None, timeout: float = 300.0):
        import shutil
        self.exe = exe or shutil.which("claude")
        self._run = run
        self.timeout = timeout
        if not self.exe and run is None:
            raise RuntimeError("no ANTHROPIC_API_KEY and no `claude` CLI on PATH")

    def argv(self, req: Request) -> list:
        a = [self.exe or "claude", "-p", "--model", pricing.resolve(req.model), "--output-format", "json", "--tools", "",
             "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "",
             "--system-prompt", req.system or "You are a careful reader."]
        if req.effort and req.effort != "none":
            a += ["--effort", self.EFFORT.get(req.effort, "low")]
        if req.schema:
            a += ["--json-schema", json.dumps(req.schema, ensure_ascii=False)]
        return a

    @staticmethod
    def prompt(req: Request) -> str:
        if len(req.messages) == 1:
            return req.messages[0]["content"]
        return "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in req.messages)

    def call(self, req: Request) -> Raw:
        import subprocess
        import tempfile
        argv, stdin = self.argv(req), self.prompt(req)
        if self._run is not None:
            out = self._run(argv, stdin)
        else:
            with tempfile.TemporaryDirectory() as cwd:
                p = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=self.timeout, cwd=cwd)
            if p.returncode != 0 and not p.stdout.strip():
                raise TransientAPIError(f"claude cli exit {p.returncode}: {p.stderr[:200]}")
            out = p.stdout
        try:
            d = json.loads(out)
        except json.JSONDecodeError as e:
            raise TransientAPIError(f"claude cli returned non-JSON: {out[:200]}") from e
        if d.get("is_error"):
            e = RuntimeError(f"claude cli error: {str(d.get('result'))[:200]}")
            e.status_code = d.get("api_error_status") or 500
            raise e
        so = d.get("structured_output")
        text = json.dumps(so, ensure_ascii=False) if so is not None else (d.get("result") or "")
        u = d.get("usage") or {}
        return Raw(text=text, in_tokens=u.get("input_tokens", 0) or 0, out_tokens=u.get("output_tokens", 0) or 0,
                   cache_read=u.get("cache_read_input_tokens", 0) or 0,
                   cache_write=u.get("cache_creation_input_tokens", 0) or 0)


def private_allowlist() -> tuple:
    env = os.environ.get("WW_PRIVATE_ALLOW")
    return tuple(x.strip() for x in env.split(",") if x.strip()) if env else PRIVATE_ALLOW_DEFAULT


@dataclass
class LLM:
    ledger: Ledger
    stub: Optional[StubBackend] = None
    cache_dir: Path = field(default_factory=lambda: config.EVAL_DIR / "cache")
    private: bool = False
    retries: int = 6
    sleep: Callable[[float], None] = time.sleep
    limiter: AdaptiveLimiter = field(default_factory=lambda: AdaptiveLimiter(int(os.environ.get("WW_MAX_CONCURRENCY", "8"))))
    _anthropic: Any = field(default=None, repr=False)
    _deepseek: Any = field(default=None, repr=False)
    _ollama: Any = field(default=None, repr=False)

    def _backend(self, model: str):
        prov = pricing.provider(model)
        if prov == "stub":
            if self.stub is None:
                raise RuntimeError("stub model requested but no StubBackend supplied")
            return self.stub
        if prov == "anthropic":
            if self._anthropic is None:   # API when a key is set, else the logged-in claude CLI (Joe, 15 Oct)
                via = os.environ.get("WW_CLAUDE_VIA") or ("api" if config.secret("ANTHROPIC_API_KEY") else "cli")
                self._anthropic = AnthropicBackend() if via == "api" else ClaudeCLIBackend()
            return self._anthropic
        if prov == "deepseek":
            if self._deepseek is None:
                self._deepseek = DeepSeekBackend()
            return self._deepseek
        if self._ollama is None:
            from .local import OllamaBackend
            self._ollama = OllamaBackend()
        return self._ollama

    # ---- cache ---------------------------------------------------------------------------------------------
    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _cache_get(self, key: str) -> Optional[dict]:
        p = self._cache_path(key)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
        return None

    def _cache_put(self, key: str, raw: Raw, model: str) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_path(key).write_text(json.dumps({"model": model, "text": raw.text, "in": raw.in_tokens,
                                                     "out": raw.out_tokens}, ensure_ascii=False), encoding="utf-8")

    # ---- one billable round trip, with retry ----------------------------------------------------------------
    def _roundtrip(self, req: Request, model: str, sha: str) -> tuple[Raw, float]:
        backend = self._backend(req.model)
        for attempt in range(self.retries + 1):
            try:
                with self.limiter:
                    raw = backend.call(req)
                break
            except Exception as e:  # noqa: BLE001 - classified below
                status = getattr(e, "status_code", None)
                name = type(e).__name__.lower()
                msg = str(e)
                m = re.search(r"concurrency limit of (\d+)", msg)
                if status == 429 and m:      # DeepSeek: limit depends on balance; obey it, and do not burn a retry on it
                    self.limiter.shrink_to(int(m.group(1)))
                    self.sleep(1.0 + random.random())
                    if attempt < self.retries * 3:
                        continue
                transient = status in RETRYABLE_STATUS or any(s in name or s in msg.lower() for s in ("ratelimit", "overload", "timeout", "connection", "transient", "chunkedencoding", "ended prematurely", "incompleteread", "remotedisconnected", "protocolerror"))
                used = getattr(e, "usage", None)
                if used is not None:   # bill what was spent even though the reply was unusable
                    self.ledger.record(scope=req.scope, stage=req.stage, model=model, prompt_sha=sha, private=self.private,
                                       in_tokens=used.in_tokens, out_tokens=used.out_tokens, cache_read=used.cache_read,
                                       usd=pricing.cost_usd(model, used.in_tokens, used.out_tokens, used.cache_read),
                                       error=f"{type(e).__name__}: {msg[:120]}")
                if getattr(e, "retry_once", False) and attempt >= 1:
                    transient = False
                if not transient or attempt == self.retries:
                    if used is None:
                        self.ledger.record(scope=req.scope, stage=req.stage, model=model, prompt_sha=sha, private=self.private,
                                           error=f"{type(e).__name__}: {msg[:160]}")
                    raise
                self.sleep(min(60.0, 2.0 ** attempt) * (0.5 + random.random()))
        usd = pricing.cost_usd(model, raw.in_tokens, raw.out_tokens, raw.cache_read, raw.cache_write)
        self.ledger.record(scope=req.scope, stage=req.stage, model=model, in_tokens=raw.in_tokens, out_tokens=raw.out_tokens,
                           cache_read=raw.cache_read, usd=usd, prompt_sha=sha, private=self.private,
                           response_sha=hashlib.sha256(raw.text.encode("utf-8")).hexdigest()[:16])
        return raw, usd

    # ---- the call ------------------------------------------------------------------------------------------
    def complete(self, req: Request, *, use_cache: bool = True) -> Result:
        model = pricing.resolve(req.model)
        if self.private and pricing.provider(model) not in private_allowlist():
            raise PermissionError(f"private (calibration) mode may not send the original to provider "
                                  f"'{pricing.provider(model)}'; allowed: {private_allowlist()}. "
                                  f"Joe must approve a provider via WW_PRIVATE_ALLOW first.")
        cacheable = use_cache and not self.private and req.temperature in (None, 0, 0.0)
        key = req.key()
        sha = key[:16]
        if cacheable:
            hit = self._cache_get(key)
            if hit is not None:
                self.ledger.record(scope=req.scope, stage=req.stage, model=model, cached_hit=True, prompt_sha=sha)
                parsed = extract_json(hit["text"]) if req.schema else None
                return Result(text=hit["text"], parsed=parsed, model=model, in_tokens=hit.get("in", 0),
                              out_tokens=hit.get("out", 0), cached_hit=True,
                              schema_errors=validate(parsed, req.schema) if req.schema and parsed is not None else [])
        self.ledger.preflight(req.scope)
        raw, usd = self._roundtrip(req, model, sha)
        res = Result(text=raw.text, model=model, in_tokens=raw.in_tokens, out_tokens=raw.out_tokens,
                     cache_read=raw.cache_read, usd=usd)
        if req.schema:
            res.parsed = extract_json(raw.text)
            res.schema_errors = validate(res.parsed, req.schema) if res.parsed is not None else ["no JSON found in reply"]
            if res.schema_errors:  # one repair re-ask, with the error text; both calls are ledgered
                fix = Request(model=req.model, system=req.system, max_tokens=req.max_tokens, effort=req.effort,
                              schema=req.schema, temperature=req.temperature, stage=req.stage + ":repair", scope=req.scope,
                              messages=list(req.messages) + [
                                  {"role": "assistant", "content": raw.text[:4000]},
                                  {"role": "user", "content": "That reply was invalid: " + "; ".join(res.schema_errors[:6])
                                   + ". Reply again with ONLY the corrected JSON object."}])
                self.ledger.preflight(req.scope)
                raw2, usd2 = self._roundtrip(fix, model, sha)
                parsed2 = extract_json(raw2.text)
                errs2 = validate(parsed2, req.schema) if parsed2 is not None else ["no JSON found in reply"]
                res = Result(text=raw2.text, parsed=parsed2, model=model, in_tokens=res.in_tokens + raw2.in_tokens,
                             out_tokens=res.out_tokens + raw2.out_tokens, cache_read=res.cache_read + raw2.cache_read,
                             usd=usd + usd2, schema_errors=errs2)
                raw = raw2
        if cacheable and not res.schema_errors:
            self._cache_put(key, raw, model)
        return res


def selftest() -> tuple[bool, str]:
    import datetime as dt
    import tempfile
    problems: list[str] = []

    def check(c: bool, m: str) -> None:
        if not c:
            problems.append(m)

    with tempfile.TemporaryDirectory() as td:
        led = Ledger(run_id="selftest", directory=Path(td) / "ledger")
        stub = StubBackend({"echo": lambda r: '```json\n{"ok": true, "n": [1, 2]}\n```'})
        llm = LLM(ledger=led, stub=stub, cache_dir=Path(td) / "cache", sleep=lambda s: None)
        schema = {"type": "object", "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}
        req = Request(model="stub-1", messages=[{"role": "user", "content": "hi"}], stage="echo", schema=schema)
        r1 = llm.complete(req)
        check(r1.parsed == {"ok": True, "n": [1, 2]} and not r1.schema_errors, f"json extraction: {r1.parsed} {r1.schema_errors}")
        r2 = llm.complete(req)
        check(r2.cached_hit and len(stub.calls) == 1, "second identical call must be a cache hit with no backend call")
        check(led.totals()["calls"] == 1 and led.totals()["cached_hits"] == 1, f"ledger totals: {led.totals()}")
        # schema repair: first reply invalid, second valid
        seq = iter(['{"nope": 1}', '{"ok": true}'])
        s2 = StubBackend({"fix": lambda r: next(seq), "fix:repair": lambda r: next(seq)})
        l2 = LLM(ledger=Ledger(run_id="fix", persist=False), stub=s2, cache_dir=Path(td) / "c5")
        rf = l2.complete(Request(model="stub-1", messages=[{"role": "user", "content": "x"}], stage="fix", schema=schema))
        check(rf.parsed == {"ok": True} and not rf.schema_errors and len(s2.calls) == 2, f"repair re-ask failed: {rf}")
        # private mode: no cache, no bodies on disk, provider allowlist
        pled = Ledger(run_id="priv", directory=Path(td) / "ledger")
        pllm = LLM(ledger=pled, stub=StubBackend({"echo": lambda r: "SECRET-RESPONSE"}), cache_dir=Path(td) / "pcache", private=True)
        pllm.complete(Request(model="stub-1", messages=[{"role": "user", "content": "SECRET-PROMPT"}], stage="echo"))
        pllm.complete(Request(model="stub-1", messages=[{"role": "user", "content": "SECRET-PROMPT"}], stage="echo"))
        check(len(pllm.stub.calls) == 2, "private mode must never cache")
        blob = "".join(p.read_text(encoding="utf-8") for p in Path(td).rglob("*") if p.is_file())
        check("SECRET-PROMPT" not in blob and "SECRET-RESPONSE" not in blob, "private mode leaked a body to disk")
        import os
        old_allow = os.environ.get("WW_PRIVATE_ALLOW")
        os.environ["WW_PRIVATE_ALLOW"] = "anthropic"
        try:
            pllm.complete(Request(model="deepseek-flash", messages=[{"role": "user", "content": "x"}]))
            check(False, "private mode must refuse a provider outside WW_PRIVATE_ALLOW")
        except PermissionError:
            pass
        finally:
            if old_allow is None:
                os.environ.pop("WW_PRIVATE_ALLOW", None)
            else:
                os.environ["WW_PRIVATE_ALLOW"] = old_allow
        check("deepseek" in private_allowlist(), "DeepSeek is approved for calibration by default (Joe, 13 Oct)")
        # transient retry vs permanent failure
        class Flaky:
            def __init__(self): self.n = 0
            def call(self, req):
                self.n += 1
                if self.n < 3:
                    e = RuntimeError("busy"); e.status_code = 529; raise e
                return Raw(text="fine", in_tokens=1, out_tokens=1)
        flaky = Flaky()
        llm2 = LLM(ledger=Ledger(run_id="r2", persist=False), stub=flaky, cache_dir=Path(td) / "c2", sleep=lambda s: None)
        check(llm2.complete(Request(model="stub-x", messages=[{"role": "user", "content": "x"}])).text == "fine" and flaky.n == 3,
              "transient 529 must be retried")
        class Broken:
            def call(self, req):
                e = RuntimeError("bad request"); e.status_code = 400; raise e
        llm3 = LLM(ledger=Ledger(run_id="r3", persist=False), stub=Broken(), cache_dir=Path(td) / "c3", sleep=lambda s: None)
        try:
            llm3.complete(Request(model="stub-x", messages=[{"role": "user", "content": "x"}]))
            check(False, "permanent 400 must raise")
        except RuntimeError:
            pass
        from .ledger import Budget, BudgetExceeded
        bl = Ledger(run_id="b", persist=False, budgets={"sec": Budget(max_calls=2)})
        bllm = LLM(ledger=bl, stub=StubBackend(), cache_dir=Path(td) / "c4")
        try:
            for i in range(3):
                bllm.complete(Request(model="stub-x", messages=[{"role": "user", "content": str(i)}], scope="sec"))
            check(False, "call ceiling must abort the third call")
        except BudgetExceeded:
            pass
        # DeepSeek request shape + usage mapping (fake HTTP)
        sent = []
        class FakeResp:
            status_code = 200
            def json(self_inner):
                return {"choices": [{"message": {"content": '{"ok": true}'}}],
                        "usage": {"prompt_cache_hit_tokens": 800, "prompt_cache_miss_tokens": 200, "completion_tokens": 50}}
        def fake_post(url, body):
            sent.append((url, body)); return FakeResp()
        ds = DeepSeekBackend(post=fake_post)
        raw = ds.call(Request(model="ds-flash", system="sys", messages=[{"role": "user", "content": "hi"}], schema=schema, temperature=0.7))
        b = sent[0][1]
        check(sent[0][0].endswith("/chat/completions") and b["model"] == "deepseek-flash", f"deepseek url/model: {sent[0][0]} {b['model']}")
        check(b["thinking"] == {"type": "disabled"} and b["temperature"] == 0.7 and b["response_format"] == {"type": "json_object"},
              f"deepseek body (no effort): {b}")
        check("json" in b["messages"][0]["content"].lower(), "JSON mode needs the word json in the prompt")
        check((raw.in_tokens, raw.cache_read, raw.out_tokens) == (200, 800, 50), f"usage mapping: {raw}")
        ds.call(Request(model="ds-pro", messages=[{"role": "user", "content": "hi"}], effort="max", temperature=0.7))
        b2 = sent[1][1]
        check(b2["thinking"] == {"type": "enabled"} and b2["reasoning_effort"] == "max" and "temperature" not in b2,
              f"thinking body must drop temperature: {b2}")
        sse = [b": keep-alive", b'data: {"choices":[{"delta":{"content":"{\\"ok\\""}}]}', b'data: {"choices":[{"delta":{"content":": true}"}}]}',
               b'data: {"choices":[],"usage":{"prompt_cache_miss_tokens":5,"prompt_cache_hit_tokens":2,"completion_tokens":9}}', b"data: [DONE]"]
        st, su = parse_sse(sse)
        check(st == '{"ok": true}' and su.get("completion_tokens") == 9, f"SSE parse: {st!r} {su}")
        # claude CLI backend: argv shape + structured_output / usage mapping (fake subprocess, no network)
        seen = []
        def fake_run(argv, stdin):
            seen.append((argv, stdin))
            return json.dumps({"is_error": False, "result": "ignored", "structured_output": {"ok": True},
                               "usage": {"input_tokens": 3, "output_tokens": 7, "cache_read_input_tokens": 11,
                                         "cache_creation_input_tokens": 13}})
        cli = ClaudeCLIBackend(run=fake_run)
        rc = cli.call(Request(model="haiku", system="S", messages=[{"role": "user", "content": "bars"}], schema=schema,
                              effort="low"))
        av = seen[0][0]
        check(av[av.index("--model") + 1] == "claude-haiku-5-5" and av[av.index("--tools") + 1] == ""
              and av[av.index("--effort") + 1] == "low" and "--json-schema" in av and seen[0][1] == "bars",
              f"claude cli argv: {av}")
        check(json.loads(rc.text) == {"ok": True} and (rc.in_tokens, rc.out_tokens, rc.cache_read, rc.cache_write) == (3, 7, 11, 13),
              f"claude cli mapping: {rc}")
        # pricing arithmetic
        check(abs(pricing.cost_usd("sonnet", 1_000_000, 1_000_000) - 12.0) < 1e-9, "sonnet price")
        off = dt.datetime(2026, 10, 10, 12, 0, tzinfo=dt.timezone.utc)   # a Saturday
        peak = dt.datetime(2026, 10, 12, 7, 0, tzinfo=dt.timezone.utc)   # Monday 07:00 UTC
        check(not pricing.is_deepseek_peak(off) and pricing.is_deepseek_peak(peak), "peak window")
        check(abs(pricing.cost_usd("ds-flash", 1_000_000, 1_000_000, when=off) - 0.75) < 1e-9, "ds-flash off-peak 0.15+0.60")
        check(abs(pricing.cost_usd("ds-flash", 1_000_000, 1_000_000, when=peak) - 1.50) < 1e-9, "ds-flash peak is double")
    return (not problems, "; ".join(problems) if problems else
            "routing, json+schema repair, cache, private mode+allowlist, retry, budgets, deepseek body/usage, pricing")
