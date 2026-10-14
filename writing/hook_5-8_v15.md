# Hook 5-8 v15 -- rebuilt on a carpet that is genuinely perfect, 13 Oct 2026

## The block (ALL PASS on check_all)

```
5  Cash back on the bier in Zurich
6  Stuck in the black van in all the traffic
7  Sitting back with a real panic
8  Might pack the backpack in Munich
```

## Why the family moved again (Joe picked -am, and -am cannot hold the shape)

Joe picked the -am family (Vietnam / tram / jam / Amsterdam). Measured, that family cannot satisfy the slot's
ENDING SHAPE: the profile's four bars of Hook 5-8 all end **soft+1** -- one weak syllable AFTER the last stress
(La-gos, fa-vours, fla-vours, Ve-gas) -- and in -am only `bedlam`, `madam` and `wigwam` have that shape.
`tram`, `jam`, `scam` and `dram` are stressed monosyllables (hard), `Amsterdam` is soft+2 (AM-ster-dam) and
`programme` is |SS. The only -am words a bar could end on and still match the shape are three obscure ones with
no true place among them, so the family was dropped with evidence rather than by preference
(`toolkit/_probe_shape.py`).

Two families survive shape + carpet + two true places:

| family | end words (true places marked) | carpet | note |
|---|---|---|---|
| **-ich (IH-k) CHOSEN** | **Zurich** (2019) / traffic / panic / **Munich** (2019) | **6/6 at 1.00** | fresh vowel (IH), clean contrast with bars 1-4's schwa-U |
| -oh (schwa-U) | **Porto** / **Oslo** / **Padstow** / zero | 6/6 at 1.00 | three true places, but bars 1-4 are already schwa-U -- eight bars of one vowel |
| -am (ae-m) | -- | -- | fails the ending shape (above) |

## Readings (check_all --slot "Hook 5-8")

| | ours | original |
|---|---|---|
| end-rhyme carpet | **6/6, min 1.00** | 6/6, min 0.92 |
| scheme | **AAAA** | AAAA |
| ending shape | **soft+1 x4** | soft+1 x4 |
| syllables | **8 / 10 / 8 / 8** | 8 / 10 / 8 / 8 |
| internal rhyme density | **8** | 8, distributed 4 / 3 / 1 / 0 |
| multisyl (two-syllable tail device) | **3** | 2 |
| flow | **4/4 bars matched** | -- |
| problems | **0 -- ALL PASS** | -- |

Every demand is met and the carpet is TIGHTER than the original's own. v14 by comparison measured 3/6 with a
0.00 minimum. Other gates on this block: meaning_gate PASS, coherence_gate PASS, regression PASS (local word
`bier`, no admin word in a rhyme slot, 2 places named), ear 2 echoes / 0 crutches, check_all ALL PASS.

The multisyl device is the one that took the work. It is a pair of two-syllable vowel runs made of two ADJACENT
CONTENT words (function words are marked unstressed and cannot carry it): `cash back` and `black van` and
`backpack` are all AE-AE, and three sequences give three pairs. The same AE cluster supplies the internal
density the original gets from its repeated frames.


## Three real bugs found while doing this

1. **The grader paid for schwas.** `phon.score`'s two-weak-vowels guard only fired when the codas DISAGREED,
   so with agreeing codas a single reduced syllable scored 1.00/perfect. That was the whole of v14's
   "min 0.92". Guard now keys on the schwa alone (`REDUCED = {schwa}`): an over-broad first version killed 17
   of the original's own verse pairs (certi~forty, Dublin~him).
2. **check_all --song read the "== Slot" headers as bars**, shifting every slot window by one. The same defect
   ratchet.py had. Fixed; it had been reporting Hook 1-4 as 10 problems when the real figure is 6.
3. **Britfone has no entry for our place names**, so `word_phones` fell through to a vowels-only fallback and
   every place name lost its consonants: "Zurich" was scored as (U, IH) with no final /k/, which capped
   Zurich/traffic/Munich at 0.80 forever. Affected Zurich, Porto, Bordeaux, Ljubljana, Majorca and the
   original's own "Spoons". `helpers.uk_phones` now resolves through the CMU dictionary plus OVR; `helpers.uk`
   stays a dictionary-only lookup because vocab.py's junk test depends on membership. Profile rebuilt with the
   corrected grader: Hook 5-8's own minimum rose 0.80 -> 0.92. calibrate.py PASSED.

## Truth flags for Joe

- **bier** is the code-switch: German for beer, and the German-speaking part of Switzerland is where Zurich is
  (material/place_sound_families.md lists it as accurate). It also satisfies the regression gate's local-word
  requirement and is the reason the song's hook now has 3 local words instead of 2.
- Zurich and Munich are the 2019 Interrail legs (material/travel_history.md, confidence H). The backpack is
  that trip's luggage; Joe confirmed a rail/hostel/hiking month.
- **the black van** is (invented) -- it carries the flat menace in bar 6 and can come out if Joe would rather
  it were the train. "Cash back on the bier" and "a real panic" are (persona): plausible, but nothing on record
  says either happened.
- "Might pack the backpack in Munich" is the closer: modal understatement, a place outside the frame, and an
  object instead of the original's chips -- the money moved to bar 5's cash back.

## Next

This block is done pending Joe's ear and his G2 call on "bier" (zipf 2.5 -- would a mate read it as a typo?).
Song-level items remain: bar 1 is 4 syllables (locked, his own line), Hook 9-16 uses "bed" four times and
needs the same rebuild, the song names 4 places of the 8 the level gate wants, and the hook needs one more
code-switch. Florence, Porto and Naples have dropped out of the draft with the rejected v14 block and still
sit in toolkit/keepers.json -- they belong in the verses (Interrail and the 2023 bike tour) rather than the
hook.
