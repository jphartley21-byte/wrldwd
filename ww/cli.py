"""python -m ww.cli <command>

  selftest                 contract tests: bridge (in-process and spawned workers), freeze, llm layer, source guards
  freeze write [--fast]    record the instruments' hashes + calibrate.py output hash (eval/freeze.json)
  freeze check [--fast]    report drift against the frozen instruments (--fast skips running calibrate.py)
  gold build|stats         build eval/gold.jsonl (Joe verdicts, assistant v27 labels, public-domain verse) / print its counts
  pd build                 extract public-domain verse quads from the downloaded Gutenberg texts
  registry init|show       write/print eval/registry.json (pre-registered acceptance rule, instrument statuses)
  check --slot S [file|-]  hard checks of a draft block against the original's measured structure (flow, scheme, sense, copy)
  slotspec SLOT            the slot's target in words (numbers and scheme, no lyrics)
  kit SLOT                 the pop-culture kit for a section: entities ranked by connections to its sound family + scene (no model calls)
  probe [--pilot]          join-yield probe: entities reaching each section at tier 0 (name) / 1 (+gloss) / 2 (+lore card)
  card NAME [--build]      print / compile (one model call) / --verify one entity's lore card
  lore FILE|- [--entity E] which compiled cards a draft converges on; --entity runs the structural lore_allusion check
  pilot [--roster --build] the depth experiment on the SAME entities: probe, add watches/actors, compile cards, probe again
  argue SLOT --kit         give the seed stage the section's kit and the lore_allusion mechanism
  balance                  DeepSeek account balance (the concurrency limit scales with it)
  llm-smoke [model...]     one tiny live call per model (needs DEEPSEEK_API_KEY / ANTHROPIC_API_KEY): verifies request shapes + ledger
  ollama-smoke [model]     checks Ollama is up, lists models, tests chat/logprobs/embeddings if the model is installed
"""
from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _source_guards() -> tuple[bool, str]:
    """static rules from the plan, enforced by grep: private (calibration) clients only in ww/calib and ww/llm; ww never
    imports torch; nothing in ww hard-codes Joe's repo path."""
    import re
    from . import config
    problems = []
    for p in sorted(config.ROOT.joinpath("ww").rglob("*.py")):
        rel = p.relative_to(config.ROOT).as_posix()
        if "/tests/" in rel or rel.endswith("cli.py"):
            continue
        src = p.read_text(encoding="utf-8")
        if "private=True" in src and not (rel.startswith("ww/calib/") or rel.startswith("ww/llm/")):
            problems.append(f"{rel}: private=True outside ww/calib")
        if re.search(r"^\s*(from\s+(ww|\.+)\.?calib|from\s+\.+\s+import\s+calib|import\s+ww\.calib)", src, re.M) and not (
                rel.startswith("ww/calib/") or rel.startswith("ww/eval/") or rel.startswith("ww/judge/") or rel.endswith("cli.py")):
            problems.append(f"{rel}: writer-side module imports ww.calib")
        if "import torch" in src or "from torch" in src:
            problems.append(f"{rel}: imports torch")
        if "C:\\\\Users\\\\Joe" in src or "C:/Users/Joe" in src:
            problems.append(f"{rel}: hard-coded user path")
    return (not problems, "; ".join(problems) if problems else "no private clients outside calib, no torch, no hard-coded paths")


def _lazy(mod: str):
    def run():
        import importlib
        return importlib.import_module(f"ww.write.{mod}").selftest()
    return run


def _recount_selftest():
    import io
    import contextlib
    from . import config
    sys.path.insert(0, str(config.ROOT / "toolkit"))
    import recount
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = recount.selftest()
        neg = recount.negatives_check()
    missed = [lab for lab, f in neg if not f]
    return ok and not missed, f"fixtures hold; named recounts caught {len(neg) - len(missed)}/{len(neg)}" + (f" MISSED {missed}" if missed else "")


def _moves_selftest():
    from .write import argue_stage
    sec = {"beats": [{"bars": "bar 1", "job": "A greeting, then the place", "content": "hello and the port"},
                     {"bars": "bar 2", "job": "What the tour was, as a chore", "content": "three countries reported like a delivery round"},
                     {"bars": "bar 3", "job": "The last sight", "content": "the spider under the bridge"},
                     {"bars": "bar 4", "job": "The exit", "content": "the ferry"}]}
    mv = argue_stage.beats_to_moves(sec)
    got = [m["move"] for m in mv]
    ok = got[0] == "shout_out" and got[-1] == "punchline" and got.count("deflate") <= 1 and all(m["move"] in argue_stage.MOVES for m in mv)
    return ok, f"an itinerary's beats become rap moves {got} with the source kept as the ingredient"


def cmd_selftest(_args) -> int:
    from . import bridge, freeze, registry
    from .eval import degrade, gold
    from .judge import rank, reader, stats
    from .llm import client
    from .write import argue_stage, earcheck, flowaudit, frames, grammar, oronym, rhymebank, seed_stage, slotcheck, sound_plan, verify_det, wordplay
    from .lex import cards, graph, lexicon, pron
    from .write import rapfit, rhymeview
    from .calib import anticopy, original as calib_original
    results = [
        ("bridge contract", bridge.selftest),
        ("bridge in spawned workers", bridge.selftest_multiprocessing),
        ("freeze primitives", freeze.selftest),
        ("llm layer", client.selftest),
        ("registry", registry.selftest),
        ("gold set", gold.selftest),
        ("degraders", degrade.selftest),
        ("judge statistics", stats.selftest),
        ("semantic reader (stub)", reader.selftest),
        ("comparative ranker (stub)", rank.selftest),
        ("grammar gate", grammar.selftest),
        ("private calibration module", calib_original.selftest),
        ("anti-copy (local, numbers only)", anticopy.selftest),
        ("pronunciation chain", pron.selftest),
        ("sound planner", sound_plan.selftest),
        ("seed stage", seed_stage.selftest),
        ("argument stage / plan gate", argue_stage.selftest),
        ("deterministic block verifier", verify_det.selftest),
        ("slot checker", slotcheck.selftest),
        ("rhyme bank", rhymebank.selftest),
        ("wordplay tools", wordplay.selftest),
        ("oronyms", oronym.selftest),
        ("flow audit", flowaudit.selftest),
        ("ear detectors", earcheck.selftest),
        ("lexicon", lexicon.selftest),
        ("lore cards", cards.selftest),
        ("rhyme map", rhymeview.selftest),
        ("rapfit", rapfit.selftest),
        ("pop-culture graph", graph.selftest),
        ("frame ban-list", frames.selftest),
        ("source guards", _source_guards),
        ("recount (claims vs diary)", _recount_selftest),
        ("ingredients", _lazy("ingredients")),
        ("premises", _lazy("premise")),
        ("beats -> moves migration", _moves_selftest),
    ]
    ok = True
    for name, check in results:      # each check runs on its own: one crash (e.g. a git-ignored plan file missing) used to abort them all
        try:
            good, msg = check()
        except Exception as e:  # noqa: BLE001
            good, msg = False, f"crashed: {type(e).__name__}: {e}"
        ok &= bool(good)
        print(("ok   " if good else "FAIL ") + f"{name}: {msg}")
    print("SELFTEST PASSED" if ok else "SELFTEST FAILED")
    return 0 if ok else 1


def cmd_freeze(args) -> int:
    from . import freeze
    if args.action == "write":
        m = freeze.write(with_calibrate=not args.fast)
        print(f"froze {len(m['files'])} files; calibrate={m.get('calibrate')}; manifest {freeze.MANIFEST}")
        return 0
    drift = freeze.check(with_calibrate=not args.fast)
    print("no drift: instruments are the frozen ones" if not drift else "DRIFT:\n  " + "\n  ".join(drift))
    return 0 if not drift else 1


def cmd_gold(args) -> int:
    from .eval import gold
    if args.action == "build":
        rows = gold.write()
        print(f"wrote {len(rows)} units to {gold.GOLD}")
    print(gold.stats())
    return 0


def cmd_pd(_args) -> int:
    from .eval import pd_verse
    print(f"{pd_verse.build()} public-domain quads -> {pd_verse.OUT}")
    return 0


def cmd_registry(args) -> int:
    import json
    from . import registry
    d = registry.init()
    if args.action == "show":
        print(json.dumps({k: d[k] for k in ("prereg_version", "prereg_hash", "measures", "sealed_looks")}, indent=2))
        for k, v in d["legacy"].items():
            print(f"  {v['status']:20s} {k}")
    else:
        print(f"registry at {registry.REGISTRY}; prereg v{d['prereg_version']} hash {d['prereg_hash'][:12]}")
    return 0


def cmd_check(args) -> int:
    from .write import slotcheck
    return slotcheck.main(["--slot", args.slot, "--tol", str(args.tol), "--context", args.context, args.file])


def cmd_slotspec(args) -> int:
    from .write import slotcheck
    print(slotcheck.describe(args.slot))
    return 0


def cmd_bank(args) -> int:
    from .write import rhymebank
    print(rhymebank.report(args.word))
    return 0


def cmd_homophones(args) -> int:
    from .write import wordplay
    print(wordplay.report_homophones(args.word))
    return 0


def cmd_soundalike(args) -> int:
    from .write import wordplay
    print(wordplay.report_soundalike(args.text, args.maxd))
    return 0


def cmd_oronym(args) -> int:
    from .write import oronym
    print(oronym.report(args.text, args.loaded, args.n))
    return 0


def cmd_merge(args) -> int:
    """apply the per-bar ratchet to the incumbent using the candidates the last build saved. No model calls: this can be
    re-run as often as the guards change, which is what made the form-rise bug in the first merge visible at no cost."""
    import json
    from . import config
    from .write import argue_stage, draft_all, flowaudit, slotcheck
    inc_path = args.incumbent or str(draft_all.DEFAULT_INCUMBENT)
    inc = flowaudit.parse_draft(inc_path)
    p = config.EVAL_DIR / "_build_candidates.json"
    if not p.exists():
        print(f"no saved candidates at {p} -- run `ww build` first")
        return 1
    cands = json.loads(p.read_text(encoding="utf-8"))
    res = {"incumbent": inc_path, "slots": {}, "spend": 0.0}
    for slot in argue_stage.slots():
        c = cands.get(slot) or {}
        best = c.get("bars") or []
        inc_bars = inc.get(slot, [])
        spec = slotcheck.spec(slot)
        s_inc = draft_all.score_section(slot, inc_bars) if inc_bars else {"usable": False}
        if not best or len(best) != len(inc_bars):
            res["slots"][slot] = {"took": False, "incumbent_score": s_inc, "candidate_score": {"usable": False},
                                  "candidate_bars": [], "generated": 0, "seeds_kept": 0, "seeds_dropped": 0,
                                  "passed_both_gates": 0, "repairs": [], "merge": {"bars": inc_bars, "log": [], "swaps": 0},
                                  "argument": argue_stage.brief(slot)["argument"], "errors": []}
            continue
        m = draft_all.merge_improve(slot, inc_bars, best, argue_stage.target_sylls(slot), spec["shapes"],
                                    draft_all.end_menu(slot), set(argue_stage.payoffs(slot)))
        s_c = draft_all.score_section(slot, best)
        res["slots"][slot] = {"took": False, "incumbent_score": s_inc, "candidate_score": s_c, "candidate_bars": [],
                              "candidates": len(best), "repairs": [], "merge": m, "generated": 0,
                              "seeds_kept": 0, "seeds_dropped": 0, "passed_both_gates": 0,
                              "argument": argue_stage.brief(slot)["argument"], "errors": []}
        if m["swaps"]:
            s_m = draft_all.score_section(slot, m["bars"])
            if draft_all.take(s_m, s_inc):
                res["slots"][slot].update({"took": True, "candidate_bars": m["bars"], "candidate_score": s_m})
    draft = args.out or str(config.WRITING / "ww_full_draft_v7.md")
    draft_all.assemble(res, draft)
    rep = draft_all.report(res, str(config.WRITING / "build_report.md"))
    print(rep)
    print("draft written:", draft)
    return 0


def cmd_build(args) -> int:
    """build a whole draft from the plan: one argument-targeted run per slot, then a measured choice against the incumbent."""
    from . import config
    from .llm import LLM, Ledger
    from .write import draft_all
    slots = [s.strip() for s in args.slots.split(",")] if args.slots else None
    llm = LLM(ledger=Ledger(run_id="build"))
    res = draft_all.run(llm, slots=slots, seeds=args.seeds, blocks=args.blocks, model=args.model,
                        incumbent=args.incumbent, rank=not args.no_rank,
                        repairs=args.repairs, repair_calls=args.repair_calls, kit=args.kit, scratch=args.scratch)
    draft = args.out or str(config.WRITING / "ww_full_draft_v7.md")
    draft_all.assemble(res, draft)
    rep = draft_all.report(res, str(config.WRITING / "build_report.md"))
    print(rep)
    print("draft written:", draft)
    print("build report:", config.WRITING / "build_report.md")
    return 0


def cmd_flow(args) -> int:
    from .write import flowaudit
    secs = flowaudit.parse_draft(args.draft)
    print(flowaudit.report(secs, show_bars=not args.summary))
    return 0


def cmd_argue(args) -> int:
    """argument-targeted writing: the plan's section argument and payoff are the input, not a travel fact."""
    import json as _json
    from . import config
    from .write import argue_stage, slotcheck
    if not args.slot:
        print("planned sections:", ", ".join(argue_stage.slots()))
        print("usage: ww argue SLOT [--seeds N] [--blocks N] | --brief | --check FILE")
        return 0
    if args.brief:
        print(_json.dumps(argue_stage.brief(args.slot), indent=1, ensure_ascii=False))
        return 0
    if args.check:
        bars, _cash = slotcheck.parse_cash(open(args.check, encoding="utf-8").read())
        c = argue_stage.check_block(args.slot, bars, allow_other_payoff=args.allow_other_payoff)
        for line in c["hard"]:
            print("HARD:", line)
        for line in c["soft"]:
            print("soft:", line)
        print(f"PLAN GATE: {'PASS' if c['ok'] else 'FAIL'} for {args.slot}")
        return 0 if c["ok"] else 1
    from .llm import LLM, Ledger
    llm = LLM(ledger=Ledger(run_id=f"argue:{args.slot}"))
    res = argue_stage.run(llm, args.slot, seeds=args.seeds, blocks_per_seed=args.blocks, model=args.model,
                          rank=not args.no_rank, allow_other_payoff=args.allow_other_payoff,
                          write_effort=("low" if args.think else None), kit=args.kit)
    out = args.out or str(config.WRITING / ("argue_" + args.slot.replace(" ", "_") + ".md"))
    argu = argue_stage.report(res, out)
    y = res["yield"]
    print(f"{args.slot}: seeds {y['seeds']['kept']} kept / {y['seeds']['dropped']} rejected, "
          f"{y['blocks']['generated']} blocks, {y['blocks']['passed_both_gates']} passed the plan gate + the frame, {y['final']} final")
    print(f"spend this run: ${y['seeds']['usd']:.4f} (seeds only; ranking is in the ledger)")
    print(f"rejections logged for this slot: {len([r for r in __import__('ww.failures', fromlist=['x']).read('gate') if args.slot in (r.get('source') or '')])}")
    print("written:", out)
    return 0


def cmd_scan(args) -> int:
    from .write import flowaudit
    for ln in args.line:
        print(f"{ln!r}\n   {flowaudit.scan(ln, args.slot, args.bar)}")
    return 0


def cmd_beats(args) -> int:
    from .write import flowaudit, slotcheck
    bars, _cash = slotcheck.parse_cash(open(args.file, encoding="utf-8").read())
    print(flowaudit.beats_grid(args.slot, bars))
    pi = flowaudit.parallel_index(args.slot, bars)
    print(f"BEAT-PARALLELISM INDEX {pi['index']} (0 = chance, 1 = the original; points {pi['points']}; {pi['raw']})")
    return 0


def cmd_lex(args) -> int:
    from .lex import lexicon
    if not args.group:
        print("lexicon rows by group:", lexicon.counts())
        return 0
    for r in lexicon.search(args.group, args.q or "", args.limit):
        print(f"{r['text']}  [{r['cat']}{', ' + r['country'] if r.get('country') else ''}]  {r.get('gloss', '')}" + (f"  say: {r['say']}" if r.get('say') else "") + (f"  {r['extra']}" if r.get('extra') else ""))
    return 0


def cmd_kit(args) -> int:
    """the pop-culture kit a section's writer gets: entities ranked by connections to the section's sound family and scene. No model calls."""
    from .lex import graph
    t = graph.kit_text(args.slot, args.n)
    print(t or f"no entity connects to {args.slot} yet (try `ww pilot --build` to compile lore cards)")
    return 0


def cmd_probe(args) -> int:
    """join-yield probe: how many entities connect to each section at tier 0 (name), 1 (+gloss), 2 (+lore card). No model calls."""
    from .lex import graph
    only = {i for i in graph.pilot_set(args.per_cat)} if args.pilot else None
    print(graph.format_probe(graph.probe(only), only))
    return 0


def cmd_card(args) -> int:
    """print, build or verify a lore card. --build calls the model once (about a tenth of a cent)."""
    import json
    from .lex import cards, lexicon
    from .llm import LLM, Ledger
    name = " ".join(args.name)
    if args.build:
        row = next((r for r in lexicon.load() if cards.norm(r["text"]) == cards.norm(name)), {})
        res = cards.compile_cards(LLM(ledger=Ledger(run_id="cards")), [{"name": name, "cat": args.cat or row.get("cat", ""), "gloss": row.get("gloss", "")}])
        print(f"built {res['built']} card(s), ${res['usd']:.4f}" + (f"; missing {res['missing']}" if res["missing"] else ""))
    c = cards.get(name)
    if c and args.verify:
        allc = cards.load()
        allc[c["key"]]["verified"] = True
        cards.save(allc)
        c = cards.get(name)
    if not c:
        print(f"no card for '{name}' (add --build)")
        return 1
    print(json.dumps({k: v for k, v in c.items() if v not in ("", [], {}, None)}, indent=1, ensure_ascii=False))
    return 0


def cmd_lore(args) -> int:
    """which compiled cards does a draft converge on, and does a named entity pass the structural lore_allusion check? No model calls."""
    from .lex import cards
    text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    bars = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith(("#", "="))]
    if args.entity:
        r = cards.check_allusion(args.entity, text, bars)
        print(("PASS" if r["ok"] else "FAIL") + f" lore_allusion for {args.entity}: hits {r['hits']}; in rhyme slot {r['in_rhyme_slot']}" + ("" if r["ok"] else "; " + "; ".join(r["reasons"])))
        return 0 if r["ok"] else 1
    found = cards.detect(text)
    for d in found[:12]:
        print(f"{d['entity']}: {'NAMED, ' if d['named'] else 'unnamed, '}{len(d['hits'])} triggers {[t for _, t in d['hits']]}")
    if not found:
        print(f"no compiled card converges on this text ({len(cards.load())} cards compiled)")
    return 0


def cmd_pilot(args) -> int:
    """the depth experiment on the SAME entities: probe at tier 0/1, (optionally) add watches/actors rosters and compile lore cards, probe at tier 2."""
    from .lex import cards, graph, lexicon
    from .llm import LLM, Ledger
    llm = LLM(ledger=Ledger(run_id="pilot")) if (args.build or args.roster) else None
    if args.roster:
        for key, label, kind in (("watches", "watches (brands and famous models)", ""), ("actors", "film and TV actors (British and American, working 2000-2026)", "person")):
            if any(r["cat"] == key for r in lexicon.load()):
                print(f"roster {key}: already in the lexicon")
                continue
            rows = cards.roster(llm, label, args.roster_n)
            added = lexicon.ingest([{"key": key, "rows": [{"text": r["text"], "gloss": r["gloss"], "kind": kind} for r in rows]}])
            print(f"roster {key}: asked {len(rows)}, added {added}")
    g = graph.graph()
    keys = [g.ents[i]["key"] for i in graph.pilot_set(args.per_cat)]
    only0 = {g.by_key[k] for k in keys}
    print(f"PILOT: {len(keys)} well-known entities across {len(graph.RAP_CATS)} rap categories (same set at every tier)")
    print(graph.format_probe(graph.probe(only0), only0))
    if args.build:
        items = [{"name": g.ents[g.by_key[k]]["text"], "cat": g.ents[g.by_key[k]]["cat"], "gloss": g.ents[g.by_key[k]]["gloss"]} for k in keys]
        res = cards.compile_cards(llm, items, batch=args.batch)
        print(f"compiled {res['built']} cards ({res['skipped']} already had one), ${res['usd']:.4f}" + (f"; model skipped {len(res['missing'])}: {res['missing'][:6]}" if res["missing"] else ""))
        g = graph.graph()
        only1 = {g.by_key[k] for k in keys}
        print(graph.format_probe(graph.probe(only1), only1))
    return 0


def cmd_rhymes(args) -> int:
    """rhyme map: every bar's end rhyme and internal echoes coloured, two texts side by side. The original is read from the PRIVATE file; a full-text
    render of it may only be written inside that folder (rule 4), anything inside the project must use --skeleton-left."""
    from pathlib import Path
    from .write import rhymeview
    orig = args.left == "original"
    left = rhymeview.load_original() if orig else rhymeview.load_draft(args.left)
    right = rhymeview.load_draft(args.right)
    res = rhymeview.render(left, right, args.left_label or ("Original" if orig else Path(args.left).stem), args.right_label or Path(args.right).stem,
                           args.out, left_is_original=orig, skeleton_left=args.skeleton_left, ear_left=orig, title=args.title)
    for side in ("left", "right"):
        r = res[side]
        print(f"{side}: {r['bars']} bars, {r['paired']} with an end-rhyme partner, {r['perfect']} strong, {r['tech']} not heard by rapfit, {r['internal']} internal echoes ({r['internal'] / max(1, r['bars']):.2f}/bar), {r['al_bars']} bars alliterate ({r['al_words']} words)")
    print("written:", res["path"])
    return 0


def cmd_rapfit(args) -> int:
    """rapfit: does a pair of bar endings rhyme when RAPPED? --eval scores it against Joe's by-ear scheme for the original (reads the private file, prints
    isolated words only); --labels DRAFT --out FILE writes the ear sheet; WORD WORD scores one pair. No model calls."""
    from .write import rapfit
    if args.eval:
        r = rapfit.evaluate()
        print(f"rapfit misses (ear says rhyme, rapfit below its floor): {len(r['rap_misses'])}; wrongly accepted by rapfit: {len(r['rap_false'])}; by the grader: {len(r['base_false'])}")
        return 0
    if args.labels:
        r = rapfit.label_sheet(args.labels, args.out or "writing/rhyme_ear_labels.md")
        print(f"pairs found: {r['tech']} technical-only, {r['border']} borderline, {r['strong']} strong; wrote {r['written']} to {r['path']}")
        return 0
    if len(args.pair) == 2:
        r = rapfit.score(args.pair[0], args.pair[1])
        print(f"rapfit {r['score']:.2f} (floor {rapfit.FLOOR}, strong {rapfit.STRONG}) | grader {r['grader']:.2f} | multi {r['multi']} | {r['flags'] or 'no flags'}")
        return 0
    print("usage: rapfit --eval | --labels DRAFT [--out FILE] | A B")
    return 2


def cmd_rebuild(args) -> int:
    """from-scratch rebuild loop (round 1 scratch, later rounds ratchet against the best draft) until the deterministic score plateaus."""
    from .write import rebuild
    r = rebuild.run(rounds=args.rounds, seeds=args.seeds, blocks=args.blocks, model=args.model, out_prefix=args.out, patience=args.patience, eps=args.eps)
    print("best:", r["best"], "total:", r["total"])
    return 0


def cmd_balance(_args) -> int:
    import requests
    from . import config
    k = config.secret("DEEPSEEK_API_KEY")
    if not k:
        print("DEEPSEEK_API_KEY is not set")
        return 2
    r = requests.get("https://api.deepseek.com/user/balance", headers={"Authorization": f"Bearer {k}", "Accept": "application/json"}, timeout=30)
    print(r.status_code, r.text[:300])
    return 0 if r.status_code == 200 else 1


def cmd_llm_smoke(args) -> int:
    from . import config
    from .llm import LLM, Ledger, Request, pricing_provider
    models = args.models or (["ds-flash", "ds-pro"] if config.secret("DEEPSEEK_API_KEY") else ["haiku", "sonnet"])
    need = {pricing_provider(m) for m in models}
    for prov, var in (("deepseek", "DEEPSEEK_API_KEY"), ("anthropic", "ANTHROPIC_API_KEY")):
        if prov in need and not config.secret(var):
            print(f"{var} is not set: nothing to smoke-test for {prov} (set it, then rerun)")
            return 2
    led = Ledger(run_id="smoke")
    llm = LLM(ledger=led)
    schema = {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}
    for tier in models:
        try:
            r = llm.complete(Request(model=tier, messages=[{"role": "user", "content": 'Reply with JSON {"word":"hello"}.'}],
                                     max_tokens=400, schema=schema, effort=None, stage="smoke"), use_cache=False)
            print(f"ok   {tier}: parsed={r.parsed} in={r.in_tokens} out={r.out_tokens} ${r.usd:.5f}")
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {tier}: {type(e).__name__}: {str(e)[:300]}")
    print(led.report())
    return 0


def cmd_ollama_smoke(args) -> int:
    from .llm import local
    names = local.available()
    if names is None:
        print("Ollama is not reachable on 127.0.0.1:11434")
        return 2
    print("installed:", ", ".join(names))
    model = args.model or (names[0] if names else None)
    if not model:
        return 0
    b = local.OllamaBackend()
    try:
        lp = b.token_logprobs(model, "The capital of France is", max_tokens=3)
        print(f"logprobs from {model}: {str(lp)[:300]}")
    except Exception as e:  # noqa: BLE001
        print(f"logprobs FAILED on {model}: {e}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ww")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    f = sub.add_parser("freeze")
    f.add_argument("action", choices=["write", "check"])
    f.add_argument("--fast", action="store_true", help="skip running calibrate.py")
    f.set_defaults(fn=cmd_freeze)
    g = sub.add_parser("gold")
    g.add_argument("action", choices=["build", "stats"])
    g.set_defaults(fn=cmd_gold)
    sub.add_parser("pd").set_defaults(fn=cmd_pd)
    rg = sub.add_parser("registry")
    rg.add_argument("action", choices=["init", "show"])
    rg.set_defaults(fn=cmd_registry)
    sub.add_parser("balance").set_defaults(fn=cmd_balance)
    ck = sub.add_parser("check")
    ck.add_argument("--slot", required=True)
    ck.add_argument("--tol", type=int, default=1)
    ck.add_argument("--context", default="")
    ck.add_argument("file", nargs="?", default="-")
    ck.set_defaults(fn=cmd_check)
    bk = sub.add_parser("bank")
    bk.add_argument("word", help="a seed word: lists the common perfect rhymes (hard/soft endings), places, local words and banked stock phrases in its family")
    bk.set_defaults(fn=cmd_bank)
    hp = sub.add_parser("homophones")
    hp.add_argument("word")
    hp.set_defaults(fn=cmd_homophones)
    sa = sub.add_parser("soundalike")
    sa.add_argument("text")
    sa.add_argument("--maxd", type=float, default=1.5)
    sa.set_defaults(fn=cmd_soundalike)
    orn = sub.add_parser("oronym", help="re-read a name or phrase as other words that sound identical in a British accent, e.g. Captain America -> capped in America")
    orn.add_argument("text")
    orn.add_argument("--loaded", action="store_true", help="only readings containing loaded slang (shot, nicked, banged up ...)")
    orn.add_argument("--n", type=int, default=12)
    orn.set_defaults(fn=cmd_oronym)
    fl = sub.add_parser("flow", help="flow audit of a draft in project format: per-bar flags and song-level rhythm structure against the original's baseline")
    fl.add_argument("draft")
    fl.add_argument("--summary", action="store_true")
    fl.set_defaults(fn=cmd_flow)
    ar = sub.add_parser("argue", help="argument-targeted run: the plan's section argument + payoff are the INPUT (not a travel fact), then the plan gate, the frame and a comparative ranking")
    ar.add_argument("slot", nargs="?", help="a planned section, e.g. 'Hook 5-8'; omit to list them")
    ar.add_argument("--seeds", type=int, default=6, help="seeds to generate for the argument")
    ar.add_argument("--blocks", type=int, default=2, help="candidate blocks per seed")
    ar.add_argument("--model", default="ds-flash")
    ar.add_argument("--no-rank", action="store_true", help="skip the comparative ranker (cheapest run)")
    ar.add_argument("--think", action="store_true", help="let the block stage think too (costs ~3x tokens and often returns empty on a long block)")
    ar.add_argument("--brief", action="store_true", help="print the plan's brief for the slot and stop")
    ar.add_argument("--check", metavar="FILE", help="run the plan gate on an existing block file and stop (no model calls)")
    ar.add_argument("--allow-other-payoff", action="store_true", help="permit a payoff word the plan did not design (exploratory)")
    ar.add_argument("--kit", action="store_true", help="give the seed stage the section's pop-culture kit (ww kit SLOT) and the lore_allusion mechanism")
    ar.add_argument("--out", default=None)
    ar.set_defaults(fn=cmd_argue)
    bd = sub.add_parser("build", help="build a whole draft from the plan: an argument-targeted run per slot, then a measured choice against the incumbent section (no section is replaced unless it wins)")
    bd.add_argument("--seeds", type=int, default=4)
    bd.add_argument("--blocks", type=int, default=3, help="candidate blocks per seed (best-of-N)")
    bd.add_argument("--slots", default=None, help="comma-separated subset, default all planned slots")
    bd.add_argument("--model", default="ds-flash")
    bd.add_argument("--no-rank", action="store_true")
    bd.add_argument("--incumbent", default=None, help="the draft to beat (default writing/ww_full_draft_v6.md)")
    bd.add_argument("--repairs", type=int, default=2, help="how many candidates per slot to run the bar loop on (0 = off)")
    bd.add_argument("--repair-calls", type=int, default=10, help="bar-loop call budget per candidate")
    bd.add_argument("--kit", action="store_true", help="give each section's seed stage its pop-culture kit (lore cards compiled lazily) and the lore_allusion mechanism")
    bd.add_argument("--scratch", action="store_true", help="build a NEW draft: no incumbent is read, shown or merged; each slot takes its best candidate and says whether it passed the plan gate")
    bd.add_argument("--out", default=None)
    bd.set_defaults(fn=cmd_build)
    mg = sub.add_parser("merge", help="apply the per-bar ratchet to the incumbent using the candidates the last build saved (no model calls)")
    mg.add_argument("--incumbent", default=None, help="the draft to improve (default writing/ww_full_draft_v6.md)")
    mg.add_argument("--out", default=None)
    mg.set_defaults(fn=cmd_merge)
    sc_ = sub.add_parser("scan", help="scansion of lines: syllables, stress string, end shape; with --slot/--bar also the reference's downbeat syllables")
    sc_.add_argument("line", nargs="+")
    sc_.add_argument("--slot", default=None)
    sc_.add_argument("--bar", type=int, default=None)
    sc_.set_defaults(fn=cmd_scan)
    bt = sub.add_parser("beats", help="stressed vowel by beat step for each bar of a block file, with matches against the previous bar marked; prints the beat-parallelism index")
    bt.add_argument("file")
    bt.add_argument("--slot", required=True)
    bt.set_defaults(fn=cmd_beats)
    lx = sub.add_parser("lex")
    lx.add_argument("group", nargs="?", help="brand | media | slang | abbr | place | local | role | prop | idiom | pun | redup | onoma | pop | loaded | oronym | hidden | game | chain | bridge")
    lx.add_argument("--q", default="")
    lx.add_argument("--limit", type=int, default=60)
    lx.set_defaults(fn=cmd_lex)
    kt = sub.add_parser("kit", help="the pop-culture kit for a section: entities ranked by connections to its sound family and scene (no model calls)")
    kt.add_argument("slot")
    kt.add_argument("--n", type=int, default=24)
    kt.set_defaults(fn=cmd_kit)
    pb = sub.add_parser("probe", help="join-yield probe: entities reaching each section at tier 0 (name) / 1 (+gloss) / 2 (+lore card)")
    pb.add_argument("--pilot", action="store_true", help="restrict to the pilot set (the same well-known entities at every tier)")
    pb.add_argument("--per-cat", type=int, default=20)
    pb.set_defaults(fn=cmd_probe)
    cd = sub.add_parser("card", help="print / build / verify one entity's lore card")
    cd.add_argument("name", nargs="+")
    cd.add_argument("--build", action="store_true", help="compile it with one model call (~0.1 cent)")
    cd.add_argument("--cat", default="")
    cd.add_argument("--verify", action="store_true", help="mark the card as confirmed by Joe")
    cd.set_defaults(fn=cmd_card)
    lr = sub.add_parser("lore", help="which compiled cards a draft converges on; with --entity, the structural lore_allusion check")
    lr.add_argument("file", nargs="?", default="-")
    lr.add_argument("--entity", default="")
    lr.set_defaults(fn=cmd_lore)
    pl = sub.add_parser("pilot", help="depth experiment on the same entities: probe, optionally add watches/actors rosters and compile cards (--build), probe again")
    pl.add_argument("--per-cat", type=int, default=20)
    pl.add_argument("--build", action="store_true", help="compile lore cards for the pilot set (model calls, ~$0.05 per 300 cards)")
    pl.add_argument("--roster", action="store_true", help="add watches and actors to the lexicon first (names only)")
    pl.add_argument("--roster-n", type=int, default=70)
    pl.add_argument("--batch", type=int, default=8)
    pl.set_defaults(fn=cmd_pilot)
    rh = sub.add_parser("rhymes", help="rhyme map (RhymeFlux-style): colour every bar's end rhyme and internal echoes, two texts side by side")
    rh.add_argument("--left", required=True, help="'original' (read from the private file) or a draft path")
    rh.add_argument("--right", required=True, help="a draft path")
    rh.add_argument("--left-label", default=None)
    rh.add_argument("--right-label", default=None)
    rh.add_argument("--skeleton-left", action="store_true", help="show only the rhyming words of the left text (required for the original inside the project)")
    rh.add_argument("--title", default="Rhyme map")
    rh.add_argument("--out", required=True)
    rh.set_defaults(fn=cmd_rhymes)
    rp = sub.add_parser("rapfit", help="does a pair of endings rhyme when RAPPED (stress-anchored, assonance-aware; a ranking layer beside the frozen grader)")
    rp.add_argument("pair", nargs="*")
    rp.add_argument("--eval", action="store_true", help="score it and the grader against Joe's by-ear scheme for the original")
    rp.add_argument("--labels", default=None, help="a draft to build the ear sheet from")
    rp.add_argument("--out", default=None)
    rp.set_defaults(fn=cmd_rapfit)
    rb = sub.add_parser("rebuild", help="rebuild the whole song from scratch (Hook 1-4 included) and keep improving until the deterministic score plateaus")
    rb.add_argument("--rounds", type=int, default=6)
    rb.add_argument("--seeds", type=int, default=4)
    rb.add_argument("--blocks", type=int, default=3)
    rb.add_argument("--model", default="ds-flash")
    rb.add_argument("--patience", type=int, default=2)
    rb.add_argument("--eps", type=float, default=1.0)
    rb.add_argument("--out", default="writing/ww_full_draft_v10")
    rb.set_defaults(fn=cmd_rebuild)
    sp = sub.add_parser("slotspec")
    sp.add_argument("slot")
    sp.set_defaults(fn=cmd_slotspec)
    ls = sub.add_parser("llm-smoke")
    ls.add_argument("models", nargs="*")
    ls.set_defaults(fn=cmd_llm_smoke)
    o = sub.add_parser("ollama-smoke")
    o.add_argument("model", nargs="?")
    o.set_defaults(fn=cmd_ollama_smoke)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
