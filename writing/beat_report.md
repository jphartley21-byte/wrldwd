# Beat report: can one quad beat each original block?

Verdict per quad vs block = BEATS when it wins more of the 13 measurable criteria than it loses and is
hygiene-clean. Reads the original from the private file; no lyrics stored.

## Original block targets (its own measured numbers)

| block | bars | syl | soft | internal | multi | cutup | enjamb | redup | carpet | flow(c/p/cl) |
|---|---|---|---|---|---|---|---|---|---|---|
| Hook 1-4 | 4 | 9-5 | 2 | 1 | 8 | 8 | 0 | 0 | 0.50 | 9/1/1 |
| Hook 5-8 | 4 | 10-8 | 4 | 1 | 2 | 2 | 0 | 0 | 1.00 | 5/0/1 |
| Hook 9-16 | 8 | 12-5 | 1 | 3 | 3 | 3 | 0 | 0 | 0.38 | 7/0/6 |
| V1 1-8 | 8 | 13-6 | 7 | 0 | 19 | 19 | 0 | 0 | 0.88 | 15/6/5 |
| V1 9-16 | 8 | 12-5 | 2 | 5 | 11 | 11 | 2 | 0 | 0.88 | 9/1/7 |
| V1 17-24 | 8 | 11-7 | 8 | 4 | 9 | 10 | 3 | 0 | 0.62 | 8/4/11 |
| V1 25-32 | 8 | 15-8 | 8 | 2 | 28 | 17 | 1 | 0 | 0.43 | 15/4/10 |
| V1 33-44 | 12 | 11-5 | 6 | 2 | 40 | 39 | 1 | 1 | 0.55 | 20/6/15 |
| V2 1-8 | 8 | 12-9 | 1 | 0 | 8 | 8 | 1 | 0 | 1.00 | 7/0/9 |
| V2 9-16 | 8 | 12-6 | 3 | 3 | 22 | 23 | 0 | 1 | 0.29 | 17/3/7 |

## Coverage: quads that BEAT each block (of 92 quads)

| block | quads beating it | best quad (margin) |
|---|---|---|
| Hook 1-4 | 29 | Q82 (+7) |
| Hook 5-8 | 40 | Q84 (+6) |
| Hook 9-16 | 25 | Q84 (+4) |
| V1 1-8 | 35 | Q91 (+4) |
| V1 9-16 | 5 | Q72 (+2) |
| V1 17-24 | 6 | Q54 (+3) |
| V1 25-32 | 2 | Q72 (+2) |
| V1 33-44 | 2 | Q72 (+1) |
| V2 1-8 | 29 | Q82 (+6) |
| V2 9-16 | 7 | Q88 (+2) |

## Song-level aggregate (best quad per block; per-bar means, carpet as a density)

| crit | criterion | ours | original | edge |
|---|---|---|---|---|
| 2 | weak/feminine endings | 0.75 | 0.55 | OURS |
| 5 | line-length spread | 1.57 | 0.70 | OURS |
| 7 | bars with internal rhyme | 0.42 | 0.28 | OURS |
| 8 | multisyllabic runs | 1.35 | 1.97 | orig |
| 8b | cut-ups (mosaic+homophone) | 1.10 | 1.84 | orig |
| 9 | enjambed rhymes | 0.23 | 0.11 | OURS |
| 10 | reduplicated words | 0.23 | 0.03 | OURS |
| 11 | end carpet density | 1.00 | 0.65 | OURS |
| 14 | number ladder | 0.05 | 0.14 | orig |
| 23 | bars in 5-14 band | 1.00 | 0.97 | OURS |
| 32a | stress clashes | 0.72 | 1.47 | OURS |
| 32b | mid-bar pauses | 0.07 | 0.33 | OURS |
| 32c | consonant pile-ups | 0.45 | 0.95 | OURS |

**We lead on 10 of 13 measurable criteria at song level.** Hygiene is excluded (the original's slang and brand names show as OOV, so it is not comparable). The 28 human criteria are still unscored: see `rubric_score.py --literary`.
