# Joe's "Worldwide" track: a Suno rap in the spirit of Pete & Bas "Mr Worldwide"

@STATE.md

## What this is
Joe (33, from Reading, lives in Bristol) wants a deadpan British world-tour rap at about 142 BPM, built from his REAL travel history, that sounds like HIM and works as good rap. Audience: Joe and his mates. Cheeky, no heavy swearing; deadpan drug/violence imagery is allowed (as in the original). Be honest and calibrated about quality; never call bars good without hedging. Keep replies short.

## Principles (revised 11 Oct 2026: the original is guidance, Joe's voice leads)
0. NEVER SHOW JOE A DRAFT THAT IS LESS THAN "AS GOOD AS IT CAN BE WITHOUT HUMAN INPUT" (Joe, 11 Oct 2026, hard guard, overrides every other instruction and every "show him options" habit). Joe is shown a draft ONLY when ALL of these are true:
   a. It has cleared `quality/gate.md`: measured floor from his own bars, a blind fresh-context critic round that scores every new bar >= 4 with nothing flagged filler / explained joke / itinerary / generic, and my written five-line read per stanza.
   b. I have kept iterating (rewrite, re-measure, re-critic) until a fresh critic round finds NOTHING further I can fix without Joe. "Good enough", "first pass", "proposal", "skeleton", "something to react to" and "let me know what you think" are banned reasons to show a draft. Do not hide weakness behind a label or caveat.
   c. What remains open genuinely needs Joe: his ear, a fact only he knows, or a taste choice between two equally strong options. List only those, briefly.
   Any bar that cannot reach that standard is CUT, not shown. A shorter draft that meets the standard beats a full-length one that does not.
   Cost cap: at most 6 critic rounds per stanza. If a stanza still cannot meet the standard, drop it and say in one line which section is missing and the one thing blocking it. Never show the failed text.
   The critic must be blind and harsh (Joe's own bars mixed in unlabelled; it is not told which are his). Keep gate results in work/<section>/ for audit, not in front of Joe.
1. JOE'S EAR IS THE ONLY GATE. Done = Joe says so. Tool output (toolkit/, /review) is a reference report: it may say a bar "differs from the original", never "fail", "reject" or "revert". Never rewrite a line Joe wrote or edited unless he asks. His edits in `writing/full_draft_v16.md` are the source of truth.
2. THE ORIGINAL IS A GUIDE. Use it for shape, flow, jobs of sections and technique ideas. Matching it is optional and never a reason to cut a line Joe likes. Never reproduce its lyrics in files or replies beyond isolated words; cite by line (Ch L1, V1 L12). Keep the lyrics file OUTSIDE the project; point tools to it with env `ORIGINAL_LINES` (optional).
3. VOICE FIRST, THEN CRAFT. Voice evidence = ONLY text tagged JOE in `voice/provenance.md` (agent-written lines are NOT his voice; never assume slang he hasn't confirmed in `voice/quiz.md`). Write in Joe's voice (`voice/profile.md`, `voice/calibration.md`), then craft-polish only syllables, rhyme tail and internal rhyme, keeping his key words. If they conflict, voice wins; log the craft note. Check lines with the 5-question card `voice/checklist.md`.
4. HUMAN IN THE LOOP, STAGE BY STAGE. Every stage writes a file under `work/<section>/` and STOPS for Joe: beats -> bank -> patterns -> draft -> polish -> review -> lock. Offer options (3 variants, tick-lists), never a single "answer". Joe picks.
5. EXHAUSTIVE BANKS, JOE PICKS INGREDIENTS. Joe does not want to read idea lists. Build exhaustive banks (`bank/`: rhymes, wordplay, slang, places, events, names) mostly by script, and let Joe browse/star ingredients (`bank/index.html`); drafts are built from his stars. Rhymes come from `toolkit/` and `research/rhyme-bank.md`, not from long reasoning.
6. TRUE OR FLAGGED. Facts come from `material/` (travel_history, place_specifics, joe_notes) or Joe. Anything else is "(invented)" or "(persona)" for him to confirm. No hobby/nerd material, real artist and brand names are allowed (Joe, 11 Oct), no heavy swearing, no instructional drug detail.
7. COMEDY = CHARACTER + WORDPLAY, carried by rhyme and flow, no setup-punchline gags (Joe's definition; see benchmark/comedy_theory.md).
8. COST. Keep it lean. Subagents only for `/bank`/`/research`, at most 4, medium effort, each told: "return at most 40 items; no rhyme-hunting loops; use the toolkit". Earlier unbounded writer agents burned 128k tokens each.
9. SUNO. v6 only; Joe signs in himself. Fill title/lyrics/style/exclude, screenshot, STOP before Create until Joe says yes. Settings in brief/suno_rap_rules.md.

## Folder map
- STATE.md: where we are, one screen. README.md: how to run the workflow.
- writing/: full_draft_vN.md (v16 = Joe's latest), iteration_log.md, older rounds. work/: per-section stage files. bank/: exhaustive CSV banks + index.html browser.
- voice/: profile.md, calibration.md, checklist.md. research/: rhyme-bank, places, events, craft, slang. material/: travel_history, place_specifics, place_sound_families, joe_notes (Joe's verbatim seeds).
- benchmark/: what the original does (reference). brief/: song_bible (partly superseded), suno prompts and rules. toolkit/: offline rhyme/flow tools (see toolkit/README.md). archive/: old stuff.

## Commands (`.claude/commands/`)
`/beats`, `/bank`, `/patterns`, `/draft`, `/polish`, `/review`, `/voice-check`, `/lock`, `/research`, `/media-notes`, `/write` (chains beats->draft with stops).

## Toolkit in one line (all advisory)
`python toolkit/rhyme_tools.py pron|rhymes|mosaic|families|check|syllmap`, `python toolkit/check_all.py --slot "<slot>" -` or `--song FILE`, `python toolkit/compare.py OLD NEW`, `python toolkit/bank.py find|stats|build|export-html`. Needs `pip install -r toolkit/requirements.txt`.

## Stuck rule (offered, not forced)
If Joe has rejected the same bars 3 times, or the same end-sound/theme twice, OFFER a pivot: park the best version in writing/contenders.md, then propose 3 fresh angles (different theme, rhyme family or structure) and let Joe pick.
