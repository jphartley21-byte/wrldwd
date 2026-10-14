# Mouth shape, transitions and vowel duration (15 Oct 2026)

STATUS: reference + inference. Nothing here is validated against Suno or the original's audio beyond the template's 16th-note steps. Numbers are US-leaning phonetics averages; British differences are flagged.

## Time per step (measured layout from benchmark/flow_template.json: a lyric line spans 2 bars at 140 BPM, 16 steps)
| layout | step | note |
|---|---|---|
| line = 2 bars @140 (= 1 bar @70 half-time) | 214 ms | the original's layout |
| line = 1 bar @140 (double speed) | 107 ms | what a fast render risks; long vowels and clusters smear |
A 1-step gap is the tightest the original uses; runs of 3+ are the "tight run".

## Vowel duration classes (inference; ms are working values in toolkit/duration.py)
- long / diphthong (~190): iː uː ɑː ɔː ɜː eɪ aɪ aʊ ɔɪ əʊ
- short (~120): ɪ ʊ ʌ e æ ɒ (US /ɑ/ in on/not/got is British short /ɒ/, corrected in code for words spelled with "o")
- schwa/reduced (~70): unstressed ə, function words
- adds: +35 ms per coda consonant in the word-final syllable, +15 ms per extra onset consonant, +40 ms phrase-final lengthening.
Rule of thumb for the writer: long vowels and heavy codas want a gap of 2+ steps (or the bar's end slot); runs of 1-step syllables should be light (short or schwa, single consonants).

## Mouth-shape transitions
- Consonant joins across a word boundary: toolkit/flow_check.py joins()/rare_joins() (place and manner; three rare shifts calibrated on the original).
- Vowel travel between adjacent content syllables: flow_check.vowel_travel() (height + backness + 2 x rounding change; front-spread iː ɪ eɪ <-> back-rounded uː ɔː əʊ is the big swing). REPORT-ONLY: par on the original not yet measured.
- Tongue-twister risk: alternating near places (s/ʃ, t/k, l/r) inside a 1-step run. Not yet detected.

## Honest limits
Suno's own timing is unobserved; ms are estimates; the last syllable of a bar is assumed to have 3 steps of room. A detector that fails Joe's approved bars 1-4 or fires on the original at a high rate stays a note (the repo's rule).

## Calibration (15 Oct 2026, original's 76 unique lines, counts only)
- Durations at scale 1.0 raised need>have on 69% of the original's bars at 214 ms/step, so they were too long. Scale scan: 0.95 -> 23%, 0.85 -> 14%, 0.8 -> 0%. Default SCALE is now 0.8 (the largest scale at which the original itself raises none): a flag now means "longer than anything the original asks of that syllable's slot".
- At 107 ms/step (one line in a single 140 BPM bar) the original raises flags on 94% of bars even at scale 0.7, so the original is NOT delivered on that layout; that view is information about a too-fast render, not a target.
- The "long vowel in a fast run" rule fires on 37% of the original's bars and is now a note only.
- Still unvalidated: whether the flag separates Joe's rejected bars from approved ones (needs their template slot; not done).
