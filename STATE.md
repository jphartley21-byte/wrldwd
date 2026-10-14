# Current state (11 Oct 2026)

## The task now
Goal: a draft that beats the original on quality overall, one 4-bar block beating each of the original's blocks, and the whole song scoring above it - including on the literary/human criteria.
NEW STANDARD (11 Oct, after Joe rejected the first rebuilt hook as "not a coherent thought... no payoff"): benchmark/craft_principles.md. Before writing a section, state its ARGUMENT in one sentence, its runs (2-4 bars: bland setup, bathetic closer cashing an idiom on the rhyme beat) and its PAYOFF bar. Then write, then run BOTH gates.
  - `python toolkit/meaning_gate.py FILE|-`      each bar is a sentence with content (G1/G3)
  - `python toolkit/coherence_gate.py --goal "..." FILE|-`  argument, runs, cashed idiom, references, images, callback
  - `python toolkit/rubric_score.py --slot "Hook 5-8" FILE|-`  form, per bar, against that slot
  Calibration is asserted: the original's own 16-bar hook PASSES both gates; a scrapbook stanza fails.
OPEN TENSION (the central problem to solve): the hook that passed the FORM metrics (Q119+Q120, beats each slot by +4) FAILS the meaning and coherence gates; the hook rebuilt to the argument (Q121) PASSES both meaning gates and LOSES form (5-8 -3, 9-16 -2) because its argument words are hard monosyllables. Next: rebuild the runs on soft-tailed families (-ing nothing/something/ringing/talking, -y country/ferry/plenty/memory, -er border/order/water/corner, -o fellow/tomorrow) so sense and sound both hold.
Hook 1-4 is Joe's, locked. Verses not yet started. Everything is done in the main thread with the toolkit; no agents (rule 6).

Tools added: toolkit/meaning_gate.py (gates G1/G3 mechanised, in calibrate.py) and `rubric_score.py --slot NAME FILE` (per-bar comparison against ONE slot).
Everything is done in the main thread with the toolkit; no agents (rule 6).

STATUS 11 Oct 2026 (later): network approach running. writing/seeds_hook5-8.md = 8 seed arguments (one sentence + one line per bar + tail family + flip pair). files/net.py grows them: nodes = candidate lines TYPED by role (agent/verb/object/recipient/crew/flip), edges = the gate rules, trees = 4-line paths that pass everything. First crop: 640 paths -> 122 passing quads in writing/net_crop_hook5-8.md. Typing was necessary: the untyped network produced sound-perfect nonsense ("Under the radar the crate took papers"). Best tree by meaning so far: Hey there boss the Bristol raiders / Under the radar the crew made takings / On the level with my makings / Might flog the Bordeaux to traders (flip takings->makings = the money becomes the kit). Awaiting Joe's ear; bar 6 is the semantic weak spot and the harness flip test must compare whole words (it currently misses onset differences).
Hook 5-8 QUAD A: Hey there boss the Bristol raiders / Under the radar the boss wrote papers / On the level with my payers / Might check Bordeaux haul to traders
  measured: syllables 8/10/8/8 exact | audio flow frames 87/90/87/100% agreement, no beat mismatch, end shape + rhyme step exact | accents only on story words, accent mass at/under par | end carpet EY+schwa+z, AAAA | (6,7) papers/payers = the register-flip pair | cash 2/2 at par (under the radar, on the level) | places 2 = par (Bristol, Bordeaux) | runs 5 vs par 2 | internal rhyme 7 vs 4 | pile-ups 0.0 vs 0.25.
  weakest bar 8 (clipped article; "check ... to traders" loose). Pass-equivalent alternates: "...Bordeaux stock to traders", "Might check the Bordeaux to traders".


## Hook 9-16 v2 WRITTEN (11 Oct 2026, writing/hook_9-16_v2.md; v1 superseded)
First bars *written* rather than recombined. Frame recovered from the map's tail sounds (three `ɑː`, three `eɪ`, one `ɑː→aɪ`, one `iː→əʊ`). v2: scheme PASS, syllables `[7,7,8,9,12,5,8,7]` exact on every known bar, by-ear `AABACBDB` exact, meaning 0 fails, coherence 0 fails, check_all 17 problems (v1 18; Joe's approved bars 1-4 have 6, the best mined quad 4 — so FORM, not rhyme or sense, is the remaining gap), judge 0.442 (v1 0.538). v1 -> v2 fixed bar 5 (`cash, cash, cash…half the night, right`: 0.93 -> 0.15) and added tag endings to bars 6 and 8. Still weak: bars 1-4 are inert reportage that cash nothing; the map's soft `~Sw` ending on bar 3 could not be built without breaking the scheme (a trailing `it` puts an `ɪ` in the rhyme slot; the frame's soft ending is a trailing schwa needing enjambment).

**Judge calibration (do not re-learn):** `ml/judge.py` cannot fairly score this slot. Word-level signal is negligible; the top drivers are structural (`end_tag` -0.62, `scheme_letters` -0.58, `in_band` -0.51), and `end_tag` is largely "does the block resemble the one positive block" (Hook 1-4, ends all `əʊ`). Bar 5's 0.93 is out-of-distribution — no positive 12-syllable bar exists, and it stayed 0.93-0.99 across four rewrites. Cross-slot comparisons are invalid; that is what the forge was doing when it scored assembled 9-16 blocks 0.79-0.83.

**Pipeline verdict (11 Oct 2026):** 3 cycles, pool_size 2, 0 variants, every slot "new but below the pooling bar" — it recombines and produces nothing. It does not write. **Stopped 11 Oct 2026 (Joe's decision)** in favour of bar-by-bar writing in the main thread.

## NOTHING IS LOCKED (Joe, 11 Oct 2026)
Joe: "Nothing is locked at this time." Bars 1-4 are open for revision like everything else. Consequences: the `locked_lines` in toolkit/keepers.json and the "LOCKED" heading below are **no longer immovable constraints** - ratchet.py treats keepers as must-keep, so a bar-1-4 change will be flagged until that is revisited. Any bar may be replaced by a better-scoring one; the measure of "better" is one scoreboard (toolkit/trybars.py), not a locked-line rule.
Yo, bonjourno / Said damn at the on-stage porno / Front row on my phone, so bored, though / So I boarded a plane out to Bordeaux (UNLOCKED 12 Oct 2026: Joe scrapped toolkit/canonical.py, so these lines are no longer a protected source; they survive only as the gates' positive control in toolkit/tests/joe_hook_1-4.txt, read through toolkit/fixtures.py)
Lessons from 12 drafts: AAAA on a TWO-syllable vowel tail (here AO-OW, all exact); sound-alike puns (Dam/damn, bored/boarded, Porto~porno); the gag is flat attitude, never explained; menace must exceed the group's normal life (coke = no shock); Joe's ear and his own ideas beat mine: offer options, let him steer.
Tools: `quad` (4-bar technique scorecard, benchmark/technique_scorecard.md), `syllmap` (every syllable, rhymes, alliteration), `/review` command.
NEXT: bars 5-8 (original Ch L5-8: greeting #2 + place, business register bridge, perfect-rhyme pair that changes register (favours/flavours), closer place outside the frame with modal understatement).

## Done
- Research: comedy theory (Joe's definition), Genius line-by-line classes of the whole original, reaction notes (small samples), rubric rev 2.
- Toolkit built and tested (toolkit/): syllables, stress, rhymes, near and vowel-only rhymes, cut-up (mosaic) rhymes, theme-word families, line and chain checker. The original's 8 bars were run through `check` (numbers in the breakdown).
- Material: travel_history.md, place_specifics.md, place_sound_families.md (accurate local words).

## Next steps
1. BATCH 11, written against the phrase audit. The lineup now beats all 9 open slots, but the assembled song still repeats the pool's syntax: "and I am" x12, "and it is" x8, "Bloke at the door" x2. Write fresh-syntax quads (verb-first, place-first, present-tense report; no "And/Nobody/So/Bloke" openers, no "and I am ..." frame) so diversity and beating can both hold.
2. Re-run the loop after each batch: `python toolkit/calibrate.py` (must stay PASSED), the lineup (writing/song_lineup_v4.md), the per-slot gap report (writing/rubric_gap_report.md), then the repeated-phrase audit.
3. HUMAN PASS. `rubric_score.py --literary` prints the 0-3 critic sheet for the 28 criteria the tool cannot decide. Joe scores the top quads on those; that is the layer where the original still wins.
Everything else from the earlier plan (sound map, beat sheet, bar-by-bar build) is now inside the quad pipeline.

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
| 5-8 | 12 (v1-v12) shown; v8-v10 internal (not shown) | 6 (v7-v12) | AO (v1-v5, mixed), ER-AH Bergen (v6-v12) | T1+T2 FIRED 9 Oct: pivot. Parked: Majorca v5 (contender), Bergen v12 (flow/meaning stall) |
| 9-16 | 5 (Q119, Q120, Q121, hook_9-16_v2, forge #2) | 2 (v2, forge #2 - "neither of these are good enough") | the map's own frame (three ɑː, three eɪ, one ɑː→aɪ, one iː→əʊ) - KEPT, the frame is fixed by the map | PIVOT FIRED 11 Oct: v3 changes THEME + STRUCTURE (courier's round sheet), not the frame. See writing/hook_9-16_v3.md |

## Bars 5-8 no-commas revision (9 Oct, internal, not yet shown to Joe)
Two gate holes closed (11 Oct): `sense_checks.content_novelty` (a block that restates its own content words) and `sense_checks.proper_nouns` (the block must name as many places as the original's own block does at that slot: 2 for Hook 5-8, one inside the greeting frame and one outside it). Wired into forge `score`/`clean(strict)`; calibrated - ORIGINAL passes both, v11 FAILS both.
VERDICT ON v11 (Joe 11 Oct: "they don't make sense… flow is worse"): he is right and the gates could not see it. v11 does 1.5 of the original's 4 jobs (bar 5 is a fragment built for the port/Porto internal rhyme; bar 7 is a food list recycling bar 6's lager; bar 8 names no place). v11 now fails 5 named checks: 2 restated content words (par 1), 1 place named (par 2), 0.75 consonant pile-ups (par 0.25), and it is only 1.25-vs-1.25 on stress clashes because the pile-up fix cost a frame beat.
CORRECTION I OWE JOE: "strict flow EXACT" is weaker evidence than I claimed. `flow_template.json`'s strong/weak pattern is written by the same `sylls()` heuristic that reads our bars (flow_fit.add_weak), so frame agreement is a spelling-level word-stress match, not heard accent. The audio-measured side is only syllable count + 16th-step timing. Consonant pile-ups are consonant texture at word joins, NOT stress placement.
Worst version to date, kept only as the anti-example (session files/q5_j.txt): `Hey port and the road to Porto / Two glasses cold lager then cut corners / Lager chips and the last orders / Might hit the road then the border` - it passed form and failed sense, which is exactly what the two new gates now catch (and it still fails 0.75 vs 0.25 consonant pile-ups).
Gate fix: job check now passes the ORIGINAL (tokenises "E-se" as one word) - calibration intact.
NEXT: rebuild 5-8 CONTENT FIRST from writing/beat_sheet.md's Hook 5-8 scene (greeting+place / routine border stop / register flip to nothing / closer place with a modal), with the sound map as a constraint rather than the driver. No bar passes on form alone.
Pivot angles for 5-8 (pick by gates, build from scratch):
A. Keep the AO carpet of bars 1-4 all 8 bars (the original keeps EY all 8): Majorca/Portsmouth, order/border, water/daughter; bank 6+.
B. Motorbike tour 2023 Bilbao / Koh Tao on OW ("now, how, allow, somehow, eyebrow"), structure: roll-call of two places in L5.
C. Interrail 2019 Bratislava / lava / java (AA-AH), structure: number ladder across 5-8 (days, countries, quid).

## 11 Oct 2026 (later) — map accuracy closed, calibration bug found, pool screened
- original_map: bar 3 now shows `plain clothes [authority (undercover police)]`, payoff in the rhyme slot, and the pun pair `plain`/`plane` (bars 3-4). New CSV columns: idioms_named, payoff_in_rhyme_slot, pun_pair_with, scheme_loose_by_ear, scheme_human_by_ear (36 cols).
- Craft_scan: BRIT_OVR adds the words britfone lacks (favours, flavours, lagos, wagwan, luego); wagwan's internal rhyme now scores (ɑː-ɑː), matching Joe's ear. loose_families is calibrated against the by-ear annotation: 5 of 10 slots exact, 76% of pairs.
- CALIBRATION BUG FOUND AND FIXED: the coherence gate's "one cashed idiom per 4 bars" made the ORIGINAL fail its own gate on lines 9-16 (its cash events are all in bars 1-8). Now the requirement is the original's own count for the same lines (cash_par): Hook 1-4 = 3, Hook 5-8 = 2, Hook 9-16 and both verse openers = 0. Selftest checks the original quad by quad.
- Pool screened (121 quads) against calibrated gates + fair per-bar form margin: 51 pass both gates, 26 beat their slot's par. Hook 9-16: Q120 PASSES (+4). Hook 5-8: NO candidate passes — Q119 has 1 cash event where the par is 2, and its payoff is not in the rhyme slot; it also has an orphan "they". That is the next writing job.

## 11 Oct (later still) — Hook 5-8 written and verified; draft v19 assembled; two more tool bugs fixed
- HOOK 5-8 (Q122): "Ola from the hills above Porto / A glass of port and a page of orders / Cut corners up at the border / Might hit the road to Majorca". VERIFIED: meaning PASS, coherence PASS at the slot's own cash par (2 events: cut corners, hit the road), form margin +4 with NOTHING below par, line lengths 9-10-8-8 = exactly the original's measured lengths for those lines, carpet 1.00 (the original's own measure). Joe's locked 1-4 + Q122 + Q120 = the full 16-bar hook, all three blocks at or above the original's par.
- TWO TOOL BUGS FIXED (both would have produced confident nonsense): (a) quality_gate.extra_measures rebound n inside a loop, so five song-level measures (breath/X lines, domestic anchors, voice tics, bursts, facts from material) were garbage - the par read 170.67 breath lines per 8 bars; (b) `--song` fell through to the verse branch, so "song level" runs were comparing the whole draft to one slot. Also song_sections now ignores table rows and fences, and --song/--line are accepted as aliases.
- DRAFT: writing/full_draft_v19.md (76 bars, no repeated lines). Song level: FAIL, margin +5, 5 below par - cashed idioms in the verses 0.21 vs 0.84, "sections the right length" 0.00 vs 1.00 (the draft is labelled in 4-bar quads, not the beat sheet's 8-bar slots), repeated 3-grams 10 vs 3, voice tics 0.21 vs 1.37, facts from material 3.37 vs 4.00. 14 measures beat par.
- NEXT: (1) re-cut the draft into the beat sheet's slot names (V1 1-8, V1 9-16, ...) so the section-length criterion is measurable; (2) give every verse quad one cashed idiom and one voice tic; (3) kill the repeated 3-grams - the pool's "Nobody.../Copper.../and it's..." frames are the templating Joe rejected, so verse quads now get written fresh in the main thread rather than picked from the pool.

## 11 Oct (evening) — the FLOW spec is now the target, and 200 quads needs a frame-first build
- THE FLOW TARGET IS PER LINE, measured from the audio (benchmark/flow_template.json): exact syllable count, the strong/weak frame, the end shape (|Sw etc), and the syllable where the end rhyme starts. flow_fit.fit checks all four. `/review` already used it; the lineup/draft work did not.
- CONSEQUENCE: Q122 (Hook 5-8) BEATS the aggregate form measure (margin +4) but FAILS the measured flow on all four lines (9 syl vs 8, stress frames 50-70% same, end shape ~Sw vs |Sw). Beating a summary measure is not flowing the bar. Any quad destined for the hook must be written to the frames.
- TRAP FIXED: flow_fit.fit returns (ok, GRID_TEXT) where the reasons sit after "FAIL: " in the TEXT. forge.py was reading the grid as a list of reasons, so every flow verdict was inverted. Now `forge.fit_fails()` parses it properly.
- TOOLKIT for the 200-quad build (in the session files dir): forge.py (score a quad against any original 4-bar block: gates + fair margin + per-line flow), forge.py --lines N (test many candidate lines for one bar), compose.py + wordbank.tsv (frame composer skeleton), keep_lines.py + lines_bank.tsv (the growing library of lines proven to fit a measured frame), detail_bank.txt (place details in 9 KB), frames.py (the frame of every bar).
- BANKED SO FAR (13 lines, all proven to fit their frame): bar 5 has 5, bar 6 has 1, bar 7 has 2, bar 8 has 2. Example: bar 5 frame SSwwSwSw takes "Cold beer and the road to Porto"; bar 7 frame SwSwwSSw takes "Lager, chips, and the last orders"; bar 8 frame SSwSSwSw takes "Cold beer and a boat to Oslo".
- SCALE: 23 original 4-bar blocks (19 unique flows; blocks 77-89 repeat 1-13). Joe wants 200 quads with 5+ per block. Hook blocks 1 and 5 also need 2-3 CASH EVENTS each (idioms or cross-bar puns) inside the frames - the hardest constraint in the project.
- NEXT: sweep the line bank per bar (fill every block's four frames with 8+ banked lines), assemble quads that also satisfy the scheme (tail family per block) and the gates, keep 9 per block, and write them to writing/pool_v4_quads.md with the forge line for each.

## 11 Oct (night) — first FLOW-CLEAN quads exist: 7 for the Hook 5-8 flow
- writing/pool_v4_quads.md is OPEN (header + tab-separated quads + a verification comment line each). pool_build.py re-verifies every quad before it is written: both gates + per-line flow + margin >= 0.
- 7 clean quads so far, all on block 5 (bars 5-8) - the first quads in the project that fit the MEASURED frames. Example: "Wet roads, in the bag, in Porto / Three weeks and six nights and cut the corners / Coffee, dark, and the long borders / Long road and a boat to Oslo" (syllables 8-10-8-8 = the original's own, scheme ABBA, 2 cash events, margin +2, every line flow-clean).
- The working recipe for a block: two cashed idioms where the slot's par needs them (bar 5 takes "... on the house/in the bag, in Porto"; bar 6 takes "... and cut the corners"); bars 6-7 share the ɔː-ə(z) family (corners/orders/borders); bars 5 and 8 share the ɔː-əʊ family (Porto/Oslo).
- SCALE so far: 7 of the 200. 19 unique flows (23 blocks; 77-89 repeat 1-13). Verse frames now read out: block 17 = 10/10/8/9 syl, block 21 = 6/8/7/13, block 25 = 7/6/5/12, block 29 = 12/10/12/11 - most verse bars end |Sw (stressed + weak) so verse lines want dactyl-ish tails (orders, hostel, water, city).
- The DP filler works but produces robot English ("Cold beer keep it quiet Hostel") and is therefore usable only as a suggestion engine: lines are authored, then verified. Do not let generated word salad into the pool.

## 11 Oct (late) — the gate holes Joe found are closed, and research is now a documented move
- THREE NEW CHECKS, all calibrated on the ORIGINAL's own block (par = its value there), added to forge.py and sense_checks.py:
  1. list_fragments - bars chaining 2+ "and/or" with no finite verb (a list, not a thought)
  2. field_spread - distinct lexical fields (vehicle/weather/food/money/authority/transport/admin/place/lodging)
  3. drift_pairs - end-pairs that rhyme ONLY because the stressed vowels share a class (Porto ɔː vs Oslo ɒ). The original's own hook pairs are all clean (identical stressed vowel + coda), so drift can never count as a rhyme for us.
  Plus: flow_fit is now read in STRICT mode for the pool - the stress frame must match position for position, because the original's own bars are 100% by construction. A 90% frame (which our line 6 had) no longer passes.
- VERIFIED: the original's own block 5 PASSES all of it (margin +3, 0 list fragments, 2 fields, 0 drift pairs); our flagship quad now FAILS on all four counts (list fragment at bar 2, 3 fields vs 2, drift pair bars 1-4, strict flow at bar 6 position 8). Joe's ear and the gates now agree.
- Also fixed, from Joe pasting the original's lines: the British-vowel lookup indexed the British list with the AMERICAN phone index, shifting every britfone word's vowels (Lagos read ɒ-ɑː instead of eɪ-ɒ); and the map's syllable column was wrong on 7 rows (it now shows the text count, flags disagreements with !, and carries syllables_audio).
- RESEARCH TOOL: toolkit/research.py - word W (pronunciation stack + is it in the original), rhymes/near/sounds W (local dictionary AND Datamuse online), mine QUERY (greps travel_history + the photo/video-derived place specifics + sound families), slang W (Wiktionary). Documented in toolkit/README.md so agents reach for it by default.
- NEXT: rewrite hook 5-8 until it passes every check (2 fields max, no list fragments, no drift pairs, exact frames, 2+ cashed idioms, one thought). Constraints already worked out: bar 5 tail Porto (ɔː-əʊ) must pair with a word sharing the STRESSED vowel (Majorca ɔː-ə is clean; Oslo ɒ-əʊ is drift), bars 6-7 want a clean pair inside ONE field (lager/guava, porter/shorter).

## 11 Oct (late 2) - first quad that passes the STRICTER gates, and the pool re-verified honestly
- REWRITE for block 5 (Hook 5-8):
    Cold beer on the house in Porto
    Two glasses, cold lager, back road corners
    Lager, chips, and the last orders
    Might hit the road past the border
  Verified: margin +1, syllables 8-10-8-8 (the original's own), scheme ABBA, meaning PASS, coherence PASS, cash 2 of 2, list-fragments 0 vs the original's 0, DRIFT PAIRS 0 vs 0, and all four lines pass the STRICT frame check (exact stress positions).
- WHAT CHANGED vs the rejected version: bars 5/8 now rhyme on an identical STRESSED vowel (Porto ɔː / border ɔː) instead of Porto ɔː / Oslo ɒ, which was the drift the ear caught; no and-chains; and every line is exact on the frame rather than 90%.
- POOL RE-VERIFIED: re-scoring all 8 entries against the current gates kept 1 and dropped 7 (all failed sense and strict-flow). The pool is now 1 quad. The dropped ones were verified before the strict checks existed, so their claim lines were stale - that is the honest count, not a regression in the writing.
- STILL NOT RIGHT in the rewrite, by the beat sheet's JOB CHECK (human, not yet mechanised): bar 5 should be a bare greeting + place and has no greeting word; bars 6-7 read as lists even though they are comma-lists rather than and-chains (the list check only catches and-chains); the field warning flags 5 fields (coarse lexicon).
- NEXT: (a) a cheap JOB check - bar 5 must carry a greeting word, the closer must carry a modal - since both are in the beat sheet; (b) keep building quads for block 5 with quadforge.py (bars 6-7 need more phrase-bank shapes: SSwSSwSSSw and SwSwwSSw are the hard frames); (c) then the other 18 flows.

## 11 Oct (late 3) - the ML layer: the 17 HUMAN gates get a screen (ml/)
Built ml/ (see ml/README.md). check_all.py measures the 24 machine-decidable criteria; the other 17 are HUMAN (benchmark/gate_coverage.md). ml/ now scores a bar's REJECTION RISK from a rule prior taken from Joe's own rejections (ml/domain.py) plus a small fitted diction model, and prints the drivers.
  - `python ml/judge.py FILE|-`      per-bar risk (0 = lands, 1 = reject) + why. Screen only.
  - `python ml/evaluate.py`          the acceptance gate. Currently PASSED on all three tests.
  - retrain after any new verdict:   `python ml/build_dataset.py` then `python ml/train_judge.py`.
WHAT IT FOUND (honest): the measurable features alone do NOT separate Joe's verdicts - the rule prior ranks the rejected fixtures LOWER than the locked bars (reject mean -0.67 vs accept -0.12). That is the same gap gate_coverage.md describes, now measured: his verdicts are driven by the human criteria, not the mechanical ones.
EVIDENCE it is not a toy: the one labelled stanza Joe called "not bad, it's a contender" (writing/contenders.md, never trained on) lands between the tiers: accept 0.13 <= park 0.59 <= reject 0.94. 49% of the ~420 never-judged bars score as LAND, so it is not collapsing to "reject everything".
DATA: 21 positive rows (4 locked bars + 17 phrases Joe kept), 56 negative (6 rejected fixtures + agents' "weakest bar" notes). Too few for a LEARNED judge - `train_judge.py` says so and reports rank separation + leave-one-positive-out instead of a fake AUC.
NEXT: (a) the flywheel - add POSITIVES (every bar Joe keeps, and the locked bars of each finished section) to ml/data/dataset.jsonl, then retrain; (b) ml/lora/preflight.py decides when a writer LoRA is trainable - today it says NO (no torch/GPU, 63 pairs vs a 1000 threshold), and ml/export_pairs.py already writes ml/data/{sft,dpo}.jsonl for when it flips; (c) wire the judge into /review as one more screen, never as the finish.
DATA NOTE for Joe: toolkit/keepers.json stores the locked bar as "Good show but the dame look bored, though"; the locked version in STATE/writing is "Damn good show but the dame look bored, though" (the Damn/damn pun). The keepers copy is missing "Damn" - flagging, not editing (the file says removing needs Joe's OK).

## 11 Oct (late 4) - research now compounds, and one dead tool is fixed
Joe asked whether the model could search the internet and grow its vocabulary while writing. Answer then: only partly - research.py could look things up, but NOTHING recorded what it found, so every session re-asked the same questions, and the `slang` lookup was DEAD (Wiktionary 403).
  - FIXED: `python toolkit/research.py slang W` works now (Wikimedia requires a User-Agent; it answered 403 without one).
  - NEW: `toolkit/vocab.py` + `toolkit/vocab_ledger.jsonl` - a persistent vocabulary ledger. Every lookup from research.py is banked with British IPA, syllable pattern, end-sound tail, rhyme family, whether the original's lines use it, and a G2 verdict. Online rhyme results are CACHED, so a repeated query costs no network call. `python toolkit/vocab.py show [--rare|--family KEY|--all]`.
  - HONEST LIMIT: the G2 verdict is a PROXY (`wordfreq` Zipf < 3.0, the same threshold as helpers.py freq) and `wordfreq` is US-weighted, so it under-scores real British words - it calls "skint" and "winnebago" G2 RISK. It prompts the ear; it never vetoes. Structural junk is dropped when banking bulk candidates, but an explicit `word W` lookup is always kept. `vocab.py selftest` is now asserted by calibrate.py (which still PASSES).
  - BOUNDARY: only a headword (<= 3 words) may leave the machine - a bar is >= 4 words, so a lyric line cannot be sent even by accident. `mine` is entirely local. Nothing of Joe's material or the song goes outward.
  - STILL TRUE: a wider vocabulary is NOT the bottleneck (his rejections were argument/coherence, and G2 is what killed the obscure words). The ledger banks FILTERED vocabulary, it does not chase volume.
  - NEXT: keep using `research.py` while writing (it now pays off twice - cached + banked); `vocab.py show --rare` before a bar ships; and if the ledger proves useful, feed its UK end-tail/family data into ml/judge.py's OOV/G2 features.

## 11 Oct (late 5) - Joe's GPU: measured, and a local generator wired to the gates
Joe asked whether the repo can run as an LLM on his RTX 5070 Ti, efficiently, to reach the original's quality.
MEASURED (not guessed): RTX 5070 Ti, 16303 MiB, driver 595.79, compute cap 12.0 (Blackwell). Ollama 0.15.6 ALREADY INSTALLED with three models (mythomax-l2-13b Q4 7.9GB, dolphin-llama3 4.7GB, llama3 4.7GB). Throughput 147 tok/s (8B). No torch, no nvcc (so training needs an install; inference does not). 37 GB free disk.
QUALITY TEST (the honest bit): given a fair version of the Hook 5-8 constraint, llama3 appended the literal token "OH" to every line instead of rhyming; dolphin-llama3 wrote three quatrains instead of four bars and closed with a moralising "So remember folks..." - verbatim on our own AI-tell list. Feed to our tools: check_all FAILS all 4 bars (syllables, ending, stress grid, rhyme depth, flow), ml/judge REJECT 0.73, meaning_gate PASS. So: the generator is the weak link, the filters work.
NEW: ml/generate.py - a LOCAL candidate generator. `python ml/generate.py --slot "Hook 5-8" -n 20` calls Ollama (localhost only), builds the prompt from the slot's MEASURED spec only (syllables, by-ear scheme, end shape - never the original's words), then filters: meaning_gate (veto) + check_all (ranking) + ml/judge (veto). Survivors -> writing/generated_<slot>.md; EVERY candidate + verdict -> ml/data/generated.jsonl (the flywheel). Live run: 3 candidates in 22s at 0 survivors, all judged REJECT 0.665-0.779 - i.e. the local model buys VOLUME, not quality. ~2.2s per candidate is the verifier, not the model.
*** FINDING THAT NEEDS JOE'S DECISION *** check_all FAILS Joe's own APPROVED bars 1-4: bar 2 is 8 syllables vs the original's 9 ("must be exact"), plus stress-grid and end-shape (|S vs ~S) misses. check_all is therefore a similarity-to-the-original's-audio gate, NOT a quality gate. This CONFLICTS with the Definition of Done ("check_all.py says ALL PASS"), which the locked section itself would not satisfy.
*** DECIDED 11 Oct (Joe): check_all is a RANKING TARGET, not a hard veto. *** The Definition of Done in CLAUDE.md is redefined: meaning_gate PASS + G1-G6 + job check + ratchet (no regressions and no RISE in form problems). Form is driven down and used to rank, not to veto; `python toolkit/check_all.py --score --slot NAME -` reports the count (toolkit/check_all.py now exposes `problems_of()`), and /review step 2 says an "x" line may be ranked-and-accepted with a reason instead of being auto-rejected.
  - NEXT: (a) Joe's call on the check_all conflict above; (b) the ml/data/generated.jsonl log is now a growing source of negative training data for ml/lora/.

## 11 Oct (late 6) - LLM GENERATION PARKED (Joe, 11 Oct): the model cannot hear the grid
Joe's decision: stop using an LLM to generate bars; put the effort into argument-first writing. The evidence, so this is not reopened without new facts:
  - One-shot naive prompt: 7 candidates, 0 survivors, best 10 form problems. One-shot MEASURED-SPEC prompt (per-bar stress grid + end shape): 3 candidates, 0 survivors, best 10 - NO GAIN.
  - REPAIR loop (feeding check_all's own complaints back, 2 rounds): form problems 10 -> 10 - NO GAIN.
  - Failure modes over 13 candidates (`python ml/generate.py --analyse`): stress grid 100%, strong/weak 100%, rhyme depth 100%, mid-bar pause 100%, rough ending 92%, syllables 85%, line length 85%. The first four CANNOT be fixed by prompting or looping: they are measured from the original's AUDIO and the model cannot perceive the beat. (Joe's approved bars: 6 form problems, risk 0.13.)
  - The meaning gate mostly PASSED: these models write register-appropriate SENTENCES, they cannot write BARS. If ever revisited, the only honest role is idea/diction generation, never the grid.
  - Throughput 147 tok/s on 8B. Registry sizes if ever upgraded (all fit 16GB): llama3.1:8b 4.9GB, qwen2.5:7b 4.7GB, gemma2:9b 5.4GB, mistral-nemo:12b 7.1GB, qwen2.5:14b 9.0GB - but all are the same 2024 generation as the three installed.
  - PARKED, not deleted: ml/generate.py stays as the harness (it is how the above was measured) and ml/data/generated.jsonl stays as negative training data. Do NOT run it for writing.
TWO BUGS FIXED while measuring (both in ml/features.py clean_bars): draft PREAMBLE PARAGRAPHS were being read as bars (5 prose blocks had leaked into the unlabeled pool - now 0), and model output prefixed "Bar 1:" was not stripped. Labelled tiers verified unchanged (accept 1, like 1, park 1, reject 6, weak_neg 11).

## 11 Oct (late 7) - back to argument-first writing: Hook 5-8 plan proposed
Per benchmark/craft_principles.md section 5 (state the argument, the runs and the PAYOFF BAR before writing words). Sound architecture measured, not guessed: the original's Hook 5-8 is A=(stressed ay) with the weak tail free to drift (L5 ay-o, L8 ay-a), B=(exact pair L6/L7), so our AO carpet from bars 1-4 can hold across 5-8 the same way.
  - Family A (AO, weak tail free): bar 5 = AO-OW (a place: Porto / Oslo / Padstow); bar 8 = AO-ER or AO-OW (modal closer, place outside the frame).
  - Family B (exact pair, bars 6-7): the register flip. Candidate found: orders / borders (AO-D-ER-Z) - admin -> geography, the favours/flavours move.
  - G2 CHECKED with the new ledger (`python toolkit/vocab.py g2`): border 4.70 PASS, corner 4.75, water 5.52, daughter 5.07, order 5.49, quarter 4.72, porter 3.98, mortar 3.75, slaughter 3.84 - the whole AO-ER soft tail is recognisable. `border` also pulls boarder/broader/disorder/recorder from the local dictionary.
  - Cashed-idiom candidates for the AO-ER tail: out of order (broken thing / unacceptable), in hot water (trouble / a bath), on the border, in order, back order.
  - NEXT: Joe steers the argument and the payoff bar; then write the 4 bars to the sound plan, then both gates.

## 11 Oct (late 8) - FORGE: exhaustive search, no input needed until the end
Joe: "I dont want to have to decide a story or theme or argument. The system should just work out all of the best options available, exhaustively without needing my input until the end."
NEW: `toolkit/forge.py`. It does not write sentences and it does not ask. It mines everything the project has ALREADY written (1,100+ unique bars and every assembled block in writing/), enumerates every combination that satisfies the slot's measured rhyme scheme, hard-filters on the meaning gate + scheme, then ranks by an objective weighted on the human-gate judge - because QUAD A passed every measured gate and was rejected, the judge is the only component that models "would Joe reject this".
  - `python toolkit/forge.py --slot "Hook 5-8"` -> writing/forge_Hook_5-8.md. Explored 1,623 combinations, 131 passed the meaning gate, 60 form-checked.
  - `--selftest` must REDISCOVER Joe's locked bars (it does, rank 16 of 40 - see the calibration note below).
RESULT for Hook 5-8 (top of the ranking):
  #1 score 1.52  risk 0.34  cash 2/2  form 4
     Cold beer on the house in Porto / Two glasses, cold lager, back road corners / Lager, chips, and the last orders / Might hit the road past the border
  #2+ are variants of QUAD A ("Hey there boss the Bristol raiders ... On the level with my shavings / Might flog the Bordeaux to traders"), form 0-1 but risk 0.51+.
THREE FINDINGS, all honest:
  1. #1 is a quad the pool had SIDELINED as "NOT YET PASSING" (writing/pool_v4_quads.md CONTENT-FIRST REBUILD). By this objective it is the best available, and its FORM (4 problems) beats Joe's approved bars (6). Third instance of the same pattern: an over-strict gate deprioritising work that would pass by the real standard (cf. check_all failing the locked bars; Majorca parked).
  2. THE JUDGE AGREES WITH JOE OUT OF SAMPLE: #1 scores risk 0.34 (LAND band) while the whole QUAD A family he rejected scores 0.51+ (EDGE). QUAD A's rejection is NOT in the training data, so this is genuine agreement, not memorisation.
  3. The search produced bars that did not exist before (recombination): "the crew made takings / my shavings", "the box took savings / my makings" (form 0-1).
CALIBRATION NOTE (the next step): the objective is NOT yet fitted to Joe. The selftest puts his approved bars only at rank 16/40, because the objective punishes the cash-event deficit - his approved section cashes 0 idioms while the gate demands ~3 at that position. Fitting the weights to his one known-good section is the obvious next move, but with one example it would overfit; better to collect 3-5 approved sections first.
TWO MORE BUGS FIXED while building (both the SAME CLASS as the check_all problem - over-strict matching that rejects Joe's own work):
  - The first enumerator keyed rhymes on (vowel + exact coda), which split bonjourno / porno / bored / Bordeaux into four families even though the map calls that passage AAAA. Now it clusters on craft_scan.tail_score (the repo's own family logic) and re-verifies every assembled quad with craft_scan.families().
  - The miner was line-based, so it silently DROPPED every quad stored on one tab-separated line - i.e. the whole of pool_v3/v4_quads.md. Tab rows are now parsed as blocks, and every consecutive 4-bar window in a file is also a candidate.

## 11 Oct (late 9) - CASH-EVENT GATE REMOVED (Joe), and the pipeline is running continuously
Joe's instructions, in order: "remove the cash event gate", then "run the writing pipeline continuously non stop. Do not stop until i manually say STOP".
CASH GATE REMOVED (it was the ONLY thing failing Joe's own approved section):
  - `toolkit/coherence_gate.py`: the `cash_events < need` FAIL is gone. Cash is still MEASURED and printed (`cash events N (par for this position M) - reported, NOT a gate since 11 Oct 2026`). Joe's approved bars 1-4 now PASS the coherence gate (they failed solely on "0 cash events, need 3"). The scrapbook calibration is unaffected: it still fails on two bare indefinites, so `--selftest` still PASSES.
  - `toolkit/quality_gate.py`: "Cashed idioms per 8 bars" moved into a new `REPORT_ONLY` set - still printed, no longer counted as BELOW par at verse or song level.
  - `toolkit/forge.py`: the W_CASH term is out of the objective (it was why Joe's approved section ranked 16th of 40 in --selftest). Cash is still printed per candidate.
CONTINUOUS PIPELINE: `toolkit/pipeline.py`. Loops the forge over all 9 open slots forever, pools only NEW quads the judge does not flag (risk < 0.45 - pooling bad quads would rot the corpus the next cycle mines), and widens its search budget each cycle (cap 12->20, confirm_k 12->40). The pool file lives in writing/ so the NEXT cycle re-mines it and the corpus feeds itself. Artifacts: writing/pipeline_pool.md, pipeline_results.jsonl, pipeline_log.md, pipeline_status.json. Stop with writing/PIPELINE_STOP. Bounded runs: --once / --cycles N.
FIRST CYCLE RESULT (honest, and it matters): only Hook 5-8 produced a quad that clears the judge bar (score 1.52, risk 0.34, form 4). The other 8 slots' BEST available combination scores risk 0.56-0.91, i.e. the existing corpus contains nothing the judge accepts for them. The loop can only search what EXISTS (plus what it pools), so it will converge and then spin - it cannot manufacture new quality. That is the real constraint on the song, and it is now measured rather than assumed.

## 11 Oct (late 10) - the pipeline converged; variant generation tried and MEASURED USELESS; objective recalibrated
JOE ASKED "has anything been produced yet?" AFTER 14 CYCLES / 126 SLOT-RUNS (~2.4 h). HONEST ANSWER: NO - 1 pooled quad, found in cycle 1. Every slot's best score was IDENTICAL in every cycle (Hook 5-8: 1.52 in cycles 1-6 and onward), i.e. the search converged immediately and has been re-finding the same answer. Only 12 distinct quads were ever seen as "best per slot" across 126 runs.
ATTEMPTED FIX - mechanical VARIANT GENERATION (`forge.variant_bars`, no LLM, no human): swap a bar's END WORD for another word in the same rhyme family with the same syllable count and a G2-passing Zipf, so the frame and the rhyme both survive. It creates real new bars (823 from 1,142). MEASURED RESULT: ZERO improvement - best score identical at 1.52 with and without variants, and the #2/#3 slots got worse. Swapping a rhyme word produces formally valid but semantically empty bars ("Shifting gear through the balconies / cantonese / colonies"): the judge rejects them all. Variant generation is kept in the code but OFF in the pipeline, with the measurement recorded so it is not tried again.
THREE MORE CORPUS LEAKS FIXED (all were polluting the ranking - a junk quad reached rank #2):
  - structure lines like "[Verse 1, Block A: Interrail on -ail]" were being graded as BARS (bracket lines are now rejected, matching check_all's own reader).
  - notes labels ("quad: syl 4,8,8,10; AAAA exact AO-OW...", "Alt 8: ...") - a leading short LABEL plus colon is now rejected.
  - annotation parentheticals ("(Porto 2023 true; timeshares invented; callback to porno in bar 2)", "(hinge to -ay)", "(was 8)") and shell/path lines ("python toolkit/calibrate.py C:\\...") are now rejected.
  Corpus 1,142 -> 1,051 bars. ~64 long/prose-ish lines remain; they lose on the gates, so they are noise rather than corruption.
OBJECTIVE RECALIBRATED, and the selftest proves it worked: W_SYL 0.5 -> 0.25 and W_ORPHAN 0.5 -> 0.2 (both are TIEBREAKERS, not drivers - Joe's approved bars sit 1 syllable off the original's frame on two of four bars, and coherence_gate's own docstring says the original has 9 orphan bars of 16). Result: Joe's APPROVED bars now rank **#1 of 179** on Hook 1-4 (they were 16 of 40 before the cash gate came out, and 47 of 179 immediately after, when removing the cash gate let far more quads compete). The selftest's assertion changed from RANK to PROPERTY (enumerated + judge recognises, risk < 0.35) because rank depends on how many rivals clear the same gates.
PIPELINE RESTARTED (cycle 1, pool 1 quad). Standing verdict unchanged: 8 of the 9 slots have nothing in the corpus that clears the judge bar (best risk 0.56-0.91). The loop cannot create material, so those slots need new bars WRITTEN. Watch: rank #2 on Hook 5-8 is the lowest-risk quad the search has ever found (risk 0.295, LAND band) - "Case in the boot, and it's ready / Back on my bike put the foot to the floor / All the shoes come off at the door / Big serve bish bosh in the belly" - the Bergen in-laws "shoes off" motif, though its form is 11.

## 11 Oct (late 11) - Joe asked "is it writing new bars?" NO - and the reason 8 slots were dead was a BUG IN THE FORGE
ANSWER: no. The live process logged "pool 1052 bars (0 variants)" - it recombines existing text and creates none. Both text-creating mechanisms are off and measured useless (ml/generate.py: parked; forge.variant_bars: 823 bars, zero gain).
BUT the check found the real reason 8 of 9 slots found nothing, and it is the SAME CLASS of bug as check_all and the coda key: THE FORGE ENFORCED A STRICTER RHYME TEST THAN THE REPO'S OWN GATES.
  - The forge grouped and verified rhymes with `craft_scan.families` (tail_score on the two-syllable tail). The gates (match.py, used by check_all and calibrated against the original) test every pair in a scheme group with `best_end(...) >= 0.78` over a 1-3 syllable span.
  - For Hook 9-16 the two disagree completely: the by-ear scheme is AABACBDB (the target, what MANUAL_SCHEME says) while the strict tail column reads ABCDEFGF. `families` therefore saw the required pairs as NON-rhyming and threw the candidates away.
  - FIXED: `forge._scheme_ok()` now tests the scheme exactly as the gates do (pairwise match.best_end >= 0.78), and the pruning cluster threshold loosened 0.78 -> 0.62 so the prune cannot hide candidates the gate would accept.
  - RESULT, measured: Hook 9-16's best form problem count went 18 -> **2** (and 1 on the runner-up). The forge selftest now ranks Joe's approved bars #1 of **345** (was 1 of 179).
  - HONEST CAVEAT, and it is the new binding constraint: the judge REJECTS those assembled 8-bar blocks (risk 0.82-0.89 vs his approved 0.13). So the search now finds formally strong candidates and the human-gate model is what stops them. The judge was trained mostly on 4-bar blocks, so its reading of an 8-bar assembly is less trustworthy than its reading of a quad - worth recalibrating.
  - Best assembled Hook 9-16 (form 2, risk 0.83): "In Bergen it's always skal / The in-laws say shoes off or it's war / Next I tipped my Porto waiter / Then rode back with a case maybe four / Nordic pine with a Nordic nine and Nordic bride / Then down Oslo way / Stayed at some mate's mate's in his bath / Fifty kroner happy days" - all Joe's real material, formally near-par, and the judge still says no.
PIPELINE RESTARTED on the corrected test (cycle 1).

## 11 Oct (late 12) - Joe rejected BOTH 9-16 candidates; PIVOT to a premise with a character; and the ONE-SCOREBOARD answer to "land on optimal bars faster"
JOE: "Neither of these are good enough" (hook_9-16_v2, forge #2). DIAGNOSIS, not a re-roll: both are accurate REPORTAGE - places and facts, no stance, no character, one cashed phrase each. forge #2 is the more misleading of the two: its lines are RECYCLED from drafts Joe already rejected ("All the shoes come off at the door", "foot to the floor" are corpus lines), which is exactly WHY it scores form 1 - the corpus lines were written against the flow template. Form-clean and idea-poor are the same thing in this corpus.
PIVOT (theme + structure, frame kept because the map fixes it): writing/hook_9-16_v3.md - the back half of the hook as a COURIER'S ROUND SHEET. The frame supplied the premise: its end sounds hand you freight/weight (eɪ), load/road/rest to go (əʊ), supplies/price (aɪ), bazaar/bar/car (ɑː). Five cashed phrases with the payoff in the rhyme slot (cash in hand, out the way, the same price, by the weight, the rest to go), a stance in every bar. Scheme PASS, syllables [7,9,8,9,12,5,8,7] exact, form 13, meaning 0, coherence 0, judge 0.730. Honest: form 13 is mid.

TOOL: toolkit/trybars.py - the fast inner loop. Scores ANY number of candidate blocks in ONE call, ranked, with per bar: syllables vs the slot frame, tail vowels, the rhyme families actually formed, hard/soft/tagged ending, meaning + coherence fails, the full check_all list, judge risk, and --detail for what drives the weakest bar. check_all is 264 ms/bar against ~2 ms/bar for everything else, so it is memoised to the temp dir: 3 s per new block cold, 0.5 s warm. Selftest passes; asserted in calibrate.py; documented in toolkit/README.md. A 9-candidate sweep across 2 slots is now 2 calls instead of ~20.

ANSWER TO "HOW DO WE LAND ON OPTIMAL BARS FASTER" - compute was never the bottleneck:
1. The repo ranked candidates with TWO instruments that disagree, and the pipeline pooled on the wrong one. Objective measures (scheme, syllables, form, meaning, coherence) are calibrated; the judge is memorisation of ONE positive block.
2. PROOF, from the judge's own coefficients (writing/scoreboard_hook.md): `block_internal_share` -0.60 - forge #2 has MORE internal rhyme than Joe's bars (+0.59 vs -0.40) and the model scores that NEGATIVELY; `end_tag` -0.62 - the reference block contains one tagged bar ("though") and any block without one is penalised. Every WORD-level effect is <= 0.014. It measures resemblance to one block, not writing.
3. So `KEEP_MAX_RISK = 0.45` discarded the corpus's most frame-accurate 9-16 blocks (0.86-0.90) - the funnel was inverted.
4. STALE CLAIMS COST THE MOST TIME: Q120 and Q119 are both marked "VERIFIED" in pool_v3_quads.md and BOTH FAIL the slot's rhyme scheme (Q120 also fails coherence 2x). Their "margin +4" is rubric margin, which never tested rhyme or syllables. Both annotated in place. RE-VERIFY any VERIFIED tag with trybars before reuse.
5. Best Hook 5-8 found in the sweep: forge #1 "Cold beer on the house in Porto..." - scheme PASS, form 4, meaning 0, coherence 0, judge 0.340. Best on BOTH instruments. It is in writing/scoreboard_hook.md and was already pooled; it has never been shown to Joe finished.
NEXT: Joe's ear on hook_9-16_v3, or form repair (13 -> ~6) which is what the original's own standard asks for.

## 11 Oct (late 13) - VOCABULARY AND PHRASE SUPPLY (Joe: "I want the writers to have as much vocabulary and phrases available as possible")
WHAT EXISTED: theme_words.txt (320 words - I earlier mis-counted this as 8, because it is many space-separated words per line), coherence_gate.IDIOMS (~56 stock phrases), vocab_ledger.jsonl (1 entry - the vocabulary-growth layer built earlier is effectively EMPTY), rhyme_tools.OVR (118 pronunciations). The gap was PHRASES: cashing a stock phrase is the core technique and there were only ~56 known.
1. OVR 118 -> 165: 47 everyday British words/slang that cmudict simply does not carry and so were UNMEASURABLE (no syllables, no stress, no rhyme): skint, knackered, chuffed, dodgy, bevvy, sarnie, butty, scran, trollied, wazzock, skive, faff, blag, cushdy, cuppa, innit, numpty, plonker, tosser, gormless, doolally, barmy, narky, mardy, buzzin, chav, pillock, stonking, chocka, chocker, caff, baccy and more. Measured: 49 of 80 tested everyday British words had NO pronunciation. Fixed and verified ("rhymes skint" now returns 62 matches; "pron" counts syllables).
2. toolkit/phrases.txt - 225 stock phrases as "phrase | payoff word | sense", across 20 end sounds. bank.py computes each payoff's ending sound, syllable count and rhyme key from cmudict+OVR, so nothing needs a hand-typed sound. Every one of the 225 resolves (bank.py check). Senses: money, admin, travel, menace, law, time, domestic, booze, food, lark, weather, mood.
3. toolkit/bank.py - the writer's supply, queryable the way a frame needs it: `slot --ends "..."` prints per bar the end sound required plus the words AND cashed phrases that fit it (`bank.py slot --ends "ɑː ɑː eɪ ɑː aɪ eɪ əʊ eɪ"` runs in 1.9 s); `phrases ɑː --sense money`; `words eɪ --syl 1`; `check`; `uk`. Words are filtered to British vowels through craft_scan (the ARPAbet index is US-vowelled, which is why "on"/"not" wrongly looked like ɑː at first) and junk-filtered by wordfreq, commonest first.
4. coherence_gate now loads phrases.txt, so IDIOMS is ONE list shared by the writers and the scoring: 56 -> 256. Verified: a test block cashes 5 banked phrases and reports 5 cash events (report-only metric, so widening it can only make the count more honest).
5. bank.py selftest asserted in calibrate.py; toolkit/README.md documents it. CALIBRATION PASSED, and the coherence gate still passes the original's own hook at every slot while still catching the scrapbook stanza.
KNOWN GAPS: the British vowel mapping is not perfect ("was" still comes back as ɑː); vocab_ledger.jsonl is still nearly empty, so the "grow the vocabulary as we write" mechanism is unused; phrases.txt needs more registers and more everyday-British idiom.

## 11 Oct (late 14) - HARVESTED SUPPLY: phrases, words and names from open sources (Joe: "fill out as much of the vocab and phrases as possible with what is available on the internet, in libraries and websites")
SOURCES (open and attributable, and nothing about the song leaves the machine - only category names and single headwords):
  - en.wiktionary.org category members (CC BY-SA 4.0): idioms, slang, British English, informal terms, reduplications, rhyming compounds, colloquialisms; plus given names, surnames, singers, towns, films, TV.
  - query.wikidata.org SPARQL (CC0): cities, countries, UK towns, films by award, TV series, bands.
  - api.datamuse.com (already wired in research.py).
BANKS NOW:
  - toolkit/phrases_raw.txt - 2,606 harvested stock phrases (plus the 225 curated = 2,831), across 20 end sounds. Every entry's payoff word is measurable (that is a filter). Ranked by a recognisability proxy: mean AND minimum wordfreq zipf of the content words, so one-off Wiktionary coinings ("ai notkilleveryoneism") and phrases hiding an obscure word are kept out. Heavy swearing blocked.
  - toolkit/entities.txt - 4,185 names: 1,446 given names, 717 surnames, 527 cities, 486 TV series, 440 bands, 209 countries, 204 UK towns, 156 films (Best Picture and Palme d'Or winners). Ordered by Wikidata sitelink count within each type, so the famous end is at the top. 2,523 measurable now; 1,662 need an OVR entry (bank.py check reports them, so OVR grows just-in-time as writers reach for names).
  - toolkit/vocab_ledger.jsonl - 2,466 harvested words recorded with their G2 data.
TOOLS: toolkit/harvest.py (phrases/words/entities, cached + resumable + --offline, selftest) and bank.py gained `entities [--type] [--end] [--types]`.
BUGS FOUND AND FIXED IN THE HARVESTER (all mine, all from real runs): the Wikimedia rate limit (429) needed backoff and per-page caching; several Wikipedia categories are CONTAINERS whose members are subcategories ("British films" returned 0 pages) so one level of recursion is needed and must be bounded; the SPARQL endpoint drops connections and times out, so those queries need a short timeout, a retry, and must never be the only source for a type; the film award query returned PRODUCERS rather than titles (P166 links the award to people) so it now requires the item to be a film; and two ordering bugs in the "replace stale rows" logic (dropping rows then re-adding them was skipped because they were still in the seen set) which silently deleted 400+ singers and a whole run of TV series. The cache is now keyed on the QUERY, not the type name, so correcting a query cannot resurrect the broken version's results.
RULE CHANGED: CLAUDE.md rule 5 said "No real artist or film names" - Joe has now asked for films, TV, music and people's names in the pool, so rule 5 now allows real names as texture (not as the joke), while keeping the no-heavy-swearing and true-or-flagged rules.
STILL OPEN: 1,662 names have no pronunciation, so their syllables cannot be counted; the fix is OVR entries, best added on demand. theme_words.txt is still only 320 words and could take the same treatment.

## 12 Oct - FIGURES OF SPEECH: simile, metaphor, bathos, litotes, hyperbole, anaphora (Joe asked whether the system could identify them; it could not - it only saw wordplay)
FOUND BY TESTING RATHER THAN ASSERTING: plays on words were already covered (cashed idioms via the 3,251-phrase bank, homophone/pun pairs across bars, the payoff word in the rhyme slot, internal rhyme, alliteration, reduplication). The FIGURES OF SPEECH were invisible: "Cold as a cellar up in Bergen" and "The van is a coffin with a radio" produced zero flags of any kind, and the one place anaphora appeared at all was the meaning gate's filler-frame rule, which scores it as a FAULT. For a deadpan rap built on bathos that was the wrong way round.
NEW: toolkit/devices.py + toolkit/tests/devices_positive.txt (labelled fixtures, including four plain-reportage lines that must stay quiet). Detectors, all pattern-based so every hit can be argued with: simile (like/as frames, split plain vs CLICHE), metaphor candidate (a VEHICLE noun predicated of something, or subject and predicate in different lexical fields using the theme-word sections as the fields), bathos (bland setup clause then a short deflating one landing on something mundane; plus the cross-bar case), litotes (negation + downgrader), hedge (modal/softener), hyperbole (absolute quantifiers), anaphora (3+ bars sharing an opener, or the same opener twice inside a bar), polysyndeton (and-chains).
CALIBRATION RESULT, numbers only from the original (92 lines): hedge 2, hyperbole 1, and NOTHING else - no simile, no metaphor, no bathos, no litotes, no anaphora, no polysyndeton. So the original's figurative inventory is essentially the modal hedge; its other devices are the ones the repo already measured (cashed idiom, pun pair, x3 list, internal rhyme). IMPORTANT CORRECTION: my first anaphora rule flagged the original 36 times, which turned out to be entirely coincidental two-bar openers; with a 3-bar threshold plus a "the repeated unit must contain a content word" rule it fires ZERO times on the original, and the fixture had to be changed too (a repeated "it is" is a filler frame, not anaphora - the meaning gate already scores that). Detector right, fixture wrong.
DIAGNOSIS THIS PRODUCED: writing/hook_9-16_v3.md has scheme PASS, syllables exact, meaning 0, coherence 0, form 13, judge 0.765 - and figures of speech: ONE (the hedge "Might" in bar 8). Eight bars with no simile, no metaphor, no bathos, no litotes, no hyperbole, no anaphora. That is the measurable version of Joe's "they say nothing", and it is now visible in `trybars.py` as a "figures of speech" line on every block.
NOT FED TO THE JUDGE YET: the device features are carried in the feature dict but deliberately NOT in NUMERIC_FEATURES, because the saved judge model expects a 46-length vector. Verified after the change that the approved bars still score exactly 0.130 and the vector is still 46. Retraining the judge with the device features is a separate, deliberate step.


## 12 Oct 2026 -- Hook 9-16 written for the first time, and 5-8 hardened
The eight slots the forge could only recombine now have real bars: writing/hook_1-16_v4.md.
- 9-16 v6 (writing/hook_9-16_v6.md): scheme PASS, form 11, meaning 0, coherence 0, judge 0.869,
  4 figures of speech (litotes, hyperbole, bathos, hedge), syllables exact on the frame
  [7,9,8,9,12,5,8,7]. Judge was 0.130 for Joe's approved 1-4 -- but the judge is NOT evidence.
- 5-8 v3 (writing/hook_5-8_v3.md): form 5, 2 figures, Majorca restored as the closer place
  (keeper) at the cost of 1 form point.
Two instrument lessons, both worth keeping:
1. COMMAS COST FORM. Dropping the mid-bar commas took 9-16 form 14 -> 11 and judge 0.797 -> 0.869.
   Keep a comma only where the pause is what makes the figure land (bar 15's bathos).
2. The rhyme-strength link: "car"->"yard" scored 0.80 where the original links its end pair at 1.00.
   A perfect partner ("bar") took form 12 -> 11. Prefer perfect end-end pairs inside the carpet.
ratchet.py verdict: REVERT on keepers lost "Whitsundays" (deliberate: the ?? carpet and a
7-syllable bar 9 cannot carry it) and on a THIRD variant of bars 1-4 in keepers.json's
locked_lines ("Good show but the dame look bored, though" -- differs from STATE.md's quote and
from writing/bars_1-4_v9.md on disk). Joe to name the canonical text; nothing is locked.

## 12 Oct 2026 -- bars 1-4 canonicalised (Joe's decision) and the harness re-anchored
Joe named writing/bars_1-4_v9.md the canonical text. It differed from the quote in STATE.md AND
from keepers.json, so the approved quad existed in three forms and the calibration harness, the
judge's selftest and the forge's selftest each hard-coded a different one.
Fix: toolkit/canonical.py holds HOOK_1_4 and is now the only place those lines are typed.
calibrate.py, meaning_gate.py, forge.py, ml/judge.py and toolkit/keepers.json all read it;
the ML accept rows were regenerated (ml/export_pairs.py: 21 rows, 63 pairs).
Verified after re-anchoring: CALIBRATION PASSED | JUDGE SELFTEST PASSED | FORGE SELFTEST PASSED
(it still enumerates and recognises the approved quad: rank 5 of 323, risk 0.247).
ratchet.py against the previous hook: REVERT on ONE line only -- keepers lost "Whitsundays".

RESOLVED 12 Oct 2026: Joe accepted the Whitsundays loss (it came from the Q120 place-roll-call
reading of 9-16, which fails that slot's own rhyme scheme at form 18). The keeper stays in
toolkit/keepers.json because the place is still real material and can carry a verse; the
ratchet red is therefore a decision, not a defect. The hook's only open item is Joe's ear test.

STATE OF THE HOOK: writing/hook_1-16_v4.md
  1-4  canonical (Joe's)         scheme PASS | form 6  | judge 0.130 | 0 figures
  5-8  v3 (Porto -> Majorca)     scheme PASS | form 5  | judge 0.435 | 2 figures
  9-16 v6 (the business register) scheme PASS | form 11 | judge 0.869 | 4 figures
Remaining work on the song: verses V1 1-8 through V1 33-44 and V2 1-16 (SIZES in check_all.py).
Still open from rule 8: strict vegetarian detail, Horfield/BS7 as a name, everyday British brand
names, invented cartoonish flourishes on true places.

## 12 Oct 2026 -- Joe rejected a line that passed every gate; the gap it exposed is now closed
Joe: bar 6 "Two glasses, cold lager, back road corners" is "a nothing line with shit flow and should
not have got through". It was right, and the failure had two parts:
1. REPORTING. check_all DID flag that bar by name (stress grid + extra mid-bar pause, 1 of the
   block's 5 problems). It was reported as a block total and treated as a ranking target, so the
   per-bar signal never surfaced, and the comma lesson from bars 9-16 was never swept across 5-8.
2. A GATE GAP. coherence_gate.ts own comment allows a fragment as long as it is not IMAGELESS, and a
   noun list supplies images while claiming nothing. Nothing tested "does this bar state anything".
FIX: meaning_gate now has an INVENTORY rule. A bar with 3+ comma-separated chunks, no verb, no
pronoun and all but one chunk naming a pictureable object FAILS as stock-taking, not a statement.
Built to be narrow because the obvious version was over-strict -- a bare comma count fires on three
of the ORIGINAL's own lines (a one-word greeting, a repeated-word refrain), which
is the same bug class that produced three earlier false rejections. Validated: 0 fires on the
original's 92 lines, quiet on Joe's approved bars, catches the rejected line and only that bar
(selftest case added), CALIBRATION PASSED. It also catches two genuine lists in full_draft_v17 and
hook_9-16_v1/v2 ("Took the ferry, tunnel, and the car").

FINAL HOOK (12 Oct 2026): writing/hook_1-16_v5.md
  1-4  Joe's canonical        scheme PASS | form 6  | judge 0.130 | 0 figures
  5-8  v5 (V-a)               scheme PASS | form 4  | judge 0.734 | 2 figures  <- all syllables on frame
  9-16 v6                    scheme PASS | form 11 | judge 0.869 | 4 figures  <- all syllables on frame
Ratchet v4 -> v5: **OK (nothing got worse)** -- the first green ratchet of the session. 5-8's
problem count fell 5 -> 4 after Joe rejected the inventory bar and chose V-a.
The judge preferred the rejected Option 1 (0.769) over the chosen V-a (0.734); the ratchet
preferred V-a. Recorded: the ratchet counts measured form problems, the judge is not evidence.
Still open: 9-16's 11 form problems (the hook's weakest block), verses V1/V2 not started, and the
rule-8 decisions (vegetarian detail, Horfield/BS7, brand names, cartoonish flourishes).

## 12 Oct 2026 -- Joe asked why the original is still better. Measured answer: benchmark/gap_analysis.md
Four metrics separate the hooks (places named 9/16 vs 4/16; end-word zipf 4.04 vs 4.58; loaded words
15% vs 3%; figures of speech ~0 vs 6) and two more where ours "wins" (lexical variety, second
readings) are supply measures that cannot see quality -- do not manage to them.
Decisive finding: the harvest contains ZERO non-English words, so the original's actual engine
(a word in each place's own language) has no supply in this repo at all. Build gap, not taste gap.
STUCK RULE T2 FIRED: same theme/register across 12 versions of 5-8 and 6 of 9-16. Parked best:
writing/hook_1-16_v5.md. Pivot angle chosen: BY LANGUAGE (a place greeted in its own tongue per
couplet, loanword ends carrying the carpet) inside THE LEDGER's courier frame, so gaps 1, 2 and 3
close together. Next: extend harvest.py with a loanwords mode, add the two missing trybars readouts
(end-word zipf, bars naming a place), then rebuild the hook from scratch.

## 12 Oct 2026 -- Joe corrected the premise: no anecdotes needed, the TELLING carries it
Joe: the original "just says 'i danced in jamaica' but the way its said is what sells it". So a
generic claim is fine; the work is in the wording (borrowed line, dance word doing double duty,
champagne as a verb, perfect rhyme in the slot). Nothing in the build may wait on Joe supplying a
story. Target restated: every bar = a generic claim rendered with a loaded word in the rhyme slot.
Built the supply that was missing (benchmark/gap_analysis.md gap 2):
- toolkit/harvest.py now has a `loanwords` mode. Source: English Wiktionary translation tables
  (CC BY-SA), one cached fetch per anchor concept, Latin script only, first entry per language only
  (the first pass kept every synonym and returned thesaurus entries such as "means of payment"
  instead of "money"). Output toolkit/loanwords.txt: word | lang | country | the English idea.
- Result: 260 primary words across 16 countries (Spain 20, Germany 21, France 20, Portugal 20...).
- ONLY 77 are pronounceable by the engine. 183 need an OVR entry (accents break the lookup:
  biere, skal, zero, hej; plus multi-word entries). That is the next blocker, not the harvest.
- Usable now, and they are exactly the engine words: hola, gracias, cerveza, ciudad, obrigado,
  bonjour, merci, oui, beau, ciao, ballo, strada, gardai...
- End-vowel carpet the 77 give us: ?? 16, ? 11, ? 10, i? 8, ? 7, ?? 6.
- Empty: Jamaica and Morocco (jam words are multi-word, "wah gwaan"; Morocco is Arabic script, which
  the rule drops as unrhymable, and French maps to France). Fix: map a language to several places.
toolkit/trybars.py now prints the two readouts from gap_analysis.md, as report lines, never vetoes:
  rhyme-slot payload (mean zipf; our 9-16 = 5.13, the original's hook = 4.04) and world named
  (proper nouns; our 9-16 = 0 of 8 real places). "I" is excluded so the pronoun is not a place.
CALIBRATION PASSED (harvest selftest extended with 6 loanword cases; trybars selftest still ok).
Next: OVR entries for the high-value loanwords, load loanwords.txt in bank.py so a writer can ask for
"words ending ?? from Italy", fix language -> several places, then rebuild the 16 bars.

## 12 Oct 2026 -- first block built on the new engine (5-8 candidate)
writing/hook_5-8_v6_candidate.md: Ola and the boat in Porto / Grazie and a quick page of the orders
/ No names at all on the borders / Might take the fjord up to Oslo.
scheme PASS, form 8, meaning 0, coh 0, syllables 8/10/8/8 exactly on frame.
THE ENGINE WORKS ON THE METRIC IT TARGETS: rhyme-slot payload 4.00 (the original's hook is 4.04;
the previous 9-16 block measured 5.13) and 2 of 4 bars name a place and carry a loanword.
THE TRADE, recorded honestly: form rose 4 -> 8 against V-a, because the audio-rhythm target rewards
plain lines and this block carries more mid-bar furniture. Payload and world improved; the strict
rhythm-similarity measure got worse.
Scheme finding worth keeping: the frame's bar 5 ends ??, so bar 8 must end ?? for the ABBA check,
and an ?? ending cannot also link to bars 6-7 (?). Bergen fixed the 6-8 links and broke ABBA 1-4 at
0.68 -> scheme FAIL. Inside this bar set that is unsatisfiable; recorded rather than fudged.
Next: the same treatment for bars 9-16, then Joe's ear on both.

## 12 Oct 2026 -- Joe asked if 5-8 was the best version or if the writer stopped early
Answer: it stopped early. ~12 hand-written candidate lines, no search. So I built toolkit/tryforms.py:
pools of per-bar candidates, cartesian product, cheap in-process prescreen (syllable distance, the
scheme's own rhyme pairs via match.best_end, meaning gate, end-word payload, places named), then
trybars.score_block on the shortlist only (the judge is not used to rank -- it is not evidence).
Selftest added and asserted in calibrate.py; it caught a real bug in my own assumption: a scheme
string whose length does not match the bar count silently checked NOTHING. Guarded and asserted now.
RESULT on the same pools I had used by hand: 700 combinations, best is form 6 (my hand-picked block
was form 8), payload 3.83 = RARER than the original's 4.04, syllables exactly on frame, meaning 0,
coh 0, scheme PASS. See writing/hook_5-8_v7_sweep.md.
LIMIT: the pools were still hand-written, so this is a bounded sweep, not an exhaustive one. Next:
generate pools from the supply (bank.py loanwords by end sound/country, phrases by payoff, places by
end sound) and sweep bars 9-16 the same way.

## 12 Oct 2026 -- "show me the best hook the system can produce, so I can see the limitations"
writing/hook_1-16_v8_best.md. Chosen by measurement: Joe's 1-4 (form 6), swept 5-8 (form 8, payload
3.60, frame-exact), business-register 9-16 (form 11, payload 5.13, no places). Whole hook = 25 form
problems, of which Joe's own bars are 6.
THE LIMITATIONS, now demonstrated rather than guessed:
1. Bars 9-16 defeated the search: 6,480 combinations, none passed the scheme. Cause identified: that
   slot's by-ear scheme rhymes on the STRESSED SYLLABLE INSIDE the end word (its own bars link a
   place name to a country that way), while every pool rhymes on the final vowel. The generator is
   blind to stressed-tail rhyme. Biggest missing capability in the toolkit.
2. The frame is a guide, not a law: Joe's approved 1-4 measure [4,8,8,10] against the frame's
   [5,9,9,9] -- off on all four bars -- and they are the benchmark. Frame-exactness may be the wrong
   target, which means tryforms is currently optimising partly the wrong thing.
3. Pools are hand-written: the supply is queryable, the phrasings were mine. The search space is
   bounded by my templates, and phrasing quality has no generator and no measure.
4. Instruments disagree (form vs payload vs judge) and every actual rejection so far came from Joe.
5. Supply half-built: 260 loanwords, 77 pronounceable; Jamaica and Morocco empty.

## 12 Oct 2026 -- Joe: "how is the writer still landing on lines that are meaningless gibberish?"
Answer: because I was substituting words to satisfy sound constraints and not re-reading. "borders" was
replaced by "quarters" for the rhyme; "None of the names on the quarters" is not English. No gate
caught it: meaning_gate tests for ABSENCE of content, not for words belonging together, and
tryforms crowned a winner without reading it.
FIX 1 (process): tryforms now prints a warning above every result that nothing in it reads for sense
and cites this case. No block gets presented to Joe without being read first.
FIX 2 (attempted, FAILED, recorded): toolkit/attest.py counts Wikipedia occurrences of a bar's head
and tail 4-grams. It flags the gibberish AND Joe's approved bar 2, "Paid him by the weight" and
"Might take the ferry to Bergen" -- no discriminating power, because a bar's tail is a clause
boundary rather than an idiom. Kept as a documented negative result and a by-hand CLI; never a gate.
FIX 3 (art): writing/hook_5-8_v9_meaning.md, written for sense with the loanword engine kept:
  Ola and the lot on the dot / A grazie and a page of the orders / Names and numbers at the borders /
  Might do a week in Ljubljana
scheme PASS, meaning 0, syllables exact, payload 3.91 (better than the original's 4.04), form 10 --
two points worse than the gibberish block, which is what sense costs.

## 12 Oct 2026 -- Joe asked how Ljubljana got into a block whose scheme demands a rhyme
Answer: the rhyme grader is wrong, in both directions. Measured on ten pairs whose verdict is known,
toolkit/phon.py -> match.best_end is wrong 4 of 10:
  FALSE POSITIVES, all at exactly 0.80: "dot" / "orders" / "borders" ~ "Ljubljana" -- a stressed-vowel
    match with no coda agreement. The grader's bands are perfect >= 0.97, near >= 0.85, slant >= 0.70,
    and the scheme floor is 0.78, so a pure assonance passes as a rhyme by 0.02.
  FALSE NEGATIVE: the original's own place-name rhyme (a matching -gas frame, ? against ?) grades
    0.45-0.50 -- below the very floor that let the assonance through.
Structural cause: total = 0.5*stressed + 0.3*rest + 0.2*final, so the coda (the actual rime) carries
0.2, and "stressed vowel must match" gates everything.
TWO FIXES ATTEMPTED, BOTH REVERTED because calibrate.py caught them:
  reweighting (coda 0.40): broke 8 of 10 "original vs own profile" rhyme-map checks.
  narrow rule (cap assonance when one final syllable is unstressed and codas disagree): fixed all
  three false positives but still broke 3 of 10 profile checks, because the original uses that same
  shape in links its own map requires. Weights are fitted to the original's vowel-dominant rhyming.
CONSEQUENCE, and it applies to everything already reported: every "scheme PASS" from trybars, forge
and tryforms is weaker evidence than it has been presented as. The check cannot separate a rhyme from
a vowel match, which is exactly the hole the place name walked through. The real fix is a refit
against a labelled pair set -- the ten cases are the start of one -- guarded by calibrate, not another
spot patch. Recorded in phon.score's source so the next writer sees it before trusting a PASS.


## 12 Oct 2026 -- the rhyme grader refit, and the root cause of Ljubljana

DONE (calibration PASSED, all 6 rejected stanzas still caught):
- phon.py: diphthong glide similarity (aɪ~eɪ is now representable), right coda comparison, weak-tail
  rules, and best_end no longer takes max() over alignments the scorer itself rejected. Label set:
  4 of 10 wrong -> 1 of 14 wrong.
- toolkit/tests/rhyme_pairs.txt: 12 pairs asserted BY EAR + 1 printed as UNSPECIFIED; match.py --selftest
  runs it and calibrate.py asserts it, so the metric cannot silently change its mind again.
- calibrate.py: prints IPA with errors="replace" (a failing check used to crash the harness on cp1252,
  hiding the verdict).
- match.py: the per-bar loop and the rhyme-strength map now demand only the pairs the BY-EAR scheme
  pairs. Benchmark spec line 18 (Joe's own correction, 9 Oct) is "L5-L8: A C C A". The original's own
  keys misread that as a b b b and were demanding our bars 2 and 4 rhyme -- a rhyme the spec never asks
  for. This was costing every block on every sweep.
- Could NOT fix, and it is structural: "dot" ~ "Ljubljana" and the ORIGINAL's own place-against-country
  link ("Jamaica" ~ "Mainz") have the same shape (matching stressed vowel, one side ending in a weak open
  tail). The model ranks our non-rhyme ABOVE the original's real link, so no floor separates them. The end
  word has to be judged by ear; the scheme check is advisory in the 0.78-0.85 band.

ROOT CAUSE OF THE LJUBLJANA COMPLAINT -- it was not the grader: a weak-tailed place name was sitting in
the rhyme slot. Structural rule adopted: THE END WORD MUST CARRY THE STRESS, and true places go INSIDE
the bar. Applied to 5-8 v10 (writing/hook_5-8_v10.md): 4 of 4 bars pass, 1 aggregate fail, scheme PASS
against the spec, rhyme-strength map PASS, payload 3.43 (original 4.04), places 2 (original 2).

WHOLE HOOK NOW (same honest tools, bars 1-4 locked): Hook 1-4 = 3 fails (Joe's own benchmark bars),
Hook 5-8 = 1 fail, Hook 9-16 = 8 fails (stress grids, a hard ending, internal density, a missing bookend).
NEXT: 9-16 is the weakest block in the song; rebuild it on the same rule (end word carries the stress,
places mid-bar, by-ear scheme AABACBDB so bars 3/6/8 rhyme on one vowel), then the verses.

HONEST TARGET: "check_all ALL PASS" is not reachable -- the original fails it too (Joe's own approved
bars 1-4 score 3 fails). The target is MATCH OR BEAT THE ORIGINAL'S OWN MEASURED NUMBERS per slot.


## 12 Oct 2026 -- Joe: "how did it get through the gates?" (the honest answer)

The bar was: "No names just numbers on folders". He was right on both counts -- unclear, and it does not flow.

WHAT FIRED: flow_fit flagged it. "strong/weak pattern SSSSwwSw" -- four stressed syllables with no weak
one between them, which is exactly the "stacks three stresses" he heard -- plus a beat mismatch at [4].
So the tool caught it. I let it stand and reported the block as "1 fail", collapsing a fired per-bar flag
into a block total. That is the SAME reporting failure as the "two glasses, cold lager" bar (12 Oct).
It is a process failure, not a tooling one.

WHY I LET IT STAND, AND WHY THAT REASONING WAS BOTH TRUE AND WRONG: measured, flow_fit's pattern-match
percentage ranks JOE'S OWN APPROVED BARS BELOW A BAR HE REJECTED --
    approved bars 1-4: 50, 50, 50, 33 % same as the original's pattern
    the rejected bar:  62 %
    other rejected stanzas: 50, 70 %
So it cannot be a gate (true), but a fired flag is INFORMATION FOR JOE, not a judgement call for me
(wrong action). Four instruments have now failed the labelled-set test: the ML judge (3 of 5 of Joe's
own rules inverted), funny.py (89% base rate), attest.py (flags good lines as hard as gibberish), and now
flow_fit's pattern percentage. The beat grid has the same problem: Joe's approved bars 1-4 fail it too.

WHAT NO GATE DOES, AT ALL: read a sentence. meaning_gate tests for the ABSENCE of content and one
inventory pattern; coherence_gate tests links BETWEEN bars. "No names just numbers on folders" has
content by every measure that exists -- two pictureable nouns and a link to its block. Nothing in this
repo asks "is this English" or "does this mean anything to Joe", which is what he actually hears.
Mechanism of the failure: the end word is chosen from the sound bank first, then a sentence is bent to
fit it. The line existed to end in -folders.

DECISIONS TAKEN:
1. Every block report now shows EVERY fired flag, per bar, next to the line and one line of what it says.
   No collapsing flags into block totals. (This is the second time; it is now a rule, not an intention.)
2. The flow_fit pattern-match percentage and the beat grid are DEMOTED: not evidence of quality, printed
   as a note only. They are anti-correlated with Joe's judgement on the only labelled data there is.
   What remains usable as fact: syllable counts per bar, end shape, the by-ear rhyme scheme, the meaning
   and devices checks, and Joe's ear. Everything else was noise being reported as a score.
3. Bar 3 fixed: "Just numbers and dates in folders" -- 8 syllables, on the beat grid, rhymes with
   "totals" at 1.00, grammatical, and it makes the point by omission instead of stating "no names".
   Alternative kept for the ear: "Boxes go straight to the owners" (best pattern fit, off the grid).


## 12 Oct 2026 -- HOOK COMPLETE (writing/hook_1-16_v11.md)

Bars 1-16 assembled and verified. Hook 1-4 = Joe's locked bars; 5-8 = v10; 9-16 = rebuilt in six passes.
GATES PASSING: by-ear scheme (9-16 A pairs 1.00/1.00/1.00, B pairs 1.00/0.80/0.80), syllable counts exact
or within 1 on all 16 bars, ending shapes, meaning gate, coherence gate, rhyme-strength map, internal
rhyme density (24 vs the original's 19), bookends.
RESIDUE, shown per bar, 7 problems, all of the stress-placement family: grid placement on bars 12 and 15
and pattern percentage on 9, 11, 12, 14, 15. WHY IT IS A NOTE AND NOT A SCORE (measured 12 Oct): Joe's
APPROVED bars score 50/50/50/33% and fail their own grids; a bar he REJECTED scores 62%; and the original
itself fails its own flow template on bar 16 (that bar is waived automatically). The metric ranks his
approved work below his rejected work, so it cannot be a gate. Usable facts only: syllable counts, ending
shapes, the by-ear scheme, meaning gate, coherence gate, devices, Joe's ear.

WHAT THE GATES CAUGHT IN 9-16, i.e. the value of the loop (each was a fired flag, not taste):
- the by-ear scheme pairs bars 9, 10 AND 12 -- bar 10 had been ending on the frame's own ɒ, which is the
  ORIGINAL's sound and not a requirement; all three now end ɑː and measure 1.00
- three syllable-count errors (13, 9, 9 where the frame says 12, 8, 8)
- coherence P10: "Half a day on a bike" was a bare indefinite with nothing to picture; and
  "Every day same fare same favour" had no image at all
- a comma pause, a soft ending where the frame wants hard
- the bookend bar must open on the block's only two-syllable end tail ("favour", eɪ-ə) -> "Eight of us"

NEW TOOL: toolkit/blockcheck.py -- a compact per-bar view (counted syllables vs frame, our end sound vs
frame, end word, and every by-ear pair's score) so a block can be iterated in one pass instead of reading
check_all's full output. It is a VIEW over flow_fit.sylls and original_profile.json; it measures nothing of
its own, so it cannot disagree with the gates.

NEXT: V1 1-8 (start bar 17): frame syls [10,10,8,9,6,8,7,13], scheme AAAAAABA -- six of eight bars end on
əʊ + a weak syllable, bar 7 is an eɪ singleton. Content: the Interrail block (Ljubljana, Bratislava,
Vienna, Zell am See, Lauterbrunnen, Florence, Munich) from brief/song_bible.md Block A.


## 12 Oct 2026 -- Joe: "where does ours still fall short, how do we fix the gates" (MEASURED)

Counted both hooks token by token (ours 16 bars vs the original's 16). THE GAPS:
                          ours   original
  local / foreign words      1          9        ours: only "bonjourno", in bars 1-4; bars 5-16 have ZERO
  third-party people         1          5        ours: only "driver"; the original has boys/man/birds/etc
  places named in a bar      4         10
  administrative words       3          0        ours: fare, folders, totals -- a filing cabinet
  ...of those in RHYME SLOT  2          0        "totals" and "folders" are END words in 5-8
  worst repeated word        4          3        ours repeats "bed" x4; the original's worst is a deliberate
                                                 anaphora ("German" x3)
  end words that are places  4         7        the original's rhyme words ARE the stamps
MECHANISM: the end-word banks are ranked by word frequency, so the commonest word with the right vowel in a
logistics register is "totals"/"folders"/"fare". Frequency ranking is what produced the filing cabinet.
SECOND MECHANISM, worse: internal-rhyme density was a GATE, it flagged, and it was satisfied by REPEATING a
word ("bed to bed bed to bed", "rail pass rail pass") instead of by writing denser meaning. A gate that
filler satisfies is a bad gate. This is the regression Joe is hearing.

GATE FIX (shipped, toolkit/regression.py, wired into calibrate.py which still PASSES):
  GATE  a local or foreign word per 4 bars
  GATE  no administrative word in a rhyme slot
  GATE  no content word used more than 3 times
  COUNT third-party people, places named (reported, NOT gates -- Joe's own approved bars contain no
        third-party person, so a people gate would fail the benchmark itself)
VALIDATED before shipping, on the only labelled data: Joe's approved bars 1-4 pass all three; our 5-8 fails
local + admin-rhyme-slot; our 9-16 fails local + crutch repetition. DISCRIMINATION: PASSED. This is the
first new checker this session to pass that test (the judge, funny.py, attest.py and flow_fit's pattern
percentage all failed it).
WHY THE OLD GATES MISSED IT: every gate we had measured SOUND (vowels, syllables, stress, rhyme strength).
None measured the SUPPLY of the world -- whether a bar had a local word, a person, a place, or a picture.
Sound gates cannot see a bar that is metrically perfect and culturally empty. That is exactly what 5-16 are.
NEXT: rebuild 5-8 and 9-16 against the new gates (a real local word per couplet from the true countries,
people in the bar, place names carrying rhyme slots where possible), then the verses.


## 12 Oct 2026 -- LEVEL-ALLOCATED GATES (benchmark/gate_architecture.md, toolkit/songcheck.py)

Joe: the gates must work for the whole song, and may need to differ by level. Done, and the distillation
is measured from the original's own 76 bars:
  property                Hook(16)  Verses(60)
  local/foreign words         9          0      <- CODE-SWITCHING IS A HOOK DEVICE. Not one verse bar has one
  places named (bars)         7         11      ~1 bar in 4 across the song
  third-party people          6          7      present everywhere, none in V2 without pronouns
  administrative words        0          1      the one use is CASHELD (a tally gag, mid-bar, not the rhyme)
  syllables per bar        5-12      5-15      hook mean 8.2, verse mean 9.4 -- the hook is tighter by design
  worst repeated word         3          4      ceilings differ by level
  type/token               0.90-1.00  0.78-0.94 the fastest verse block is the LEAST varied, deliberately
  reused lines                0          0      the chorus is the only repetition in the song
Song level: the chorus returns bar-for-bar identical, the title lands exactly once, in a verse, and the 76
unique bars contain no duplicate line.

THE VALIDATION THAT MATTERS: songcheck is run AGAINST THE ORIGINAL. A gate the benchmark fails is a wrong
gate. Four were wrong and were fixed:
  1. local words were demanded per 4-bar block; the original clusters them 3/0/6 -> moved to HOOK level
  2. "no admin word in a rhyme slot" flagged the original's own cashed tally line -> allowed when cashed
     (and the cash test had to be a shared STEM, not a prefix: "tally"/"totals" share "tal")
  3. a place count per section and "one long bar" per section: the original fails both in three sections
     (V2 names ONE place in 16 bars) -> places gated at hook+song only, long bar per VERSE
  4. required rhyme pairs came from the by-ear scheme alone; the original's own measured keys cannot
     confirm 19 of those pairs -> a pair is demanded only when BOTH agree; the rest print as grader limits
Wired into calibrate.py, which asserts it: "level gates (line/quad/verse/hook/song) hold on the original:
all levels PASS". CALIBRATION PASSED.

WHAT IT CATCHES IN OUR DRAFT RIGHT NOW (writing/full_draft_v20.md, 7 problems, all real):
  Hook 1-4 bar 1: 4 syllables, outside the hook band 5-12   <- Joe's own locked bar; the original's shortest
                                                              hook bar is 5
  Hook 5-8 bar 2: uncashed admin word "totals" in the rhyme slot
  Hook 9-16: "bed" used 4x (hook ceiling 3)                  <- the crutch repetition I introduced
  SONG: 4 named places, need >= 12                            (verses not written)
  SONG: the hook has 1 local/foreign word, need >= 4          <- the code-switching gap
  SONG: 2 uncashed administrative words (fare, totals)
  SONG: the title appears 0 times, expected once, in a verse
NEXT: write the verses to this architecture (places, code-switching only in the hook, no admin rhyme slots,
one long bar per verse, no reused lines), and fix the three hook regressions above.


## 12 Oct 2026 -- Joe: "does the system capture what makes THESE bars good?" (V1 bars 7-8, the suede/prego couplet)

Breakdown and status, element by element. TWO INSTRUMENTATION ERRORS FOUND WHILE CHECKING, both mine:
  1. is_place() accepted ANY capitalised word over 3 letters, so the place counts were inflated. The
     original's real count is 11 named places, not the 18 I reported earlier. Fixed: gazetteer membership
     OR a geo-adjective (Italian, German, Transatlantic...), nothing else.
  2. My claim "code-switching is a hook device, verses have 0 local words" WAS WRONG. The supply simply
     did not contain the words. Hand-counted against a known list, the original's 60 verse bars carry five
     local words (a shop word, a drink, police slang, money slang, a slang plural). The gate is now a
     SONG-level rate: >= 1 local word per 12 verse bars. One whole verse still has none -- the rate, not a
     per-verse rule, is what the benchmark supports.
NEW SUPPLY: toolkit/local_words.txt -- local words built by REGISTER (greeting, cheers, thanks, drink,
bill, shop, police, money, slang) for the countries Joe actually visited, because the Wiktionary harvest
had country translation tables and none of the transactional words the original actually uses.
WHAT THE SYSTEM CAPTURES FROM THAT COUPLET, and what it does not:
  ENFORCED: short-bar-then-long-bar (7 then 12-13; the frame itself measures 7 then 13); the hinge rhyme
    (bar 7 steps off the carpet on eɪ, bar 8 returns to əʊ -- the scheme letters are AAAAAA B A and
    check_all demands those pairs); cashed admin words (the "cashed" exception is exactly why that bar
    passes the admin gate); repetition ceiling; place/stamp density; chorus identity; title placement.
  NOW LOGGED (was invisible): a country conjured by an ADJECTIVE (a material plus its nationality) counts
    as a place stamp.
  PARTLY: a cashed phrase is RECOGNISED but nothing REQUIRES one per quad, though the bible lists it as a
    must-have technique; reduplication/echo has no detector at all (devices.py has cash + anaphora only).
  NOT CAPTURED, and it is the actual joke: THE REGISTER COLLISION -- luxury in one bar, bookkeeping in the
    next, the boast deflated by the ledger. That is rule 1 of the bible mechanised, and nothing measures it.
    A co-occurrence counter is possible, but measured on our own bars it cannot separate a working
    collision from a name-drop, so it stays a HUMAN gate and is labelled as one.
  NOT CAPTURABLE: flat menace ("I tell a man"), and the local counterpart implied by the transactional word.
ANSWER TO JOE: no, not fully. The skeleton is captured and enforced; the engine -- collision, transactional
local word, a required cashed phrase per quad, menace -- is at best half-captured, and the vocabulary layer
was the weak link: the system did not contain the words the original uses.
NEXT: a cashed-phrase-per-quad requirement and a reduplication/echo detector, both validated against the
original before shipping; and the collision counter shipped as a COUNT with a human gate, not a gate.


## 12 Oct 2026 -- Joe: "what about the reason it SOUNDS so good to the ear?" (the ear devices)

The couplet (V1 bars 7-8), measured from the ARPAbet dictionary, not by impression:
  PIVOT  the local word starts on the vowel the PREVIOUS bar ends on (EY) and finishes on the vowel THIS bar
         ends on (OW). One word hands the ear from one rhyme to the next. Bar 7 ends EY, bar 8 ends OW.
  DRUM   one consonant frame three times with the vowels moving: same T_L skeleton on EH, then AE, then OW,
         landing on the block's rhyme. This is the reduplication device.
  PATH   stressed vowels across the couplet: EH AW AE EY | AY EH AE EY AY AE AH OW -- a tight front-vowel
         clatter (EH/AE/EY/AY) that lands on the round back vowel OW. The AE-EY-AY run recurs inside the bar.
  STOPS  6 and 7 plosives per bar; "stepped out" enacts its own verb phonetically (st-pt-t).
NEW TOOL: toolkit/ear.py -- measures pivot, drum, echo (same frame, same vowel, DIFFERENT words) and crutch
(same word 3+ times). THE CRUTCH/DRUM SPLIT IS THE POINT: internal-rhyme density rewarded "bed x4" (a crutch)
while the thing we fail at is the drum, in which the vowel CHANGES each time. Separated, and validated:
  the couplet: pivot + T..L drum EH->AE->OW
  Joe's APPROVED 1-4: a drum (AO->EY) + an echo (bored/boarded/bordeaux), zero crutches
  our 5-8: NO device at all     our 9-16: 3 drums but 'bed' x4 as a crutch
  our flat bars: quiet, and 'beds' v 'bed' is no longer miscounted as an echo (same stem)
GATE, allocated to the quad: the drum/echo RATE >= 60% of quads. A per-quad demand fails the benchmark in 3
of its 19 quads, so the gate is the rate (the original is 14/19 = 74%). Quads with no device are printed as
notes. Wired into songcheck + calibrate (which asserts it); the original still PASSES, CALIBRATION PASSED.
STILL NOT CAPTURED: WHICH vowel to move to, and whether a given drum sounds good or silly. The tool sees the
device and the progression; it cannot rank EH->AE->OW above EH->EH->OW. That last judgement stays Joe's.


## 12 Oct 2026 -- Joe corrects the DRUM's unit (word -> syllable), and it changes the numbers

Joe: "for the drum, you missed the T in italian. theres tal in italian, then tel in tell, tal in tally and
to* and tal in totals." He was right, and it was a definition error, not a small omission. Two wrong units:
  1. WORD level (first consonant ... last consonant): grouped tell/tally/totals and MISSED the first step,
     because that word's last consonant is N, not L.
  2. strict onset-maximising syllabifier: stripped the L out of "tally" into "ly", because phonetically that
     L does start the next syllable -- so it found no frame there either.
THE UNIT THE EAR USES: each vowel paired with the nearest consonant on either side, with ambisyllabic
consonants shared, and a frame free to CROSS THE BAR LINE. Measured with that: one frame, FOUR steps,
AE -> EH -> AE -> AH, spanning bars 1-2, occurrences i-TAL-ian (bar 1), TELl, TALly, the TAL of TOtals.
Note the motion: it rocks back to AE before landing, and the last step sits immediately before the rhyme
word's stressed vowel -- i.e. the drum SETS UP the rhyme rather than being decoration.
WHAT IT CHANGED, honestly: with the corrected unit the original carries a device in 10 of its 19 quads
(53%), not the 74% the word-level version claimed. So the 60% gate I had just built FAILED the benchmark and
was wrong; the floor is now 40% and the whole check is DEMOTED to a diagnostic with per-quad notes. It does
not discriminate on the labelled data either way: our own 5-8 passes it, because the Porto/port pun is a
genuine echo. Where it IS useful: as a printed per-quad report -- 5-8 has no drum at all, 9-16 leans on a
repeated word while carrying three cross-bar drums.
FIFTH TIME TODAY a new measure turned out to be diagnostic rather than gate-worthy (judge, funny, attest,
flow pattern, now the device rate). The pattern is stable: measures of SOUND rank us about as well as the
original; the measures that discriminate are the ones about what a bar is MADE OF (supply, stamps,
repetition, cashed words) plus the ones that are exact (lengths, scheme, chorus identity, title).
STATE: songcheck original PASS, calibrate PASSED with the ear selftest asserting the four-step cross-bar drum.


## 12 Oct 2026 -- Joe: "does the system pick up all the markers of quality" on the grab-him/shipped quad

Ran that quad through every instrument. It scored ZERO devices before this session's fixes. Two real bugs
found, both fixed and validated:
  1. SIMILE "like + bare proper noun" was MISSED. The pattern required a determiner after "like"
     (a/an/the/his...), so the one simile in the quad -- the punchline -- scored nothing. Fixed with a
     proper-noun branch; verified it fires on the quad's last bar and stays quiet on our own bars.
  2. THE REPEATED VICTIM WAS FLAGGED AS A CRUTCH. The word recurs four times and the tool called it filler.
     It is the opposite: the same anonymous man, with a NEW VERB doing something to him each time. Fixed:
     a repeat governed by a different lexical verb each time is now an ACCUMULATION (a device); only a repeat
     with no new action is a crutch. Measured on the quad: ACCUMULATION 'him' x4, verbs [boxed, grab, having,
     packaged]. Our filler ("bed to bed") still reports as a crutch.
RULE-4 REPAIR: the couplet's lines had been hardcoded in ear.py's selftest. Replaced with SYNTHETIC fixtures
exercising the same mechanisms (a pivot word, a four-step cross-bar drum, an accumulation). The real lines are
checked by "ear.py --check-original PATH", which reads them from outside the project and prints counts only.
MARKERS IN THAT QUAD vs THE SYSTEM (11 markers):
  caught            lengths (11/10/10/10, shortest last); the simile (after today's fix); the accumulation
                    (after today's fix)
  partial           the ABAB structure (the tool sees two groups, not the one nasal-coda family the ear
                    hears); the cashed idiom (cash detection exists, but nothing ties it to the rhyme slot);
                    the anonymous victim (counted as a person)
  NO INSTRUMENT     the metaphor chain (sparks -> lights -> the bulb word); two lexical sets fused, bridged
                    by one word; the imperative "go on then ... then" cadence; plosive texture miming the
                    action (counted, never interpreted); the brand-name payoff (banned in our song by rule)
THE CEILING, stated plainly: every instrument we own is phonetic or lexical-class. NOTHING follows an IMAGE
across bars. A figure that starts in one bar and finishes in the rhyme word, or one action described in
another trade's vocabulary, is invisible to all of it. That is the honest limit of the current system.


## 12 Oct 2026 -- IMAGE-CHAIN DETECTOR built (toolkit/imagery.py), because nothing followed an image

Joe asked for it after the honest answer that every instrument we had was phonetic or lexical-class. It
measures three things at QUAD level:
  CHAIN   two or more words from one image field, across two or more bars (the picture develops)
  LANDS   one of those words sits in the rhyme slot (the last two words of a bar) -- where the original puts
          the payoff
  BRIDGE  a word belonging to two fields at once. Not a data error: it is the metaphor pivot.
Fields = toolkit/theme_words.txt plus the sensory fields it lacked (light, parcel, violence, drink, money,
police, sleep, trade, weather, sea). A gazetteer and a grammar list are excluded from chains: a list of
places is not an image.
MEASURED on the quad Joe asked about: violence chain (bars 1-3), parcel chain (bars 3-4) that LANDS on the
rhyme, and two bridges -- one verb that is light+violence, one that is parcel+violence. That is the whole
machinery of the bars, visible for the first time.
RATES: the original has a chain in 5 of its 19 quads and one that lands in 3. Joe's APPROVED bars have ZERO
chains: they are sound-led (sound-alike puns) rather than image-led, so a chain requirement would fail the
benchmark. It is therefore a DIAGNOSTIC with a writing target (~1 landing chain per 6 quads), not a veto.
Ours: 5-8 has a real drink chain (beer -> port -> glass) that does NOT land on the rhyme; 9-16 has a
travel-admin chain and a sleep chain (mostly the repeated bed), three bridges, none landing.
BUG FIXED while validating: the stemmer stripped "es", so "fares" indexed as "far" and the word "far" read
as a trade term on our own bars. Now a token matches only by exact word, a plural, or -ed/-ing.
Wired into songcheck (notes) and calibrate (asserts the selftest); original still PASSES, CALIBRATION PASSED.


## 12 Oct 2026 -- HOOK 5-8 v12 written WITH the new gates (the demo Joe asked for)

Joe: "now lets write some bars again with these new gates to see how they come out" (tagging the v9_meaning
file, the one where word-substitution had produced the Os/orders/corners gibberish). Same slot, rebuilt from
scratch with imagery + ear + regression in the loop. writing/hook_5-8_v12.md, writing/full_draft_v21.md.

  Cold beer on the house in Porto
  Bought it by the barrel off the sellers
  Left the vinho in the cellars
  Might take the long way to Oslo

READINGS: scheme ABBA all pairs 1.00; syllables 8/10/8/8 exact; shape |Sw x4; meaning PASS; coherence PASS;
regression PASS (1 local word, 0 admin words in rhyme slots); image CHAIN drink beer->barrel->vinho->cellars
that LANDS ON THE RHYME; ear ECHO sellers/cellars (the register flip, visible as a frame for the first time);
internal rhyme bar present (left ~ cellars); check_all problems 3 -> 1. The one flag left is bar 6's
strong/weak pattern percentage, which survives six rewritings at 50-60% and is the metric already measured as
non-discriminating (Joe's approved bars: 50/50/50/33%; a bar he rejected: 62%). Kept as a note.
WEAKEST BAR: 6 -- its main job is to set the pair up.
STUCK RULE: hook 5-8 remains in PIVOT (12 versions shown, 6 rejected in a row); v12 is the first built under
the pivot's angle A (keep the AO carpet) with the new instruments rather than by substitution.

TWO INSTRUMENT FIXES, both blocking, both validated by calibrate PASSED afterwards:

1. imagery.py DRINK field listed only the glass (beer, port, vinho, bottle) and not the storage half, so
   beer -> barrel -> cellars was invisible and the one image the Porto material actually offers could not be
   seen. Added cellar/barrel/cask/keg + the verbs of consumption, the way PARCEL already carries
   depot/warehouse/loads. Measured before and after on the original: identical (4 chains, 2 landing), i.e. a
   coverage gap, not a threshold move.
   CORRECTION to the entry above: the rate printed there (5 quads with a chain, 3 landing) is STALE. Measured
   today with the current code: 19 quads, 4 with a chain, 2 landing. The earlier figure came from a run
   before the stemmer fix.

2. THE TRANSACTIONAL LOCAL WORDS HAD NO PRONUNCIATION AT ALL. 32 entries from local_words.txt were OOV in the
   toolkit (vinho, cerveja, conta, zdravo, hvala, prosim, pivo, kava, dakujem, danke, rechnung, grazie, birra,
   conto, scusi, flics, cuenta, tio, yamas, ouzo, parakalo, efharisto, takk, ol, regningen, khop, bhat, farang,
   xin, bia, certi, guap). Consequence: ANY bar built on one of them read as a vowel blob -- no consonants, no
   stress, no stops, unrhymable in the rhyme slot. That is the whole code-switching supply, i.e. the exact
   device the local-word gates were built to reward, silently unmeasurable. 32 OVR entries added (anglicised
   on purpose: the song is English and the word must scan in an English line). Unblocks the supply, not just
   this block: `rhyme_tools.OVR`.
NEXT: V1 1-8 (Interrail) with the same loop; the hook still needs a 4th local word and the place count for the
song is 4 of 8 (verses will carry it).


## 12 Oct 2026 -- JOE CAUGHT A REGRESSION: the end-rhyme CARPET, and the stale profile behind it

Joe on v12: "Lagos, favours, flavours and vegas are near perfect rhymes, vs our porto, sellers, cellars,
oslo. Also the originals has more alliteration and internal rhymes than ours". Both halves measured, both
correct, and the cause was the benchmark file, not the words.

MEASURED (all six pairs of a 4-bar block):
  ORIGINAL Hook 5-8   6/6   min 0.80      (0.80 0.80 0.80 1.00 0.92 0.92)
  Joe locked 1-4      6/6   min 1.00
  v11 / v12           2/6   min 0.00      <- the regression: two thirds of the block's sound links absent
  v13                 6/6   min 1.00
The checker only demanded the pairs the by-ear scheme names, so a block could pass with four of its six
relationships missing. Nothing measured the carpet.

1. THE PROFILE WAS STALE, WHICH IS THE REAL CAUSE. benchmark/original_profile.json had been written before
   recent fixes, so three gates were calibrated against the wrong benchmark:
     internal rhyme density, Hook 5-8:  4 recorded, 8 actual   (the gate demanded HALF of the original)
     rhyme scheme, Hook 5-8:      abbb recorded, aaaa actual   (the file said the carpet was not a carpet)
     rhyme map:                   3 links recorded, 8 actual   (five sound links not in the benchmark)
   Rebuilt from the original with the current functions (`match.py --build`). This is why v11 and v12 were
   shown to Joe with PASS verdicts.

2. THE CARPET IS NOW A GATE: `match.carpet_of()` + a form check. A 4-bar hook block is held to ALL its pairs
   (both of the original's are 6/6); the original's 8-bar blocks are compared as a share (its own range is
   14%-100%, because they change family mid-stanza). v12 fails it, the locked bars pass it, v13 passes it.

3. "DO THESE TWO BARS RHYME" WAS TWO MEASURES. The per-bar loop used the strict key comparison while the
   by-ear scheme and the carpet used best_end, so the same pair scored 1.00 on the carpet and FAILED the
   per-bar check in one run (Porto ɔː-əʊ vs Oslo ɒ-əʊ -- the ear accepts them; Joe's own bars rhyme that
   way). Now one measure (best_end >= 0.78) everywhere, and the depth clause built on the strict comparison
   is gone (it counted a shared stressed vowel as depth and a shared final vowel as nothing; multisyllabic
   depth is gated separately by the quad's multisyl count).

4. cmudict MARKS THE -ow/-o FAMILY INCONSISTENTLY, AND IT WAS FAILING PERFECT RHYME WORDS. It gives the
   final syllable of borrow, shadow, willow, potato, tomato, tobacco, tornado, solo, photo, tempo, kilo,
   memo as secondary stress (OW2) and the identical syllable of sorrow, follow, hollow, yellow, window,
   burrow, polo, demo, weirdo, logo, zero as OW0. The hook's end shape is |Sw (Joe's bars and the original's
   both), and an OW2 final made a whole rhyme word read as two strong syllables, so a bar written to the
   shape FAILED as if the word were wrong. 14 OVR corrections (rhyme_tools.py). The original never uses
   those words, so its profile is unchanged.

DEMOTED to notes, on the same evidence rule that demoted the flow pattern %: the OPENING-TO-END rhyme links
and the rhyme-strength map that carries them. Joe's locked bars 1-4 fail one (bar 4's opening vs bar 2's end,
0.45 against the original's 0.83) -- a link his ear does not require cannot be a gate. `match.py` also needed
`sys.stdout.reconfigure(encoding="utf-8")` and calibrate needed `errors="replace"`: the new messages carry
IPA and the harness died decoding them instead of reporting.

HOOK 5-8 v13 (writing/hook_5-8_v13.md, full_draft_v22.md): carpet 6/6 min 1.00, internal rhyme 12 vs the
original's 8 (was 5), multisyl 6 vs 2, allit bars 1 vs the original's 1, drink chain pint -> cellars -> vinho
that LANDS on the rhyme, "pint" also a BRIDGE (British-everyday + drink = the register collision), meaning
PASS, coherence PASS, regression PASS, check_all problems 3 -> 1 (bar 6's pattern %, the non-discriminating
metric: the locked bars score 33-50% on it).

OPEN, and it is the next real gap: THE EAR DEVICE PER QUAD. Measured today, the original's hook carries a
drum or an echo in ALL FOUR quads (echo, echo, drum, drum); ours carries one (bars 1-4, Joe's bored/boarded
pun) -- v13 lost the sellers/cellars echo that v12 had. songcheck's floor (40% of quads) therefore fails.
A pun pair inside the /əʊ/ family is essentially unavailable: searching the whole family for same-frame,
same-vowel word pairs returns exactly one (weirdo/window). So restoring the pun means changing the family
the block lives in, which needs the A pair (the two places) to move with it -- and only Naples (true, May
2026) is a real place that ends in the -els shape the pun pair sellers/cellars needs.
RATCHET BASELINE IS STALE for the same reason as the profile: v21 -> v22 compares against problem counts
computed with the old profile, so Hook 9-16 "rose 15 -> 16" without its bars changing.


## 12 Oct 2026 -- HOOK 5-8 v14: the pun is back, and the block's family moved to carry it (Joe's call)

Joe chose: "move the block's family to bring the pun back (sellers/cellars or equivalent) and rebuild the two
places around it". Done. writing/hook_5-8_v14.md, full_draft_v23.md.

  Cold pint on the house in Naples
  Rolled the lot home from the Porto sellers
  Left the vinho in the cellars
  Might flog the whole lot in Florence

WHY THE FAMILY HAD TO MOVE. v13 kept Porto/Oslo at the ends and got a perfect carpet, but its quad carried no
ear device: measured, the original's hook fires a drum or an echo in ALL FOUR quads and ours in one. Inside
the /əʊ/ family a near-homophone pair effectively does not exist -- searching the whole family for same-frame,
same-vowel word pairs returns exactly one (weirdo/window). So the pun forces the family and the family takes
the places with it: the places now sit inside the bars and the rhyme slots carry the trade.

MEASURED, v14 vs the benchmark and against v13 (the block that had the perfect carpet and no pun):
  carpet            6/6 min 0.92   (original 6/6 min 0.80; v13 6/6 min 1.00)
  internal rhyme    10             (original 8; v13 12)
  multisyl          3              (original 2; v13 6)
  allit bars        1              (original 1; v13 1)
  internal bars     1              (original 1; v13 1)
  ear ECHO          sellers / cellars -- the favours/flavours move, and the device the quad was missing
  shapes            |Sw on all four bars; syllables 8/10/8/8 exact
  check_all         1 problem (bar 6's pattern percentage, the non-discriminating metric)
  songcheck         device-rate fail (25% of quads) GONE: 4 problems, all song-level and verse-shaped
  imagery           drink chain pint -> vinho -> cellars, LANDS on the rhyme; "pint" is a BRIDGE
                    (British-everyday + drink: the register collision, now visible to the tool)
  meaning/coherence/regression  PASS (local word; no admin word in a rhyme slot; 3 places named)

TRUTH: Florence is the 2019 Interrail and Porto the 2023 motorbike tour, both real, and the port cellars are
documented. NAPLES IS THE PRIVATE STAG TRIP -- material/travel_history.md marks it "private; Joe decides" and
it is in keepers.json as a favourite word, so it is his call.

RATCHET BUG FIXED while validating: `lines_of()` counted the "== Slot" headers as BARS, so every slot window
was shifted by the number of headers before it and the ratchet reported problem counts for the wrong block
("Hook 9-16 rose 15 -> 16" with no bar changed; v21 -> v22 then said REVERT). blockcheck and songcheck already
skipped the headers; now the ratchet does too, and v21 -> v22 is OK again.
OPEN, needs Joe: the ratchet now says REVERT for one honest reason -- "keepers lost: Oslo". keepers.json lists
Oslo under "places" and its own note says an item may only be removed with Joe's OK, so the block cannot drop
it silently. Either Oslo comes out of the list or it goes back into the song somewhere.

## 13 Oct 2026 -- Joe: "why aren't we using better end rhymes?" Both his claims measured TRUE

1. THE GRADER WAS PAYING FOR SCHWAS. phon.score's guard against two weak vowels only fired when the codas
DISAGREED (final < 0.5). With agreeing codas (z/z, s/z) a single reduced syllable scored 1.00/perfect: two
reduced vowels give vsim(schwa,schwa)=1.0, `rest` defaults to 1.0 because a one-syllable span has no middle,
and the coda matched. So v14's "carpet 6/6, min 0.92" was mostly credit for the reduced -ers/-als ending.
TRUE READINGS after the fix: v14 = 3/6, min 0.00 -- Naples~Florence and both ~Florence pairs are 0.00, their
STRESSED syllables never rhymed; the original's Hook 5-8 unchanged at 6/6 min 0.80; Joe's locked bars
unchanged at 6/6 min 1.00. v14 is a regression, exactly as Joe said, and the old numbers are why it passed.
2. THE FIRST FIX WAS TOO BROAD and had to be narrowed. Guarding on all of WEAKV killed 17 of the ORIGINAL's
own verse pairs: certi~forty, thirsty~shortly, curly~thirty (an unstressed /i/ ending is a real rime) and
Dublin~him, in~him (/I/ + nasal). A gate the benchmark fails is a wrong gate. So REDUCED = {schwa} alone.
calibrate.py PASSED after the narrowing, 0 original pairs demoted, the 12 rhyme fixtures still pass.
3. check_all.py --song READ THE "== Slot" HEADERS AS BARS -- the same defect ratchet.py had. Every slot window
was shifted by one (it scored "== Hook 5-8" as a 1-syllable bar and thought bar 1 of Hook 5-8 was "So I
boarded a plane out to Bordeaux"). "--slot -" was unaffected, which is why blocks built on stdin looked fine.
Fixed; the garbage run reported Hook 1-4 = 10 problems, the real figure is 6.
4. "MUST RHYME WITH BAR 4" IS INTRA-BLOCK (bar 8 of the block), not a quad boundary: the original's own quad
boundary does NOT rhyme (L4 "home" ~ L5 "Lagos" = 0.00). The locked bars 1-4 therefore do not constrain the
new family.
5. THE CARPET LATTICE for Hook 5-8. The original's quad 2 is aaaa with every end word EY + reduced (keys
["eI","schwa"] x4, weakest pair 0.80). Three fresh families in material/ give a PERFECT carpet -- 6/6 at
1.00, better than the original's own 0.80 -- each with two true places:
   -am (aem): Vietnam (2015) / Amsterdam (2013-2023) / tram / jam | scam | dram | cram
   -ow (aU):  Bilbao (2023) / Koh Tao (2015) / ciao (true local word, Florence) / allow | now | how
   -ay (eI):  Pompeii (2026) / Calais (2023) / Byron Bay | Hervey Bay (2017) / delay | pay
   -oh is spent (T2: v1-v5) and ER/schwa is spent (v6-v14, incl. the two that failed here).
   Register pair: -am gives tram/jam (transport -> trouble), -ow gives ciao/allow, -ay gives delay/pay
   (both money). Amsterdam's documented material (King's Day, truffles, the festival, cola tins) is the
   densest true character material in the file.
## 13 Oct 2026 (2) -- Hook 5-8 v15: a carpet that is genuinely perfect, and a THIRD bug (place names had no consonants)

- Joe picked -am (Vietnam / tram / jam / Amsterdam). MEASURED IMPOSSIBLE: Hook 5-8's four bars all end
  soft+1 (one weak syllable after the last stress: La-gos, fa-vours, fla-vours, Ve-gas) and in -am only
  bedlam / madam / wigwam have that shape -- tram, jam, scam, dram are hard monosyllables, Amsterdam is
  soft+2, programme is |SS. No true place in -am can end a line. Evidence: toolkit/_probe_shape.py.
- Two families survive shape + carpet + two true places: -ich (Zurich / traffic / panic / Munich, carpet
  6/6 at 1.00, fresh IH vowel) and -oh (Porto / Oslo / Padstow / zero, 6/6 at 1.00 but bars 1-4 are already
  schwa-U, so eight bars of one vowel). CHOSE -ich.
- THIRD BUG: britfone has no entry for our place names (ZURICH, PORTO, BORDEAUX, LJUBLJANA, MAJORCA, and the
  original's own SPOONS), so phon.word_phones fell through to a VOWELS-ONLY fallback and every place name was
  scored WITHOUT CONSONANTS. "Zurich" read as (U, IH) with no final /k/, which capped Zurich~traffic / Munich
  / panic at 0.80 forever. helpers.uk_phones now resolves through CMU + OVR; helpers.uk stays dictionary-only
  because vocab.py's junk test depends on membership (the first attempt broke its selftest, which is how the
  split was found). Profile rebuilt: Hook 5-8's own minimum rose 0.80 -> 0.92. calibrate.py PASSED.
- v15 (writing/hook_5-8_v15.md): carpet 6/6 min 1.00 (original 0.92), scheme AAAA, ending soft+1 x4, syllables
  8/10/8/8 exact, internal density 8 = the original's 8, multisyl 1 of 2, 4 problems left (density spread:
  ours 1 in bar 5 vs the original's 4; one more AE-AE run; two flow patterns).
- The multisyl device, measured: two ADJACENT CONTENT words sharing a full vowel ("black van", "sat back" =
  AE-AE). Function words carry stressed=False, so "ten quid" ~ "then it" cannot carry it.
## 13 Oct 2026 (3) -- Hook 5-8 v15 reaches ALL PASS on the -ich family

Final block: Cash back on the bier in Zurich / Stuck in the black van in all the traffic / Sitting back with a
real panic / Might pack the backpack in Munich. check_all --slot Hook 5-8: ALL PASS (was 4 problems, then 1).
Readings: carpet 6/6 min 1.00 (original 0.92), scheme AAAA, ending soft+1 x4, syllables 8/10/8/8 exact,
internal density 8 = 8, multisyl 3 vs the original's 2, flow 4/4 bars matched. Also: meaning_gate PASS,
coherence_gate PASS, regression PASS (local word bier, no admin word in a rhyme slot, 2 places named),
ear = 2 echoes 0 crutches, songcheck still 4 problems but all song-level (bar 1's 4 syllables is Joe's locked
line, Hook 9-16 uses bed 4x, 4 places of the 8 wanted, one more code-switch wanted in the hook).
What solved multisyl: the device is a pair of two-syllable vowel runs of two ADJACENT CONTENT words (function
words are unstressed and cannot carry it). cash back / black van / backpack are all AE-AE; three sequences give
three pairs. The same AE cluster supplies the internal density. What solved the flow: bars 6 and 7 need STRONG
syllables on beats 4 and 7 (the original's own grid), which is why "stuck in the black van in all the traffic"
beats "sitting in the black van in the traffic".
RATCHET REFUSES v23 -> v24 for one reason: keepers lost Napoli, Porto, Florence. They disappeared because v23's
Hook 5-8 was the REJECTED v14 black, which was the only place they appeared -- they belong in the verses
(Interrail and the 2023 bike tour), and keepers.json still lists them.
## 13 Oct 2026 (4) -- keepers.json edited on Joe's instruction, ratchet OK

Joe removed Naples (was under "phrases"), Porto and Florence (both "places") from toolkit/keepers.json: the
block that held them was the rejected v14, so keeping them would have made every future ratchet refuse the
improved draft for no real loss. Both edits are his call per the file's own note. After the edit: ratchet
v23 -> v24 = OK (nothing got worse); calibrate still PASSED. Hook 5-8 v15 is therefore the first section in
this song that meets the full definition of done: check_all ALL PASS, meaning_gate / coherence_gate /
regression PASS, ear clean, ratchet OK. Remaining work is song-level: bar 1 (4 syllables, locked),
Hook 9-16 (bed x4, next rebuild), 4 places named of the 8 wanted, one more code-switch in the hook.
## 13 Oct 2026 -- THE POOL IS OPENED: swearing, the slang of the trade, and pop culture (Joe)

Joe, in three instructions: "all swear words and vulgar slang should be available to use and never discouraged"; "all slang
for drugs and guns and weapons and money should also be available"; "all pop culture references". Measured what was
actually there, which was not what the rule said.

FOUND: `harvest.py` had a `VULGAR` blocklist that deleted entries containing fuck/shit/crap/bollocks/cunt from the
harvest -- and it did not contain bitch or dick, so 23 "bitch" phrases ("bad bitch", "bitch fight") and 8 "dick" ones walked
straight in while the rest were silently dropped. Two writer prompts ordered the model to avoid swearing
(`block_writer.SYSTEM`, `seed_stage` HARD RULES), and the rubric's criterion 17 read "understated menace: euphemism, no
swearing". So the rule was enforced in four places, inconsistently.

CHANGED:
- `harvest.VULGAR` is now a LABEL, not a filter: nothing is dropped by it, and it gained the words it was missing.
- Writer prompts: swearing and vulgar slang are stated as allowed and never softened (the "nothing instructional" limit on
  drug/violence detail stays, and so does "no named real person" for the menace itself). Rubric criterion 17 now reads
  "euphemism or a flat swear".
- Categories: phrases gained English vulgarities / swear words / minced oaths / British slang / military slang / prison
  slang; words gained the domains the song lives in (en:Drugs, en:Recreational drugs, en:Weapons, en:Firearms, en:Money,
  en:Crime, en:Prison, en:Violence, en:Prostitution).
- Words are recorded PER CATEGORY, so the ledger remembers the domain ("wiktionary:en:Money") and `bank.py slang money`
  answers "what money words do we have". New command: `bank.py slang [DOMAIN] [--end ɒ] [--rare] [--report]`.
- Pop culture: new entity types game (203), brand (260), meme (164) and person (520: rappers, comedians, YouTubers), so
  entities.txt is 4,185 -> 5,333 names, 3,437 measurable. People come from Wikidata OCCUPATION (P106), not instance-of.
- VERIFIED: no gate rejects a swear (meaning_gate and regression run on a block containing one, no complaint about the
  word); `rt.BANNED` holds 18 entries and none is a swear; the new layers are queryable (`bank.py slang money` returns
  cash/change/fiver/launder; quid and brass are tagged en:Money and English slang).

HONEST GAPS: the harvest is partial - Wiktionary's topic categories do not reach everything (dosh, skint, buckshee and
bifters are NOT in the ledger), and 1,896 of the 5,333 names still have no pronunciation, so they cannot be counted or
rhymed until an OVR entry is added. footballer/singer/actor classes time out on the Wikidata endpoint and were left out
rather than guessed; the harvest is resumable, so adding them later costs one run.

DOCS: rule 5 in CLAUDE.md rewritten; toolkit/README.md documents the layers and the probe-before-adding rule.

## 13 Oct 2026 (2) -- the build can now take BARS, not just sections, and the guard that was missing
Content-good/form-bad was the whole story of the last build: the candidates passed the plan gate in 6 of 9 sections and
cashed 21 of the plan's 34 payoffs against the incumbent's 4, and carried 145 frame problems against its 17. A
whole-section swap therefore lost 9 times of 9. Bars are separable, so `draft_all.merge_improve` is a PER-BAR RATCHET: a
candidate bar is swapped in only where it passes every deterministic bar check, and the swap is kept only if the section
passes `take()`. `ww merge` re-applies it from `eval/_build_candidates.json`, which the build now saves, so a guard change
costs no model calls.

TWO GUARD BUGS FOUND BY THE RATCHET ITSELF, both now closed:
1. The merge compared sections with `_score_key` (plan gate, then frame, then cashes), which let a section buy content with
   a form rise: five sections "improved" while their frame problems rose (5 vs 1, 18 vs 6, ...). Swaps now use `take()`.
2. `take()` itself measured form with the slot frame's own hard list, a weaker measure than the ratchet the Definition of
   Done is written in. A merged V1 33-44 bar passed every guard and `toolkit/ratchet.py` still refused the draft ("problems
   rose 19 -> 20"). `score_section` now carries `check_all`'s own problem count and `take()` may not raise it.

## 13 Oct 2026 (3) -- JOE'S CHARACTER RULE: two references per person, partners and mates before family
Joe, seeing the draft: "why is mum references so much in this draft?" then the rule: "limit any reference to a character
to 2 references. prefer romantic partners or mates over family."

MEASURED, and his ear was right against the benchmark: the ORIGINAL names no family at all (0 references in 76 bars; 2
partners, 7 mates). Our v7 had **11 family references** (mum 9, in-laws 1, nan 1), **0 partners** and 3 mates. Two of the
Mum bars were the plan's own beats; the other seven were the writer amplifying a role the brief repeats in every section,
and `quality_gate`'s "Domestic anchors" measure (its word list contains mum/mam) rewarded the habit rather than flagging it.

NEW: `toolkit/characters.py` -- FAMILY / PARTNER / MATE / ROLE classes, a possessive-and-plural-aware counter, the hard cap
of 2 per character, and a printed preference (family must not outnumber partners+mates). Wired into the plan gate per
block, into `merge_improve` song-wide, and into `argue_stage.guidance` so the writer hears the rule before any gate fires;
`--selftest` asserted by calibrate, which still PASSES. Deliberately NOT asserted against the original: its largest count
is "mate" x4, so the cap is stricter than the benchmark and is a Joe rule, not a calibration.

PLAN AMENDED: Mum's role is now "TWO references maximum" (V1 1-8, V2 9-16) and her Marrakesh errand is a mate's; recorded
in eval/plan_amendments.json for V1 1-8, V1 25-32 and V2 9-16.

DRAFT v8 (writing/ww_full_draft_v8.md), eight bars rewritten so the rule holds: Mum 9 -> 2, nan -> bird, one 'lads' -> the
driver, the fete stall and the hammer line lose the family. Final counts: mum 2, bird 2, lads 2, mate 2, debtor 2, taxman
2 -- every character at or under 2; family 3 vs partners+mates 7. SONG check_all problems 120 -> 116, Hook 5-8 4 -> 2 and
V1 25-32 14 -> 12 (its plan gate now passes); ratchet v7 -> v8 **OK (nothing got worse)**.

TWO THINGS THE REWRITE TAUGHT, both measured:
1. THE FAMILY WORDS WERE DOING METRICAL AND SONIC WORK. The obvious swaps cost two to four form problems each: "Mum's"
   was a stressed monosyllable on a downbeat and "Mum" was carrying internal rhyme. Every replacement had to be chosen
   through check_all itself, not by ear: b3's first drafts (a mate, the driver, the missus) all added a weak-on-beat flag,
   and only "Bad payers get a knock from my bird who's got a hammer" cleared it with two problems fewer than v7.
2. The section's frame_hard rose 1 -> 4 while check_all's problem count FELL 14 -> 12, because the slot frame and
   check_all are different instruments. The ratchet counts check_all's problems (the Definition of Done's measure); the
   frame number is reported so the divergence is visible rather than hidden.

## 13 Oct 2026 -- Phase-A tool built (toolkit/carpet.py), Hook 9-16 rebuilt, and the honest state of the verses

NEW TOOL: toolkit/carpet.py (the skill's Phase A, the one thing that makes every later section faster).
Pick the SOUND first, then write the words. It reads the slot's measured target (syllables from
original_profile.json, the end SHAPE from flow_template.json, the scheme, the measured carpet), searches
material/*.md (true places, each with the file that documents it), theme_words.txt, local_words.txt,
entities.txt and the OVR table, and prints (a) a per-bar BANK of end words that fit that bar's vowel, shape
and length, commonest first, places starred, and (b) whole-slot SETS where every pair the by-ear scheme
requires clears match.best_end >= --threshold and at least --min-places words are documented places.
A complete carpet (hook quads, V2 1-8) is searched as ONE clique; a looser slot is grouped by (scheme
letter, end vowel, end shape), and a group with no clique prints as UNMET rather than being hidden --
demanding a rhyme across two different end vowels fails a benchmark the original itself fails (its own
Hook 9-16 A group mixes ɑː and ɒ and carpets only 4 of 28 pairs). Caches to benchmark/carpets_<slot>.json.
selftest wired into calibrate.py (7 assertions: grouping, shape/budget filter, symmetry, best_end parity,
clique search). CALIBRATION PASSED.
PERFORMANCE NOTE: the first version asked bank.words_by_vowel for 16 vowels; each call rebuilds the whole
cmudict index and re-scores every candidate, so a slot took minutes and 8 parallel slots never finished.
It now scans the index ONCE (n=1,2,3), filters by wordfreq first, computes phon.syllables only for
survivors, and searches commonest-first with a node budget: ~10 s per slot, all 8 in parallel in ~4 min.
Measured output, all 8 unwritten slots, in benchmark/carpets_*.json.

HOOK 9-16 REBUILT (writing/full_draft_v25.md). v24 measured 7 problems; the rebuild measures 2, and
meaning_gate PASSES. Method: the profile and the audio template give each bar an exact syllable count, an
end SHAPE and the original's own strong/weak pattern, so each bar was fitted against flow_fit directly
(the session used a throwaway probe, NOT added to the toolkit: it only re-prints flow_fit's own numbers).
What the fitting cost: bars 1, 6 and 7 of the block went through 3-4 pattern revisions each; a line that
reads fine can still put a weak syllable on a beat the original stresses (see the bar-15 note).
Remaining 2 flags: bar 12's comma pauses and the internal-density spread (ours 23 vs 19).
Honest caveat: bar 12 and bar 13 are formally clean and semantically thin ("Booked, packed, paid, and
cash, cards, keys, the pass") -- the pattern (SSSwSSSwS) needs three stressed monosyllables before a weak
word, which pushes toward lists. Joe's ear may reject them; that is his call, not the tool's.

THE VERSES ARE FIRST PASS, NOT DONE. v25 adds all 60 verse bars for the first time. Measured:
  V1 1-8   19 problems (endings hard vs the frame's soft+1; internal density 10 vs 27; multisyl 6 vs 19)
  V1 9-16  11 problems (scheme AABAAAAA all pairs rhyme; syllable counts now exact)
  V1 17-24, V1 25-32, V1 33-44, V2 1-8, V2 9-16: schemes still broken (end words not yet moved onto the
           carpet tool's sets), 'crew' 6x in V1 33-44, one line duplicated in V1 25-32
  songcheck: 22 problems; type/token 0.65 vs 0.70; 1 local word across 60 verse bars vs 5 wanted; the hook
           has 2 local words vs 4; device rate 7 of 19 quads vs the original's 10.
WHY: each verse bar needs the same fitting Hook 9-16 just had -- end word from a carpet set, then the line
written onto that bar's own stress pattern. That is ~4-15 revisions per bar, and the verse frames are
looser (V1 17-24 wants a 3-syllable ʌ tail on bars 2-4; V2 1-8 is an 8-bar uː monorhyme). Costed at the
rate measured here, the remaining 60 bars is roughly 4-6 more sessions of this thread.
TWO BUGS FOUND AND FIXED WHILE ASSEMBLING: (1) songcheck.bars_of read a BOM on line 1 as a BAR and then
crashed on a None slot -- now strips the BOM (same class as the two reader bugs fixed on 13 Oct);
(2) writing a draft with PowerShell's default utf8 adds a BOM, so drafts are now written BOM-free.

## 13 Oct 2026 (2) -- V1 1-8 fitting: the constraint that was hiding, and 4 of 8 bars now on the audio frame
Joe chose "keep fitting verse by verse, weakest section first"; started on V1 1-8 (19 check_all problems).
Fitted bar by bar against flow_fit (throwaway probe in the session folder; no toolkit change).
V1 1-8 now 16 problems, and FOUR bars are on the original's audio frame (17, 18, 23, 24).
THE CONSTRAINT THAT HIDING: the A group of a verse block must share the SAME END TAIL, not just the same
vowel. check_all names it directly -- "must rhyme with bar 3 (original does; ours ɒ-ɪ vs ɒ-ə)". A block whose
other bars end in "going" (əʊ + ɪ) cannot accept a bar ending in "over" (əʊ + ə), however well both score as
individual rhymes. So the END WORD FAMILY for a whole verse block has to be chosen up front with the tail
fixed: either the -ing set (going, showing, growing, knowing, holding, hoping, loading, rolling, phoning) or
the -er set (over, colder, closer, older, lower, lower, sober, owner, roller). carpet.py already forces the
same tail inside a clique (>=0.78 pairwise), so its SETS are the safe thing to write to; the failure here came
from writing bars by hand off the per-bar BANK, which lists both tails together.
SECOND COST RECORDED: commas. Every comma is a fired "extra mid-bar pause". The frame wants staccato, and the
register that fits is monosyllabic chunks ("Booked, packed, planned and the road, the rail going" -- seven
stressed syllables in a 10-syllable bar). Flowing clauses come out 2-4 syllables too long every time; that is
why the first pass measured 19 problems.
NOT YET DONE in V1 1-8: bars 19-22 (the number ladder and the snow walk) are meaningful but off the frame;
the block still needs internal density ~27 (ours 23), multisyl ~19 (ours 12), a bookend multi on bar 3, and
the carpet at 21/28 (ours 13/28).

## 13 Oct 2026 (3) -- WHERE THE REPEATS, THE "MIGHT" TIC AND THE MISSING FLOW CAME FROM, and the guard that closes it
Joe asked how the song ended up with repeated bars, eight "Might" openers, and flow that does not match the
original's. Measured answers, in order:
1. REPEATS. v24 held only 16 bars (three hook blocks): the song had never been assembled as one file, so
   songcheck's song-level counters had nothing to run on. Every block was drafted in isolation and each
   reached for the same filler frames. v25 measured: 8 bars opening "Might", 7 opening "Booked", 16 leaning
   on "and the whole / the whole of the", 4 on "the lot", 3 on "Might do the last of it", and one line
   repeated verbatim -- 32 of 76 bars.
2. THE "Might" TIC. devices.py calibrated the original's WHOLE figurative inventory as 2 modal hedges in 92
   lines, and song_map.md turned "modal understatement" into a per-block requirement. Applied once per
   section eight times over, a device becomes a tic. One "Might" is kept (Hook 5-8's, the only section that
   passes check_all); the other seven bars were rewritten.
3. FLOW. There is no single flow to match: flow_template.json holds 76 templates, one per bar, measured from
   the original's audio (syllables, strong/weak pattern, end shape, rhyme landing). "Matching the flow" means
   fitting each bar separately, and only the bars that were explicitly fitted are on frame: 16 of 76. The
   verses were written to syllable counts and the carpet, not to the stress pattern. Cost of fitting, measured:
   4-15 revisions per bar.
CORRECTION TO MY OWN EARLIER CLAIM: I said "each comma is a fired extra mid-bar pause". WRONG. The original
carries commas in 23 of its 92 bars; check_all's pause flag is a comparison against each bar's own template,
not a ban. The comma work was still worth doing for readability, but the honest statement is a RATE (ours 2 of
76 = 3%, the original 25%), and that is how the new guard measures it.
NEW TOOL: toolkit/phrase_audit.py -- the song-level repetition guard (duplicate lines outside the hook, a
content opener used >3x, a content 4-gram used >2x, commas on >30% of bars). Thresholds calibrated so the
ORIGINAL PASSES all four; --calibrate prints counts only; --selftest proves it catches a duplicate, a tic
opener, a repeated phrase and a comma flood; wired into calibrate.py (CALIBRATION PASSED).
THE STRIP (writing/full_draft_v26.md): 32 crutch bars rewritten with their own content.
  phrase_audit: v25 4 problems -> v26 PASS (Might 8->1, crutches 14->0, duplicate 1->0, comma bars 28->2)
  songcheck:    v25 22 -> v26 17; the "line reused outside the chorus" failure is gone; type/token 0.61->0.65
  section problem totals: v25 129 -> v26 115 (V1 1-8 16->5, V2 1-8 16->14, V1 33-44 23->25 was the one
    regression, caused by my own rewrites leaving that block's C group off its uː ending -- fixed, and the
    block's ten broken rhyme pairs are gone)
  bars on the audio frame: 16/76 -> 16/76, redistributed (V1 1-8 4->6, Hook 9-16 6->5). The strip traded
  fitted-but-repetitive bars for distinct-but-unfitted ones; that is the order Joe asked for, and the
  per-bar flow pass is next, weakest section first (V1 17-24 and the 12-bar V1 33-44 have 0 bars on frame).
STILL OPEN, unchanged and real: the four SONG-level content gaps -- device rate 7/19 quads (original 10),
hook local words 2 of 4, verse local words 1 of 5, type/token 0.65 of 0.70.

## 13 Oct 2026 (4) -- WHY NONSENSE STILL PASSED THE GATES: two bugs in the one rule that looked for it
Joe asked how so many nonsensical bars and nothing-verses still got through. Measured answer:
NO GATE READS A SENTENCE. check_all/match/flow_fit measure SOUND (rhyme, syllables, stress, end shape,
density). coherence_gate measures LINKS between bars. songcheck/regression measure COUNTS (places, local
words, repeats, type/token). phrase_audit measures REPETITION. ml/judge is learned from one positive block
and is not evidence. The only rule that ever asked "does this bar claim anything" is meaning_gate's
INVENTORY rule, built on 12 Oct for "Two glasses, cold lager, back road corners". AND IT WAS BROKEN TWICE:
  BUG 1 (mine, 13 Oct). The rule split the bar on COMMAS to find its noun chunks. That same day I removed all
  28 commas from the draft to stop check_all's mid-bar-pause flags. With no commas the rule could not fire at
  all, and the comma-free version of the very line it was built for -- "Pass maps plans and the road the rail
  going" -- passed it. A fix for one gate silently disabled another.
  BUG 2 (older, hidden). _verbish() counted ANY -ing/-ed word as a verb, and the end-rhyme family for whole
  sections of this song IS the -ing family (going, holding, riding). Every FITTED bar therefore read as
  having a verb, so the rule was blind to precisely the bars being fitted.
FIXED, and calibrated: the rule now works comma-free (a bar whose content words are all pictureable objects,
with no verb up to its tail and nobody in it, is stock-taking however it is punctuated); the verb test
excludes the end-rhyme tail, because the tail is where the -ing tag sits; and the object vocabulary now
carries the song's own nouns (rail, cash, card, pass, map, plan, kit, van, ferry... cg.OBJECTS had "road" but
not "rail"). CALIBRATION PASSED: 0 fires on the original's 92 lines, quiet on Joe's approved bars, still
catches the fixture it was built for.
EFFECT on writing/full_draft_v26.md: meaning_gate fails 7 -> 4, including the two noun-stack bars written an
hour earlier. Cost, stated plainly: songcheck 17 -> 23, because the two replacements that make a claim came
off the audio frame. A claim and a dense monosyllabic frame pull against each other -- measured on bar 17: a
natural sentence scores 60% on the pattern, a noun stack 100%. That is the structural reason the bars came out
as lists: THE FLOW FRAME REWARDS NOUN STACKS. Writing order must therefore be claim first, then fit, never
fit first and hope.
STILL NOT CAUGHT, and this is the honest limit: "A packed bag a long rail a whole month a road going" passes
even the widened rule (its content words include non-objects, "long" and "whole"), and the general question
"does this mean anything to a person" has now failed mechanisation in this repo five times (judge, funny.py,
attest.py, the flow pattern %, the device rate). Each fix closes one SHAPE of nothing; Joe's ear remains the
only test that reads the sentence.

## 13 Oct 2026 (5) -- the same question, asked again, and answered with the loophole closed

Joe asked the same thing a second time ("how are so many nonsensical bars and nothing verses still getting
past the gates?"). Asking twice was the correct instinct: the previous session's fix was real but PARTIAL, and
measuring it properly showed 4 of the 6 known-dead bars still walked through the inventory rule.

MEASURED, before this pass -- the 11 bars Joe has called nothing (or that read as nothing) against the rule
that exists to catch them:
  caught 2 of 6   -- only the two purest lists.
WHY THE OTHER 4 ESCAPED (both loopholes now closed, both measured, not guessed):
  1. MODIFIERS DISARMED THE RULE. The stack test demanded that EVERY content word name a pictureable object,
     so one adjective or one numeral was enough: "A packed bag a long rail a whole month a road going" and
     "Nine countries four walks cash going" were invisible to it. Fix: a MODIFIERS set (whole, long, cold,
     packed, same, real, little, last, two..twelve...) is stripped before the object test, so a qualifier
     cannot disarm it.
  2. A PARTICIPLE MID-LIST READ AS THE BAR'S VERB. _verbish() counted "packed" in "a packed bag" as a
     sentence. Fix: an -ed/-ing word counts as the verb only where a clause would put one -- first in the
     bar, after somebody doing it ("and paid"), or after a coordinator/pronoun. Elsewhere it is a modifier.
  Plus the object vocabulary now carries the nouns the rejected bars are made of (country, walk, lad, town,
  month, week, day, way, street, border).
AFTER: caught 6 of 11. The 5 that pass are honestly NOT claimless -- "Cash cards and paid the same day" and
"Gave them the cash the cards and the pass" contain real transactions ("paid", "Gave them"), "Police on the
road and the glovebox" and "Christchurch and a black backpack" are short scene-setters, "Rest of it goes..."
has a pronoun and a subject. Joe rejected those bars for being FLAT, which is a different complaint from
being EMPTY, and no rule in this repo measures flat. LABEL CORRECTION: two of my own "nothing" labels were
wrong, and the LLM judge was right about them.
VALIDATED: meaning_gate --selftest now asserts the four newly-caught lists AND that six of Joe's own bars stay
clean; meaning_gate --calibrate PATH (counts only, rule 4) asserts the inventory rule fires on 0 of the
original's 92 lines. CALIBRATION PASSED.
EFFECT on v26: meaning_gate 4 -> 7 fails, the new ones being V1 1-8 bars 16, 22, 23, 28 -- the nothing-verses
in the two weakest sections, now visible to the tools instead of only to Joe.

## 13 Oct 2026 (6) -- can a model read the bars? Measured: as a sifter, not as a gate

Joe asked whether AI can automate a meaning/literary gate now. Built ml/meaning_judge.py: a local Ollama
model restates each bar as a plain sentence and labels it action / stance / scene / summary / phatic
("summary" = a list of things with nothing happening). The PARAPHRASE is the evidence; the label is the
verdict. A 14-bar labelled set: 8 bars Joe wrote or that pass every gate, 6 of the inventory bars he rejected.
  llama3:latest        93%  -- 6 of 6 lists caught, 7 of 8 real bars passed
  mythomax-l2-13b      71%  -- and it ECHOES the bar instead of restating it, so it is not usable
The single llama3 error is a bar it paraphrased CORRECTLY and then mislabelled. n=14 means one bar is 7% of
that figure: the set is small and half of it is mine, so 93% is a direction, not a certificate.
ON THE REAL DRAFT: llama3 flags 17 of 76 bars in v26 as listed nonsense -- 5 of the 6 the toolkit's inventory
rule also catches, plus 12 more, of which about half read to me as real (a journey, a price, an outcome) and
half as dead. So the honest verdict: it SIFTS (76 bars -> 17 to adjudicate, with a paraphrase that shows why),
it does not gate. Kept as a report, wired into nobody's blocking path; only its parser/verdict selftest is in
calibrate.py, because a calibration that needs a GPU is not a calibration. ml/README.md documents it.

## 12 Oct 2026 (7) -- canonical.py scrapped; and MEASURED, the two devices our verse never used

Joe: "scrap canonical.py, lets build the next draft from scratch" -- and why do the bars we have not rhyme
like the eight he quoted? Both answered with measurements.

CANONICAL SCRAPPED. toolkit/canonical.py is deleted. Nothing in the song is a protected source any more.
Six modules imported it (calibrate.py, meaning_gate.py, ear.py, regression.py, forge.py, ml/judge.py) and all
six now read toolkit/fixtures.py -> toolkit/tests/joe_hook_1-4.txt, which exists for ONE reason: the gates
need a positive control. If a gate starts failing those four bars, the gate has changed, not the song.
CALIBRATION PASSED after the scrape.

WHY V1 17-24 -- the block Joe quoted -- IS OUR WORST BLOCK (0.14 carpet, 4 of 28 end pairs).
The tool handed the writer almost nothing. carpet.py groups candidate end words by (scheme letter, end vowel,
end shape) and for this slot that produced groups [[1,2,3], [4,6]]: three end words for bars 1-3
(government / currently / wonderful) and two for bars 4 and 6, with bars 5, 7 and 8 given NO end word at all.
Two bugs in that grouping, both now understood:
  1. It grouped on the profile's STRESSED vowel, but this block rhymes on the TAIL. Bars 1-4 end on the
     [AH, IH] / [AH, schwa, IH] tail and bars 5-8 on [AE, IH, IH] / [AE, schwa, schwa]: the stressed vowels
     differ, the tail does not, and best_end says 24 of the 28 pairs rhyme (0.8 and up). Splitting the block
     by stressed vowel cut a family that rhymes in half.
  2. It used the scheme letters aaaabbbb as part of the key, which separates bars 1-4 from 5-8 -- the two
     halves that rhyme WITH EACH OTHER. For a tail-rhymed block the scheme letter is the wrong key.
The block that Joe judges the whole song by is the one block whose sound map the tool failed to produce.

THE TWO DEVICES JOE NAMED, counted across all 76 bars (original vs writing/full_draft_v26.md):
  THREE-SYLLABLE RHYME TAILS   original 8, of which SEVEN are in V1 17-24   |   ours 1 (none in that block)
  BOOKEND (the line opens on a sound it also closes on)   original 3 (bars 3 and 4 of V1 17-24)  |  ours 2
  CHAIN BOOKEND (one line's tail opens the next line)      original 3         |   ours 2
So Joe is right on the headline: the triplet tail is a device of that verse and our draft does not have it.
Honest caveat: the bookend counter reads the bar's FIRST syllable pair only, so it under-counts what Joe
hears inside "boxed him up nice and packaged him" (the repeated unit there is the weak tail -ed him, not the
bar's opening). The device Joe describes is a repeated two-syllable WEAK unit at both ends of a line, and no
counter in the repo measures it. That is the next tool to write, not the next thing to argue about.

WHAT THE REBUILD MUST DO (agreed direction):
  - claim first, then fit -- the flow frame rewards noun stacks (measured: a claim scores 60% on bar 17's
    pattern, a stack 100%), so fitting first is what produced 60 bars that say nothing;
  - ONE held family per block, chosen by TAIL not by stressed vowel;
  - three-syllable tails (shape Sww) in V1 17-24, the block whose model uses them;
  - the repeated weak two-syllable unit at line start and line end.

## 12 Oct 2026 (8) -- V1 17-24: the two tool fixes, and the block rebuilt to r3

FIXED (carpet.py), both faults that made this block unbuildable:
  1. GROUPING. The groups are now the BY-EAR SCHEME (AAAA / BBBB), not (scheme letter, STRESSED vowel,
     shape). The old key split this block into [1,2,3] and [4,6] and left bars 5, 7 and 8 with an EMPTY
     end-word bank -- the writer was asked to rhyme against nothing. Measured after the fix: two groups of
     four, all eight bars with a bank.
  2. THE BANK. A word now qualifies if its LAST syllable carries one of the frame's tail vowels, instead of
     the frame's stressed vowel (this block rhymes on the TAIL: bars 1-4 land on AH+IH, bars 5-8 on AE+IH,
     same tail, and the original's own carpet is 24 of 28). And when a frame's shape carries no leading
     stress ("|w", "|SwS" -- shapes almost no word has) the shape is no longer a filter, which is what had
     emptied those three banks. Plus: the Isle of Man and Donegal names are in OVR now (Laxey, Castletown,
     Douglas, Ramsey, Tynwald, Snaefell, Maughold, Donegal, Letterkenny, Bundoran, Malin) -- the tools could
     not pronounce one of them before, so this block's true places were invisible.
  carpet --selftest updated and PASSED; CALIBRATION PASSED.

MEASURED FAMILIES (match.best_end) for this block:
  -it family 1.00 across: profit / counted it / posted it / sorted it / signed for it
  "…him in" family 0.90 against Castletown (strapped/packed/dropped/had/sent/taped him in)
  "…of him" family 0.80 against Tynwald
  Laxey ~ Ramsey ~ carry ~ money ~ ferry = 1.00, but a 2-syllable "…ey" word does NOT reach 0.78 against a
  "…ed it" phrase, so a group cannot mix the two.

writing/v1_17-24_v1.md holds the beat sheet, the block (r3) and the numbers. check_all 19 -> 17 -> 13 -> 13.
The block is NOT done: 13 problems left, all of them flow-grid or internal-density. The one structural
question is stated in that file -- bar 40's frame wants a STRONG three-syllable tail (Castletown is exactly
that) while bars 37 and 39 want ONE WEAK syllable ("him"/"in"), and Castletown ~ him = 0.00. Joe's call:
place inside a bar, or the -own family at the ends.

## 12 Oct 2026 (9) -- full draft v27 written; the verses are new

writing/full_draft_v27.md. 10 sections, 76 bars. Hook 1-4 and Hook 5-8 unchanged (the fixture bars and the
one block that passes everything), Hook 9-16 and V2 1-8 carried over, and EVERY verse section rebuilt to the
method: claim first, then the family the measured carpet allows, then exact line lengths. The eight bars Joe
judged the song by (V1 17-24) are the rebuilt block from writing/v1_17-24_v1.md.

PER SECTION (check_all --song): Hook 1-4 6 | Hook 5-8 ALL PASS | Hook 9-16 2 | V1 1-8 14 | V1 9-16 10 |
V1 17-24 13 | V1 25-32 20 | V1 33-44 18 | V2 1-8 14 | V2 9-16 15.
SONG LEVEL: songcheck 23 (v26) -> 8, phrase_audit 4 -> 1, meaning_gate 10 bars read as saying nothing.
Families now held per section: V1 1-8 the -o/-ow weak tails with bar 7 on its own eɪ; V1 9-16 aɪ; V1 17-24
-it plus the "him in" family; V1 25-32 ɜː-i and ɔː-i; V1 33-44 uː with ɪ-i and ʌ-i islands; V2 9-16 the
ʌ/ɒ/æ-æ/aʊ mix the original itself uses there.
WHAT songcheck STILL SAYS: 'him' 6x inside V1 17-24 (verse ceiling 4 -- the block leans on one pronoun);
two 0.76 pairs in V1 25-32; sound-device rate 26% against the original's 53%; local words 2 in the hook and
1 in the verses against 5 wanted; lexical variety 0.69 against 0.70; Hook 1-4 bar 1 is 4 syllables and the
benchmark fails that bar too. NEXT: the per-bar flow fitting, section by section, weakest first (V1 25-32
20, V1 33-44 18), and vary the pronoun inside V1 17-24.


## 14 Oct 2026 -- WHY THE FLAGGED COUPLET FLOWED BADLY (Joe's report on ww_full_draft_v5 bars 5-6)

Joe: "flow issues" in "Cop in whites, he's wrecked my picket / Gnome's in good nick, so he says I nicked it",
"difficulty mouth shape transitions: whites, hes / he's wrecked", "line 1: 3 pause 5 / line 2: 4 pause, 6",
"Line 2: stresses bunch up in the middle so rhyme cant land on same beat as line 1".

MEASURED. (1) A PAUSE INSIDE THE TIGHTEST RUN. Bar 5 puts syllables 3, 4, 5 on 16th steps 10, 11, 12 --
three syllables across one beat -- and the comma fell between 3 and 4, inside that run: that IS the "3 pause 5"
reading, confirmed against the template. The original's Hook 5-8 carries NO comma (its first 16 bars have one,
in bar 1; 23 of its 92 bars have one), so bars 5-8 each added a pause match.py flags as "extra mid-bar pause".
(2) THE TWO JOINED TRANSITIONS WERE INVISIBLE TO EVERY TOOL. rhyme_tools.pron() stripped the apostrophe BEFORE
looking the word up, so "he's" -- present in cmudict AND in OVR -- returned None and fell through to a
vowel-group estimate with no consonants, killing both /ts/->/h/ and /z/->/r/ from every measurement. Fixed:
`raw` is tried first in both tables. Verified non-destructive: the original's own syllable counts and stress
patterns are unchanged bar for bar; 1 bar of 92 shifts elsewhere ("would've", bar 64, gains the syllable it
always had). (3) THOSE JOIN TYPES ARE THE RAREST IN THE SONG: counting the original's 92 lines, fricative->/h/
occurs 3 times and voiced-fricative->liquid 3 times, and 2+ rare joins in ONE bar happens in 6 bars of 92
(78% of its bars have none) -- our bar 5 held both of the rarest at once. (4) THE "BUNCHING" IS NOT OUT OF
DISTRIBUTION: the original averages 1.73 adjacent stress pairs per bar (2+ in 44 of 92) and runs of 3+ in 37
of 92, and our bars measured clash 2/run 3 and clash 1/run 2 -- inside its range. What IS out of distribution
at bar 6 is the 16th before the rhyme: the frame stresses step 14 (original pattern wSwSSwSSSw) and ours puts
the weak "I" there, so the rhyme is not set up. (5) THE RHYME STEP WAS NEVER WRONG: both bars land the rhyme's
stressed syllable on step 16 of the 2-bar phrase, the frame's own landing. What the ear read as "the rhyme
can't land" is the mismatched split (3+5 against 4+6) plus the pause inside the run.

FIXES SHIPPED (all calibrated; CALIBRATION PASSED; `ww selftest` exit 0; instruments re-frozen, drift none).
  * rhyme_tools.pron(): the apostrophe survives the lookup (above). This is the root cause of "no tool could
    see it", and it also un-blinded every contraction in every bar the repo has ever scored.
  * flow_check.joins() / rare_joins(): the mouth-shape measure, with the original's per-bar par printed.
    Wired into ww `flow` and `scan` (bridge.rare_joins) and into flowaudit.rates()/the baseline
    (benchmark/flow_baseline.json rebuilt: rare_joins 0.216/bar, 2+ in 5.4%).
  * flow_fit.WEAKFN: was a 23-word list missing every pronoun and contraction, so "so he says I nicked"
    scored as four consecutive STRONG syllables; now identical to ww/write/flowaudit.FUNC (the live auditor),
    and the stored per-bar patterns rebuilt with it (flow_fit.py --add-weak / --add-rhyme-pos).
  * flow_fit's "weak syllable on the beat" rule was failing the ORIGINAL in 14 of 76 bars, so it is now a PAR
    comparison (flag only when worse than the reference bar, and print the reference's count) -- the same
    par pattern every other measure in this repo uses. Original's own flow score 66/76 -> 74/76.
  * two latent crashes/readers fixed while measuring: flow_fit.fit indexed past the step list when a stored
    pattern was longer than the audio's (it killed the run at bar 64); benchmark/original_profile.json and
    flow_template.json were stale for the corrected pronunciations and were rebuilt with match.py --build.

BARS (writing/ww_full_draft_v6.md): bar 5 -> "Copper in whites wrecked my picket" (rare joins 2 -> 0, pause
1 -> 0, clash 2 -> 1, flow_fit pattern 62% -> 75%, block problems 7 -> 5), bar 6 -> comma dropped (the
original's hook has none). Scheme ABBA still PASS, rhyme pairs still 1.00, meaning_gate PASS, coherence_gate
PASS, syllables 8/10 on frame, ratchet v5 -> v6 = OK. LEFT PRINTED, NOT ARGUED AWAY: bar 6's weak pre-rhyme
16th (the rhyme has nothing to push off), and bars 7-8 still carry a pause the original's bars 7-8 do not
(dropping both commas takes the block to 3 problems but reads worse).
LESSON, for the third time in this project: the reader/model bug hid the defect (the composer could not
pronounce the word the whole complaint was about), and a metric that was never calibrated against the
benchmark (weak-on-beat, failing the original itself) was manufacturing 14 false failures.


## 14 Oct 2026 (later) -- THE ARGUMENT STAGE: the plan is now the input, and every rejection is data

Joe: "try and improve the system so it will produce a better draft". Done, and the first run measured the new bottleneck.

WHY THIS AND NOT MORE SEEDS. Before changing anything I measured the candidate-count curve over the nine round files (23 slot-rounds,
each scored by one judge call against that call's reference): best-of-N sat 1.0-3.5 points below the reference on the judges' own
0-10 craft axes, and Hook 5-8's best was 7.00 at N=7, 7.00 at N=36 and 7.00 at N=44. Six times the candidates moved the best by
0.00; Spearman(N, gap) = +0.42 (the sign is wrong for "more helps"; it is confounded with which generator ran, so the honest reading
is flat). The 823 generated variant bars, the 126 pipeline slot-runs and the ~1,100-bar pool all returned the same flat result.

THE FIX, IN THE ORDER THE DIAGNOSIS IMPLIED.

1. eval/_plan_v3.json IS NOW MACHINE-READABLE INPUT (`ww/write/argue_stage.py`). `brief(slot)` returns the section's argument, its
   mechanisms (mapped from the plan's own "1 CASHED IDIOM" labels to the seed stage's names), the payoff words it designed (from the
   concepts, the ledger and the beats), the ledger phrases assigned to that section, the per-bar syllable counts and end shapes, the
   calls/callbacks/closer, and the plan's own CRITIC note for that section. `seed_request(slot)` generates seeds whose FACT IS THE
   ARGUMENT, constrained to the plan's mechanisms and to the plan's payoff words. `plan_jobs(slot)` now puts the plan's per-bar JOBS
   into the writer prompt, replacing the generic four hook jobs.
2. THE PLAN GATE (`argue_stage.check_block`). Deterministic, and it fails exactly what was missing: no planned payoff word closes any
   bar (the defect that left 13 of the 14 planned payoffs out of the draft), an end word repeated inside the block, fewer cashes than
   the plan's rate. Reported not blocked: planned-payoff coverage, first-person share, per-bar end shape vs the plan, the closer.
   It is switchable (`--allow-other-payoff`) and it is NOT in toolkit/calibrate.py: this gate enforces OUR PLAN; calibrate's benchmark
   is the original's own numbers. Calibration of the gate itself: it PASSES the plan-true block from eval/_round4.json
   ("Hoi Rotterdam, I own the quarry / Council want the gnome back, I am not sorry / Gnome off the back of a lorry / Might lie low over
   in Gorey") and FAILS the draft's current Hook 5-8, in the asserted selftest.
3. RULE R10 IS WIRED. `ww/failures.py` had `log()`/`read()` and NO caller, and eval/failures.jsonl did not exist, so "every rejection
   becomes data" collected nothing. Now: every block rejected in `argue` and in `draft.filter_blocks` is logged with its gate findings;
   `bridge.oov_words` queues unpronounceable words (once per word, de-duplicated against the log, asserted in bridge.selftest);
   a stage failure is logged rather than swallowed; and `argue_stage.guidance(slot)` builds the negatives from that log plus the plan's
   critic note and feeds them into the NEXT seed prompt. The loop is closed.
4. THREE DEFECTS THE NEW LOG FOUND WITHIN ONE RUN, all fixed:
   * the writer never saw the plan's per-bar lengths. `build_request` passed `sylls=` to str.format while the SYSTEM template had no
     placeholder for it, so the plan's own 8/10/8/8 targets were computed and dropped, and the model wrote 10- and 12-syllable
     opening bars against an 8-syllable frame. `_length_rule()` now states them bar by bar.
   * with `effort` set, ww/llm/client.py adds 6000-40000 THINKING tokens to the cap, so a 5000-token block request became 11000 and
     the model spent all of it and returned EMPTY content (finish_reason=length): whole seeds lost, reported as "0 candidates". The
     writer stage now runs with thinking OFF (the seed stage has already done the thinking); a long answer is retried at half the
     batch size instead of dropped.
   * the frame I first checked candidates against was wrong: verify_det's Hook 5-8 spec demands a six-pair carpet, which rejects the
     plan's own A/B block. Candidates are now checked with `slotcheck.check` -- the repo's own slot frame, which knows the by-ear
     scheme (Hook 5-8 is ABBA: 1&4 rhyme, 2&3 rhyme) -- with the plan DECLARING its own cashes (`plan_cash`) instead of the writer
     self-reporting them (round 1 self-reported cashes that did not exist).
5. A PLAN/SLOT CONFLICT, FOUND AND RECORDED (`eval/plan_amendments.json`). The plan designs Hook 5-8 as two rhyme pairs
   (A: garden/pardon, B: lorry/sorry) and names 'garden' in bar 1's own job, while the slot's measured carpet is a MONORHYME -- the
   original holds 6 of 6 end-pairs, slotcheck requires 85% of them, and the repo's own accepted Hook 5-8 (Zurich/traffic/panic/Munich)
   is a monorhyme. Every plan-true candidate therefore failed the carpet at 2/6. Resolution, recorded as data and applied in the
   prompt: ONE family per block, chosen as the family holding the most planned payoffs (Hook 5-8 -> lorry/sorry; V1 1-8 -> the -erry
   set; V2 9-16 -> shot/plot); the deferred words keep their turn inside bars. Seven slots carry such an amendment. This needs Joe's
   eye: it changes the plan, and the plan is his design.

FIRST RUNS (live, DeepSeek flash; ~$0.01 per run, 12 candidates): 6 seeds on the argument, all cashes landing in the rhyme slot
("I had the four-foot black bronze gnome off the back of a lorry"), and candidates that follow the plan beat by beat -- greeting +
place + gnome's whereabouts, the council's complaint with no remorse, the cashed idiom, the 'Might' closer in Oslo. The plan gate
reports 4 of 4 planned payoffs in the rhyme slots where the draft has 0 of 4. NOTHING PASSED THE SLOT FRAME YET, and the logged
reason is unambiguous: 42 of 48 rejections are SYLLABLE-COUNT misses (bar 1: 10 need 8; bar 2: 12 need 10; the rest 11-12 against 8),
then 8 carpet, 8 flow (weak syllables on downbeats), 9 mechanism mismatches. So the argument layer is solved and the writer's
syllable discipline is now the single binding constraint -- which is what flow_research already prescribes fixing at the BAR level
("produce 8-20 variants per bar, drop the off-count ones, then rerank"): the driver now makes that cheap, but does not do it yet.

COMMANDS: `ww argue <slot>` (argument-targeted run, writes writing/argue_<slot>.md), `--brief` (print the plan's brief),
`--check FILE` (run the plan gate on any block, no model calls), `--seeds/--blocks/--no-rank/--allow-other-payoff/--think`.
Verified: `ww selftest` PASSED (26 checks, including the new argument-stage and OOV-queue assertions), `toolkit/calibrate.py` PASSED
(the toolkit's benchmark is unchanged), freeze drift none.


## 13 Oct 2026 -- POP-CULTURE LORE LAYER built (Joe: "the deeper the lore, the more connections, the easier the bar")

WHAT EXISTED: ww/lex/lexicon.py had the BREADTH (6,050 brands, 1,481 TV/music, 866 pop) but reached it only by END SOUND and only through each
entity's NAME; 52 of the brand rows carried any detail beyond a one-line gloss. WHAT IS NEW (all in ww/, no agents, no toolkit change, freeze: no drift):
- ww/lex/cards.py   LORE CARDS: aliases, parts, figures (real idioms + reading), hidden readings, famous_for, neighbours, ladder, register,
                    living_person. Compiled by ONE cheap model call per 8 names (about $0.00015 a card), cached in ww/lex/banks/cards.jsonl, every field
                    src=llm verified=False (rule 5: flagged). `hidden` is DERIVED IN CODE from oronym.py, not asked of the model (it returned non-words).
- ww/lex/graph.py   one index over lexicon + cards. TIERS: 0 name only, 1 + gloss, 2 + card. Edges: SOUND (a carrier word IS a payoff word, or
                    rhymes >= 0.9) and SCENE (shared content word with the section's argument/beats; words shared by > 25 entities are noise and dropped).
                    kit(slot) ranks <= 24 entities (~1,500 tokens); ensure_cards(slot, llm) compiles cards LAZILY for the section's best uncarded
                    candidates (30 cards = $0.0035). Built per process in about two seconds.
- seed_stage / argue_stage: mechanism `lore_allusion` (seed carries `entity`); `ww argue SLOT --kit` adds the kit + a rule that >= 2 seeds must use it.
                    STRUCTURAL validator: the entity needs a card, the BAR-BOUND text (claim, closer, payoff) must hit >= 2 distinct card triggers
                    and must not name the entity. Rejects mislabelled seeds only; it is not a quality score.
- CLI: kit SLOT | probe [--pilot] | card NAME [--build|--verify] | lore FILE [--entity E] | pilot [--roster --build]. selftest has two new checks.
- Rosters added to the lexicon (names only): 70 watches, 71 actors.

MEASURED (the probe counts connections; it does not judge them):
- SAME 320 well-known entities across 16 rap categories, 288 carded: sound reach to the 9 sections 16 (name) -> 36 (+gloss) -> 212 (+card);
  reach-and-scene joins 2 -> 5 -> 91. Whole lexicon with only 289 of 7,956 carded: reach 627 -> 803, joins 57 -> 139.
- I READ 24 of the 86 card-only joins: about half usable (Rolex `crown` IS the planned payoff `crown`; Best Western `bed`/head; Capital One `in the red`/head;
  Man United `glory`/lorry), the rest loose. A join count is not a verdict.
- LIVE seed run on Hook 9-16 (2 calls, $0.016): WITHOUT a stated requirement the model used the kit 0 times of 6. With KIT RULE: 2 of 6 seeds used
  lore_allusion; the validator kept 1 (Our Price: "a reduced-price label on his head", via records/high street), rejected "Long Way Down" (names it
  outright) and a single-trigger Plan B. Sample of 6; Joe's ear has NOT judged any bar from this.
- Total spend building and testing: $0.083 (DeepSeek flash).

KNOWN WEAKNESSES (not fixed):
- Card `figures` drift to the NAMESAKE (Rolex Daytona got racing idioms, not watch idioms). Parts, aliases and famous_for read well. Treat figures as the least reliable field.
- 32 of 320 pilot names got no card (non-brand rows such as "Unit price", "Bag for life", "M&S"). The pilot's top-by-zipf ordering also over-samples variants of one brand.
- The audience score is a wordfreq PROXY (US-weighted); it ranks, never vetoes. Nothing yet knows what Joe's mates know.
- Scene edges are token overlap, so they are noisy; reach (sound) is the number to trust, joins are a tie-break.
- PRE-EXISTING, noticed not changed: `ww argue` without --kit dropped 5 of 6 seeds for using mechanisms outside the plan (the model names mechanisms the prompt does not list) - wasted spend per run.
- Status in ww/registry.py terms: every new measure is UNVALIDATED. Nothing shows the kit improves bars; the test is Joe's ear on `ww argue "Hook 9-16" --kit` against the same run without it.
- Deferred by Joe: the strike/star list for each category (it would set the audience prior).


## 13 Oct 2026 (later) -- from-scratch draft v9, the rhyme map, and rapfit (a rap-aware rhyme layer)

FROM-SCRATCH DRAFT writing/ww_full_draft_v9.md (`ww build --kit --scratch --no-rank`, 9 sections, $0.18 total, no incumbent read or merged; report writing/build_report.md, previous one kept as build_report_prev.md).
VERDICT: WORSE than draft 8. 3 of 9 sections FAIL the plan gate (V1 1-8, V1 25-32, V1 33-44), all 9 fail the slot frame, several bars are 15-20 syllables, and V1 1-8 / V1 25-32 /
V1 33-44 contain bars that do not parse ("validated bury", "I give him adjust", end words reused). The kit contributed 3 structurally valid lore_allusion blocks of 8 attempts (Dial-a-ride,
Broadchurch, Table service); none is a bar Joe has judged. The writer's real ability without an incumbent to lean on is the finding. v8 stays the best draft.

RHYME MAP: `ww rhymes --left original --right writing/ww_full_draft_v8.md ...` (ww/write/rhymeview.py). End tails grouped (grader for drafts, Joe's by-ear scheme for the original), internal
assonance echoes, and vowel-only groups such as stage/plane. Joe caught that the first version missed stage, plane and boarded (it compared inner words only with the END rhymes); fixed.
RULE 4: the original is read from the private file; render() REFUSES a full-text original anywhere but ~/Documents/WORLDWIDE_PRIVATE (selftest asserts it), and the in-project file shows only
rhyming words, never more than 3 in a row (checked: 0 unbroken 4-word runs). Full-text map: ~/Documents/WORLDWIDE_PRIVATE/rhymes_original_vs_v8.html.

RAPFIT (ww/write/rapfit.py, UNVALIDATED ranking layer; the frozen grader is untouched): Joe, 13 Oct: the detector must favour rhymes that sound good rapped and not "technically rhyme"
pairs. Anchors the rime on the last stressed syllable (plus the final syllable when it is a full vowel), scores vowel + coda + tail, rewards matching tails, caps a pair at 0.30 when the
stressed vowels differ. Demotes "audit/biscuit/credit/orbit" and "limit/jacket/pocket/knit" (graded 28/28 PERFECT by the grader; stressed vowels all differ).
MEASURED against Joe's by-ear scheme for the original (274 pairs): AUC 0.931 vs the grader's 0.792; at its own floor 0.50 it finds 90% of true rhymes and accepts 6% of non-rhymes (grader: 93% and 28%).
CAVEATS: the floor is fitted IN-SAMPLE; the "non-rhyme" labels are different-letter pairs, so some (Lagos~favours) are really loose rhymes, which flatters rapfit; I tuned the tail weights while looking
at four original pairs, so it is not fully out of sample; it is blind to the original's 3-syllable tails (Dublin ~ double it), moi/dance, Jamaica/Spain, and V2 9-16 (AUC 0.5).
NEEDS JOE'S EAR: writing/rhyme_ear_labels.md (40 pairs from draft 8, kinds hidden). Nothing in the repo is labelled "technically rhymes but sounds flat", so rapfit's cap can be checked, not fitted, until he marks it.


## 13 Oct 2026 (latest) -- rhyme THEORY research, a syllable-level map, and the first rhyme rules enforced in the writing process

RESEARCH: benchmark/rhyme_theory.md (sources marked by how much I read: Hirjee & Brown 2009 and DopeLearning and Tait et al. in full; Kawahara, Katz, Knoop 2021, Zwicky from abstracts or summaries).
Findings that matter: the rhyme starts at the LAST STRESSED syllable (Hirjee & Brown filtered one-syllable rhymes containing unstressed syllables out as noise); stressed syllables sit on strong beats and
rappers bend words to make that happen (Tait); assonance is the working rhyme and multisyllabic matching is selective (DopeLearning rhyme density 0.87-1.19); allowed mismatches are the small ones
(m/n, place-only plosives, height/length vowels). No English rap LISTENER study and nothing on unstressed-only rhyme was found: "sounds good" is inferred from practice plus one German experiment plus Joe's ear.

JOE'S CLAIM, MEASURED. "The original almost always rhymes on 2+ syllables" is NOT what the numbers say: of 137 pairs inside its rhyme groups 56% are ONE stressed syllable (Hook 1-4, V1 9-16, V2 1-8),
24% two, 3% three or more (all in V1 17-24). What does separate draft 8 is that 11% of ITS pairs (19 of 172; 19 of the 28 pairs in the -it verse) are unstressed-tail echoes, against 0% (1 pair) in the
original. The rule is "rhyme on a stressed syllable", with multis used selectively - not "always 2+".
MULTI-SYLLABLE INTERNAL RHYME (Joe's meat-out / beach-house / chicas-out pattern, a repeated vowel pair): the detector now finds it (3 occurrences). But the count over a whole song is at CHANCE level in the original,
draft 8 and draft 9 alike (24 vs 21.5, 12 vs 16.3, 23 vs 27.1 expected from shuffled vowels), so it is DIAGNOSTIC ONLY until made stricter. It also does not flag Joe's draft-9 complaint (one vowel
piled up, then reused as the end rhyme): that remains Joe's ear only.

ENFORCED NOW (13 Oct): slotcheck.check -> rapfit.check_block, HARD: a bar in a rhyme group whose only matches are an unstressed tail ("-it" of biscuit / credit) fails (switch off with WW_RAPFIT_GATE=0).
Calibrated first: the original 0 of 69 bars fail, draft 8 fails 2 (biscuit, credit - Joe's example), draft 9 fails 0 but has 19 bars where the tool hears no syllable match (soft note). A first version that also
hard-failed "no match" flagged 13% of the ORIGINAL's own bars (its loanword and loose-section blind spots), so that case is a soft "check by ear". Also: end-word menus keep only words that rhyme through a
stressed syllable (draft_all.end_menu), and the writer prompt now says what counts as a rhyme. Per-slot depth targets from the original are in benchmark/rhyme_depth_targets.json (reported soft).
SYLLABLE MAP: ww rhymes now colours syllable by syllable (solid vowel+ending, dotted vowel only, wavy red unstressed tail echo, dashed no match), shows the rhyme depth per bar, and marks chains and alliteration.
Fixed on the way: loanwords known only to ww (chicas) had no syllables in the rhyme tools; syllabic l/n/m (Dublin ~ double it) is now read as one syllable.
STILL OPEN: Joe's marks on writing/rhyme_ear_labels.md (the only way to fit the cap), a stricter chain detector, landing-step equality across a rhyme group (R6), and whether depth targets should become hard.


## 13 Oct 2026 (latest 2) -- por-no / bor-deaux: a DETECTION bug (syllable units), not just a drawing bug
Joe: "por in porno doesn't rhyme with bor in bordeaux? is this detection or visualisation?" It was detection. phon.syllables glues every consonant before the next vowel onto the PREVIOUS syllable
(por = ɔː+n, Bor = ɔː+d), so the syllable-level view called an open /ɔː/ followed by a new onset a vowel-only match. rapfit._syl now marks syllables that have a following syllable in the same word, and
syl_match / the exact-rime classes read the consonant either as an ending or as the next onset (ambisyllabic). porno~Bordeaux is now a full two-syllable match; Lagos~favours, Dublin~double it, ferry~Mary keep
working; exact-rime classes link por / Bor / bored / boar-ded / jour and use a two-bar window. The PAIR SCORE (rapfit.score) deliberately stays strict: the ambisyllabic version ranked Joe's by-ear pairs worse
(AUC 0.917 vs 0.931). WHAT DID NOT CHANGE: rhyme depth counts, the stress-anchor gate (original 0/69 hard, draft 8: biscuit and credit, draft 9: 0) and every all-pairs percentage, because they count a vowel
match as a match; the bug understated how EXACT a match was (dotted instead of solid) and kept por and Bor in different colours. Selftest now pins porno~Bordeaux and Lagos~favours.
Also in this pass: Lagos / favours / flavours / Vegas share one colour (groups that rhyme with each other form a carpet).


## 13 Oct 2026 (latest 3) -- "eye rhymes with ba but ba doesn't rhyme with plain / plane / luego": three causes, and the colour model is now vowel-first
Causes: (1) phon.vsim puts aɪ ~ eɪ at 0.93 (a shared glide), and I let >= 0.9 count as an EXACT rime, so eye (aɪ) was linked to ba (eɪ); exact now needs the identical vowel, a near vowel is assonance only.
(2) the map stacked four colour layers (end groups, exact-rime classes, chains, single-vowel echoes), so ba, plain and plane (all eɪ) landed in different layers and different colours. Colour is now RhymeFlux-style:
FILL = the syllable's vowel (same vowel, same colour; a vowel is coloured when it recurs in different words of the slot or closes an end rhyme), UNDERLINE = solid if another word within two bars has the same ending too
(an exact rime), dotted if only the vowel matches; a pale fill carries a matched weak closing syllable; wavy red = unstressed tail echo; dark bar = multi-syllable internal rhyme.
(3) luego was pronounced with a short e (LWEH-go) but is sung lway-go, and Mainz with aɪ but is sung maynz (Joe's ear): rapfit.SUNG overrides them. By-ear AUC went 0.931 -> 0.932 with the overrides.
Also: hyphenated words (on-stage) lost their per-syllable colouring because the splitter dropped the hyphen; they are split part by part now.


## 13 Oct 2026 (latest 4) -- transatlantic: trans / at / lan all rhyme with man, tic with chips (prominence widened)
Joe: transatlantic in Hook 5-8 should flag trans-at-lan against "man" and -tic against "chips". The cause was the prominence rule: only dictionary-STRESSED syllables (plus long vowels) counted, so trans
(unstressed full æ), at (dictionary schwa) and tic (weak ɪ) were invisible. Now: ANY full vowel is a beat-bearing syllable (rapfit.prominent: stressed or not in {ə ɪ i}; the 'it' of biscuit / credit is still a
tail), and a weak ɪ in a content word may JOIN a vowel family that has a prominent member within a bar (tic ~ chips) but can never make a family alone. As-sung overrides (rapfit.SUNG, all from Joe's ear):
luego, Mainz, chicas, transatlantic. Rendered Hook 5-8: Tran / lan = æ exact with man, sat = æ vowel-only, tic = ɪ with chips. Re-calibrated: stress-anchor gate unchanged (original 0 of 69 hard, draft 8 biscuit and
credit, draft 9 0); by-ear AUC 0.932; chain counts still at chance level (original 25 vs 22.8 expected, draft 8 20 vs 20.7), so chains stay diagnostic.
COSMETIC: the written word is cut by sound (Tran|sat|lan|tic), not by morpheme (trans|at|lan|tic).


## 13 Oct 2026 (latest 5) -- "why is whip not highlighted with stick and chick? / num in numbers?": detected, but the PROJECT file hid the words
Both are detected and coloured in the full-text map (whip, stick, chick = one ɪ family, whip dotted; num = ʌ with run, up and mon-ey). The project version printed only words flagged by the older layers
(end tails, exact links, chains, alliteration), so whip and num showed as plain dots. Showing every coloured word would reveal ~59% of the original's text (344 of 583 words), which breaks rule 4, so hidden
syllables now render as DOTS THAT KEEP THEIR COLOUR, underline and chain bar (a yellow dot in stick / chick's colour is the whip you cannot read). Rule-4 check: 0 unbroken 4-word runs. The letters stay in
~/Documents/WORLDWIDE_PRIVATE/rhymes_original_vs_v8.html.


## 13 Oct 2026 (latest 6) -- TEMPLATE and BLOCK rules enforced; internal-echo REWARD added (not validated)
Joe: the original's V1 17-24 puts the stressed rhyme syllable at the same distance from the end in every bar, runs one 3-syllable rhyme per 4-bar block, and echoes the end vowel inside the bars at about the same
point in neighbouring bars. Measured on the original: bars 1-4 have the stressed syllable 3 from the end in 4 of 4 bars, bars 5-8 likewise (the existing beat-parallelism index scores the original -0.19 / -1.0
and is useless here).
ENFORCED (rapfit.check_block, via slotcheck): in 3-syllable slots (V1 17-24) a 4-bar block needs >= 3 of 4 bars on a 3-syllable rhyme (HARD); in any slot with target depth >= 2 the bars of a block should share ONE
depth (SOFT note). Calibrated first: the ORIGINAL has 0 hard failures. Draft 8 now fails 4 hard (biscuit, credit, and both V1 17-24 blocks), draft 9 fails 2 (both blocks). Writer prompt (block_writer.SYSTEM) states the template.
REWARD: rapfit.internal_echo(bars) in 0..1 (share of bars whose end vowel returns inside the bar + closeness of those echoes in adjacent bars as a share of bar length; 1 syllable apart in 10 = 0.6).
It is wired ONLY as the last tie-break when the build picks among candidates (draft_all.score_section "echo"). HONEST STATUS: it does NOT separate the texts - original mean 0.42, draft 8 0.44, draft 9 0.54 (draft 9 is the
worse draft on sense) - so it is unvalidated and gameable. Needs Joe's marks of the internal rhymes in V1 17-24 bars 1-4 (he counts 7) before it can rank anything.


## 13 Oct 2026 (latest 7) -- the rebuild was still deciding with the OLD rhyme and flow instruments; now it uses the measured ones
Joe: "is this still using the old broken rhyme and flow map to match with the original?" Partly yes. The first rebuild's decisions (slotcheck hard list, draft_all.take, rebuild.total_score) still used: the beat-grid
"weak syllables on a downbeat" check (registry: failed_validation), check_all's problem count (failed_validation as a quality gate; it sat in the ratchet AND the plateau score), the old grader's 0.78 pair floor
(credits unstressed tails) and its carpet share. The new rhyme pieces (stress-anchor, 3-syllable block rule, menu filter, prompt text) were in beside them; the map's vowel-family / ambisyllabic / cluster logic is display only.
CHANGED (slotcheck.check; WW_LEGACY_FLOW=1 restores the old behaviour): beat-grid checks, the old pair floor and the carpet share are NOTES; the scheme-pair check is a note on rapfit's pair score (a first version hard-failed it and
failed the ORIGINAL on 13 issues because the pair score cannot see its 3-syllable tails, so the bar-level syllable-by-syllable stress-anchor rule is the gate); draft_all.take no longer counts check_all problems; rebuild.total_score
drops them too. Calibrated: ORIGINAL rhyme/flow hard failures 25 -> 0, draft 8 10 -> 4 (all V1 17-24), the old-gates round 1 79 -> 4. STILL OLD, by choice: syllable counts (+-1) and end shape (registry: accepted exact facts), the weak-run,
mouth-shape and grammar/sense checks (Joe's own ear complaints). STILL OLD, not by choice: the end-word MENU's carpet bank (benchmark/carpets_*.json) was built with the old grader; the write-time vowel/cluster
logic is not in the prompt beyond the template sentence. Old-gate round 1 kept in writing/_old_gates/. Rebuild restarted as writing/ww_full_draft_v11_r*.md.


## 13 Oct 2026 (latest 8) -- story seeds rewritten to things Joe actually did (parties, adventures, fun)
Joe: "Update the story seeds to be things I actually did like partying, travelling adventures and fun." The plan's story (a crime-business operator with a debtor, a quarry, a mayor, accountants and a snooker kill) was
persona invention. Replaced with eval/_plan_v4.json (v3 untouched; argue_stage.PLAN_PATH now prefers v4) + eval/plan_extra_sections.json (Hook 1-4) + seven new true Fact cards in ww/schema/joe_facts.py. Every slot keeps its
measured frame (syllable counts, end shapes, rhyme family); only the story changed. ASSISTANT-AUTHORED, NOT APPROVED by Joe (rule 2 waived by his instruction); anything beyond the material is marked (cartoon) or (persona).
SEEDS BY SLOT: Hook 1-4 end of the 2023 motorbike tour at Bilbao (spider under the bridge, ferry home) | Hook 5-8 Rolling Loud Rotterdam 2023, lime wristband, the giant garden gnome ("off the back of a lorry" = the stage) |
Hook 9-16 Boomtown (posters, tents wet/dusty/dry, pink top hat; "off my head") | V1 1-8 the ferries with the bike (Isle of Man, Dublin, Brittany; "make merry") | V1 9-16 Australia 2017 hostels to K'gari 4WD
("along for the ride"; the one "worldwide") | V1 17-24 King's Day Amsterdam 2019, truffles, the film, passed out in the aisle (two 3-syllable blocks: "stumbled in" family, then an æ family) |
V1 25-32 Marrakesh 2025 haggling at Jemaa el-Fna ("pedal to the metal") | V1 33-44 the 2019 Interrail, 12 stops, 72 waterfalls, the Black Forest honesty stall ("take it on trust") |
V2 1-8 the Interrail walks in the wrong shoes ("in my shoes", uːz monorhyme) | V2 9-16 the Naples stag weekend ("paint the town red"). Removed: debtors, the quarry, the mayor, the accountants, the snooker finale, the guillotine murder.
Ledger of once-only idioms rewritten to match. Old-plot drafts moved to writing/_old_gates/. Rebuild restarted as writing/ww_full_draft_v12_r*.md.

## 14 Oct 2026 (later) - plan v5, cadence, Aussie slang, place assumptions
Joe: re-plan as CLAIMS not events (the original has no story: sound picks the places; one voice and a returning hook hold it); per-block CADENCE (ww/write/cadence.py: describe + check, a note and a small plateau penalty, UNVALIDATED); embellishment of true places allowed (cartoon); assumed by Joe: weed and the red light district in Amsterdam, partying in Sydney and the beach. New: eval/_plan_v5.json, material/place_assumptions.md (general-knowledge traveller lore, NOT verified or researched online, all flagged assumed), Aussie slang (toolkit/local_words.txt, toolkit/phrases.txt, 37 OVR pronunciations, toolkit/aussie_harvest.json = noisy Wiktionary pull, ledger-recorded). Rebuild restarted as writing/ww_full_draft_v13_r*.md.

## 14 Oct 2026 (night) - draft v13 written BY HAND, section by section (writing/ww_full_draft_v13.md, Suno format brief/suno_prompt_v13.md)
The automated from-scratch rebuild (plan v5 + cadence) produced a poor round 1 (total -133, 29 min/round, lines like "Found pink top hat, wear it like bread"): the gates cannot read a sentence, so more rounds would only polish nonsense. Moved to main-thread writing with the toolkit as a FIT tool: every section was fitted with slotcheck.check (syllables, ending shape, scheme, cadence, cashed idioms) via a fit script; the commented version is writing/ww_full_draft_v13_commas.md, the comma-free one (commas cost form; the original has them on 25% of bars) is ww_full_draft_v13.md.
STATUS per section (hard failures left, all shape/cash/density, none sense): Hook 1-4 1 | Hook 5-8 0 | Hook 9-16 2 | V1 1-8 0 | V1 9-16 2 | V1 17-24 4 | V1 25-32 2 | V1 33-44 3 | V2 1-8 2 | V2 9-16 1. songcheck: 3 problems (sound-device rate 26% vs 53%; hook names 3 places not 4; 3 local words in verses not 5). meaning_gate: 8 fails, ALL the same cause: V1 17-24's tails end on "in" (a function word) - kept on purpose, it is the 3-syllable cluster device (tumbled/mumbled/crumbled in) and the gate fails it; also "way out" in Hook 9-16.
Aussie slang pool, 37+ OVR pronunciations (kaixo, shukran, prost, napoli, lorry/quarry/corrie vowel fixes), material/place_assumptions.md (generic traveller lore, NOT verified), plan v5 (claims not events).

## 14 Oct 2026 (later) - SENSE GATE: v13 regressed to telegraphic nonsense; v14 rewritten as full sentences (writing/ww_full_draft_v14.md, brief/suno_prompt_v14.md)
Joe: "this regressed and wrote nonsense bars, we need to enforce sense making better" and "also enforce sense making across bars". He was right: to hit syllable counts v13 dropped articles, verbs and commas, so 39 of 76 bars were fragments ("Queue round the block for the film I'm buying in"). No gate read a sentence.
BUILT ww/write/sensecheck.py: a cached ds-flash read (temperature 0, no thinking, a few thousandths of a cent per block). PER BAR: restate as one complete sentence from the bar's own words, grammatical y/n, sense 0/1/2; fail on sense < 2 or not grammatical, plus a deterministic screen (dangling in/on/out/up/off at the end, fewer than two content words). ACROSS BARS: one thread per block and every bar must follow the one before it; hard fail on coherent 0, "NO THREAD", or more broken links than 1 per 4 bars. WIRED INTO slotcheck.check as a HARD failure (WW_SENSE=0 switches off; a network failure only adds a note), so the automated build, merge ratchet and rebuild cannot accept a nonsense bar. CLI: python -m ww.write.sensecheck FILE | --calibrate.
CALIBRATION (honest): bar judge passes Joe's approved bars + 3 good bars (0 of 7 failed) and fails the 7 known-bad bars (0 of 7 passed). n=14 and half the labels are mine: a direction, not a certificate. The BLOCK judge does NOT separate Joe's approved 4 bars from the known anti-example (both coherent 1), so its hard threshold is a real break only; its per-bar notes are what to read. It is a model opinion; Joe's ear still decides.
RESULT: v13 39 bars failing -> v14 0 bars failing, 0 across-bar failures (after adding real connectors: "Stop one...", "Then...", "While I haggle...", "If police ask...").
THE COST, measured and not hidden: form got worse. Hard form failures per section v13 -> v14: Hook 1-4 1->4, Hook 5-8 0->4, Hook 9-16 2->6, V1 1-8 0->6, V1 9-16 2->7, V1 17-24 4->17, V1 25-32 2->10, V1 33-44 1->19, V2 1-8 2->4, V2 9-16 1->6. Full sentences are longer and put weak words on beats (syllable counts now off by up to 2-4 on some bars). V1 17-24 lost the 3-syllable tail cluster: the rhyme is now -ade / -ation, real words but suffix-carried and only 1-2 syllables deep. That block is the one Joe prizes, so it is the first thing to rebuild: keep the sense gate and recover the device with words that carry a genuine 3-syllable tail.

## 14 Oct 2026 (late) - pass 5: the aftermovie, a fresh Google Photos pass, nightlife assumptions (Joe: "the song needs more information")
- Aftermovie (YouTube mfZGjU6aS78, 5:41, GoPro, Thailand/Laos/Vietnam/NZ/Australia/Bali) watched frame by frame in the browser (every 6 s): scenery and ADVENTURE only (Pai ridge, Laos buffalo and scooters, Ha Long kayaks, parasailing, scuba, elephants, Pinnacles 4WD, campervan, NZ rafting, a canyon swing/bungee). NO bars, parties, drugs or nightlife in the sampled frames. material/aftermovie_and_photos_pass5.md.
- Google Photos pass: 2015 has 4 photos (Pai canyon, a robot tattoo 15 Dec 2015), 2016 none, 2017 Australia dated and varied (Brisbane neon club + park stumble 16 Apr, hostel dorm 23 Apr, K'gari 4WD convoy 27 Apr, Whitehaven group 30 Apr, pool noodles 5 May, Magnetic Island, Cairns dinner for ten 10 May); beer/cocktail/party searches are 2020-2026 UK pubs, Naples cocktails, Boomtown nights.
- material/nightlife_assumptions.md (git-ignored): assumed nightlife story seeds per place, innuendo only, plus drinks and local words by country. Plan v5 patched: V2 1-8 is the backpacking years, V1 9-16 gains real 2017 photo stamps, V2 9-16 a hen-party stamp.
- evolve loop: the run with the carpet gate used about $3.2 in ~40 min with NO round completed (strict carpet + repairs = many rejected candidates); stopped. DeepSeek balance $2.53. Before the next run: cap repairs, try ds-flash for candidate volume, or top up.
- 14 Oct 2026: festival and event lineups researched (WebSearch, standard) and saved: material/festival_lineups.md (Rolling Loud Rotterdam 2023, Boomtown 2019/22/23/24/25, Reading 2013/2017, Wasteland 2023 (no lineup found), with sources and sound-alike pun hooks). Plan v5 stamps added to Hook 5-8, Hook 9-16 and V1 9-16. Names are texture only; Suno may block famous names, so the writer describes them.
- 14 Oct 2026: Joe told the Vietnam story in his own words (Honda Wins Hanoi to Ho Chi Minh, biblical rain, separated, bike ditched, key lost, helmets stolen, drunk rental place, flew to NZ): material/joes_own_stories.md (REAL, top confidence). V2 1-8 rewritten as that story (uːz monorhyme: clues/views/shoes/queues/blues/news/booze/lose), sense gate 0 problems, writing/ww_full_draft_v17.md = v14 + this verse; plan v5 V2 1-8 follows it.

- 14 Oct 2026 (later): Joe gave six more REAL stories: material/joes_own_stories.md (git-ignored, personal). Plan v5 re-cut around them (V1 1-8, V1 9-16, V1 25-32, V1 33-44, V2 1-8). Marrakesh and the Interrail list are out of the plan (still in material/). Improver loop idle (balance $2.53).
- 14 Oct 2026 (later): Joe's Wasteland story recorded in material/joes_own_stories.md (git-ignored); plan v5 V2 9-16 is now that story (Naples stag out of the plan, still in material/).
- 14 Oct 2026: Joe on the pool hustle sum: 'I think it was 1 mil, but it might have been Laos or Vietnam'. Laos is landlocked and the chase was on a beach, so Thailand or Vietnam; a million dong is about 30 pounds (a better joke than a million baht at about 18,500). Currency left open in the plan.
- 14 Oct 2026: a further personal story recorded in material/joes_own_stories.md; that file and nightlife_assumptions.md are git-ignored (the repo is PUBLIC; personal stories must not be pushed). Capacity note: the real stories now exceed the 76-bar frame; Joe to rank them.

## 15 Oct 2026 - mouth shape, transitions and vowel duration added (report-only)
Gap found: only consonant joins were measured (flow_check rare_joins); no vowel duration, no time-per-syllable, no vowel travel, nothing for 70 half-time. Added toolkit/duration.py (selftest asserted in calibrate.py), flow_check.vowel_travel(), benchmark/mouth_and_duration.md, and a MOUTH PASS step in .claude/commands/write.md. NOT DONE: calibration on the original (private file absent in the cloud session; run `python toolkit/duration.py --calibrate PATH` on Joe's PC), rejected-vs-approved separation table, wiring into ww flowaudit/trybars, block_writer prompt, Suno A/B. Until calibrated these are notes, never gates.
15 Oct 2026 (calibration, counts only): duration.py on the original's 76 unique lines (214 ms/step layout): 69 bars lay on the template (7 skipped: count mismatch or no audio steps for template bars 10, 60, 86), and 49 of 69 (71%) carry >=1 need>have flag. So the duration estimates are too long (rapped vowels are shorter than citation form) and the flag cannot be a gate; scale BASE down (~0.6x) and re-run before use. flow_check on the same lines: 5 of 76 bars have 2+ rare joins (par 6 of 92), 78% have none (par 78%): the mouth-shape measure sits at the original's own rate.
15 Oct 2026 (rescale done): duration.py SCALE default 0.8 (0% need>have on the original at 214 ms; 0.85 -> 14%, 1.0 -> 69%); the 107 ms layout flags 94% of the original so it is info only; the fast-run rule fires on 37% so it is a note. Still to do: rejected-vs-approved separation, wiring into flowaudit/trybars/block_writer.
15 Oct 2026 (Joe's correction): 'same-place stop-stop' (ship|packs, up|postal) REMOVED from flow_check.RARE. Joe: no articulator moves between two stops at the same place, so it is the EASIEST join (said as one held closure), not a hard one; I had it backwards. It is now EASY_JOIN, named by joins() but never counted. The kept rare joins still fire on the bar Joe flagged on 14 Oct. Effect on the original's 76 pasted lines (from the earlier per-bar output, not re-run): 5 bars have one rare join (fricative->h in 2, voiced fricative->liquid in 3) and none has 2+, so the old par (0 in 78% of bars, 2+ in 6 of 92) is STALE: it was inflated by stop-stop. TO DO on Joe's PC: rebuild benchmark/flow_baseline.json (rare_joins 0.216/bar) and re-run `python toolkit/flow_check.py --calibrate PATH`. A 2+ threshold now never fires on the original, so it may need to be 1+ for a note.
15 Oct 2026 (PanPhon + Klatt wired in): toolkit/articulation.py (join_cost from PanPhon place features + an articulator rule; Klatt table in toolkit/klatt_durs.scm, CSTR notice kept), duration.py now uses both (SCALE 0.45, JOIN_T 3.0). Selftests pass (articulation, duration, flow_check). Original re-run: flow_check 5 bars with one rare join and none with 2+ (stop-stop removed); duration 0 need>have bars, 7 bars with a hard join (t|k etc). Still report-only; rejected-vs-approved separation and wiring into flowaudit/trybars/block_writer still to do. `pip install panphon` needed on Joe's PC.

## 15 Oct 2026 - flow tools run on the original vs an AI-written song; check_all crash bug; the original now passes every flow check
Joe asked for all flow tools on the original vs an AI-generated song (his stories, 76 unique bars: hook 16, three verses), then tweak the tools until the AI version fails and the original passes. Lyrics were handled via stdin / a temp file outside the repo (deleted); nothing from either text is committed except numbers.
FOUND, and it mattered: `check_all` printed ALL PASS for ANY text whenever a sub-check crashed (here `wordfreq` was missing, match.py and flow_fit.py died, `run()` read only stdout, no problems = pass). `run()` now raises on a non-zero exit or a traceback. With the instruments actually running: original 3 problems, AI 138.
THE ORIGINAL'S 3 FAILURES were not flow, they were the by-ear rhyme-scheme check tripping on pronunciation and loose groups, fixed in principle not by loosening everything: (1) as-sung pronunciations: `moi` ("mwah", helpers.SUNG, beats Britfone), `Mainz` ("maynz", was the German "mynts" in rhyme_tools), `Fumez`, `Federali` (OVR); (2) match.py now demands only the by-ear pairs the grader CONFIRMS ON THE ORIGINAL ITSELF (benchmark/rhyme_confirmed.json, `match.py --confirm`; same rule songcheck already used: a gate the benchmark fails is a wrong gate), and prints how many pairs it did not demand; (3) original_profile.json rebuilt with the corrected pronunciations (2 bars changed); (4) flow_template.json bar 55 marked `advisory` (the original's own proper noun cannot fit its audio template's end shape; same waiver bar 1 has).
calibrate.py: the by-ear scheme line is no longer exempt from "original passes" (that exemption hid the 3 failures), and two stages added: the original passes `check_all --song` in every slot, and passes `flowverdict --calibrate`. CALIBRATION PASSED (39 checks).
NEW toolkit/flowverdict.py: per section, five template-laid flow numbers (check_all form problems, share of bars off the syllable count by 2+, end-shape mismatch share, flow flags per bar, 4+-unstressed-run share). A section fails a metric when it is worse than the original's worst section by half the original's own range; a section fails on 2+ metrics; the draft passes if no section fails. VALIDATION is leave-one-section-out on the original: 0 of 10 original sections fail. The AI song: 9 of 10 sections fail (6 of 10 on the four non-form metrics alone). `form` has threshold 0 because the original now has 0 problems everywhere, which is partly by construction (I tweaked the tools until it did); the other four metrics were not tuned.
HONEST LIMITS: everything above measures similarity to the original's audio template, not quality; n = one original and one AI draft; the AI version's bars were split from a paste with no line breaks, so some splits are mine. Mouth/time measures (duration, PanPhon joins, flow_check) do NOT separate the two texts (hard-join rate 0.37 vs 0.38 per bar; time packing 0.33 vs 0.32); earcheck hard-join bars 28% vs 18%. `slotcheck` needs spacy (not installed here), so its grammar and rhyme-depth gates were not run; meaning_gate is not a flow tool and failed both (orig 5, AI 3).
TO DO on Joe's PC: `pip install panphon wordfreq`, `python -m ww.cli freeze write` (the freeze check here only shows this container's packages), `python toolkit/calibrate.py PATH`, `python toolkit/flow_check.py --calibrate PATH` and rebuild benchmark/flow_baseline.json (stale since the stop-stop change).

## 15 Oct 2026 (later) - cross-bar flow: rhyme landing, stress alignment across bars, tension (toolkit/flowshape.py)
Joe: what matters is whether rhyming syllables land on the same part of the beat across bars, how stress patterns match across bars, and how tension is built and released from those. Built toolkit/flowshape.py (text profile + audio-timed profile; baseline benchmark/flow_shape_baseline.json, numbers only; selftest in calibrate.py).
VALIDATED FIRST: the text-side rhyme index equals the audio rhyme_idx in 70 of 71 original bars; equal tails (syllables after the rhyme) land within 1 step 62% of the time vs 19% for unequal tails; an even-spacing guess of the step was poor (mean abs error 3.75 steps) so it is NOT used.
THE ORIGINAL ON AUDIO (benchmark for any render): rhyme anchors land on beat 4 of the bar 65% of the time (46/71, beat 3 in 14); rhyme partners land on the same beat 60% of the time and the same step (within 1) 50%, so the original varies its landing on purpose; adjacent bars share only 28% of their stressed steps.
AI SONG, TEXT PROXIES vs ORIGINAL: it is NOT worse on landing or stress alignment (equal tails 92% vs 71%; end-aligned stress agreement 0.63 vs 0.62; rhyme coverage 0.97 vs 0.91). It is smoother: clashes per bar 1.04 vs 1.47, run-on bars 4% vs 13%, tension spread 1.42 vs 1.73, range inside a 4-bar group 2.80 vs 3.52, build-then-release groups 53% vs 32%, tension peak on bar 3 in 42% of groups vs 26% (only 19 groups each, so 10 vs 6 groups: weak). Per section none of these separates the two under the leave-one-out rule (the original's own sections vary too much), so they stay profile rows.
READING: the AI song fails flowverdict because it was not written to the original's rhythm (syllable counts, end shapes, flags per bar), not because its rhymes land inconsistently; if anything it is too regular. Whether its rhymes land on the same part of the beat can only be measured on audio: render the lyrics in Suno at 140, run toolkit/flow_map.py (conda env flow) on Joe's PC, then `python toolkit/flowshape.py --audio TEMPLATE FILE`.

## 15 Oct 2026 (later still) - why the analyser got Joe's ear verdict wrong (quad: orig V2 9-12 vs an AI "two weeks" line)
Joe's ear: the original quad sounds good (bar 1 has space and its two chunks match; bar 2's mouth transitions are natural); the AI line does not flow. Analyser had it backwards. MEASURED causes:
1. CONNECTED SPEECH not modelled: "and|get" cost 3.5 (hard join) but spoken it is an' get (final t/d dropped after a consonant, n takes the next stop's place). FIXED in duration.hard_joins (connected(), nasal assimilation); the original's 3.5 joins fell 7 -> 4, selftest and need>have (0/71) unchanged. Report-only.
2. OBSTRUENT-CLUSTER LOAD does NOT separate them (tested, negative): obstruent share per line orig 0.60 vs AI 0.64, 8 vs 7 lines over the original's p90. Not built.
3. CHUNK SPACE is real but unwired: 18 original bars are two chunks around a pause, 8 of them balanced (+-1 word); the AI text has 3 two-chunk bars. Only a text-punctuation proxy (the AI paste's commas are mine), so a note, not a gate.
4. Bars whose syllable count != template are SKIPPED by duration/join checks (the AI line before the quad was one): no template-free fallback yet.
5. Rhyme grader gives the some/lonesome/long one/long johns consonant-frame family 0.0-0.3 (kept: calibrated best_end untouched).
(calibrate.py run here with a hand-split scratch original fails "original vs own profile" identically with and without this change - the scratch sectioning, not duration.py; re-run on Joe's PC with the real file.)
15 Oct 2026 (frame echo): Joe's second ear point - the long-one bar and the lonesome bar match "for flow perfectly" - was a SIXTH cause: nothing saw two adjacent bars finishing on one frame. NEW toolkit/frameecho.py (report-only; selftest asserted in calibrate.py): near-equal stress over the last 5 syllables (>=4 of 5) AND a shared non-stop word in the last 6 words. On the original (re-pasted, 75 adjacent pairs, scratch copy deleted) it fires on 5 pairs (6.7 per 100), including Joe's pair (bars 70-71) and the next (71-72). NOT YET COMPARED to the AI song (its text was not re-pasted), so it is a note, not a gate; rate for AI unknown. Consonant-frame echo (some/lonesome) is still not credited.
15 Oct 2026 (frame echo, AI song): on the AI song (60 bars after my capital-letter split of the unbroken paste, so bar boundaries are mine) frameecho finds 1 echo in 59 pairs (1.7 per 100) against the original 5 in 75 (6.7 per 100). One event vs five: a direction, not a gate. Scratch copies deleted.

## 15 Oct 2026 (night) - flow-fitted rewrite of the AI song (Joe: "build a version that matches the original's flow so I can see how well our flow analysis works")
writing/ww_flowfit_v1.md (comma-free; writing/ww_flowfit_v1_commas.md has the commas) and brief/suno_flowfit_v1.md (Suno layout). Same facts as the AI song (Joe's stories as pasted; nothing new invented beyond the AI paste's own details), rebuilt bar by bar to the original's measured frames: syllable counts (flowaudit's counter), end shapes, scheme families, no 4+ unstressed runs, one -ing/-y/-it family per block.
RESULT, flowverdict: AI paste 9/10 sections FAIL -> this draft 1/10 FAIL (V2 9-16: 6 of 8 end shapes off; its template wants |Sw, |SS, ~w endings that need words this story does not offer). Also: phrase_audit PASS, characters within cap (mate 2, crew 2), meaning_gate only header artefacts + enjambment notes, frameecho 3 echoes in 76 bars (AI paste 1/59, original 5/75). check_all form problems are still 6-21 per section (original 0): form is not reached. 
WHAT TO LEARN FROM IT (Joe's ear is the test): sections that PASS flowverdict may still sound wrong; if they do, the metric is the gap. Fitting costs: end shapes were the binding metric (|w needs a weak-pronoun ending, ~Sw needs a stress-inside word like tomorrow), and flowaudit and flow_fit disagree on syllable counts for some words (Hanoi, wearing), so a bar can be exact on one counter and 2 off on the other.

## 15 Oct 2026 (night 2) - COUNT-FREE flow fit (toolkit/timefit.py) and a song written with it (writing/ww_timefit_v2.md, brief/suno_timefit_v2.md)
Joe: replace the syllable counter with a fit on stress, mouth transitions and vowel length, and write a song to the original's flow with it. BUILT toolkit/timefit.py (report-only, selftest in calibrate.py): dynamic-programming lay of a bar's syllables onto the original's 16th-note steps, no count required. Costs: strong syllable on the original's weak step / off its grid, weak word on its stress, an original stress nobody fills, the last syllable not on the original's last step, Klatt time (duration.py) and PanPhon + connected-speech mouth joins on 1-step gaps. Baseline from the original (numbers only, benchmark/timefit_baseline.json): bar mean 0.45, 39 of 65 bars cost 0, section means 0.02-1.77 (waived: the 3 advisory/no-step bars). Pass limit = worst original section + half its range (2.65).
FIRST TEST (flowfit v1, which flowverdict had passed 9/10): timefit FAILS 4/10 sections. v2 (35 bars rewritten with timefit in the loop): timefit PASS 10/10, but the OLD flowverdict now FAILS 3/10 (V1 1-8 and V2 1-8 on count, V2 9-16 on end shape) - the two instruments disagree exactly where bars were allowed to change length, which is the point of the change and is unproven until Joe's ear/Suno confirms.
HONEST LIMITS: (1) the strong/weak flags on both sides come from the same spelling-level heuristic, so "stress" here is not heard stress; (2) the DP can slide a bar around the grid, so it is easier to satisfy than a fixed count - the baseline limit is generous (original's worst section 1.77 is partly heuristic noise: bars 7/68 have pick-up steps); (3) 11 bars still cost >2.5 (7, 29, 36, 37, 40, 54, 64, 66, 68, 70, 71, 74), listed per bar by `python toolkit/timefit.py FILE`; (4) cost 0 for a 6-syllable bar is possible if it drops weak fillers, so sense can thin out ("Dawn came covered and itching"); (5) KNOWN WRONG: "Rice paddy ... what a bore" (Joe's bar 58) now costs under 1.6, so timefit does NOT flag the weak "and" he heard - it dropped "and" in v2 but the old flow audit still lists that class of flag; read both.
15 Oct 2026 (timefit bug, Joe: "how did 'The officers wanted a bribe so the boys ended paying' get through?"): timefit skipped the template's 9 `advisory` bars (1, 16, 28, 30, 32, 35, 42, 55, 76) in BOTH the baseline and our song. `advisory` marks bars the original fails on the OLD checks (count/end shape); it says nothing about the new fit, so those 9 bars of ours were never scored. Bar 42 costs 4.6 (stress missed at steps 16, 26, 27, 28: the original packs five strong syllables before "paying"), bars 32/55/76 cost 5-6. FIXED for our song (advisory bars now scored; V2 9-16 then fails at 2.74 vs 2.65). The BASELINE still excludes them until the original is re-pasted and `--calibrate` is re-run, so the 2.65 limit is not yet like-for-like.
