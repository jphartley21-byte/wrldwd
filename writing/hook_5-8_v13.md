# Hook 5-8 v13: full end-rhyme carpet, and the instrument that was blind to it (12 Oct 2026)

```
5  Cold pint on the house in Porto
6  Rolled the lot home and nothing to borrow
7  Down the cellars for the vinho
8  Might take the long way to Oslo
```

## What each bar says

| bar | what it says | job |
|---|---|---|
| 5 | a pint on the house in Porto; *on the house* cashed, `pint` is the British word in a foreign bar | place + transaction register |
| 6 | rolled the lot home and borrowed nothing; *the lot* cashed | the business line the pair sits on |
| 7 | down the cellars for the wine — the local word, and the payoff | the register flip's second half |
| 8 | modal understatement, out to the next place | closer place outside the frame |

## Joe's verdict on v12 was right: it was a regression, and the profile was why

He said the original's four end words (Lagos / favours / flavours / Vegas) all rhyme near-perfectly and
ours did not. Measured: the original's block rhymes **all six pairs** (0.80-1.00), Joe's locked bars 1-4
rhyme all six at 1.00, and **v12 rhymed two**. The checker only demanded the pairs the by-ear scheme names,
so a block could pass with two thirds of its sound relationships missing.

| | carpet (pairs of 4 bar-ends) | min pair | internal rhyme | allit bars | multisyl | `check_all` |
|---|---|---|---|---|---|---|
| ORIGINAL Hook 5-8 | **6/6** | 0.80 | 8 | 1 | 2 | — |
| Joe's locked bars 1-4 | **6/6** | 1.00 | 16 | 3 | 17 | 6 (all grid/pattern) |
| v11 | 2/6 | 0.00 | — | — | — | 3 |
| v12 (rejected) | **2/6** | 0.00 | 5 | 1 | 2 | 3 |
| **v13** | **6/6** | **1.00** | **12** | 1 | 6 | **1** (bar 6 pattern %) |

Bar 6's strong/weak pattern percentage is the same metric already measured as non-discriminating: the
locked bars score 50/50/50/33% on it and a bar Joe rejected scores 62%.

## Four instrument faults found by this complaint (all fixed, `calibrate` PASSED)

1. **THE PROFILE WAS STALE.** `benchmark/original_profile.json` had been written before recent fixes, so
   the gates were calibrated against the wrong benchmark:
   - internal rhyme density for Hook 5-8: **4 recorded, 8 actual** — the gate demanded half of what the
     original does, which is exactly why our 5 passed;
   - its rhyme scheme: **`abbb` recorded, `aaaa` actual** — the original's block is a carpet and the file
     said it was not;
   - its rhyme map: **3 links recorded, 8 actual** — five of the original's sound relationships were not
     in the benchmark at all.
   Rebuilt from the original with the current functions. This is the single biggest reason v11 and v12
   were shown to Joe with PASS verdicts.

2. **THE CARPET IS NOW A GATE.** `match.carpet_of()` counts how many pairs of bar-ends rhyme; a 4-bar hook
   block is held to all of them, because both of the original's are 6/6 and so are the locked bars. The
   original's 8-bar blocks are compared as a share (its own range is 14%-100%, since they change family
   mid-stanza). v12 fails this gate; the locked bars and v13 pass.

3. **"DO THESE TWO BARS RHYME" WAS TWO DIFFERENT MEASURES.** The per-bar loop used a strict key comparison
   while the by-ear scheme and the carpet used `best_end`, so a pair could score 1.00 on the carpet and
   FAIL the per-bar check in the same run — which is what happened to Porto/Oslo (both end /əʊ/, the ear
   accepts them, the locked bars rhyme the same way). One measure now. The depth clause that sat on the
   strict comparison is gone with it: it counted a shared *stressed* vowel as depth and a shared *final*
   vowel as nothing. Multisyllabic depth is gated separately, by the quad's multisyl count.

4. **`cmudict` MARKS THE -ow/-o FAMILY INCONSISTENTLY, WHICH BREAKS THE HOOK'S END SHAPE.** It gives the
   final syllable of *borrow, shadow, willow, potato, tobacco, tornado, solo, photo, tempo, kilo, memo* as
   secondary stress (OW2) and the identical syllable of *sorrow, follow, hollow, yellow, window, burrow,
   polo, demo, weirdo* as unstressed (OW0). The hook's end shape is `|Sw` — the locked bars and the
   original's own both — so an OW2 final made a perfect rhyme word read as two strong syllables and the
   bar FAIL as if it were wrong. 14 OVR corrections added; the original never uses those words, so its
   profile is unaffected.

Also demoted to notes, on the same evidence rule: the **opening-to-end rhyme links** and the rhyme-strength
map that carries them. Joe's locked bars fail one of those links (bar 4's opening vs bar 2's end, 0.45
against the original's 0.83) — a link his ear does not require cannot be a gate.

## Devices, read by the new detectors

```
imagery: CHAIN drink: pint(1) -> cellars(3) -> vinho(3)  LANDS ON THE RHYME
         BRIDGE 'pint' belongs to ['British-everyday', 'drink']  <- the register collision, visible
ear:     0 pivots, 0 drums, 0 echoes, 0 accumulations, 0 crutches
scheme:  A pair 5-8: 1.00 | B pair 6-7: 1.00 | ALL PAIRS RHYME
carpet:  6/6 (min 1.00) | internal rhyme 12 vs the original's 8 | allit bars 1 vs 1
meaning: PASS   coherence: PASS   regression: PASS (vinyl register, no admin in a rhyme slot)
```

## Truth flags and the weak spot

- Porto 2023, the port cellars, the barrels and the glasses are real (material/place_specifics.md).
- `rolled the lot home and nothing to borrow` is **(persona)** — the transaction is invented.
- Norway June 2024 is real, so the Oslo turn is true; `the long way` is **(persona)**.
- Weakest bar: **6**. It carries the densest internal run (Rolled / lot / home / borrow) and the flip,
  but "nothing to borrow" is the plainest thing the block says. Bar 7 is the strongest.
- Alliteration is now one alliterating bar (`pint` / `Porto`), the same as the original's own block; the
  locked bars carry three. Raising it is a craft pass, not a word substitution: it needs an object whose
  onset repeats with the place.
