# Hook 9-16 — v1 (written 11 Oct 2026, main thread) — SUPERSEDED by hook_9-16_v2.md

First bars **written** rather than recombined by the forge. Every check run; numbers below.

## The 8 bars

    1  Rain in Bergen, then the bar
    2  Skal from the in-laws, bizarre
    3  The coast is one road, all the way
    4  Took the ferry, tunnel, and the car
    5  Load up, load up, load up, and then drive half the night
    6  Skint the next day, mate
    7  Boomtown, the souk, three in a row
    8  Then all back the same, anyway

## Measured

| check | result |
|---|---|
| scheme, tested gate-style (`forge._scheme_ok`) | **PASS** |
| by-ear scheme `AABACBDB` | **exact** (ends `ɑː ɑː eɪ ɑː ɑː-aɪ eɪ iː-əʊ eɪ`) |
| syllables vs frame `[7, ?, 8, 9, 12, 5, 8, 7]` | `[7, 7, 8, 9, 12, 5, 8, 8]` — 7 of 8 exact |
| `meaning_gate` hard fails | **0** |
| `coherence_gate` hard fails | **0** |
| `check_all` problem count | **18** (Joe's approved bars 1-4: 6; best mined quad: 4) |
| judge risk | **0.538** (was 0.682 before the fixes; assembled candidates 0.79-0.83; approved bars 0.13) |
| judge per-bar | 0.53 0.81 0.54 0.61 **0.93** 0.36 0.43 **0.08** |

Bar 8 (0.08) scores below the approved mean of 0.13. Bars 5 and 2 do not.

## How the frame was recovered

The map's rows give L9-16 as `i-ah* / oo-ah* / ay-a / a-ah* / a-i* / i-ay* / ee-ow* / i-ay*` with by-ear
`AABACBDB`. Reading those tails as sounds gives the end families used here: three `ɑː`, three `eɪ`,
one `ɑː→aɪ`, one `iː→əʊ`. Local words that fit: *bar, car, bizarre* (`ɑː`); *way, mate, anyway* (`eɪ`);
*far cry* (`ɑː→aɪ`); *three in a row* (`iː→əʊ`).

True material used: Bergen (in-laws, skål, west-coast single road, fjord ferries and tunnels),
Boomtown (August), Marrakesh souk.

## The two techniques that landed

- **bar 7** cashes `three in a row` with the payoff word (`row`) in the rhyme slot, over two real places.
- **bar 6 / bar 8** end on conversational tags (`mate`, `anyway`) that also carry the `eɪ` rhyme — the
  same trick the approved block uses when it ends a bar on `though`.

## What is still weak (honest read)

- bars 3 and 4 are inert reportage: true and deadpan, but they cash nothing.
- bar 5 is the slot's 12-syllable triple (`load up` x3) and says almost nothing; it is technique without content.
- bar 2's `bizarre` is a lazy one-word verdict, the kind of thing rule 1 warns about.

## Judge calibration finding (do not re-learn this)

`ml/judge.py` **cannot fairly score this slot**. Attribution of the 0.538:

- word-level signal is negligible (max `|coef|` ~0.014) except that the model partly memorised the
  approved bars' own vocabulary;
- the top drivers are structural: `end_tag` (-0.62), `scheme_letters` (-0.58), `in_band` (-0.51),
  `clash` (-0.47), `payoff_slot` (-0.33), `domestic` (-0.33);
- `end_tag` = "the bar ends on a conversational tag" (`like, nah, then, mind, though, anyway, innit,
  mate, right, yeah`). The approved block is Hook 1-4, whose ends are all `əʊ` and which contains exactly
  one tagged bar, so `end_tag` is largely "does this block resemble the one positive block".

Consequences: (a) the 0.13 reference is a Hook 1-4 number, not a general quality bar; (b) bar 5's 0.93 is
out-of-distribution — the judge has no positive example of a 12-syllable bar, and it stayed 0.93-0.99
across four rewrites, so rewriting it is not evidence-driven; (c) cross-slot comparisons are invalid and
were what the forge was doing when it scored assembled 9-16 blocks 0.79-0.83.
