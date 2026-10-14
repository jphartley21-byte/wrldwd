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
