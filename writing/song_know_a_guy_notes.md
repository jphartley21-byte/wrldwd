# I Know a Guy: gate result, open notes and what the naive-writer run showed about the pipeline (15 Oct 2026)

## Result
- `python -m ww.cli gate writing/song_know_a_guy.md`: PASS, 0 hard issues, all 10 sections. Sense read OFF (no DEEPSEEK_API_KEY).
- fitbar per-bar fit: 74/76. Bars 37 and 39 fail on end shape only (see finding 2).
- recount 8% (original 20%); swagger hook 7/16, verses 22/60; meaning gate, phrase audit, songcheck, character cap: pass.

## Notes listed to Joe (rule 10: fixed or listed, never skipped)
- 114 FLOW/EAR notes (jammed stresses 27, reduced syllable on a downbeat 41, weak syllables on the beat 14, stress clash 29,
  "stress inverted" 25, pauses/commas 8, mouth-shape 3). NOT fixed: run on the original's own 76 bars the same notes fire as
  often or more (jammed 23, downbeat 39, beat 16, clash 24, inverted 30, mouth-shape 18). They do not separate the benchmark
  from a draft, so fixing them is not evidence of better flow. Your ear decides.
- 3 end-rhyme carpet notes (the original holds one sound family across the block; ours does not): Hook 5-8 2/6 (original 6/6),
  V1 17-24 10/28 (24/28), V1 25-32 9/28 (21/28). Real, not fixed: each needs the section re-rhymed on one vowel family.

## What the naive-writer run found in the pipeline (none of these were changed during the run)
1. fitbar and the gate disagree on end shape. slotcheck accepts a mid-word rhyme (~Sw) for |Sw and, in verses, checks only
   hard vs soft; fitbar demands the exact shape, and write.md says a mid-word rhyme cannot fill a |Sw slot (Majorca).
2. V1 17-24 bars 37/39: the template's weak-only ending (|w) with a three-syllable rhyme is only reachable with "him", the
   original ends both bars on it, and the draft rules forbid a repeated end word. A draft cannot satisfy fitbar and the gate here.
3. Bar 37's template has 4 weak syllables in a row; the weak-run rule fails any bar with 4. The template breaks its own rule.
4. characters.py counts "copper" but not "cops", "police", "Garda", "guards" or "customs": the police could be referenced 5
   times under a cap of 2. I held them to 2 by hand.
5. songcheck fails a rhyme pair on the OLD grader (match.best_end < 0.78) while fitbar prints that grader as a note only.
6. The local-word supply contains English words ("sea", "police", "yes", "part", "route", "mat"): 2 of the verses' 5
   counted local words are these. The gate can be passed without any real code-switching.
7. The cashed-idiom check can be gamed: the payoff only has to be the bar's last word, not part of the idiom
   ("#cash | top dog | nightlife" verified). I removed that declaration; the remaining declarations are real.
8. Punctuation changes spaCy's mid-bar restart count: deleting two commas from bar 76 turned a pass into a hard fail.
9. The stress model reads some words unexpectedly (gendarme SS, statue SS, speedy SS, radar SS, Rotterdam SwS, Hanoi Sw,
   Laos 2 syllables, "John o' Groats" SSS): a writer has to test every word, not every bar.
10. The pronoun-ending cap grows with song length (2 per 38 bars, 4 at 76), so partial drafts fail a check the song passes.

## Findings 11-12 (15 Oct 2026, after Joe: "originals end rhymes are better rn" and the Lagos/favours/flavours/Vegas carpet)
11. The gate passed cheap, samey end rhymes: rapfit's pair score rewards an identical, common rime with 1.0, and nothing measured
    rhyme quality. Now HARD (rapfit.quality_hard): cheap rimes and identical rimes per section, at most the original's count + 1.
12. The gate passed Hook 5-8 with two separate rhymes (people/sequel, solid/wallet) where the original rhymes all four bars: the
    by-ear letters (ABBA) mark closest partners, not families, and the carpet check had been a note since 13 Oct. I skipped that
    note when writing this song. Now HARD (carpet >= 85% of the original's).
This draft fails the gate in 7 sections under the new rules; the rewrite follows.

## Rewrite of the end rhymes (15 Oct 2026, same day): ww gate PASS again under the new rhyme rules
Changed bars only (everything else as before). Each bar re-fitted with fitbar; fitbar 74/76 (bars 37, 39 as before).
- Hook 5-8: posse / solid / wallet / copy: one family across all four bars (rapfit carpet 6/6; the old block was 2/6).
- Hook 9-16 bar 4: through the floor (was the wall: call/Saul/wall were three identical rimes).
- V1 1-8 bars 5-6: Barbour parka, the judge gets lager (four identical -arma rimes became one pair, karma/drama).
- V1 9-16 bars 6-8: living the dream, top thief, he's discreet (six bare -ee rimes became three: me / we / free).
- V1 33-44 bars 8-10, 12: saving face, ten days' grace, fair game, no names (pay/sway/day/play/okay became pay alone).
- V2 1-8 bars 3, 8: top fried rice, it's mine (six bare -eye rimes became four: guy / die / high / fly).
- V2 9-16 bars 1, 3, 4: my own code, the East Coast, struck gold (phone/known/home-grown were one common rime).
Song-level fixes found on the way: songcheck still judges scheme pairs with the old grader (posse ~ profit 0.76, so bar 8 became
"copy"); "weight" is on the admin-word list (bar 57 became "ten days' grace"); dropping "well known" lost the W-L drum in V2 9-16
(bar 69 now opens "Well,") and the device rate fell to 37% until it was back (8 of 19 quads, 42%).
HONEST READING: on cheap and identical rimes the song now sits AT the original's count or one over it in 7 sections, never better
than the original except Hook 5-8 (0 identical vs 2). The rules bound it at "no worse than the original + 1"; they do not make
the rhymes as good as the original's, and the original's rarer multi-syllable and mosaic endings are still not matched.
NOTES LISTED TO JOE (rule 10; 121, all from the unvalidated beat-grid / ear diagnostics): 28 "two stresses jammed together",
14 comma / pause placement, about 20 reduced syllables on a downbeat, 3 hard mouth-shape transitions (inside the par).
Suffix check: it counts "seed" as an -ed ending by spelling (seating / keyring / seed tripped it); worked around, not fixed.

## Finding 13 and the second rewrite (15 Oct 2026, Joe: "Why is hook 5-8 still ABBA when the original is AAAA?")
13. Two causes. The scheme letters still said ABBA (from the 9 Oct "A C C A" note, which marked closest partners), and the
    carpet I had just added counted a pair when rapfit's pair score reached 0.50, which a shared stressed vowel alone does
    (posse ~ solid 0.66). So posse / solid / wallet / copy passed as "6/6" while it was two pairs. Now: Hook 5-8 is AAAA in
    toolkit/match.MANUAL_SCHEME, and the carpet counts a pair only when the endings chain syllable by syllable from the end
    (the original's Hook 5-8: all six pairs two syllables deep). The same rule then failed Hook 1-4, V1 1-8, V1 9-16,
    V1 25-32 and V2 1-8 (each had a bar sharing the stressed vowel but not the ending).
Rewrite (bars changed): Hook 1-4 Cheers to the venue / Left out on the rocks? I continue / ... all on a day's cruise /
... there's a good few (one ending: venue / continue / cruise / few). Hook 5-8 honest / solid / wallet / profit (all six
pairs two syllables deep, as the original's). V1 1-8 bar 1 ... the rest is larger. V1 9-16 bar 5 ... with all the athletes.
V1 25-32 bar 4 My boots in Bergen? Dead fatal. V2 1-8 bar 4 ... the sharks were in the crossfire; bar 5 ... jets at night.
Pronoun endings held at the cap (4): "got it" and "than I" were tried and dropped for that reason.
ww gate PASS (0 hard, sense read OFF); fitbar 74/76 (bars 37, 39 as before).
