# Joe's "Worldwide" track: a Suno rap in the style of Pete & Bas "Mr Worldwide"

@STATE.md

## What this is
Joe (33, from Reading, lives in Bristol) wants a Suno track that sounds like he wrote it: a deadpan British world-tour song at 142 BPM built from his REAL travel history, as good as the original in craft. Audience: Joe and his mates. Cheeky, no heavy swearing; deadpan drug and violence imagery is allowed (as in the original). Joe expects a long iterative process and wants calibrated, honest feedback: never call bars good without hedging. He is cost-sensitive and has hit usage limits: keep replies short, no waste.

## Rules (hard-won in the first sessions)
1. COMEDY = CHARACTER + WORDPLAY, sold by rhyme scheme and flow. Joe: "there's not really any jokes at all". Character: something big or illicit reported flatly in an everyday British register (parcel delivery, pub, telling-off, prices), domestic person MENTIONED not addressed. Wordplay: a stock phrase cashed into a literal thing, the payoff word in the rhyme slot (last word). No setup-punchline gags, no puns that announce themselves. Evidence: benchmark/comedy_theory.md, benchmark/genius_line_classes.md.
2. EVERY BAR MUST SAY SOMETHING. Agree a one-line-per-bar beat sheet with Joe BEFORE writing words. Round-1 and round-2 bars "said nothing" and were rejected.
3. SOUND MAP FIRST, THEN WORDS. Choose a vowel carpet, a consonant skeleton and at least one perfect-rhyme pair from the toolkit; build bar by bar; run `check` on every bar; end words come from toolkit banks. One-syllable AAA triples (puff/huff/stuff) are too weak. The original's chorus bars are 5-10 syllables (mean 8); its verse lines go up to 15.
4. NEVER reproduce the original's lyrics in files or replies beyond isolated words; cite by line number (Ch L1, V1 L12). Joe can re-paste them in chat when needed.
5. TRUE OR FLAGGED: facts come from material/. Anything else is "(invented)" or "(persona)" for Joe to confirm. No hobby or nerd material. No real artist or film names. No heavy swearing, no instructional drug detail. Do not copy the original's frames ("[greeting] to the boys in [place]", the plane/plain pun, "tell her ... back shortly").
6. COST. Subagents inherit this session's max reasoning effort and ran away: 6 of 8 writer agents burned 128,000 output tokens each and returned nothing. Do NOT launch writer or judge agents unless Joe asks and the effort is lowered. Work in the main thread with the toolkit. Do not re-read big files or redo research that is already in benchmark/.
7. SUNO: v6 only. Joe signs in himself. Fill title, lyrics, style and exclude fields, screenshot, then STOP before Create until Joe says yes. Variety 0, Style Influence about 70, Weirdness about 30, vocal gender male; exclude: singing, melodic hook, autotune, choir, female vocals. Test 142 BPM and 71 half-time. Details in brief/suno_rap_rules.md. Leave the key out of the prompt.
8. DECISIONS STILL OPEN (ask Joe once, concisely): strict vegetarian detail in the song? Horfield/BS7 as a name? everyday British brand names (the original uses them)? invented cartoonish flourishes on true places (a bribe, a rival firm)?

## Folder map
- STATE.md: where we are and the next three steps (imported above).
- brief/: song_bible.md (premise and bar budget; parts superseded by rule 1), suno_rap_rules.md (Suno settings and a draft style prompt).
- benchmark/: bars_1-8_breakdown.md (the CURRENT TASK's benchmark), benchmark_rubric.md (41 criteria, rev 2; section I is Joe's definition), comedy_theory.md, genius_line_classes.md (line-by-line classes of the whole original), reaction_findings.md, genius_and_reviews_findings.md, original_technique_map.md.
- material/: travel_history.md (2012-2026 timeline), place_specifics.md (visual specifics and Joe's own details), place_sound_families.md (places by rhyme sound and accurate local words).
- toolkit/: rhyme_tools.py and theme_words.txt (see toolkit/README.md). Needs `pip install cmudict` (already done on Joe's PC).
- writing/: pool_r2.md (candidate bars, first pass, mostly weak: mine them for ideas, not as drafts), iteration_log.md (history), draft_v0_1.md (rejected baseline).
- archive/: superseded briefs, old drafts, the approved plan, and the scripts that read Joe's Seagate drive (outputs are on Joe's Desktop in seagate_probe; not needed again).

## Commands
`/write <sections>` drafts with parallel agents until every check passes; `/review <draft or slot>` runs every check (toolkit/check_all.py + human gates). Original lyrics stay in C:SERSJOEDOCUMENTSWORLDWIDE_PRIVATE (NEVER IN THE PROJECT).

## TOOLKIT IN ONE LINE
`python toolkit/rhyme_tools.py pron "text" | rhymes WORD [--n 0|2|3 --mode perfect|assonance|near] | mosaic "phrase" --nsyl 3 | families --min 3 | check FILE|- | syllmap FILE|-` (syllmap = every syllable: internal, multisyllabic, slant rhymes, alliteration)

## Stuck rule (Joe, 9 Oct 2026)
Count every version of a bar set shown to Joe in STATE.md ("Attempts"). PIVOT when any trigger fires:
- T1: 3 versions in a row rejected or "not landing" for the same bars.
- T2: the same end-sound family or theme used in 3 rejected versions (the constraint is the problem, not the words).
- T3: a fix for one gate breaks another twice (e.g. fixing flow kills meaning).
- T4: the end-sound bank has fewer than 6 words that pass gate G2 (recognisable), checked with `rhymes`.
PIVOT protocol: park the best version in writing/contenders.md with one line on why it stalled; write 3 fresh angles (each: one-line beat sheet, end-sound family, a 6+ word G2 bank, true places) that change at least two of theme / rhyme family / structure; pick one by gates G1-G3; build it from scratch without reusing the stalled lines. Tell Joe in one line that a pivot fired and why. Joe's own lines are inputs, not fixed constraints (gate G4).

## Definition of done for a section (Joe, 9 Oct 2026)
`toolkit/check_all.py` says ALL PASS AND gates G1-G6 + job check pass AND `toolkit/ratchet.py` against the previous draft says OK (no regressions, no keepers in toolkit/keepers.json lost). Agents keep looping until then (hard cap 10 passes for cost), applying the stuck rule to any bar that fails 3 passes.
