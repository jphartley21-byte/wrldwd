---
description: Stage 6. Advisory report on a draft or section: what it says, voice, craft, nearest original job, flow. Never fails or rewrites
argument-hint: <draft file or slot, e.g. writing/full_draft_v16.md or "V1 17-24">
---
Review $ARGUMENTS. Main thread. Advisory only: report, suggest, never reject, never rewrite Joe's lines.
1. WHAT IT SAYS: one plain line per bar; flag bars that say little.
2. VOICE: run the /voice-check logic (voice/profile.md, voice/calibration.md). 
3. CRAFT HINTS: `python toolkit/check_all.py --slot "<slot>" -` or `--song FILE` (differences from the original are information, not errors; set ORIGINAL_LINES only if available); `python toolkit/rhyme_tools.py syllmap`. Say what is working (internal rhyme, multis, sound-alikes) as well as gaps.
4. JOB CHECK (hint): the original line's job (greeting+place, register flip, cashed idiom, list, closer) vs ours; note orphaned words.
5. FIVE-QUESTION CARD (voice/checklist.md) per stanza in one line each, and the weakest bar with one fix direction. Never claim parity with the original.
6. If this is a revision: `python toolkit/compare.py <old> <new>` for gains/losses (information only).
Report concisely: keep / tweak / cut per bar as a suggestion; open questions for Joe. Append 3 lines to writing/iteration_log.md. If Joe rejects a stanza, note it in voice/calibration.md (NOT ME) with his reason.
