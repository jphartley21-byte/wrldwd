# Detection test: how well the wrldwd tools detect rhyme schemes, internal rhymes and flow

**Date:** 14 Oct 2026.

**Where it ran:** a Linux cloud container on Python 3.13, with no LLM calls (`WW_SENSE=0`).

**Rule 4:** this file holds only bar numbers and isolated words from the original. Full outputs are kept outside the
repo, in the session's private scratch folder.

**What was tested:**
1. The **original**. The repo already holds ground truth for it, so each detector could be scored.
2. Joe's **travel draft**, which was pasted 14 Oct and is saved as `travel_draft.md` in this folder. Its ground truth is my
   own by-ear labelling and is unconfirmed.

**What was not used:** Joe's Hook 1-4 bars in `toolkit/tests/joe_hook_1-4.txt`, at Joe's instruction ("they're not
good"). Note that `calibrate.py`, `meaning_gate`, `ear`, `regression` and `forge` all use those bars as their positive
control. Their selftests passing is therefore **not** evidence of quality.

---

## 0. Headline

| Dimension | Best detector | How good | Main failure |
|---|---|---|---|
| End-rhyme scheme (original) | `rapfit.score` ≥ 0.50 | MCC 0.86, F1 0.93. **But it is in-sample:** its floor and its sung-pronunciation overrides were fitted to this song. | Every detector stays ≤ 0.46 F1 on V2 9-16. Truth itself is ambiguous on Hook 5-8 (see §1). |
| End-rhyme scheme, out-of-sample | `match.end_key` | MCC 0.75 (precision 0.95, recall 0.78) | It keys on the primary-stress vowel, so it misses rhymes carried by a secondary-stressed or unstressed final syllable. |
| Internal rhymes | No single tool | Recall vs precision trade off (§2) | Recall runs from 3/15 to 15/15 across tools. The high-recall layers are mostly noise. Two layers still link aɪ with eɪ (the glide bug Joe reported). |
| Flow | `flow_fit.sylls` for counting; `flow_fit` / `match` for conformance to the original | Counting: 73 of 74 bars exact | **Flow quality cannot be validated.** With the approved bars excluded, there is no good bar outside the original to test against. The template-free flow detectors do not separate the bars Joe rejected from the original. |

**The most important finding is a bug.**
- **What happens:** `ww/lex/banks/pron_overrides.json` stores brand and lexicon pronunciations under keys with the
  digits stripped:
  - A1 → **"a"** becomes "ay-one"
  - More4 → **"more"** becomes "more-four"
  - E4 → **"e"**
  - WWE → **"wwe"** becomes one syllable
- **Why it spreads:** every `ww` command loads these overrides into the shared dictionary. Affected commands: `ww check`,
  `ww flow`, `ww rhymes`, rapfit, the build, merge and ratchet stages, and slotcheck's syllable gate. Inside those
  processes:
  - **23 of the original's 74 bars** are mis-counted (the main counter: 50 of 74 exact, against 73 of 74 without the
    overrides; the 24th miss is bar 64, which is off either way).
  - `flow_fit` fails **30%** of the original's own bars.
  - syllmap's internal-rhyme links inflate by **+24%** (single-syllable) and **+67%** (multisyllabic).
- **Why the toolkit looks fine:** the toolkit CLIs (`check_all`, `match`, `flow_fit`, `calibrate`) never load the file,
  so they are unaffected. That is why calibrate still passes.

---

## Setup and fidelity
- **Fidelity of the pasted original.** It matches Joe's private file for every measured quantity:
  - `match.profile_of` against `benchmark/original_profile.json`: **0 differences** across all 10 slots and every
    per-bar field.
  - `flow_fit.sylls` against `flow_template.json`: 73 of 74 identical. Bar 64 is the known "would've" case; bars 10 and
    60 have no template.
  - The raw sha256 differs from `eval/freeze.json`, so the text is not byte-identical, for example in punctuation or in
    the repeated chorus lines 77-92 that the tools don't read.
- **`toolkit/calibrate.py`: CALIBRATION PASSED on Linux.** The original fits 74 of 76 of its own flow templates, all 6
  rejected stanzas are caught, and every selftest holds.
- **`python -m ww.cli selftest` aborts.** `argue_stage` needs `eval/_plan_v3.json`, which is git-ignored. The checks are
  built eagerly in one list, so none of them report. Running the 11 detection-related checks individually, **all
  pass**: bridge, grammar, calib, anticopy, pron, verify_det, slotcheck, flowaudit, earcheck, rhymeview, rapfit.
- **Platform:** the toolkit's private path (`Worldwide_private`) and ww's (`WORLDWIDE_PRIVATE`) differ only in case.
  They are the same folder on Windows but two folders on Linux.
- **Two run modes.** Because of the override bug, every test ran twice:
  - **clean:** the toolkit as its own CLIs run it.
  - **ww:** overrides loaded, as every `ww` command runs.
  Toolkit numbers below are from clean mode unless marked; rapfit, rhymeview, flowaudit and earcheck numbers are from ww
  mode (their production state).

---

## 1. End-rhyme schemes: the original against `MANUAL_SCHEME`
- **Truth:** by-ear letters for all 10 slots. Joe corrected Hook 1-8; the rest was annotated by the assistant.
- **Pairs:** 274 bar pairs within slots, of which **137 rhyme**.
- **Baselines (watch these):** calling every pair a rhyme scores F1 **0.667**. Shuffled letters score F1 0.63. So F1
  alone flatters weak detectors; MCC is the fair column.

| Detector | P | R | F1 | MCC | Hook 1-8 F1 | Exact slots |
|---|---|---|---|---|---|---|
| `rapfit.score` ≥ 0.50 (ww) **in-sample** | 0.947 | 0.905 | 0.925 | **0.855** | 0.80 | – |
| `match.end_key` (the profile's scheme) | 0.947 | 0.781 | 0.856 | **0.749** | 0.40 | 3/10 |
| `match.best_end` ≥ 0.78 (the grader) | 0.762 | 0.891 | 0.822 | 0.62 | 0.80 | – |
| `rhymeview` grader clusters (ww) | 0.781 | 0.883 | 0.829 | 0.641 | 0.80 | 4/10 |
| `craft_scan.loose_families` **tuned to this truth** | 0.733 | 0.883 | 0.801 | 0.574 | 1.00 | 5/10 |
| RhymePad (`helpers.py rp`) | 0.894 | 0.555 | 0.685 | 0.529 | 0.50 | 1/10 |
| `craft_scan.families` | 0.884 | 0.555 | 0.682 | 0.519 | 1.00 | 3/10 |
| `rhyme_tools check` end-key | 0.672 | 0.299 | 0.414 | 0.184 | 0.55 | 1/10 |

The grader's MCC is estimated from its clean run; with the ww overrides loaded it scores F1 0.845, MCC 0.672.

**Stored claims reproduced:**
- `match --selftest` 12/12.
- rapfit AUC **0.932** against the grader's **0.792** (claimed 0.931 / 0.792).
- `loose_families` 5/10 exact slots; pair agreement 78% (claimed 76%).

**Not reproduced, now out of date:** STATE.md says rapfit is "blind to moi/dance and Jamaica/Spain". Today it gets all
of Hook 9-16 right, because the `SUNG` overrides were added after Joe's ear corrections. That is in-sample by
construction.

**Where the detectors fail:**
- **V2 9-16 (bars 69-76):** every detector stays ≤ 0.46 F1. The B group mixes "backhand", "round" and "Smackdown" with
  bar 75 as a singleton; the grader's AUC there is 0.63 and rapfit's 0.50.
- **V1 17-24 B group (bars 37-40, the "-ed him" 3-syllable tails):** rapfit misses 4 of 6 pairs. The grader instead
  merges the A and B groups (12 false pairs).
- **Hook 5-8, a truth problem rather than a detector one:** `MANUAL_SCHEME` says ABBA, but Joe called all four ends
  "near perfect rhymes", and the measured carpet is 6/6. Every detector that hears AAAA is "wrong" by the annotation.
  **Joe should decide what Hook 5-8's truth is.**
- **Hook 1-4:** `match.end_key` reads "abcc", because it keys on the last *primary*-stressed vowel and so misses the
  eɪ-əʊ tails. The pair-graders get it.

---

## 2. Internal rhymes: the original against Joe's ear notes
**Fixture.** 15 links Joe identified in STATE.md:
- the eɪ family in bars 1-4
- trans/at/lan ~ man, and -tic ~ chips (bars 6-8)
- whip / stick / chick (bar 13)
- meat / beach / chicas and out / house (bars 15-16)
- num(bers) ~ running / up / money (bar 18)

**Must-not links:** eye ~ ba and eye ~ plain.

**Spot-check.** 10 random links per detector, judged by me (assistant-judged, flagged as such): did it plausibly sound like
a rhyme?

| Detector | Recall /15 | Must-not fired | Links found | Spot-check plausible | Verdict |
|---|---|---|---|---|---|
| `rhymeview` vowel colours + echo marks (ww) | **15** | **1** (eye~plain) | 886 | 3/10 | Finds everything; colours whole slots, so most links are weak. |
| `rhyme_tools syllmap` single-syllable | 9 | 0 | 701 (clean) / 872 (ww) | 7/10 | Usable; no distance limit, so it links across whole slots. |
| RhymePad groups | 9 | 0 | 392 | 5/10 | Medium. |
| `match.internal_density` (traced) | 7 | **1** (eye~plain) | 259 | 4/10 | aɪ/eɪ glide false positives. |
| `rhymeview` multi-syllable chains (ww) | 7 | 0 | 35 | **10/10** | Precise, but the original's count is at chance (25 vs 22.8 shuffled). |
| `rhyme_tools check` same-vowel pairs | 6 | 0 | 56 | **9/10** | Precise, but within-bar only. |
| `craft_scan.internal_pairs`, uncapped | 6 | 0 | 117 | 4/10 | Function-word noise. |
| `rhyme_tools syllmap` multisyllabic runs | 5 | 0 | 249 (clean) / 416 (ww) | **0/10** | Noise: function words, 4-9 bars apart. |
| `craft_scan.internal_pairs`, cap 2 (as shipped) | 3 | 0 | 85 | 5/10 | The cap throws away real pairs (whip/stick/chick: 1 of 3). |

- **Missed by almost everything:** -tic ~ chips (only rhymeview's weak-ɪ joiner gets it), house ~ out across bars
  15-16, and luego ~ plain.
- **Glide bug still live:** rhymeview's vowel-colour layer correctly leaves "eye" uncoloured. But its older end-echo
  layer still marks "eye" as an echo of the eɪ end group, because it uses vsim ≥ 0.9 and aɪ~eɪ scores 0.93. The
  draft shows the same thing ("I'll ~ say", bar 76).
- **Devices (`ear.py`):** the T_L drum across bars 23-24, the pivot word at 23-24 and the "him" ×4 accumulation in bars
  37-40 are all found. These are its own selftest targets, so the result is in-sample. Drum-or-echo in **10 of 19**
  quads reproduces the stored claim.
- **Signal against chance:**
  - Positional assonance (same vowel on the same 16th step in neighbouring bars): **0.28 against 0.13** shuffled
    (claimed 27% vs 15%). Real signal.
  - Chains: 25 against 22.8. No signal.

**Still not labelled anywhere:** the 7 internal rhymes Joe hears in bars 33-36. Marking them would double this fixture.

---

## 3. Flow: the original

### Syllable counters (clean)
Measured against the stored template count. That count is itself a CMU text count; no audio syllable count exists.

| Counter | Exact |
|---|---|
| `flow_fit.sylls` | 73/74 (bar 64) |
| `rhyme_tools check` | 69/74. Out-of-vocabulary words are dropped: bar 76 counts 3 instead of 12, and bars 16, 52 and 55 also miss. |
| `flow_check.bar_profile` | 68/74. Hyphenated words get +1 (bars 5, 19, 54, 73), and bar 72 also gets +1. |
| `phon.syllables` | 68/74 |

- All four counters agree on only **64 of 76** bars.
- **With the ww overrides loaded,** `flow_fit.sylls`, `flowaudit` and `bridge.syllable_count` drop to **50/74**, all
  because of "a", "more" and "e". `phon` and `rapfit` rise to 71/74: the same file also carries good loanword entries,
  and britfone shields them from the bad ones.

### Self-consistency
This is circular: the template was written by the same code that reads the bars.
- Clean, `flow_fit` passes the original 74/76, and `match --slot` passes every slot.
- The `flowaudit` baseline mostly reproduces, but two rates have drifted:
  - grid clashes: 0.47 stored, 0.39 now
  - 4+ unstressed syllables in a row: 0.014 stored, 0.068 now

### Discrimination
The groups: the original (76 bars), the 6 stanzas Joe rejected (44 bars), and 4 bars Joe flagged specifically for
flow (the "Cop in whites" couplet, "Two glasses…", "No names…").

| Detector | Original | Rejected | Flagged for flow | Separates? |
|---|---|---|---|---|
| `flow_check` stress clashes | 1.47 | 1.11 | 1.75 | No (rejected is *lower*) |
| `flow_check` longest weak run | 2.28 | 2.00 | 1.50 | No |
| `flow_check` rare mouth-shape joins | 0.32 | 0.34 | 0.50 | Weakly (fires on the Cop bar it was built for) |
| `flow_check` consonant pile-ups | 1.01 | 1.18 | 1.25 | Weakly |
| `earcheck` hard joins (ww) | 0.21 | 0.48 | 0.50 | **Yes, about 2×** |
| `earcheck` jammed stresses (ww) | 0.49 | 0.52 | 0.25 | No |
| `flowaudit` flags per bar (ww) | 1.54 | 1.86 | **0.50** | No: flagged bars get fewer flags than the original |
| `flow_fit` FAIL rate | 0.00* | 0.57 | 0.75 | Only "differs from the original" |
| `flow_fit` strong/weak pattern % | 0.97* | 0.78 | 0.63 | Only "differs from the original" |
| `match.py` per-bar FAIL | 0.00* | 0.30 | 0.75 | Only "differs from the original" |

\* The original is scored against its own template, so these entries are circular.

- **Template detectors measure distance from the original, not flow quality.** Any rewrite fails them, and without good
  non-original bars, "rejected because bad" can't be told apart from "rejected because different". Joe's "Two glasses,
  cold lager, back road corners" (STATE: "shit flow") **passes `flow_fit`** (90% pattern). It fails `match` on the
  stress grid, and `flow_check` gives it 4 clashes, the highest of any bar tested.
- **Bugs reproduced from reading the code:**
  - `flow_fit.WEAKFN` lacks contractions: "he's wrecked" reads as two strong syllables.
  - `blockcheck`'s end column prints the bar's first letter instead of its end sound.
  - `flow_fit`'s CLI scores a `== Slot` header as bar 1.
  - Bar 5 counts 9 syllables in `flow_check` against 8 in the template.

---

## 4. The travel draft
**Truth for the draft is my by-ear labelling and is unconfirmed.** It equals `MANUAL_SCHEME` (the draft was written to
those frames) except:
- Hook 5-8, which I hear as AAAA (quarry/sorry/lorry/Corrie).
- "bowing" (bar 22), which is ambiguous.

The draft's end rhymes are mostly perfect one-syllable rhymes, so the detectors score *higher* than on the original:
grader F1 0.956, rhymeview 0.954, `match.end_key` 0.928, RhymePad 0.901, rapfit 0.875. The all-rhyme baseline is 0.68.

**Errors specific to the draft:**
- **Secondary-stress rhymes are missed.** "torchlight" (bar 30, against white/night) is missed by `match.end_key`,
  `rhyme_tools check`, rapfit and rhymeview. "King's Day / anyway / holiday / Saturday" (bars 33-36) is missed by `end_key`, which keys on
  the primary stress.
- **eɪ ≈ ɛ merges.** rapfit and `loose_families` merge "-day" (bars 33-36) with "red / dead / instead / bed" (bars 37-40).
  The grader, rapfit and rhymeview pair "gate" (bar 15) with "bread / said / head".
- **The unstressed -ing tail.** "swimming" (bar 44) is paired with waiting/paying/saying by the grader, rhymeview,
  `rhyme_tools check` and `craft_scan.families`. rapfit correctly refuses it, which is what it was built for.
- **The UK vowel of "sure"** (bar 53, against roar/four/door) is missed by `rhyme_tools check`, `loose_families`
  and RhymePad, because CMU gives /ʊr/.

**Internal rhymes:** 24 assistant-labelled links, such as tyre~fright, swore~roar, shakes~awake, Seven~Elephant and
stayed~cable.
- Recall is highest for `craft_scan` uncapped (22/24), rhymeview colours (22/24), syllmap single (19/24) and
  `craft_scan` cap 2 (19/24).
- Chains find 1/24: the draft's internal rhymes are single syllables, not vowel sequences.
- The glide false positive appears again, "I'll ~ say" (bar 76), from `match.internal_density` and rhymeview.

### The draft against the original, using the tools that do discriminate

| Measure | Original | Draft |
|---|---|---|
| Bars on the original's audio frame (`flow_fit`) | 74/76 (its own) | **1/76** |
| Bars more than 1 syllable off the original's bar | – | 13/76 (mean +0.5 syllables per bar) |
| `check_all` problems per slot | 0 | 8 / 6 / 14 / 14 / 15 / 18 / 12 / 21 / 13 / 16 |
| Strong end rhymes (rapfit ≥ 0.80) | 35 of 69 paired | 66 of 70 paired |
| Positional assonance (vs shuffled) | **0.28** (0.13) | **0.15** (0.10) |
| Drum-or-echo quads | 10/19 | 6/19 |
| Chains (vs shuffled) | 25 (22.8) | 25 (17.9). The counter rates the draft *further above chance* than the original. |
| `songcheck` | PASS | 6 problems: two bars outside the length band, device rate, places and local words |

**Reading it:** the draft out-rhymes the original on the end-rhyme detectors, because perfect monosyllables are what
those detectors reward. It loses on the measures tied to delivery: the audio frame, positional assonance and devices.

---

## 5. Bugs and defects found (none fixed: reported only)
1. **P1: `pron_overrides.json` digit-stripped keys** (A1 → "a", More4 → "more", E4 → "e", WWE → "wwe"). They are marked
   "reviewed / phonetician agent", and they corrupt syllables, stress and rhyme for every `ww` command (see §0). Also
   note "chicas" → SH IY1 K AE2 Z ("chic+as": the wrong first consonant).
2. **The aɪ/eɪ glide (vsim 0.93) still links eye/I'll/like with eɪ words.** This happens in rhymeview's end-echo marks
   and in `match.internal_density` (threshold 0.85).
3. **`ww selftest` is all-or-nothing:** one missing git-ignored plan file hides all 31 results.
4. **The private-path case mismatch** between the toolkit and ww breaks on Linux and macOS.
5. **`flow_fit.WEAKFN` lacks contractions** ("he's" reads strong), even though its comment says it is identical to
   `flowaudit.FUNC`.
6. **`blockcheck`'s end column** passes the line, not its end key, to `_k`.
7. **`flow_fit`'s CLI reads `==` headers as bars.**
8. **The `flowaudit` baseline has drifted** on clash (0.47 → 0.39) and gap ≥ 4 (0.014 → 0.068).
9. **rhymeview's skeleton guard treats hyphenated words as one word.** "duck-duck" counts as one, so a 4-word run of the
   original appears in the in-project skeleton map (bar 60). I kept that file **out of the repo** for that reason.
10. **`rhyme_tools check` and `phon` drop out-of-vocabulary words.** Bar 76 counts 3 syllables of 12; "Federali",
    "Fumez" and "chicas" are unmeasured in clean mode.

## 6. Verdict per tool
- **Reliable:**
  - `flow_fit.sylls` (clean) for syllable counts.
  - `match.end_key` for end rhymes on stressed syllables, with high precision.
  - `rhyme_tools check` same-vowel pairs and rhymeview chains as precise, low-recall internal-rhyme finders.
  - Positional assonance as a delivery signal that separates the original from the draft.
- **Useful, in-sample:** rapfit and `loose_families` (both fitted to `MANUAL_SCHEME`); `ear.py` devices (fitted to the
  original's couplet and quad).
- **Diagnostic only:**
  - The grader (`best_end`), rhymeview colours and syllmap single-syllable: high recall, low precision.
  - `flow_fit` / `match` / `flowaudit` as flow *quality* checks: they measure distance from the original.
  - `earcheck` hard joins: the only template-free flow check that separated the groups.
- **Broken or noise:** syllmap multisyllabic runs (0/10 plausible), `craft_scan.internal_pairs` with cap 2, the chain
  *count* as a quality measure, `rhyme_tools check` end-key families (MCC 0.18), and anything run inside `ww` until
  bug 1 is fixed.

## 7. Needs Joe's ear
1. **Hook 5-8's truth:** ABBA (as annotated) or AAAA (as Joe described it)? This flips several detectors' scores.
2. **Bars 33-36:** mark the 7 internal rhymes Joe hears.
3. **The draft labels in §4,** especially "bowing" (bar 22) and "Amsterdam" (bar 75): rhyme or not?
4. **Flow validation needs good bars that aren't the original.** Without them, no flow detector can be shown to measure
   quality rather than distance from the original. A Suno render with Joe's verdict per bar would provide them; the
   `audio/my_song.mp3` question is still open.

---

## 8. Update (later the same session): fixes applied and the redraft
**Fixed in the toolkit:**
1. `ww/lex/pron.py`: persisted overrides now fill gaps only. A cmudict word keeps its dictionary pronunciation.
   - 57 corrupt entries were removed from `ww/lex/banks/pron_overrides.json`, among them A1→"a", More4→"more", E4→"e", Film4→"film" and Jet2→"jet".
   - "chicas" and "WWE" were corrected.
   - Inside `ww`, the syllable counters now agree with the template on 73/74 bars (they were at 50/74), and `flow_fit` fails 0% of the original's bars (it was failing 30%).
2. The aI/eI glide:
   - `match.internal_density` now needs an identical vowel.
   - rhymeview's end-echo layer now needs vsim ≥ 0.999.
   - eye~plain is no longer linked.
3. `ww selftest` runs each check on its own. 30/31 pass; the failure is a git-ignored plan file that isn't in this clone.
4. `toolkit/private_path.py`: one resolver for the private original (it was split by the Worldwide_private / WORLDWIDE_PRIVATE case difference). `make_original_map.py` no longer hard-codes `C:\Users\Joe`.
5. `flow_fit.WEAKFN` now includes the contractions.
6. `blockcheck`'s end column now shows the end key.
7. The `flow_fit` CLI skips `==` headers and a BOM.
8. The rhymeview skeleton guard counts hyphenated words as their parts.
9. Pronunciations added for the original's out-of-dictionary words (chicas, federali, fumez, wwe, smackdown), plus shirty and proost.

**Benchmarks rebuilt with the repo's own commands:** `flow_fit --add-weak/--add-rhyme-pos`, `match.py --build`, `flowaudit.baseline`.
- They changed only the bars the fixes touch: contractions are now weak, and Federali, Fumez and WWE are corrected.
- CALIBRATION PASSED afterwards (74/76 flow templates).

**Supply:** `local_words.txt` gained kaixo (Bilbao 2023), hoi and proost (Rotterdam 2023).

**Finding:** the meaning gate's song-level caps (pronoun endings ≤ 4, "And" openers ≤ 2) fail the original itself, which has 8 and 4.

**Redraft:** `travel_draft_v5.md`, with the Suno version in `song_v5_suno.txt`.

| Measure | Pasted draft | v5 | Original |
|---|---|---|---|
| Bars on the original's audio frame | 1/76 | 74/74 | 74/76 |
| By-ear scheme pairs heard (grader or rapfit) | – | 136/137 | 132/137 |
| check_all problems | 136 | 37 | – |
| songcheck | 6 problems | PASS | – |
| phrase_audit | – | PASS | – |
| Character cap | over | within | – |
| Meaning gate | – | 3 "-in" device tails + pronoun cap | fails the same cap |
