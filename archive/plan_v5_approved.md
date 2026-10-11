# Plan v5: Joe's "Worldwide" track built from his real travel history, with a benchmark-and-critic loop

## Context
Draft v2 ("BS7 Worldwide") was a long way off: blocks were 4 bars where the original runs 8-16, it had almost no internal rhyme, and much of the material was hobby stuff (Warhammer, gym stats) or invented gags. Joe wants to rethink: drop the nerd stuff and cringe specifics, base the song on his actual travel history over about 15 years, understand the original fully (Genius, reviews, YouTube reaction transcripts), and then run every draft past a critic that compares it with the original until it is as good.

## Decisions so far
- **Content:** true travel places and events only. No nerd/hobby material (Warhammer/D&D, gym numbers, pull-ups). Any line not backed by the travel history is flagged "invented" and Joe decides. Some cartoonish drug/violence imagery is allowed in the original's deadpan way; swearing stays cheeky, not heavy. Audience: Joe and mates; real names and places allowed (names list shown to Joe before generating).
- **Beat (from the analysis Joe pasted):** 142 BPM, G minor with dorian colour, straight 8th-note groove, deep sub bass, dark warm low-heavy mix, low baritone register (E3-G3), i-V minor harmony with a major-chord lift in the bridge, sparse dark intro building to a full beat, dense loud master, short abrupt ending. Genre/instrument/vocal filled in as UK drill-style rap, gruff deadpan baritone rapper, south england accent. I do not capture or download the YouTube audio (the permission check blocked it, and Joe supplied the analysis).
- **Suno:** v6 only (V5.5 retired). Style box about 1,000 chars, lyrics 5,000; Variety 0, Style Influence about 70, Weirdness about 30, Vocal Gender male; test full-time 142 and half-time 71. Joe signs in himself; I stop before Create.
- **Travel-history sources approved by Joe (all read-only):** the Seagate drive (the main store), Google Photos in Joe's Chrome, Gmail booking confirmations, Google Calendar, Strava; Notion already mined. Joe also allows me to look at some images to identify events; I skip faces and people and report only place, date and event type. Nothing is moved, shared or uploaded; no email text is kept beyond trip facts.
- **Drive route chosen by Joe:** Paragon HFS+ trial, plus installing small metadata tools.
- **Agent reliability rules:** never set a `model` override; put every input inline or in the session folder (not under ~/.claude/plans); agents write output within their first minutes; if an agent shows no tool use or tokens after 3-5 minutes, stop and respawn or do it myself. Agents refuse browser work while plan mode is on (the Photos agent only returned a plan), so the browsing agents (Photos in Chrome, Genius, YouTube) run, or are resumed, right after this plan is approved.

## Part 1: Rebuild the travel history
**Findings so far:** Drive and local folders hold no travel photos (screenshots and research images only). No Google Photos connector exists. The Seagate BUP Slim (about 1 TB, healthy) has a 931 GB hidden partition with GPT type Apple HFS+, no drive letter, so Windows can't read it. Joe says it is all travel photos and videos. Winget has `Paragon.HFS+` (HFS+ for Windows, commercial with trial), `Catacombae.HFSExplorer` and `DiskInternals.LinuxReader` (free, copy-out only), and `OliverBetz.ExifTool`. This PC has Python 3.13 with numpy, scipy and Pillow; no Java, no WSL, no exiftool.

Steps (run after approval):
1. **Mount the drive read-only.** `winget install Paragon.HFS+` (Joe approves the admin prompt; a reboot may be needed). Set the volume to read-only in Paragon if the option exists, otherwise never write. Confirm the drive letter and list top-level folder names only. If the volume is a Time Machine backup (Backups.backupdb) or won't mount (encrypted or dirty journal), stop and tell Joe the options (free copy-out tools or a Mac).
2. **Install metadata tools** (Joe approved): `winget install OliverBetz.ExifTool`; `python -m pip install pillow-heif reverse_geocoder` (offline place names, no upload).
3. **Scan, read-only** with a script in the session folder (`scan_drive.py`): walk the drive (skip hidden/system), read capture date and GPS from every photo and video (exiftool for videos and HEIC), never copy or open pixel content, then cluster by date and GPS into trips (consecutive days away from home area, Bristol/Reading), reverse-geocode offline to country and place, and write `drive_timeline.csv` plus per-year counts. Folder names are used as hints (e.g. a folder named for a country or year). Photos without GPS keep their folder name and date range.
4. **Google Photos in Chrome** (Explore agent, resumed after approval): Joe's logged-in Chrome (Browser 1 is the one on this computer; if the account isn't Joe's, stop and ask). Places list with counts, album titles and date ranges, timeline year by year 2011-2026, info panel only for date and location captions, images viewed only when event type is unclear, faces skipped, no clicks on anything that edits, shares or deletes. Default: overnight trips included, day trips flagged low confidence, shared-with-Joe albums listed but flagged.
5. **Bookings, calendar, fitness** (Explore agent): Gmail search for flight, ferry, hotel and festival confirmations (destinations and dates only), Calendar past trips, Strava activity locations by year.
6. **Merge** into `travel_history.md` in the session folder: year, places, what happened, source, confidence, anecdote hook. Then interview Joe: pick the 10-15 best places, mark off-limits ones, and give the true story or detail behind each (what went wrong, what was funny), because labels won't give punchlines.

## Part 2: Benchmark the original completely
- Done: `original_technique_map.md` (line-by-line map from the lyrics Joe pasted: chains, X lines, hinge, mosaic rhymes, echoes, number ladder, lexical sets, bathos, length variance).
- Agents already launched: (a) Genius annotations (browser route, since WebFetch is blocked for genius.com) plus reviews and articles; (b) YouTube reaction/breakdown transcripts and comments. If they only return plans because of plan mode, resume them after approval with the same briefs.
- Merge into `benchmark_rubric.md`: each technique with a definition, where the original uses it, a measurable target, and what reviewers or reactors say makes it land. Scoring 0-3 per criterion with the original defined as 3. Criteria: chain length and coverage, X lines, hinge lines, rhymes per bar, mosaic/cut-up rhymes, echo-with-twist callbacks, number ladder, lexical-set metaphor, bathos, line-length variance, joke density, hook/bookend, escalation arc, voice tics, no AI-tell words.
- Optional literal no-copy check: Joe saves the pasted original lyrics to a file in the session folder himself (I won't write them to disk); otherwise I check by hand.

## Part 3: Draft, critique, redraft until it matches
- **Writer** (me; optionally 2-3 writer agents on separate sections): block-first method. Pick 6-7 sound families, build word banks from `travel_history.md`, write 8-16-line monorhyme chains with one X setup line, a hinge into the next block, two rhymes per bar where possible, varied line lengths, echo-with-twist, a number ladder, one lexical-set metaphor, bookend hook. The hook must not copy the original's "greeting to the lads in place" template.
- **Critic agent** after every draft (inputs: `benchmark_rubric.md` and the draft file, no model override): scores each criterion 0-3 against the original, quotes the draft's 8 weakest bars, lists missing techniques with concrete rewrite targets, flags AI-tell words, invented/cringe/nerd lines, and any phrase that echoes the original. A **voice-check** reads Joe's nine Suno lyrics and says whether Joe could have written it.
- **Redraft** only the weak blocks, keep the best ones (`draft_N.md` files). Repeat.
- **Stop when:** every criterion is at least 2 with none below, the critic finds no weak bars in two consecutive rounds, no invented/cringe flags remain unresolved, and Joe approves on his own read-through. Cap at 8 rounds, then check in with Joe.

## Part 4: Suno
- Style prompt from the analysis, e.g. `UK drill rap, 142 BPM, G minor, i-V minor harmony, deep sub bass, tight straight-8th programmed hi-hats, dark warm low-heavy mix, gruff deadpan baritone male rapper, south england accent, sparse dark intro building to full beat, major-chord lift in the bridge, dense loud master, short abrupt ending`; exclude `singing, melodic hook, autotune, choir, female vocals`.
- Structure tags per the analysis (intro, build, verse, pre-chorus, breakdown, chorus, bridge, final chorus, outro, end). Around 60 lyric lines or fewer. Line length guided by Joe's tap count: how many taps does one hook line take (4 = one bar per line, 8 = half-time)?
- Open suno.com/create in the built-in browser (it timed out earlier and is logged out) or Joe's Chrome if he's signed in there. Fill title, lyrics, style, exclude; screenshot; ask for a clear yes; then Create. At least 2 generations per variant (142 and 71 half-time), judge by ear with Joe, change one variable at a time.

## Verification
- Every claim in the lyrics maps to a row in `travel_history.md` or is flagged invented and approved by Joe.
- Final critic round: no criterion below 2, no weak bars, no AI-tell words, no echo of the original.
- The drive is never written to (check no write access was used); no media is copied; only dates, GPS-derived place names and folder names are recorded.
- Suno form screenshot before Create; results reported only when they appear in the library.

## Risks
- Paragon HFS+ may fail on an encrypted, dirty or Time Machine volume; fallbacks are the free copy-out tools or a Mac.
- Photos from before about 2014 may lack GPS; folder names and dates carry those trips, so the interview matters.
- Genius and YouTube need the browser pane or Chrome with site approvals; if blocked, Joe pastes annotations or transcripts.
- Photo content is private: metadata first, images only for unlabeled events, faces skipped.
