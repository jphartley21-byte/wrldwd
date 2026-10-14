---
description: Write or rewrite sections of the song with parallel agents that loop until every check passes
argument-hint: <which sections, e.g. "all" or "V1 17-24, V2 9-16"> [source draft, default the latest writing/full_draft_vN.md]
---
Write $ARGUMENTS using the process that worked (9 Oct 2026). Joe has approved multi-agent drafting for this command.

SETUP (main thread)
1. Calibrate: `python toolkit/calibrate.py C:\Users\Joe\Documents\Worldwide_private\original_lines.txt` must PASS.
2. Song map: writing/song_map.md (each section's original job, Joe's true places for it, places owned by one section only). Read material/travel_history.md only for new places.
3. Score the source draft: `python toolkit/check_all.py --song <draft>`; list each section's failures.

NO-REGRESSION RULES (why: in Oct 2026 each round undid the last: exact lengths deleted Boomtown, rhyme strength deleted Portsmouth, fixes rewrote passing bars)
- Choose end words by SHAPE as well as vowel: before picking a rhyme word or place, read the original bar's end shape from benchmark/flow_template.json ("end_shape", e.g. w|Sw = a weak word, then the rhyme STARTING a word, then one weak syllable: 'in LA-gos'). A word whose stress lands mid-word (Ma-JOR-ca) or with a different tail cannot fill that slot, however good the vowel (Oct 2026: Majorca in Ch L5 broke the hit of the rhyme). flow_fit enforces this.
- TIMING FIT (15 Oct 2026, the fit that decides flow): write CLAIM FIRST, then fit each bar to the original's timing with `python toolkit/timefit_try.py grid N` (the stress target), `bar N "cand" ...` (cost + flags, best first) and `gen N "a|b" "c|d"` (all combinations). It aligns our syllables one-for-one to the original's 16th steps (an extra or missing weak syllable like "the" or "-ed" costs), checks syllable length against the gap and mouth joins on 1-step gaps. Limits come from the ORIGINAL alone (bar <= ~3.0, section mean <= ~3.45, no floor from Joe's approved bars). Finish with `python toolkit/timefit2.py FILE` (ACCOUNTED line must read 76 expected, 74 scored, 2 by ear). Sense first: a bar that only passes by going telegraphic is a fail; say so rather than ship it. Fit and mouth costs are similarity to the original, Joe's ear overrules.
- MOUTH PASS (15 Oct 2026, report-only): after the fit, read each bar aloud against its template gaps. Long vowels / diphthongs and heavy codas need a gap of 2+ 16th steps or the end slot; runs of 1-step syllables must be light (short vowels, single consonants); avoid a front-spread vowel (ee, i, ay) straight into a back-rounded one (oo, aw, oh) on a 1-2 step gap, and avoid 2+ rare consonant joins in one bar. Check: `echo BAR | python toolkit/duration.py --slot-bar N`, `python toolkit/flow_check.py -`. Reference: benchmark/mouth_and_duration.md. Joe's ear overrules.
- Every constraint is known BEFORE writing: agents get ALL checks from the first pass (check_all + gates + job check + keepers), never one new check per round.
- Only FAILING bars may change. A passing bar may change only if a stanza-level check (scheme, density) needs it, with a one-line reason.
- After every pass: `python toolkit/ratchet.py <before> <after>`. If it says REVERT (a section passed before and fails now, problems rose, a keeper phrase or true place vanished, a locked line changed), undo that change and try another fix.
- Keepers (toolkit/keepers.json: Joe's locked lines, lines he liked, true places) are never dropped to pass a check. If a check and a keeper truly conflict, stop and ask Joe in one line which wins.
- A fix that breaks something else twice is the stuck rule's T3: pivot the bar (new angle) instead of trading one fail for another.
- Ratchet the score: accept a pass only if total problems fall or stay equal with a keeper won back.

AGENTS (one per section, run in background, effort medium; reuse existing agents with SendMessage when they exist)
Each agent's prompt MUST include:
- the REAL original lines for its slot, read from the private file (never a paraphrase; tell it never to quote them in replies or files, cite as V1 L17 etc.; if a content filter blocks it, retry with the same instruction, not a paraphrase, and tell Joe);
- its starting bars and the specific failures from check_all;
- the rules: CLAUDE.md rules 1, 4, 5; memory lessons (no gags, no obscure idioms, menace beyond Joe's normal life, southern voice, domestic people mentioned not addressed, real relatives kept out of crime lines);
- the no-regression rules above and its section's keepers;
- the loop: `python toolkit/check_all.py --slot "<slot>" -` until ALL PASS (run ALL checks every pass, then ratchet), plus /review steps 3-5 (gates, job check, side-by-side) every pass; stuck rule after 3 failed passes on a bar; cap 4-6 passes;
- output: a "Round N" section in writing/agents/<id>.md (bars, side-by-side table, weakest bar); reply under 120 words. No agent may claim parity.

ASSEMBLY (main thread)
4. Build writing/full_draft_v<N+1>.md and run `python toolkit/ratchet.py <previous draft> <new draft>`; it must say OK. For each section, keep a previous bar if it passes the checks and is more human (do not let fixes silently delete good lines or true places; test swaps with check_all before keeping them).
5. Run `python toolkit/check_all.py --song` and calibration again; fix cross-song issues (repeated end words or images, place clashes, character consistency: Gaz, Dave, the missus in Bristol, in-laws in Bergen).
6. Report to Joe: the full draft, what each round gained and lost, the weakest bars, open truth questions. Update STATE.md and writing/iteration_log.md.

LIMITS: this gets the FORM to match the original (rhyme scheme, rhyme strength, internal rhyme, measured rhythm, line lengths, rhyme landing). It cannot guarantee the bars are funny or sound like Joe: his ear (and a Suno render, then `toolkit/flow_map.py` on it) is the final test. Every time Joe catches something the tools missed, add a check and a toolkit/tests case.
