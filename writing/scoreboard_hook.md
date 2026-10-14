# Hook scoreboard (11 Oct 2026) — one pass, one instrument

Produced by `python toolkit/trybars.py --slot "<slot>" FILE`. This is the answer to "why weren't we
landing on the best bars": the candidates existed, but two instruments ranked them in *opposite* order
and the pipeline pooled on the wrong one.

## Hook 9-16

| # | block | scheme | syllables vs `[7,?,8,9,12,5,8,7]` | form | meaning | coh | judge |
|---|---|---|---|---|---|---|---|
| 1 | **forge #2** (in the repo since 11 Oct) | PASS | `7,9,8,9,12,5,8,7` **exact** | **1** | 0 | 0 | 0.902 |
| 2 | forge #1 | PASS | exact | 2 | 0 | 0 | 0.860 |
| 3 | hook_9-16_v2 (written 11 Oct) | PASS | exact | 17 | 0 | 0 | **0.442** |
| 4 | hook_9-16_v1 (written 11 Oct) | PASS | 7 of 8 | 18 | 0 | 0 | 0.554 |
| 5 | Q120 (marked "VERIFIED" in pool_v3) | **FAIL** | all off | 18 | 0 | **2** | 0.870 |

## Hook 5-8

| # | block | scheme | form | meaning | coh | judge |
|---|---|---|---|---|---|---|
| 1 | **forge #1** (`Cold beer on the house in Porto`…) | PASS | **4** | 0 | 0 | 0.340 |
| 2 | forge #2 (`Case in the boot, and it's ready`…) | PASS | 11 | 0 | 0 | **0.295** |
| 3 | Q122 (marked "VERIFIED") | PASS | 6 | 0 | 0 | 0.768 |
| 4 | Q119 (marked "VERIFIED") | **FAIL** | 5 | 0 | **1** | 0.806 |

## Why the judge cannot be the objective here

Attribution of forge #2's 0.902 against the reference block (Joe's bars 1-4), from the model's own
coefficients — `coef * (z_candidate - z_reference)`:

    -0.620  end_tag                candidate -0.20  ref +1.09
    -0.604  block_internal_share   candidate +0.59  ref -0.40   <-- MORE internal rhyme, scored worse
    -0.512  in_band                candidate +0.59  ref +0.02
    -0.483  scheme_letters         candidate +0.10  ref -1.02
    -0.471  clash                  candidate -0.18  ref +0.83

Every word-level effect is `<= 0.014` (`'to bordeaux' -0.014`), i.e. the model's verdict has almost
nothing to do with the words. `end_tag` means "the bar ends on a conversational tag" (`though`, `mate`,
`anyway`, `innit`, `right`, `yeah`…): the reference block contains exactly one such bar, and any block
that does not is penalised. `block_internal_share` penalises a candidate for having MORE internal rhyme
than the reference. Both are memorisation of a single positive block, not craft judgement.

Consequence: `KEEP_MAX_RISK = 0.45` in the pipeline threw away every best-form candidate, because the
judge rated the corpus's most frame-accurate blocks 0.86-0.90.

## What the instruments do and do not settle

- **scheme, syllables, form, meaning, coherence** are objective and calibrated (the original passes its
  own profiles; Joe's bars 1-4 score 6 form problems, so form is a target, not a veto).
- **the judge** is a screen with 21 positive rows from one block. It ranks within a slot only if the
  candidates share an end family with the reference. It cannot certify a slot.
- **G1-G6 and the ear** remain the only tests of whether a bar is good.

## Weakest bars to fix first

- 9-16 bar 5 (`Nordic pine with a Nordic nine and Nordic bride`, judge 0.99): a technique carrier —
  alliteration and the x3 job with no proposition in it. Rule G3.
- 9-16 bar 7 / 5-8 endings: the 5-8 candidates all end soft (`s` on every line); the original has 1
  soft ending in 8 there.
- Q120 and Q119 should not be reused: Q120 fails the slot scheme, Q119 fails scheme and coherence.

## 12 Oct 2026 -- the eight never-written bars now exist
Hook 9-16 v6: scheme PASS, form 11, meaning 0, coherence 0, judge 0.869, 4 figures,
syllables exact on frame. Hook 5-8 v3: form 5, 2 figures, keeper place restored.
Best previous 9-16 was v3 (form 13, coherence 1). Joe's own 1-4 at form 6.
