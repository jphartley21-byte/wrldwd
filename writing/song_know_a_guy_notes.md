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
