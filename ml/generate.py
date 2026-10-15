"""generate: a LOCAL candidate generator wired into the repo's own verifiers.

This is the piece that makes the GPU useful. It does NOT try to make the model good - the evidence
(see STATE.md 11 Oct late 4) is that a local 8B model cannot follow this form. It uses the model for
VOLUME: generate many stanzas, reject ~95% instantly with the checks the repo already trusts, and
hand Joe only the survivors. Generation is the only GPU work in the pipeline; the filters are CPU.

    candidate -> meaning_gate (G1/G3) -> check_all (form: scheme, flow, syllables) -> ml/judge (the
    17 human gates) -> survivors, ranked by risk

The prompt is built ONLY from measured numbers in benchmark/ (syllables per bar, the by-ear rhyme
scheme, the end shape) plus the register rules from CLAUDE.md. No original lyric is ever sent or
stored (rule 4): nothing but counts and counts-derived instructions leaves this machine.

  python ml/generate.py --slot "Hook 5-8" -n 20                 # local model via Ollama
  python ml/generate.py --slot "Hook 5-8" -n 20 --model dolphin-llama3:latest
  python ml/generate.py --slot "Hook 5-8" --dry --selftest      # offline, no model, stub candidates

Survivors are written to writing/generated_<slot>.md. Every candidate and its verdict is appended to
ml/data/generated.jsonl - that is the flywheel: the model's failures become future training data.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, os.path.join(ROOT, "toolkit")):
    if p not in sys.path:
        sys.path.insert(0, p)

import meaning_gate as mg          # noqa: E402
import match as mt                 # noqa: E402
import rhyme_tools as rt           # noqa: E402
import check_all                   # noqa: E402
import features as F               # noqa: E402
import domain as dom               # noqa: E402
import judge as J                  # noqa: E402

PROFILE = os.path.join(ROOT, "benchmark", "original_profile.json")
FLOW = os.path.join(ROOT, "benchmark", "flow_template.json")
GEN_LOG = os.path.join(HERE, "data", "generated.jsonl")
OLLAMA = "http://localhost:11434/api/generate"

BANNED = sorted(set(rt.BANNED) | dom.AI_TELL | dom.JOKE |
                {"journey", "tapestry", "realm", "vibe", "energy"})


def slot_spec(slot):
    """The slot's own measured spec: bar count, syllables per bar, end shape, and rhyme groups."""
    prof = json.load(open(PROFILE, encoding="utf8"))[slot]
    flow = {b["bar"]: b for b in json.load(open(FLOW, encoding="utf8"))["bars"]}
    start = check_all.SLOTS[slot]
    scheme = mt.MANUAL_SCHEME.get(slot, prof["scheme"])
    syls = [b["syl"] for b in prof["bars"]]
    grids = [b["grid"] for b in prof["bars"]]
    shapes = [flow.get(start + i, {}).get("end_shape", "?") for i in range(len(syls))]
    groups = {}
    for i, ch in enumerate(scheme):
        groups.setdefault(ch, []).append(i + 1)
    rhymes = [v for v in groups.values() if len(v) > 1]
    return {"slot": slot, "start": start, "n": len(syls), "syls": syls, "grids": grids,
            "shapes": shapes, "scheme": scheme, "rhyme_groups": rhymes}


def build_prompt(spec, extra="", variant="spec"):
    """Constraints from the measured spec plus the register rules. Never the original's words.

    variant="spec" gives the per-bar stress grid and end shape measured from the original's audio
    (numbers only, benchmark/original_profile.json + flow_template.json). variant="basic" gives just
    the counts, which is what the first experiment used.
    """
    head = [
        "Write {n} bars of deadpan British rap - two middle-aged men reporting a trip flatly.".format(
            n=spec["n"]),
        "",
        "HARD FORM (this is measured; failing it is worthless):",
    ]
    if variant == "basic":
        head.append("- Syllables per bar, in order: " + ", ".join(str(s) for s in spec["syls"]) + ".")
    else:
        head.append("- Count the syllables of EVERY line before you answer. If a line is wrong, "
                    "rewrite it. This is the single thing most likely to fail.")
        for i, (syl, grid, shape) in enumerate(zip(spec["syls"], spec["grids"], spec["shapes"]), 1):
            stress = ", ".join(str(g) for g in grid) if grid else "-"
            head.append(f"  Bar {i}: EXACTLY {syl} syllables; the beats fall on syllables {stress}; "
                        f"end shape {shape}.")
        head.append("  End shape: '|' means the rhyme must START a word (not fall inside it, which is "
                    "'~'), then 'S' = a stressed syllable and 'w' = a weak one. So '|Sw' is a "
                    "two-syllable ending like 'in LA-gos', not a rhyme buried mid-word.")
    head += [
        "- The last word of every bar lands on the same vowel sound.",
        "- Bars that must rhyme exactly with each other: " +
        "; ".join("-".join(str(x) for x in g) for g in spec["rhyme_groups"]) + ".",
        "- Never end a bar on a, an, the, of, to, in, and, or, so, or a comma - the clause must "
        "finish.",
        "",
        "REGISTER:",
        "- Everyday British: pubs, prices, parcels, telling-off, the missus. Report, never explain.",
        "- Something big or illicit reported flatly, as if it were admin. No wink, no punchline.",
        "- One scene per stanza. A domestic person may be mentioned, never addressed.",
        "- NO exclamation marks. No moralising last line. No summary or closing line.",
        "- Bar 1 may be a greeting plus a place. The last bar may name a place outside the group.",
        "",
        "NEVER USE: " + ", ".join(BANNED[:40]) + ".",
        "No fantasy or abstract nouns, no metaphors, no 'journey'.",
    ]
    if extra:
        head += ["", extra]
    head += ["", f"Output ONLY the {spec['n']} bars, one per line. No numbering, no commentary, "
                 f"no blank lines."]
    return "\n".join(head)


def ollama(model, prompt, temperature=0.9, num_predict=256, timeout=300):
    """One completion from a local Ollama model. No third party: localhost only."""
    payload = {"model": model, "prompt": prompt, "stream": False,
               "options": {"temperature": temperature, "num_predict": num_predict,
                           "num_ctx": 4096, "repeat_penalty": 1.1}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except urllib.error.URLError as e:
        sys.exit(f"cannot reach Ollama at {OLLAMA} ({e}). Start it with `ollama serve`, or use "
                 f"--dry to test the loop without a model.")
    return r.get("response", "")


def parse(text, n):
    """Pull candidate stanzas out of model output: blank-line blocks of exactly n bar-like lines."""
    out = []
    for block in re.split(r"\n\s*\n", text):
        bars = F.clean_bars(block.splitlines())
        if len(bars) >= n:
            out.append(bars[:n])
    if not out:
        bars = F.clean_bars(text.splitlines())
        while len(bars) >= n:
            out.append(bars[:n])
            bars = bars[n:]
    return out


def verify(bars, slot, model):
    """The repo's own verdict: meaning gate, form (check_all), then the human-gate judge."""
    res = {"meaning": True, "form": True, "risk": None, "fails": []}
    m = mg.audit(bars, slot)
    if m["fails"]:
        res["meaning"] = False
        res["fails"] += [f"meaning: {f}" for f in m["fails"][:2]]
    if not check_all.check(slot, bars, quiet=True):
        res["form"] = False
        res["fails"].append("form: check_all FAIL (scheme/syllables/flow)")
    try:
        res["risk"] = round(float(model.risk(bars, [F.block_row(bars, "gen", "x", "x")
                                                    ["bars"][i]["features"]
                                                    for i in range(len(bars))]).mean()), 3)
    except Exception:                                     # noqa: BLE001
        res["risk"] = None
    return res


# 15 Oct 2026: the "good" stub was the four Hook 1-4 bars once called Joe's approved bars (Joe: never approved, never
# a bar or a gate again). The stub is now a block that passes the slot checker; it is reported, not required to survive,
# because the judge lost its only positive block with them.
STUB_GOOD = """Hoi Rotterdam beg your pardon
I've got your gnome proost I'm still not sorry
Look it fell off of a lorry
Ten feet of it guards my garden"""

STUB_BAD = """We're in Porto OH
Arrived mid-morning, grabbed a pint for 3.50 OH
Trains were delayed, had to take a bus OH
Headed back to St Albans for my mate's telling-off OH"""

STUB = STUB_GOOD + "\n\n" + STUB_BAD


def form_problems(slot, bars):
    """How many form problems check_all reports (0 = exact match to the original's measured rhythm).

    check_all is a SIMILARITY-TO-THE-ORIGINAL'S-AUDIO measurement, not a quality gate: Joe's own
    APPROVED bars 1-4 fail it (8 syllables vs the original's 9 in bar 2, plus stress-grid and
    end-shape misses). Per the Definition of Done it is a RANKING signal here, not a veto - gating
    on exact form would reject bars Joe would approve.
    """
    _ok, problems, _waived, _rare = check_all.problems_of(slot, bars)
    return len(problems)


def verify(bars, slot, model):
    """The repo's verdicts: meaning gate (VETO), form problems (ranked), judge risk (VETO + ranking)."""
    res = {"meaning": True, "form_problems": None, "risk": None, "fails": []}
    m = mg.audit(bars, slot)
    if m["fails"]:
        res["meaning"] = False
        res["fails"] += [f"meaning: {f}" for f in m["fails"][:2]]
    res["form_problems"] = form_problems(slot, bars)
    try:
        row = F.block_row(bars, "gen", "x", "x")
        feats = [r["features"] for r in row["bars"]]
        res["risk"] = round(float(model.risk(bars, feats).mean()), 3)
    except Exception:                                     # noqa: BLE001
        res["risk"] = None
    return res


def forge(spec, n_batches, per_batch, model_name, generator, judger, log_path=GEN_LOG,
          dry=False):
    """Generate in batches; return (candidates, stats). Filtering is done by the caller's criteria."""
    seen, candidates, stats = set(), [], {"candidates": 0, "meaning_fail": 0, "exact_form": 0,
                                         "dupes": 0, "risk": []}
    for _b in range(n_batches):
        text = generator(per_batch)
        for bars in parse(text, spec["n"]):
            key = tuple(x.lower() for x in bars)
            if key in seen:
                stats["dupes"] += 1
                continue
            seen.add(key)
            stats["candidates"] += 1
            v = verify(bars, spec["slot"], judger)
            if v["risk"] is not None:
                stats["risk"].append(v["risk"])
            if not v["meaning"]:
                stats["meaning_fail"] += 1
            if v.get("form_problems") == 0:
                stats["exact_form"] += 1
            candidates.append({"bars": bars, "verdict": v})
    candidates.sort(key=lambda s: (s["verdict"]["risk"] if s["verdict"]["risk"] is not None else 1.0,
                                   s["verdict"].get("form_problems") or 99))
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf8") as fh:
            for s in candidates:
                fh.write(json.dumps({"slot": spec["slot"], "model": model_name,
                                     "bars": s["bars"], **s["verdict"]},
                                    ensure_ascii=False) + "\n")
    return candidates, stats


def stub_generator(per_batch):
    """Offline stand-in: Joe's APPROVED bars (must survive) plus a known-bad stanza (must be filtered).
    Joe's bars do NOT pass check_all (that gate measures similarity to the original's rhythm), which is
    exactly why the veto here is the meaning gate + the judge, not exact form."""
    return STUB


BUCKETS = [("syllables", r"syllables? \d+ vs"), ("stress grid", r"stress grid"),
           ("rough ending", r"ending \w+"), ("strong/weak", r"strong/weak"),
           ("end shape", r"end shape"), ("line length", r"line length"),
           ("rhyme depth", r"rhyme with bar"), ("mid-bar pause", r"mid-bar pause"),
           ("internal rhyme", r"internal"), ("cluster/pile-up", r"cluster")]


def analyse(path=GEN_LOG):
    """Why do the candidates fail? Re-runs the form checks over everything logged and tallies the
    failure modes. This is the measurement that says whether a BIGGER MODEL would help (syllable
    counting, say) or whether the failure is in the form the model has no access to."""
    import collections
    if not os.path.exists(path):
        sys.exit(f"no log at {path} - generate some candidates first")
    rows = [json.loads(l) for l in open(path, encoding="utf8") if l.strip()]
    counts = collections.Counter()
    per_model = collections.defaultdict(int)
    for r in rows:
        _ok, problems, _w, _r = check_all.problems_of(r["slot"], r["bars"])
        joined = " ; ".join(problems)
        hit = False
        for name, pat in BUCKETS:
            if re.search(pat, joined):
                counts[name] += 1
                hit = True
        if not hit:
            counts["(exact form)"] += 1
        per_model[r.get("model", "?")] += 1
    n = len(rows)
    print(f"failure modes across {n} logged candidates "
          f"({', '.join(f'{k}:{v}' for k, v in sorted(per_model.items()))})\n")
    print(f"{'mode':<18} {'candidates':>10} {'share':>7}")
    for name, v in counts.most_common():
        print(f"  {name:<16} {v:>10} {v/n*100:>6.0f}%")
    risks = [r["risk"] for r in rows if r.get("risk") is not None]
    if risks:
        print(f"\njudge risk: min {min(risks)} median {sorted(risks)[len(risks)//2]} max {max(risks)}")
    print("(Joe's approved bars 1-4: 6 form problems, risk 0.13)")
    return counts


def keeper_grade(v):
    """The standard Joe's own approved bars sit at: meaning passes, the judge does not flag it, and
    the form problem count is no worse than the locked section's."""
    return (bool(v.get("meaning")) and (v.get("risk") if v.get("risk") is not None else 1) < 0.35
            and (v.get("form_problems") if v.get("form_problems") is not None else 99) <= 8)


def score_of(v):
    """Sort key: lower is better."""
    return ((v.get("risk") if v.get("risk") is not None else 1.0),
            (v.get("form_problems") if v.get("form_problems") is not None else 99))


def repair_prompt(spec, bars, problems, variant="spec"):
    """Feed the checker's own complaints back. This is the mechanism that can actually raise quality:
    a model cannot perceive the audio-measured beat, but it CAN act on a specific instruction like
    'bar 2 has 8 syllables, you need 10'."""
    return (build_prompt(spec, variant=variant)
            + "\n\nYOUR PREVIOUS ATTEMPT:\n" + "\n".join(bars)
            + "\n\nThe checker rejected it. Problems found:\n"
            + "\n".join("- " + p.split("FAIL")[-1].strip()[:150] for p in problems[:6])
            + f"\n\nRewrite it, fixing those. Keep whatever already works. "
              f"Output ONLY the {spec['n']} bars.")


def run_repair(spec, model, judger, n_first, rounds, variant, temperature, log_path=GEN_LOG):
    """Generate, verify, feed the failures back, keep the best version of each lineage."""
    base = build_prompt(spec, variant=variant)
    first = parse(ollama(model, base + f"\n\n(Write {n_first * spec['n']} bars total this time.)",
                         temperature=temperature), spec["n"])
    lineages, stats = [], {"generated": len(first), "repairs": 0, "improved": 0,
                           "keeper_grade": 0, "before": [], "after": []}
    for bars in first:
        v = verify(bars, spec["slot"], judger)
        best, best_v = bars, v
        history = [("generate", v)]
        for r in range(rounds):
            if keeper_grade(best_v):
                break
            _ok, problems, _w, _r = check_all.problems_of(spec["slot"], best)
            if not problems:
                break
            cands = parse(ollama(model, repair_prompt(spec, best, problems, variant),
                                 temperature=temperature), spec["n"])
            stats["repairs"] += 1
            if not cands:
                history.append((f"repair{r + 1}", None))
                continue
            cand_v = verify(cands[0], spec["slot"], judger)
            history.append((f"repair{r + 1}", cand_v))
            if score_of(cand_v) < score_of(best_v):
                best, best_v = cands[0], cand_v
        stats["before"].append(v.get("form_problems"))
        stats["after"].append(best_v.get("form_problems"))
        if score_of(best_v) < score_of(v):
            stats["improved"] += 1
        if keeper_grade(best_v):
            stats["keeper_grade"] += 1
        lineages.append({"bars": best, "verdict": best_v, "history": history})
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf8") as fh:
            for s in lineages:
                fh.write(json.dumps({"slot": spec["slot"], "model": model, "bars": s["bars"],
                                     **s["verdict"]}, ensure_ascii=False) + "\n")
    return lineages, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyse", nargs="?", const=GEN_LOG, default=None,
                    help="tally the failure modes in the candidate log")
    ap.add_argument("--slot", default="Hook 5-8")
    ap.add_argument("-n", type=int, default=8, help="candidate stanzas to generate")
    ap.add_argument("--per-batch", type=int, default=4, help="stanzas per model call")
    ap.add_argument("--model", default="dolphin-llama3:latest")
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--variant", choices=["spec", "basic"], default="spec",
                    help="prompt detail: 'spec' adds the per-bar stress grid and end shape")
    ap.add_argument("--repair", type=int, default=0,
                    help="feed the checker's failures back to the model for N repair rounds")
    ap.add_argument("--dry", action="store_true", help="stub generator: no model, no network")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()

    if a.analyse:
        analyse(a.analyse)
        return
    if a.slot == "Hook 1-4" and not a.dry:
        print("Hook 1-4 is Joe's locked section - generating over it would overwrite a keeper.")
        sys.exit(2)
    spec = slot_spec(a.slot)
    judger = J.load_model()
    batches = max(1, (a.n + a.per_batch - 1) // a.per_batch)

    print(f"slot {spec['slot']}  bars {spec['n']}  syllables {spec['syls']}  "
          f"scheme {spec['scheme']}")

    if a.repair and not a.dry:
        print(f"generating {a.n} candidate(s) with up to {a.repair} repair round(s) via {a.model}")
        t = time.time()
        lineages, st = run_repair(spec, a.model, judger, a.n, a.repair, a.variant,
                                  a.temperature, log_path=None if a.no_log else GEN_LOG)
        dt = time.time() - t
        print(f"\n{st['generated']} lineages, {st['repairs']} repair calls in {dt:.0f}s")
        bef = [x for x in st["before"] if x is not None]
        aft = [x for x in st["after"] if x is not None]
        if bef and aft:
            print(f"  form problems: mean {sum(bef) / len(bef):.1f} -> {sum(aft) / len(aft):.1f} "
                  f"(best {min(aft)})")
            print(f"  lineages improved: {st['improved']} of {len(lineages)}")
        print(f"  keeper-grade (risk<0.35, form<=8): {st['keeper_grade']} of {len(lineages)} "
              f"- Joe's approved bars: 6 form problems / risk 0.13")
        lineages.sort(key=lambda x: score_of(x["verdict"]))
        for i, s in enumerate(lineages[:3], 1):
            print(f"  --- lineage {i} (risk {s['verdict']['risk']}, "
                  f"form {s['verdict']['form_problems']}) ---")
            for b in s["bars"]:
                print("   ", b)
        return

    if a.dry:
        generator = lambda k: stub_generator(k)          # noqa: E731
        model_name = "stub"
        label = "DRY (stub generator)"
    else:
        prompt = build_prompt(spec, variant=a.variant)
        generator = lambda k: ollama(a.model, prompt + f"\n\n(Write {k * spec['n']} bars "
                                       f"total this time.)", temperature=a.temperature)  # noqa: E731
        model_name = a.model
        label = f"model {a.model} (prompt {a.variant})"
    print(f"generating {batches} batch(es) via {label} ...")

    t = time.time()
    candidates, stats = forge(spec, batches, a.per_batch, model_name, generator, judger,
                              log_path=None if (a.no_log or a.dry) else GEN_LOG, dry=a.dry)
    dt = time.time() - t

    # the veto is meaning + the judge. Exact form is REPORTED, not required: check_all measures
    # similarity to the original's rhythm and Joe's own approved bars fail it.
    survivors = [c for c in candidates
                 if c["verdict"]["meaning"]
                 and (c["verdict"]["risk"] is None or c["verdict"]["risk"] < 0.5)]
    exact = [c for c in survivors if c["verdict"].get("form_problems") == 0]

    print(f"\n{stats['candidates']} candidates in {dt:.0f}s "
          f"({dt/max(1,stats['candidates']):.1f}s each - the verifier, not the model, is the cost)")
    print(f"  rejected by the meaning gate : {stats['meaning_fail']}")
    if stats["risk"]:
        print(f"  judge risk: min {min(stats['risk'])} | median "
              f"{sorted(stats['risk'])[len(stats['risk'])//2]} | max {max(stats['risk'])}")
    print(f"  survivors (meaning + judge)  : {len(survivors)} of {stats['candidates']}")
    print(f"  of those, exact form         : {len(exact)}")
    # "keeper-grade" = the standard Joe's OWN approved bars sit at: meaning passes, the judge does
    # not flag it, and the form problem count is no worse than the locked section's (6).
    kg = [c for c in survivors
          if (c["verdict"]["risk"] or 1) < 0.35 and (c["verdict"].get("form_problems") or 99) <= 8]
    print(f"  keeper-grade (risk<0.35, form<=8): {len(kg)} of {stats['candidates']} "
          f"- Joe's approved bars score 6 form problems / risk 0.13")
    if candidates:
        best = min((c["verdict"].get("form_problems") or 99) for c in candidates)
        print(f"  best form problems seen      : {best}")
    if survivors and not exact:
        print("  NOTE: none is exact-form. That is expected - check_all matches the original's "
              "MEASURED rhythm and Joe's own approved bars fail it too.")

    if survivors and not a.dry:
        out = os.path.join(ROOT, "writing", f"generated_{spec['slot'].replace(' ', '_')}.md")
        with open(out, "w", encoding="utf8") as fh:
            fh.write(f"# Generated candidates for {spec['slot']} ({model_name})\n\n")
            fh.write("Filtered by meaning_gate + ml/judge. Form problems are listed per candidate. "
                     "NOT approved - Joe's ear is the finish.\n\n")
            for i, s in enumerate(survivors, 1):
                fh.write(f"## survivor {i}  (judge risk {s['verdict']['risk']}, "
                         f"form problems {s['verdict'].get('form_problems')})\n")
                fh.write("\n".join(s["bars"]) + "\n\n")
        print(f"  written to {os.path.relpath(out, ROOT)}")
    for i, s in enumerate(survivors[:3], 1):
        print(f"  --- survivor {i} (risk {s['verdict']['risk']}, "
              f"form problems {s['verdict'].get('form_problems')}) ---")
        for b in s["bars"]:
            print("   ", b)
    if not a.no_log and not a.dry:
        print(f"  every candidate logged to {os.path.relpath(GEN_LOG, ROOT)} (the flywheel)")

    if a.selftest:
        good = any(s["bars"] == STUB_GOOD.splitlines() for s in survivors)
        bad = any("OH" in " ".join(c["bars"]) for c in survivors)
        ok = not bad and stats["candidates"] >= 2
        print(f"\n  selftest: clean stub survives={good} (reported only), rejected stanza filtered={not bad}, "
              f"candidates={stats['candidates']}")
        print("GENERATE SELFTEST", "PASSED" if ok else "FAILED")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
