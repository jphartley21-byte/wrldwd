---
description: Stage 2. Build/extend the exhaustive banks (rhymes, wordplay, slang, places, events, names); Joe browses and stars INGREDIENTS, not lines
argument-hint: [build | add <topic> | find <query>]
---
Banks live in `bank/*.csv` (schema: id,type,text,items,sound,places,tags,source,joe_says_it,status) and are browsed in `bank/index.html` (offline, search/filter, star button, "Copy my stars").
- `build`: add new places/words to `bank/seeds.csv` (and `bank/ovr.txt` for pronunciations), then `python toolkit/bank.py build` (rhymes + sound-alike cut-ups, scripted) and `python toolkit/bank.py export-html`.
- `add <topic>`: extend a non-scripted bank (wordplay_idioms, slang, names_culture, places_events) with new rows, via a bounded subagent (max 4, 150-250 rows each, no lyrics, mark unverified) or directly. Use `status`=verified only with a source URL. `joe_says_it` stays blank until Joe answers voice/quiz.md.
- `find <query>`: `python toolkit/bank.py find --q X --type Y --place Z --rhymes W --joe y`. Show 10-20 best hits, not everything.
Joe stars ingredients in the HTML page and pastes the stars back; record them in `work/<section>/2_stars.md`. Never present long idea lists for ticking. Next: `/patterns` then `/draft`.
