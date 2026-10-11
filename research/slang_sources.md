# UK slang sources: what exists, access, licence (checked 11 Oct 2026)
The repo's own library: bank/slang.csv (+ mundane.csv, names_culture.csv, register_stiff.csv). Grow it with every correction from Joe (e.g. "certi" = certified, authentic, cool).
Workflow: `python toolkit/glossary.py FILE` lists words needing a gloss; resolve each (Joe first, then sources below); add to bank/slang.csv; paste glosses into every critic prompt for ALL stanzas.

| Source | What it is | Access / licence (as far as checked) | Fit |
|---|---|---|---|
| Urban Dictionary | huge crowd-sourced slang, noisy, often rude/wrong | Unofficial lookup API (api.urbandictionary.com/v0/define?term=X) works per-word with no key; bulk data is now sold under a commercial licence (urbandictionary.biz/data); older community dumps exist (Figshare corpus 1999-May 2016, Hugging Face daspartho/urban_dictionary, a Mendeley subset) with unclear licences | Best for ON-DEMAND single-word lookup of current slang. Do not scrape in bulk or commit dumps. Treat definitions as hints; vote counts and Joe decide. |
| Wiktionary (via kaikki.org / wiktextract JSONL) | structured, citable, tags like "UK", "slang", "British" | Wiktionary text is CC BY-SA; kaikki.org offers downloadable JSONL and asks for attribution (cite Ylonen 2022 LREC). Could filter to UK/slang entries into a compact CSV with attribution. | Best for a committed offline library (attribution needed). |
| Green's Dictionary of Slang (greensdictofslang.com) | the large historical slang dictionary | Free basic entries online; citations/fuller search historically subscription; no stated API or reuse licence | Good for checking etymology by hand; do not bulk copy. |
| Genius annotations | song-specific explanations (e.g. the original's lines) | Per-page, user-contributed; used by the repo in benchmark/ (paraphrased) | Best for the original's own references; Joe pastes when needed. |
| Cockney rhyming slang / regional lists | small curated lists | various | Add selected entries to bank/slang.csv by hand. |

## Status 11 Oct 2026 (network opened by Joe)
- Urban Dictionary: per-word endpoint works from the sandbox (`toolkit/slang_lookup.py`). Quality is mixed: right for certi/wagwan/guap/zilch, wrong or junk for Federali and "deck"; Wiktionary's top sense for "plod" was the wrong one. Always treat as HINTS; Joe's corrections and the lyric context decide.
- Wiktionary: the live API rate-limits this shared network address (HTTP 429); kaikki.org works and serves per-word and full-dump data. `toolkit/import_wiktionary_slang.py` stream-filters the 3.3 GB dump into `bank/slang_wiktionary.csv` (attribution: `bank/SLANG_WIKTIONARY_ATTRIBUTION.md`).
- Tools: `python toolkit/slang_lookup.py WORD...`, `python toolkit/glossary.py FILE --lookup`.

## Network note (earlier, now resolved)
From the Claude cloud sandbox these hosts returned HTTP 403 (blocked by the environment's network policy) on 11 Oct 2026: api.urbandictionary.com, en.wiktionary.org, kaikki.org. To use them, Joe adds them under Allowed domains in the environment's Network access settings (cloud environment menu -> Edit), or runs lookups on his own machine. Until then: Joe's corrections + bank/slang.csv are the library.
