---
description: Review lyric bars against the original with every check we have (main thread, no agents)
argument-hint: <draft file or slot, e.g. writing/full_draft_v14.md or "V1 17-24">
---
Review $ARGUMENTS. Main thread only. Original lyrics live OUTSIDE the project at C:\Users\Joe\Documents\Worldwide_private\original_lines.txt (92 sung lines, chorus repeated); never copy them into the project or quote them in replies (CLAUDE.md rule 4). Run the steps IN ORDER; a bar that fails a gate is rewritten, not scored.

1. CALIBRATE: `python toolkit/calibrate.py C:\Users\Joe\Documents\Worldwide_private\original_lines.txt` must say PASSED (original passes its own profiles and rhythm templates; Joe's locked bars pass; every Joe-rejected stanza in toolkit/tests/ is caught). If it fails, fix the tools first; never trust a PASS from an uncalibrated tool.
2. AUTOMATED CHECKS, one command: `python toolkit/check_all.py --slot "<slot>" -` (or `--song FILE`). Slots: Hook 1-4, Hook 5-8, Hook 9-16, V1 1-8, V1 9-16, V1 17-24, V1 25-32, V1 33-44, V2 1-8, V2 9-16. It runs:
   - match.py: the original's rhyme scheme annotated BY EAR (MANUAL_SCHEME; every pair the original rhymes must score >= 0.78, slant counted, British vowels), the rhyme-strength map (end-to-end and opening-to-end links incl. "Come on then ... Dublin"), bookends, internal rhyme density, syllables, endings, multis, alliteration;
   - flow_fit.py: the rhythm MEASURED from the original audio: exact line length, end rhyme starting on the original's 16th-step, END SHAPE (the rhyme must start a word where the original's does, with the same weak syllables before/after: 'in LA-gos' w|Sw is not 'Ma-JOR-ca' wSw), strong/weak pattern, no weak syllable on a beat; advisory triplets in benchmark/flow_template.json;
   - helpers freq: rare words (gate G2 prompt).
   Text stress flags are auto-waived only where the measured flow passes. Every "x" line must be fixed OR explicitly ranked and accepted with a reason: since 11 Oct 2026 check_all is the form TARGET, not the definition of done (it measures similarity to the original's rhythm and Joe's approved bars 1-4 fail it). Drive the problem count DOWN vs the previous draft; the hard gate is the meaning gate + G1-G6.
2b. TIMING FIT: `python toolkit/timefit2.py FILE` (per bar: cost and the reason, e.g. a weak word on a stressed step, an extra strong syllable, a syllable too long for its gap, a hard mouth join; ACCOUNTED must cover all 76 bars). Verdict from the original alone (bar <= p95, section mean <= worst original section + half its range). Try fixes with `python toolkit/timefit_try.py bar N "line" ...`. Report every failing bar by name, never a section total.
3. MEANING GATES (human; tools cannot judge these):
   G1 plain sense (a sentence a mate would say in the pub; the stanza is one connected thought);
   G2 recognisable (Joe's mates, 30s, southern English, get it instantly; no dated idioms like "gone for a Burton");
   G3 not a technique carrier (a bar that exists only for a rhyme, pun or alliteration fails);
   G4 if Joe gave a skeleton, also offer one fresh angle and say if his constraint is the weak point;
   G5 never claim parity; always name the weakest bar;
   G6 human voice: full spoken sentences, one scene per stanza, max one place per 2 bars in verses, accurate details (benchmark/authenticity_guide.md).
   SCREEN (optional, never a finish): `python ml/judge.py -` scores each bar's rejection risk against the 17 human gates and names the drivers (ml/README.md). It ranks; it cannot sign a gate off.
4. JOB CHECK: for each bar, name the original line's job (roll-call greeting + place, register flip, cashed idiom, x3 list, short place line, closer, etc.) and confirm ours still does it; flag orphaned words (e.g. "kroner" after Norway was cut).
5. SIDE BY SIDE: table, original vs ours per bar: rhyme tail (vowels + syllables), internal run, wordplay, imagery, character, other devices (benchmark/technique_audit.md). Truth flags: (invented) / (persona) / brands.
5b. RATCHET: if this is a revision, `python toolkit/ratchet.py <previous draft> <this draft>` must say OK (no section went pass->fail, no keeper or true place lost, locked lines unchanged).
6. STUCK RULE: +1 in STATE.md "Attempts"; if a trigger T1-T4 (CLAUDE.md) fires, pivot instead of editing again.
7. REPORT (short): verdict per section, the weakest bar and one fix direction, open questions for Joe. Append 3 lines to writing/iteration_log.md. If Joe rejects a stanza, save it as toolkit/tests/rejected_<name>.txt (first line '# SLOT STARTBAR') so calibration catches it next time.
