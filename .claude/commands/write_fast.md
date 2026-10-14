---
description: Write the remaining sections of the song as fast as possible, using the local GPU for volume and the main thread for taste
argument-hint: <sections, e.g. "all" or "Hook 9-16, V1 1-8"> [source draft, default the latest writing/full_draft_vN.md]
---
Write $ARGUMENTS of the "Worldwide" song so that every section passes the repo's own definition of done, as
fast as possible: the RTX 5070 Ti for volume, this thread for taste, the repo's tools as the only judge.

## 0. Read first, in this order, nothing else
1. `CLAUDE.md` -- the rules are law. Rule 4 (never reproduce the original's lyrics in any file or reply beyond
   isolated words; cite by slot/line) and rule 6 (subagent cost: writer agents burned 128k output tokens each
   and returned nothing) are the two that have already burned this project.
2. `STATE.md`, last ~400 lines -- every measurement so far, the three tool bugs fixed on 13 Oct, and the
   shape/carpet constraints for a hook quad.
3. `writing/hook_5-8_v15.md` -- the standard. That block passes `check_all` with 0 problems, carpet 6/6 at
   1.00, multisyl 3 against the original's 2. Match its method, not just its numbers.
4. `writing/song_map.md` -- each section's job and the places it owns.
5. `benchmark/gate_architecture.md` and `benchmark/original_profile.json` -- the level gates and the original's
   own measured numbers.
6. `ml/README.md` -- the local generation loop that already exists.

## 1. Verify the instruments before believing a single number
`python toolkit/calibrate.py "C:\Users\Joe\Documents\Worldwide_private\original_lines.txt"` must print
CALIBRATION PASSED. If it does not, fix the tools first: a gate the benchmark fails is a wrong gate, not a
strict one. Re-run it after ANY tool change, and rebuild `benchmark/original_profile.json` if the grader
changed (it must always be measured by the current grader).

## 2. The facts you inherit -- do not re-derive, they cost a full session
- **End words are chosen by SHAPE and by a measured carpet, never by vowel alone.** A hook quad's four end
  words must each be two syllables, first stressed, second weak -- `flow_fit.end_shape` prints that as `|Sw`
  ("soft+1") -- and all SIX pairs must score >=0.78 on `match.best_end`. The original's own weakest hook pair
  is 0.92. A word whose stress lands mid-word (`~S`) or in a different tail cannot fill the slot however good
  the vowel: `-am` (tram/jam/Amsterdam) is impossible for Hook 5-8 for exactly this reason.
- **The rhyme must come from the stressed syllable.** A reduced-schwa ending is not a rhyme; the grader now
  scores a pair that matches only on two schwas as 0.65/none. Unstressed `/i/` and `/I/` DO rhyme (certi ~
  forty, Dublin ~ him) -- only the schwa is excluded.
- **Check a word is even pronounceable by the tools before you build on it.** Britfone lacks many place names
  (Zurich, Porto, Bordeaux, Ljubljana, Majorca); `helpers.uk_phones` now resolves those through CMU + OVR. If
  a place keeps scoring 0.80 against everything, check its phones before you change the line.
- **multisyl** (the two-syllable tail device; the original fires 2 per hook quad) is a pair of two-syllable
  vowel runs made of two ADJACENT CONTENT WORDS. Function words are marked unstressed and cannot carry it.
  Three sequences give three pairs: `cash back`, `black van` and `backpack` are all AE-AE.
- **Flow is checked against the original's audio template bar by bar:** line length exact, and no weak
  syllable on a beat the original stresses (e.g. beats 4 and 7 of hook bars 6-7). It is worth rewording a bar
  to move a strong syllable onto a beat -- "stuck in the black van in all the traffic" beats "sitting in the
  black van in the traffic" for that reason alone.
- **`meaning_gate` is a FLOOR, not a judge.** A noun-stack with the right registers passes it (Joe's rejected
  `Ola and the lot on the dot` / `A grazie and a page of the orders` passes meaning_gate today). So "says
  something" is human: **agree a one-line "who does what" per bar BEFORE writing any words**, and keep it in
  the section file.
- **Two counters, both must pass:** `check_all --slot "<slot>" -` for the sound of one section (project format
  on stdin: one bar per line, no headers), `check_all --song <draft>` for the whole file with `== Slot`
  headers. `songcheck.py` is the level gate. `ratchet.py <before> <after>` must say OK after every pass.
- **`toolkit/keepers.json`** (Joe's locked lines, phrases he liked, true places) is never dropped to pass a
  check. Removing an item needs Joe's OK. Locked lines are never rewritten.

## 3. Build the one tool you will use in every section -- do this first, it is the real speed-up
A single script `toolkit/carpet.py --slot "<slot>"` that:
- reads the slot's measured target from `benchmark/original_profile.json` (syllables per bar, end shape, the
  scheme, the carpet);
- searches `material/place_sound_families.md`, `material/travel_history.md`, `toolkit/theme_words.txt`,
  `toolkit/local_words.txt` and the OVR table for candidate END-WORD SETS;
- keeps only sets where every pair scores >=0.78 on `match.best_end` (aim for >=0.95), every word has the
  slot's ending shape, at least two words are TRUE places from `material/travel_history.md`, and the syllable
  budget can be met;
- prints them ranked, with each word's shape, truth source and the pairs' scores, and caches to
  `benchmark/carpets_<slot>.json`.
Rationale: asking a model to invent end words is the slow, unreliable path that produced the regressions.
Exhaustive search takes seconds of CPU and never proposes a fake rhyme. Run it for every unwritten slot in
parallel before writing a word.

## 4. Parallel plan (this is where the GPU earns its place)
**Phase A -- CPU, all slots at once.** `toolkit/carpet.py` for every unwritten slot, as parallel processes. No
model involved. Output: a sound map per slot for Joe to see and for you to write to.
**Phase B -- GPU, 3 slots at a time.** Per slot:
`python ml/generate.py --slot "<slot>" -n 60 --per-batch 6`
with the chosen end words and the beat sheet PINNED into the prompt (do not let the model choose rhyme words
-- it cannot hold this form; its job is volume and phrasing). Ollama runs on localhost. On 16 GB VRAM keep ONE
model resident (a 7-14B instruct model at q4-q5; check `ollama list` first and do not load two), set
`OLLAMA_NUM_PARALLEL=3`, and keep the context small. Measured on this machine: ~147 tok/s, ~2.2 s per
candidate, and the CPU verifiers are the bottleneck, not the model.
**Phase C -- this thread, the strong model.** Per slot: beat sheet -> pick and patch the survivors -> run the
gates -> ratchet. Only bars that FAIL may change; a passing bar changes only if a stanza-level check (scheme,
density, multisyl distribution) demands it, with one line of reason. A fix that breaks something else twice is
the stuck rule's T3: pivot the bar, do not trade one failure for another.
**Phase D -- assembly.** `writing/full_draft_v<N+1>.md`, then ratchet, `check_all --song`, `songcheck`,
calibrate, report.

Critical path: judgement in this thread. Generation and search are cheap and parallel -- never serialise on
the model, and never wait on a model to decide something a script can measure.

## 5. If you use subagents
One agent per SECTION, never per bar -- bars interlock through the carpet, the flow grid and the multisyl
distribution, so splitting by bar produces stanzas that do not cohere. Cap them: reasoning effort low or
medium, 4-6 passes maximum, hard stop after 3 failed passes on the same bar (the stuck rule), and give each
agent a DISJOINT allocation of places and an exclusive rhyme family so two sections cannot collide.
Their prompt must contain: the slot's real original lines read from the private file, with the instruction
never to quote or paraphrase them in any file or reply; the Phase A carpet; the beat sheet; the exact failing
checks; rules 1, 4, 5; the ratchet rule; and the keepers.
Their reply: bars only, in project format, plus a note under 120 words. No essays, no "this is excellent", no
parity claims. If an agent returns nothing usable once, do not relaunch it -- continue in this thread.

## 6. Definition of done, per section
`check_all` ALL PASS + `meaning_gate` PASS + `coherence_gate` PASS + `regression` PASS + `ml/judge` risk read
and explained (it ranks the 17 human gates; do not treat a low risk as good) + `ratchet` OK.
Song level: `songcheck` 0 problems, >=8 named places, no word above the level ceiling for repeats, at least
one code-switch per 4 bars in the hook, and the title landing where the song map says.

## 7. Stop and ask Joe, in one line, before writing
- every G2 call (a rare word: would a mate get it?), every truth flag ((invented)/(persona) vs documented),
- the still-unasked rule-8 questions: strict vegetarian detail, Horfield/BS7 as a name, everyday British brand
  names, invented cartoonish flourishes on true places,
- anything needing a place he has not confirmed, and any place the private notes mark as his to decide.

## 8. Report, then hand over to Suno
Report short: per section the bars, the numbers (carpet / syllables / density / multisyl / flow), the weakest
bar, the truth flags. Then the song-level state. Append every finding to `STATE.md` and
`writing/iteration_log.md`, and add a `toolkit/tests/` fixture for anything Joe rejects that the tools let
through -- that is how the gates get better.
Finally, rule 7: fill the Suno title, lyrics, style and exclude fields, screenshot, and STOP before Create
until Joe says yes. Leave the key out of the prompt.

## Last honest note on the GPU
The 5070 Ti buys volume, not judgement: it can generate hundreds of candidate bars for free and the filters
throw ~95% away, but it cannot hold this form and it cannot tell whether a joke lands. `ml/lora/` has a
writer-model recipe and a `preflight.py` that says when training is worthwhile -- with roughly one positive
block in the dataset, training now would be premature. The `ml/data/generated.jsonl` flywheel that this run
writes IS the thing that makes it trainable later, so log every candidate and its verdict.
