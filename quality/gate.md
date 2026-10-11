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
