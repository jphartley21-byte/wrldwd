---
description: Stage 4. Three variants per bar in Joe's voice from his picks; Joe chooses per bar
argument-hint: <section>
---
Section: $ARGUMENTS. Inputs: approved beats, Joe's ticked ideas in `ideas/<section>.md`, chosen direction in `work/<section>/3_patterns.md`, voice/profile.md, voice/calibration.md (SOUNDS LIKE ME is the model, NOT ME is the warning), research/rhyme-bank.md. Keep any line Joe already wrote unless he asks to change it.
For each bar write 3 variants, labelled A/B/C, in a bloke-talking register (full clauses, his slang, flat delivery, the funny word on the rhyme). One end-sound plan per stanza with a one-line why. Mark facts (invented)/(persona) where needed.
Before showing ANYTHING, run the quality gate (quality/gate.md): per stanza write 3 candidate versions, `python toolkit/quality.py`, then a blind critic agent (fresh context, Joe's bars mixed in unlabelled); fix and repeat up to 3 rounds. Show Joe only stanzas that clear every gate; otherwise one short message on what blocks. Write `work/<section>/4_draft.md`. Do not run pass/fail loops. Optionally run `python toolkit/check_all.py --slot "<slot>" -` and add its notes as hints only. STOP: Joe picks A/B/C (or mixes) per bar.
