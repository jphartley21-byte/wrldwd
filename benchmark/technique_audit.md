# Technique audit (round 3, 9 Oct 2026): every agent fills this for its slot, original vs ours, bar by bar
Run first: `python toolkit/helpers.py rp -` and `tails -` on the ORIGINAL slot lines and on OURS (pipe via printf, never save the original); `python toolkit/flow_check.py -` (original, ---, ours); `python toolkit/rhyme_tools.py quad -` and `syllmap -` on both.

| Column | What to compare (original bar vs our bar) |
|---|---|
| 1 Syllables | count; ours within ±1 |
| 2 Stress grid / cadence | stressed positions (by ear; rp meter as a hint); pickup before beat 1; where the rhyme stress lands; long-short line shape across the stanza (the original's deliberate short-short-long runs) |
| 3 End rhyme | last-two-syllable vowels (British `tails`); scheme letter; exact / near |
| 4 Multisyllabic | 2-4 syllable rhymes (rp groups, syllmap multisyl), incl. multi-word mosaics |
| 5 Internal | in-bar and cross-bar vowel runs (like trans-at-lan -> man) |
| 6 Alliteration / consonance | repeated onsets or clusters |
| 7 Wordplay | pun, cashed stock phrase, double meaning; is the payoff in the rhyme slot? |
| 8 Imagery | one concrete, visual, specific image (object + place + action) vs generic |
| 9 Character / register | deadpan British, domestic aside, menace slipped in |
| 10 Other devices | echo with a twist, repetition (x3), number ladder, enjambment, voice tic (mate), AXAA break, callback |
Then: list every column where ours is below the original, fix the biggest gaps first WITHOUT breaking gates G1-G6 (sense and human voice win ties), re-run the tools after each change. Max 3 passes. Put the filled table for the final version in your file.
