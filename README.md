# wrldwd: writing Joe's "Worldwide" rap

A human-in-the-loop, AI-assisted workflow for writing a deadpan British world-tour rap from Joe's real travels, in Joe's voice.

## The funnel (one command per stage; each writes a file and stops for Joe)
1. `/beats <section>`: one line per bar of what it says. Joe edits/approves.
2. `/bank`: exhaustive banks (rhymes, wordplay, slang, places, events, names). Browse `bank/index.html`, star ingredients.
3. `/patterns <section>`: what your stars have in common (sounds, places, devices), gaps. Pick a direction.
4. `/draft <section>`: 3 variants per bar in Joe's voice. Joe picks per bar.
5. `/polish <section>`: voice-preserving craft pass with one-line reasons. Joe accepts/rejects.
6. `/review <section>` and `/voice-check <draft>`: advisory reports only.
7. `/lock <bars>`: keep what Joe likes (calibration + keepers).
Support: `/research <topic>`, `/media-notes <trip>` (details from photos/videos).

## Principles
The original song is guidance, never a gate. Joe's voice and ear decide. Tools only report. See CLAUDE.md.

## Setup
`pip install -r toolkit/requirements.txt` for the toolkit. Optional: `export ORIGINAL_LINES=/path/to/original_lines.txt` (kept OUTSIDE the repo).
