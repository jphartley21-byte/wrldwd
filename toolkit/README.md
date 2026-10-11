# toolkit: rhyme and flow checks (offline, no model tokens)

Needs the `cmudict` pip package (installed). US CMU pronunciations with a UK-ish layer (post-vocalic R dropped for rhyme matching). Out-of-dictionary words (place names, slang) go in the OVR table at the top of rhyme_tools.py as ARPAbet; the tool prints "OOV word" when it hits one.

```
python toolkit/rhyme_tools.py pron "double it"                 # phones, UK-ish phones, syllables
python toolkit/rhyme_tools.py rhymes tobago --n 0               # n=0: from the last stressed vowel (default). n=2,3: last N syllables
python toolkit/rhyme_tools.py rhymes "double it" --n 3 --mode assonance --max 40   # vowel pattern only (dactylic carpets)
python toolkit/rhyme_tools.py mosaic "double it" --nsyl 3       # cut-up rhymes: word pairs that sound like the phrase; --loose merges voiced/unvoiced
python toolkit/rhyme_tools.py families --min 3 --top 25         # rhyme families ranked by how many words from theme_words.txt they hold
python toolkit/rhyme_tools.py syllmap chain.txt     # every syllable mapped; perfect/slant/assonance, multisyllabic runs, 2-syl end tails, alliteration
python toolkit/rhyme_tools.py check chain.txt                   # one bar per line, blank line = new chain; "-" reads stdin
```

`check` prints per bar: syllables, accent upper bound (monosyllables count as stressed except function words, so treat as a ceiling), end word, rhyme key from the last stressed vowel, vowel carpet, same-vowel word pairs inside the bar, flags (LEN <5 or >14, STRESS <3 or >8, OOV, banned words), plus per chain: vowel-carpet counts, adjacent end-sound match depth in phones, internal-rhyme bar count, repeated end words, "mate" count.

Benchmark numbers from the original's opening 8 bars: 5, 9, 9, 9, 8, 10, 8, 8 syllables; carpet EY x5, OW x2, EH x1; one perfect rhyme (favours/flavours); sparse internal rhyme.

Edit theme_words.txt to steer `families` toward the vocabulary you want (categories are # comment lines; use _ for spaces in phrases).
- `python toolkit/flow_check.py -`: per-bar stress clashes, weak runs, mid-bar pauses (commas), consonant pile-ups; put the original bars (pasted, not saved) above a `---` line to compare. A text screen, not an ear.
- `python toolkit/helpers.py freq|uk|tails|rp|dm` (see benchmark/flow_references.md): British IPA, rare-word flags, RhymePad scheme/groups/meter, Datamuse rhyme lists.
- `python toolkit/match.py --slot "V1 1-8" -`: hard PASS/FAIL per bar against the original profile (numbers only, benchmark/original_profile.json).
- `python toolkit/flow_fit.py START_BAR -`: our bars vs the original rhythm measured from audio (benchmark/flow_template.json, built by flow_map.py in the "flow" conda env).
- `python toolkit/phon.py "a" "b"`: graded British rhyme score (perfect/near/slant). match.py now includes a rhyme-strength map vs the original.
- `python toolkit/check_all.py --slot "V1 17-24" -` or `--song FILE`: EVERY automated check in one verdict. Commands: /review (check bars), /write (parallel agents loop until checks pass). Original lyrics: C:\Users\Joe\Documents\Worldwide_private\original_lines.txt (outside the project).
