# ml/: the human-gate layer (a screen for the 17 criteria no tool can decide)

`toolkit/check_all.py` measures the 24 machine-decidable rubric criteria. `benchmark/gate_coverage.md`
is explicit that **17 criteria are HUMAN gates** - cringe, does the joke land, plain-beats-clever,
nonchalance, poster test, character by words alone - and that a measured PASS is never a finish.

This folder attacks that gap the only honest way available: it scores a bar's *risk of being rejected*
from (a) a rule prior transcribed from Joe's own rejections and (b) a small fitted diction model over
his verdicts. It **ranks and explains**; it does not judge. A low risk is not "good".

## Files

| File | What it does |
|---|---|
| `domain.py` | Joe's rejection reasons as a lexicon + the reason -> gate map + proxy lexicons (shout, joke, domestic, AI-tell) |
| `features.py` | one numeric vector per bar from the **existing** toolkit (meaning_gate, craft_scan, rubric_score, sense_checks, flow_check); also the shared bar cleaner |
| `build_dataset.py` | mines the repo's verdict history into `data/dataset.jsonl` |
| `train_judge.py` | fits the judge, prints honest metrics, saves `models/judge.joblib` |
| `judge.py` | **the working tool**: `python ml/judge.py FILE\|-` -> per-bar risk + drivers |
| `evaluate.py` | the acceptance gate (contract + held-out sanity + discrimination); exits 1 on failure |
| `export_pairs.py` | SFT/DPO data for a future writer model |
| `generate.py` | **local candidate generator**: N stanzas from a local Ollama model, filtered by meaning_gate + check_all + the judge, survivors written out; every candidate logged to `data/generated.jsonl` |
| `lora/` | the writer-model recipe and a `preflight.py` that says when (and if) it is trainable |

## Workflow

```
python ml/build_dataset.py     # mine verdicts -> ml/data/dataset.jsonl
python ml/train_judge.py       # fit -> ml/models/judge.joblib  (prints the honest metrics)
python ml/evaluate.py          # MUST PASS before trusting the judge
python ml/judge.py FILE|-      # score bars in the drafting loop
```

Add the judge to a review pass, after the form checks:

```
python toolkit/check_all.py --slot "Hook 5-8" -     # the 24 measurable criteria
python toolkit/meaning_gate.py -                    # does the bar say anything
python ml/judge.py -                                # the 17 human gates: risk + why
```

## Generating candidates locally (the GPU)

```
python ml/generate.py --slot "Hook 5-8" -n 20                    # local model via Ollama
python ml/generate.py --slot "Hook 5-8" -n 20 --model dolphin-llama3:latest
python ml/generate.py --slot "Hook 1-4" --dry --selftest         # offline, no model needed
```

The loop is `candidate -> meaning_gate -> check_all -> ml/judge -> survivors`, and it exists to buy
**volume**, not quality: a local 8B produces stanzas at ~147 tok/s for free, the filters run on CPU,
and Joe sees only what survives. Measured on the RTX 5070 Ti: ~2.2 s per candidate, dominated by the
verifier, not the model.

Survivors go to `writing/generated_<slot>.md`. Every candidate and its verdict is appended to
`ml/data/generated.jsonl` - that is the flywheel: the model's failures become future training data.

**Important, read before trusting a "0 survivors" result.** `check_all` is a *similarity-to-the-original's-audio*
gate, not a quality gate - **Joe's own approved bars 1-4 fail it** (`8 syllables vs the original's 9`,
plus stress-grid and end-shape misses). So `generate.py` uses it as a RANKING signal and reports
`form problems` per candidate; the VETO is the meaning gate plus the judge. Gating on exact form
would reject bars Joe would approve.

## The flywheel (how the judge gets better)

The judge is data-starved by construction: one locked stanza, the phrases Joe kept, six rejected
fixtures and the agents' own "weakest bar" notes. **Every new verdict is a row.** To add one, either
let `build_dataset.py` pick it up from a fixture / `keepers.json` / `contenders.md`, or edit
`ml/data/dataset.jsonl` directly (one block per line, `"label"` in
`accept | like | park | reject | weak_neg`). Then re-run `build_dataset` -> `train_judge` -> `evaluate`.

Prefer adding **positives**: the model's real weakness is positive examples, not negatives.

## Honest limits (do not skip this)

- With one positive block, **cross-validated classification is degenerate**. `train_judge.py` says so
  and reports rank separation plus a leave-one-positive-out test instead of faking an AUC.
- The contract in `evaluate.py` is *nearly in-sample*. The only genuine held-out evidence is the
  **park** stanza (Joe's "not bad, it's a contender"), which is never trained on and lands between
  accept and reject: `accept 0.13 <= park 0.59 <= reject 0.94`.
- The discrimination check exists because a screen that calls everything a reject is useless. Today
  ~49% of the ~420 never-judged bars score as LAND, so the judge is not collapsed.
- **The original's lyrics are never read here** (CLAUDE.md rule 4). Only repo files are read, so no
  model trained from this data can memorise the original.

## Rule 6 note

No writer or judge *agents* are launched (rule 6: subagents burned 128k tokens each and returned
nothing). This layer is cheap, local, offline and deterministic - it is the opposite of that failure
mode: it makes the drafting loop tell Joe *why* a bar is risky instead of asking him to be the filter.

## `meaning_judge.py` - the paraphrase test, done by a local model (13 Oct 2026)

Joe asked whether AI can now gate *meaning*, which nothing in `toolkit/` really does: the gates police
sound (flow, rhyme, syllables) and the meaning gate is a floor. This tool asks a local Ollama model to
**restate** each bar as a plain sentence and to say what the bar is: an action, a stance, a scene, a
**summary** (a list of things with nothing happening) or phatic. The paraphrase is the evidence; the
label is the verdict.

```
python ml/meaning_judge.py --selftest                 # offline: parser + verdict rule (in calibrate.py)
python ml/meaning_judge.py --bars writing/full_draft_v26.md     # a report on a draft
python ml/meaning_judge.py --model llama3:latest      # the labelled set: accuracy, then every error
```

Measured on a 14-bar labelled set (8 bars Joe wrote or that pass every gate; 6 of the inventory bars
he rejected as "nothing verses"); `--model llama3:latest` scores **93%** - 6 of 6 lists caught, 7 of 8
real bars passed, and the one error is a bar it paraphrased correctly and then mislabelled. The
13B fiction model (`nollama/mythomax-l2-13b:Q4_K_M`) scores 71% and mostly *echoes* the bar instead of
restating it, so it is not usable. On `full_draft_v26.md` llama3 flags 17 of 76 bars as listed
nonsense, 5 of which are the bars the toolkit's inventory rule also catches; of the other 12, roughly
half read to me as real (a journey, a price, an outcome) and half as dead. **So this is a sifter, not
a gate**: it turns 76 bars into 17 for a human to adjudicate, and its paraphrases show *why*.
Keep one model resident on the 16 GB card; 76 bars took about 5 minutes at ~4 s each.

