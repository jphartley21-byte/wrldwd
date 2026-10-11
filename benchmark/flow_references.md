# Flow and rhyme references (researched 9 Oct 2026). Tools installed are in toolkit/helpers.py.
| Reference | What we use it for | How |
|---|---|---|
| RhymePad (Kenneth Reitz, pip `rhymepad`, module `rhymes`) | Second-opinion rhyme scheme incl. multi-word rhymes (orange ~ door hinge), internal rhyme groups, per-line meter | `helpers.py rp -`. Rules: perfect = all phones from the last stressed vowel; slant = shared vowel run; reject vowel-only false pairs. US pronunciations: check end rhymes with `tails`. |
| Britfone (MIT, ~16k words, British IPA) | British end-rhyme check (bored/porno = ɔː; certain/curtains = ɜː) | `helpers.py uk WORD`, `helpers.py tails -`. Missing words show '?': judge by ear, add to rhyme_tools OVR. |
| wordfreq (Zipf scale) | Gate G2 automation: rare words (esky 1.9, jacksie 0.0) | `helpers.py freq -`; Zipf < 3.0 = flag. Cannot see idioms made of common words (gone for a Burton): G2 stays manual for phrases. |
| Datamuse API (free, no key, 100k/day non-commercial; RhymeZone's engine) | Rhyme / near-rhyme / sounds-like lists ranked by commonness | `helpers.py dm WORD rhy|nry|sl MINFREQ` |
| MCFlow corpus (Condit-Schultz 2017, 374 verses, rhythm on a 16-step grid) and Ohriner (Music Theory Online) | Norms: stressed syllables sit on strong 16th positions; gaps between accents are mostly 2 or 3 sixteenths; rappers drift off the grid on purpose | Manual: when a bar feels off, count its stresses on a 16-step grid; prefer 2-3 step gaps. |
| DeepRapper pipeline (Demucs + forced alignment / WhisperX + librosa beats) | Future: measure real flow from a Suno render or Joe's voice memo | Not installed (heavy). Set up once there are renders. |
