---
description: Stage 2. Bulk-generate raw ideas (lines, rhyme pairs, punchlines, scenes) for a section; Joe ticks favourites
argument-hint: <section> [count, default 150]
---
Section: $ARGUMENTS. Goal: QUANTITY, no self-filtering. Write `ideas/<section>.md` as tickable lines: `- [ ] <idea> | device | place | end-sound | true/persona/invented`.
Sources, in order: the approved `work/<section>/1_beats.md`; material/joe_notes.md (his seeds first: Rotter damn, Brisbane~Lisbon, monkey=£500, animals, goon, etc.); research/rhyme-bank.md and places/events; voice/profile.md and voice/calibration.md (write the way Joe talks).
Mix: raw bars (any length), rhyme/end-word pairs, punchline ideas, scene seeds, number ladders, place x register pairings, sound-alike puns. Get end words from `python toolkit/rhyme_tools.py rhymes|mosaic|families`, do not hunt rhymes by long reasoning.
Subagents optional: at most 4, medium effort, each told "return at most 40 items in the format above, no rhyme-hunting loops, use the toolkit, no quotes from the original". Merge, dedupe, then STOP: tell Joe to tick favourites (or say which clusters to push). Then suggest `/patterns <section>`.
