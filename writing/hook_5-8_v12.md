# Hook 5-8 v12: image-led, with the register flip and the pun landing on the rhyme (12 Oct 2026)

```
5  Cold beer on the house in Porto
6  Bought it by the barrel off the sellers
7  Left the vinho in the cellars
8  Might take the long way to Oslo
```

## What each bar says

| bar | what it says | job (the original's own line job) |
|---|---|---|
| 5 | free beer in Porto; *on the house* cashed, and the city pays off the drink | place + transaction register |
| 6 | bought it by the barrel off the sellers | the business line that sets the pair up |
| 7 | left the wine in the cellars — bought a barrel and walked off | the register flip, and the payoff |
| 8 | modal understatement, and out to the next place | closer place outside the frame |

## Why this block and not v11

| | v11 (Porto / totals / folders / Oslo) | v12 |
|---|---|---|
| by-ear scheme ABBA | all pairs rhyme | **all pairs rhyme (1.00 / 1.00)** |
| perfect-rhyme pair that changes register | none (totals ~ folders, both admin) | **sellers / cellars — homophones, trade -> drink** |
| admin word in the rhyme slot | 2 (`totals`, `folders`) FAIL | none |
| local word per 4 bars | 0 FAIL | 1 (`vinho`) |
| image chain | 1 (beer -> port -> glass), **not landing** | 1 (beer -> barrel -> vinho -> cellars), **LANDS ON THE RHYME** |
| internal rhyme bar | 0 (original 1) FAIL | 1 (`left` ~ `cellars`) |
| `check_all` problems | **3** | **1** |

The one surviving flag is bar 6's strong/weak pattern percentage, and it survives every rewording
tried (six variants, 50-60% either way). It is the metric already measured as non-discriminating on
12 Oct: Joe's **approved** bars score 50/50/50/33% on it and a bar he rejected scores 62%. It is a
note, not evidence.

## The devices, read by the new detectors

```
imagery: CHAIN drink: beer(1) -> barrel(2) -> vinho(3) -> cellars(3)   LANDS ON THE RHYME
ear:     ECHO frame S..L (EH): sellers(2) / cellars(3)   <- the flip, now visible to the ear tool
ear:     0 pivots, 0 drums, 0 accumulations, 0 crutches
scheme:  A pair 5-8: 1.00 | B pair 6-7: 1.00 | ALL PAIRS RHYME
meaning: PASS      coherence: PASS      regression: PASS
```

## Truth flags

- Porto 2023 is real and so are the port cellars, the barrels and the glasses (material/place_specifics.md).
- `bought it by the barrel off the sellers` and `left the vinho in the cellars` are **(persona)** — the
  transaction is invented; only the drinking is documented.
- Norway June 2024 is real, so the Oslo turn is true; `the long way` is **(persona)**.
- Weakest bar: **6**. It is the only bar whose main job is to set up the pair. Its sense is clean and
  its register is right, but if the block gets cut, this is the one to cut.

## Two instrument fixes made while writing this (both were blocking, both validated)

1. **`imagery.py` DRINK field was the glass only** (beer, port, vinho, bottle). A chain running
   beer -> barrel -> cellars was invisible, so the one image the Porto material actually offers could
   not be seen. Added the storage half (cellar, barrel, cask, keg) and the verbs of consumption, the
   same way the PARCEL field already carries depot/warehouse/loads. Measured: no change to the
   original's own counts (4 chains, 2 landing over 19 quads) — it was a coverage gap, not a threshold.
   The rate previously recorded in STATE.md (5 chains, 3 landing) was stale; corrected.
2. **The transactional local words had no pronunciation at all.** `vinho`, `cerveja`, `conta`, `takk`,
   `grazie`, `yamas` and ~26 others were OOV, so any bar built on one read as a vowel blob: no
   consonants, no stress, no stops, unrhymable. 32 OVR entries added from toolkit/local_words.txt,
   anglicised on purpose. This unblocks the whole code-switching supply, not just this block.

`calibrate.py` PASSED after both changes.
