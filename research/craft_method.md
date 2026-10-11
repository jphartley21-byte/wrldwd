# The method: how the original's best chains are built, and how we build ours (11 Oct 2026)
Source: Joe's question about five lines of the original (V1 L24-L31 region: the Turkey / ouzo / hair / quit-smoking run) + benchmark/genius_line_classes.md + original_technique_map.md. Joe's correction: great lines do NOT need real autobiographical detail; they need SPECIFIC vocabulary and numbers, which can be invented or researched. The narrator is a persona.

## Why those lines work (7 things)
1. One sound holds for 8-16 lines: stressed vowel + ANY consonants + soft ending (Turkey, certi-, dirty, thirsty, curly, thirty, forty, shortly, quickly). Every end word is DIFFERENT, so it chimes without repeating.
2. The place/word is chosen for its SOUND first (Turkey sets ER-C-ee).
3. The funniest word is the last word, in the rhyme slot (thirsty, curly, thirty).
4. Tone clash: stiff/stoic/formal British phrases ("needs must", "Lord knows I tried", "I must apologise") applied to trivial vices (fags, hair, a pint). The persona stays unbothered.
5. Idiom surgery: cut a stock phrase and swap its tail so the rhyme word completes it a new way (needs must + thirsty), or read it literally; or cut a word mid-way so a rhyme exists ("certi").
6. Two rhymes per bar (dirty ... thirsty in one line).
7. Specific numbers and vernacular ("twenty deck", "one pound thirty", then "one pound forty": a price ladder / callback) and a concrete noun in almost every line. No filler: each line adds a new fact, a new register or a new rhyme.

## The build recipe (what /sound and /chain do)
1. SOUND SET (toolkit/soundset.py): pick a seed word; get hundreds of words in the family (stressed vowel + consonants + soft ending), plus places, names, bank phrases that END in the family, and number words. Choose 8-16 DIFFERENT end words, favouring ones that carry a joke (a number, a drink, a vice, a place, an idiom tail).
2. REGISTER PAIRS: pick a stiff phrase (bank/register_stiff.csv) and a trivial item or price (bank/mundane.csv). The line is the clash.
3. IDIOM SURGERY: take idioms from bank/idiom_surgery.csv whose swap ideas land on a chosen end word; write the line so the idiom is cut or cashed on the rhyme.
4. NUMBER LADDER: choose one measurable thing and change it between lines (1.30 -> 1.40).
5. WRITE BACKWARDS from the end word. Put a second rhyme inside the bar. Keep 7-13 syllables, no filler.
6. TEST: toolkit/bartest.py (diagnostic: techniques per bar), toolkit/quality.py (diagnostic), then the blind critic with the original's chains mixed in (quality/gate.md). Only a chain that clears the guard is shown to Joe.

## Persona and content
Narrator: unbothered, low-level trader who "imports all sorts" (Joe's hook). Content can be invented: it only has to sound specific. Joe's real trips supply places, activities and seeds, not required incidents. Flag anything invented, as always; no copying of the original's frames or phrases.

## Corrections from Joe, 11 Oct 2026 (I had these wrong or missing)
- "certi" is real UK slang (short for "certified": authentic, cool, highly respectable), NOT a word cut off mid-way. The device is: a swagger slang word whose clipped form fits the rhyme and also means something. Add slang words like this to the sound set (soundset.py section C draws from bank/slang.csv).
- "ouzo" is a dry anise-flavoured aperitif from Greece and Cyprus; "back" = drink. My tools did not know either word (OOV): critics and tools also lack UK slang and cultural knowledge, so every critic prompt must carry a glossary for BOTH original and new lines.
- Duck-duck goose line: the Genius annotation (Joe's paste) explains it: the children's playground game (a picker taps heads saying "duck" then "goose" and runs) given a dark twist, the debtor being hit on the head, probably with a bat, for not paying. Device: PLAYGROUND GAMES AS VIOLENCE EUPHEMISM (also ping-pong, football, WWE in the same song). Add this as a category in the idiom/surgery work: children's games, sports and domestic pastimes mapped onto menace, reported flatly.
- My measures called that block "no internal rhyme" and the critics never credited it: the quality is the cashed game + the dark turn on the rhyme word, which no surface metric sees.
