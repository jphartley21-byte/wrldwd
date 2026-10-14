# Hook 9-16 — v3, PIVOT (11 Oct 2026, main thread)

Fired after Joe rejected both v2 and forge #2 ("Neither of these are good enough"). Pivot changes
**theme** and **structure** together: the back half of the hook is no longer "places I went" but a
**courier's round sheet** — scale (worldwide drops) against an admin register, with a persona who is
unimpressed, blames the map, tips to get through, and refuses ownership. The frame itself supplied the
premise: its end sounds hand you `freight`/`weight` (eɪ), `load`/`road` (əʊ), `supplies`/`price` (aɪ),
`bazaar`/`bar`/`car` (ɑː).

## The 8 bars

    1  Cash in hand and cheap cigar
    2  Second drop's a bazaar, parked the car
    3  Left it on the step, out the way
    4  Tipped him at the border and said ta
    5  Same box, same box, same box, and it's all the same price
    6  Paid him by the weight
    7  Load half gone, and the rest to go
    8  Might do the same again, mate

## Measured (toolkit/trybars.py)

| check | v2 | forge #2 | **v3 (pivot)** |
|---|---|---|---|
| scheme, gate-style | PASS | PASS | **PASS** |
| by-ear `AABACBDB` | exact | near | **exact** (`ɑː ɑː eɪ ɑː aɪ eɪ əʊ eɪ`) |
| syllables vs `[7,?,8,9,12,5,8,7]` | exact | exact | **exact** |
| form problems | 17 | **1** | **13** |
| meaning fails | 0 | 0 | **0** |
| coherence fails | 0 | 0 | **0** |
| judge risk | **0.442** | 0.902 | 0.730 |

## Why this one is not the same shape as the others

Rules 1 and 3 say comedy is character + wordplay, and that a bar existing only for a rhyme, pun or
alliteration fails. v2 and forge #2 are accurate reportage: facts, places, no stance. forge #2 is
especially misleading because its lines are recycled from drafts Joe already rejected
("All the shoes come off at the door", "foot to the floor" are corpus lines), which is exactly why it
scores form 1 — the corpus lines were written against the flow template.

v3 cashes five phrases with the payoff word in the rhyme slot: `cash in hand`, `out the way`,
`the same price`, `by the weight`, `the rest to go`. It takes a stance in every bar (tipped to get
through, wouldn't sign for it, monotony, "might do the same again").

## Honest weaknesses

- **form 13 is mid, not good.** forge #2's 1 shows what a form-clean block looks like; getting there
  without recycling rejected lines is the real work left.
- bar 3 (`Left it on the step, out the way`) is a soft-ending bar where the frame wants hard, and the
  map's L11 wants a *soft* one — this frame wants exactly one and it is not landing in the right slot.
- bar 7 (`Load half gone, and the rest to go`) has the weakest internal rhyme of the eight (1 vs the
  original's 4).
- bar 5's triple is the slot's `x3` technique and it is the only bar with a laugh in it; the rest lean
  on flat register.
- the judge's 0.730 is not evidence against it (see writing/scoreboard_hook.md: the judge penalises
  `block_internal_share`, so it scores MORE internal rhyme as worse).
