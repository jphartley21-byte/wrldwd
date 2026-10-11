# Current state (9 Oct 2026)

## The task now
Joe wants to FOCUS on writing our own version of the original's opening 8 bars (the chorus's first eight lines) at matching quality, meticulous about every syllable, without wasting tokens. Benchmark and spec: benchmark/bars_1-8_breakdown.md (section 4 is the spec). Do this in the main thread with the toolkit; no agents.


## LOCKED: bars 1-4 (9 Oct 2026, writing/bars_1-4_v9.md)
Oh, bonjourno / Front row at the on-stage porno / Damn good show but the dame look bored, though / So boarded a plane out to Bordeaux (Joe's rewrite, 9 Oct)
Lessons from 12 drafts: AAAA on a TWO-syllable vowel tail (here AO-OW, all exact); sound-alike puns (Dam/damn, bored/boarded, Porto~porno); the gag is flat attitude, never explained; menace must exceed the group's normal life (coke = no shock); Joe's ear and his own ideas beat mine: offer options, let him steer.
Tools: `quad` (4-bar technique scorecard, benchmark/technique_scorecard.md), `syllmap` (every syllable, rhymes, alliteration), `/review` command.
NEXT: bars 5-8 (original Ch L5-8: greeting #2 + place, business register bridge, perfect-rhyme pair that changes register (favours/flavours), closer place outside the frame with modal understatement).

## Done
- Research: comedy theory (Joe's definition), Genius line-by-line classes of the whole original, reaction notes (small samples), rubric rev 2.
- Toolkit built and tested (toolkit/): syllables, stress, rhymes, near and vowel-only rhymes, cut-up (mosaic) rhymes, theme-word families, line and chain checker. The original's 8 bars were run through `check` (numbers in the breakdown).
- Material: travel_history.md, place_specifics.md, place_sound_families.md (accurate local words).

## Next steps
1. SOUND MAP. Run `families --min 3`, `rhymes` and `mosaic` on candidate end words. Offer Joe 3-4 compact options, each: vowel carpet (about 5 of 8 end words), consonant skeleton for the place lines, one perfect-rhyme pair that changes register, one assonance pair for the two-line pun, plus 4-6 candidate places with accurate local words. Joe picks.
2. BEAT SHEET. One plain sentence per bar saying what it says (nonchalant report, or wordplay cashing a phrase). Joe approves.
3. BUILD bar by bar: end word from the bank, fill backwards onto the beat, run `check -` on the whole chain, keep a short list of rejected words. Show Joe the 8 bars with a 3-line "why". Iterate on his reaction (his ear is the real test).
4. Only after the 8 bars pass, extend to the full hook (the original's chorus is 16 bars), then the verses by the same method.

## Joe's reaction so far to first-pass bars (all rejected)
"Terrible flow and rhyme schemes and they say nothing." The Pompeii run (puff/huff/stuff) was "really weak and lame" (AAA on one-syllable words). Bars he has not rejected outright: none confirmed good. The hook idea of days of the week ending at a grey English beach (writing/pool_r2.md, HK1-HK8) was not specifically praised either.

## Cautions
- The toolkit uses US pronunciations with a UK-ish R-drop; add place names and slang to OVR in rhyme_tools.py. Its stress count is an upper bound, not the real beat placement.
- Reactions evidence is thin (6 transcripts, auto-captions, laughter inferred).
- writing/contenders.md: parked lines Joe may revisit (Majorca bars 5-8).

## Full draft v14: writing/full_draft_v14.md (9 Oct 2026), awaiting Joe's read (v1, v2 kept)

## Attempts (stuck rule, CLAUDE.md)
| Bars | Versions shown | Rejected in a row | Families tried (rejected) | Status |
|---|---|---|---|---|
| 5-8 | 12 (v1-v12) | 6 (v7-v12) | AO (v1-v5, mixed), ER-AH Bergen (v6-v12) | T1+T2 FIRED 9 Oct: pivot. Parked: Majorca v5 (contender), Bergen v12 (flow/meaning stall) |
Pivot angles for 5-8 (pick by gates, build from scratch):
A. Keep the AO carpet of bars 1-4 all 8 bars (the original keeps EY all 8): Majorca/Portsmouth, order/border, water/daughter; bank 6+.
B. Motorbike tour 2023 Bilbao / Koh Tao on OW ("now, how, allow, somehow, eyebrow"), structure: roll-call of two places in L5.
C. Interrail 2019 Bratislava / lava / java (AA-AH), structure: number ladder across 5-8 (days, countries, quid).
