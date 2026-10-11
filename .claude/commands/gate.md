---
description: Run the quality gate on a draft or stanza file (measured floor + blind critic prompt). Required before showing Joe anything
argument-hint: <file with bars one per line, blank line between stanzas>
---
1. `python toolkit/quality.py $ARGUMENTS`. Any BELOW BAR block: rewrite, do not show.
2. Spawn ONE fresh-context critic agent (medium effort, output under 300 words). Prompt: Joe's bars (hook 5-8 and V1 1-4 from writing/full_draft_v16.md) mixed unlabelled and shuffled with the candidate bars; score every bar 1-5 harshly; list bars weaker than the best of the unlabelled set, filler, explained jokes, itinerary lists, bars anyone could write; one-line fix each; do not reveal or guess authorship. PASS = all candidate bars >= 4 and none flagged.
3. Write the five-line self-read per stanza (quality/gate.md gate 3).
4. Max 3 rounds. If still failing, tell Joe in one short message what blocks; show no draft.
