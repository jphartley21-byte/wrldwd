# Hook 9-16 — v2 (11 Oct 2026, main thread) — supersedes v1

Bar 5 rewritten (content + tag), bars 6 and 8 given tag endings, bars 1-4 unchanged from v1.

## The 8 bars

    1  Rain in Bergen, then the bar
    2  Skal from the in-laws, bizarre
    3  The coast is one road, all the way
    4  Took the ferry, tunnel, and the car
    5  Cash, cash, cash, and then we drive it half the night, right
    6  Skint the next day, mate
    7  Boomtown, the souk, three in a row
    8  Then back the same, anyway

## Measured

| check | v1 | v2 |
|---|---|---|
| scheme, tested gate-style | PASS | **PASS** |
| by-ear scheme `AABACBDB` | exact | **exact** |
| syllables vs frame `[7, ?, 8, 9, 12, 5, 8, 7]` | 7 of 8 were `[7,7,8,9,12,5,8,8]` | **`[7,7,8,9,12,5,8,7]` — exact on every known bar** |
| `meaning_gate` hard fails | 0 | **0** |
| `coherence_gate` hard fails | 0 | **0** |
| `check_all` problem count | 18 | **17** |
| judge risk | 0.538 | **0.442** |
| judge per-bar | 0.53 0.81 0.54 0.61 **0.93** 0.36 0.43 **0.08** | 0.53 0.81 0.54 0.61 **0.15** 0.36 0.43 **0.10** |

Bar 5: 0.93 -> 0.15. Its old text (`load up, load up, load up, and then drive half the night`) was the
slot's 12-syllable triple with nothing in it; `cash, cash, cash` keeps the x3 technique, adds the flat
menace the slot needs, and lands the trailing tag. The four rewrites that kept `load up` all stayed
0.93-0.99, so the improvement is the content, not tuning. (Those numbers are still frame-tainted: the
judge has no positive 12-syllable bar. The bar is kept because it now matches the frame and says something.)

## What was tried and rejected

- **Soft (`~Sw`) ending on bar 3.** The map says L11 should end soft. Every candidate broke the scheme:
  a trailing `it` (e.g. `...and we paid it`) puts an `ɪ` in the rhyme slot and the pair test fails. The
  frame's own soft ending is a trailing schwa (`...paid a`, `...made a`), which needs enjambment into the
  next bar. Left hard for now — it is the one frame deviation in the file, and `check_all` flags it.
- **Internal rhyme + W alliteration on bar 4.** Every candidate cost a syllable and raised risk
  (0.538 -> 0.57-0.63). Bar 4 keeps its plain reading; this is a known technique gap.
- **Bar 2 (`bizarre`).** Best alternative scored 0.76 vs 0.81 but was 8 syllables against a 7 target.
  Kept the frame-exact version; the difference is noise.

## Still weak (honest read)

- bar 3 and bar 4 are inert reportage: true, deadpan, cash nothing.
- bar 2's `bizarre` is a lazy one-word verdict.
- bar 1 is a plain scene-setter.
The best three are 5, 7 and 8 (triple+tag, cashed `three in a row` with the payoff in the rhyme slot,
and the flat tagged closer).
