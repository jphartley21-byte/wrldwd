# Hook 5-8 v10: the Ljubljana bug fixed at the root (12 Oct 2026)

```
Cold beer on the house in Porto
Port in the glass and a page of totals
Just numbers and dates in folders
Might take the long way to Oslo
```

| measure | this block | the original's 5-8 | v9 (rejected by Joe) |
|---|---|---|---|
| bars passing the per-bar form check | **4 of 4** | 4 of 4 by definition | 3 of 4 |
| block form verdict | **1 fail** (aggregate `internal_bars` only) | -- | 3 fails |
| rhyme scheme vs the spec (A C C A, Joe's own correction) | **PASS** | PASS | PASS via a false positive |
| rhyme strength map (3 measured links) | **PASS** | PASS | FAIL 2 of 3 |
| syllables | **8 / 10 / 8 / 8**, exact | 8 / 10 / 8 / 8 | exact |
| rhyme-slot payload (mean zipf, lower = less obvious) | **3.43** | 4.04 | 3.91 |
| places named | Porto, Oslo | 2 | 1 |
| meaning / coherence problems | 0 / 0 | -- | 0 / 1 |

## Why this block exists

Joe asked how Ljubljana got into v9 when it does not rhyme with the other end words. Measured answer:

* v9's A-pair was `dot` ~ `Ljubljana`, graded **0.80**, above the 0.78 scheme floor.
* The original's own A-pair in the hook is a **slant of the same shape** (`ɒ` against a weak `ə`), and the
  metric ranks our non-rhyme *higher* than it ranks the original's real link (`Jamaica` ~ `Mainz` = 0.85).
* So no threshold can separate them. The metric is now honest about that: `match.py --selftest` asserts
  12 pairs by ear and prints the 13th as **unspecified** (`toolkit/tests/rhyme_pairs.txt`).

The root cause was not the grader. It was that a **weak-tailed place name was sitting in the rhyme slot**.
The fix is structural: every end word in this block is now a word whose *stress falls on the rhyme*, and
the places are named **inside** the bar, where they cannot wreck the rhyme. All three end links measure
1.00, and the places still get named (2, against the original's 2).

## The wordplay (rule 1)

* Bar 1 cashes the stock phrase **"on the house"** literally, and the place pays it off: *Porto* is where
  port comes from, so bar 2's *port in the glass* is the same word twice, the second time as a noun.
* Bar 3 is the flat illicit register, and it *implies* it rather than saying it: the folders carry
  numbers and dates and nothing else. "No names" was stated in the first version; Joe rejected that
  line on 12 Oct as unclear and badly flowing, so the claim moved under the surface. See the note below.
* Bar 4 is the modal exit, the original's own closer device, with a true place outside the frame.

## Tool changes that produced it (all locked by tests)

1. `phon.py`: diphthong glide similarity (aɪ/eɪ), right coda comparison, weak-tail rules. The rhyme label
   set went from 4 of 10 wrong to **1 of 14** wrong (that one is the documented metric limit above).
2. `match.py`: the per-bar loop and the rhyme-strength map now demand **only the pairs Joe's by-ear scheme
   actually pairs**. Benchmarked spec line 18 is *A C C A*; the original's own keys misread it as `a b b b`
   and were demanding that our bars 2 and 4 rhyme — a rhyme the benchmark never asks for.
3. `calibrate.py`: prints IPA safely instead of crashing, and asserts the rhyme label set.
   **Calibration PASSED**, all six of Joe's rejected stanzas still caught.

## Kept / rejected

* Kept from Joe's own draft: *Cold beer on the house in Porto* (his line, and the block's best pun).
* Rejected here: `A glass of port and a page of the dough` (hard ending where the original has a soft one);
  `No names just numbers in the folders` (9 syllables); `One week in Oslo with locals` (killed the A-pair:
  `Porto` ~ `locals` = 0.00, which is the very fault Joe flagged).
* Bar 3, after Joe's 12 Oct note ("not sure what this means, and 'numbers on folders' doesn't flow well"):
  seven replacements tested. `No names just numbers on folders` (unclear, ungrammatical, three stresses
  stacked); `Numbers and dates in the folders` and `No names and no Christmas bonus` (both fail the beat
  grid); `Boxes go straight to the owners` (best S/w pattern at 75%, but off the grid -- kept as the
  by-ear alternative); `Only numbers and dates in folders` (9 syllables). Chosen: `Just numbers and dates
  in folders` -- 8 syllables, on the beat grid, rhymes with `totals` at 1.00, grammatical, and it makes
  the illicit point by omission.
* Still open: bar 6 and bar 7 do not reproduce the original's *off-beat* stress pattern (70% and 62% same).
  Their lengths, end shapes, rhyme steps and (now) beat grids all match. **This measure is a note, not a
  gate**: on the only labelled data that exists it ranks Joe's own approved bars 1-4 at 50/50/50/33%
  against 62% for a bar he rejected, so it is anti-correlated with his ear. Recorded 12 Oct after Joe asked
  why the rejected "numbers on folders" line got through — the answer being that this flag *did* fire and I
  overrode it instead of showing it to him. Every flag is now shown per bar, next to the line.
