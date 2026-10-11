# Quality gate (11 Oct 2026). Joe: "I never want to read another draft that is not already high quality."
RULE (Joe, 11 Oct 2026): Joe is never shown a draft that is less than "as good as it can be without human input" (full wording: CLAUDE.md principle 0). Clear every gate below, then keep iterating until a fresh critic finds nothing more fixable without Joe. Max 6 critic rounds per stanza, then cut the stanza and report the one blocker. "Workable skeleton" is not a thing Joe is shown.
Why this exists: the v17 run (writing/rejected/full_draft_v17_REJECTED.md) skipped real drafting variants, polish and critique, then handed Joe a draft the review itself called unfinished. In round 1 the strict original-matching gate was removed (Joe asked for less strict matching) and no quality gate replaced it. Less strict about the ORIGINAL does not mean no standard.

## Gate 1: measured (toolkit/quality.py), floor taken from Joe's own bars
Bars 6-10 syllables (Joe's run 4-10, mean ~8); at least 1 per block ends weak/feminine; at most 1 bar per 4 with no 2-syllable end-rhyme partner; 2+ multisyllabic runs and an internal rhyme per 4-bar block; no filler/cliche phrases; no unconfirmed slang; at most 2 place names per 4 bars. Joe's own bars must still clear it (calibration check).

## Gate 2: independent critic (fresh context agent, blind)
Give the critic Joe's bars (hook 5-8, V1 1-4) mixed unlabelled with the candidate bars. It scores every bar 1-5 and says which bars are weaker than Joe's. PASS = every candidate bar >= 4, none flagged weaker than Joe's, none flagged "filler / explains the joke / itinerary / could be said by anyone". The critic must not know which bars are Joe's.

## Gate 3: Claude's own read (written down, 5 lines per stanza)
Does each bar say something distinct and concrete? Is the funny word the rhyme word? One scene per stanza (not a list of places)? Would Joe say it (JOE-tagged devices only)? Anything invented is flagged? If any answer is no, rewrite. Never claim parity with Joe's bars.

## Gate 4: Joe's rules
No explained jokes, no setup-punchline gags, no holiday itinerary lists, no heavy swearing, nothing from his NOT-ME list, nothing in voice/provenance.md marked JOE is changed.

## Process per stanza (internal, never shown)
1. 8+ candidate end-word pairs from bank/ (toolkit/bank.py find) on a sound with 2-syllable tails.
2. Write 3 full candidate versions of the stanza.
3. quality.py on each; discard those below bar.
4. Critic on the best one; fix flagged bars; repeat (max 6 rounds).
5. Only a stanza that clears all four gates goes into a draft. Joe sees the draft once, complete.

## Gate 0: ANCHOR = THE ORIGINAL SONG'S CRAFT (corrected 11 Oct 2026)
Joe, looking at the calibration sample (his own hook bars and my best bars): "none are anywhere close to the quality of even the worst line from the original song."
So the quality floor is the ORIGINAL's worst bar, in CRAFT terms (rhyme architecture, density, wordplay payoff, flow). Not its content, frames or phrases, which stay uncopied. Earlier "calibrate to Joe's own bars" was the wrong anchor: Joe's hook bars are also below this bar.
- A critic's scores count only if the original's own lines, mixed in blind, score in its top half. The original lyrics are in reference/original_lyrics.txt (saved at Joe's request, 11 Oct 2026). Critic calibration uses them blind. Never copy its lines into our song.
- The measured floor is re-derived from the original, not from Joe's bars: long single-sound chains (benchmark_rubric criteria 1, 2: runs of 8-16 lines, ~90% coverage, weak/soft multisyllabic endings), internal rhyme in ~60% of dense lines (7), 4+ cut-up/mosaic rhymes (8), 5+ echo-with-twist (13), payoff word in the rhyme slot (38), plus the measured numbers in benchmark/original_profile.json and flow_template.json. toolkit/quality.py gets these thresholds, replacing the Joe-bars floor.
- Plain flat single bars with no rhyme architecture (what I wrote on 11 Oct) are below this bar by construction.
## Lessons from the 11 Oct rounds
- Flat, specific, deadpan bars with one turn ("Forty frozen birds. Cold turkey.", "Sign's in the river.") outscored every rhyme-driven bar I wrote.
- My rhyme-chasing stanzas (-ape, -ide, -happy, -oon) scored 2-3 on every critic; do not write stanzas to fit a sound.
- Joe's own bars are sound-play and chantable; page critics underrate that. The best bars are specific AND sonic (pavos/turkeys, Win-win).
