# How lyricists actually write, and where the repo's writer differs (14 Oct 2026)

Joe asked two things: compare the writer with songwriting and rap best practice, then check his assumption that rappers "get an idea, write the hook, feel the flow, work out the rhyme words, fill the gaps". Sources were mostly interviews reproduced second-hand; strength is marked. Nothing found for Kendrick, Nas, Rakim, Black Thought, Pete & Bas, or UK rappers other than Mike Skinner. Many web hits were SEO pages and their statistics were dropped.

## 1. Craft sources
| Practice | Support | Source |
|---|---|---|
| Rhyme is a roadmap for the ear (listeners cannot see line breaks); form should match the idea (Pattison's stable / unstable prosody) | Solid | [Writer's Digest](https://writersdigest.com/wd-books/writing-better-lyrics-interview), [Berklee](https://online.berklee.edu/takenote/?p=18154) |
| Object writing: ~10 minutes of sensory detail on one object, senses not feelings, as a source of concrete words | Solid | [Writer's Digest excerpt](https://writersdigest.com/wd-books/writing-better-lyrics-excerpt), [Soundfly](https://flypaper.soundfly.com/write/how-to-generate-great-songwriting-ideas-with-object-writing-technique/) |
| Rap flow is a voice against a steady 4/4 beat; slant rhyme, enjambment and stress placement are the variation tools | Solid (publisher / review level) | Adam Bradley, [Book of Rhymes](https://en.wikipedia.org/wiki/Book_of_Rhymes) |
| Punchline craft: misdirect, punch word last, a real link to the setup, specificity; in rap, twist a familiar idiom | Generic but consistent | [Toastmasters](https://www.toastmasters.org/magazine/magazine-issues/2018/july2018/humor), [Soundverse](https://www.soundverse.ai/blog/article/how-to-write-funny-rap-lyrics-0039) |
| Machine lyrics sit at the statistical centre (first-association words, stock images); fixes are concrete briefs, sensory detail, treating output as disposable | Practitioner level, one qualitative study | [Trinity Laban](https://researchonline.trinitylaban.ac.uk/download/3438) |
| Evaluation: rhyme accuracy / density are the usual metrics, flow is rarely measured, humans judge fluency, coherence, style | Solid | [DeepRapper](https://arxiv.org/pdf/2107.01875) |

## 2. Is there a standard order? No.
| Step in the assumed sequence | Evidence | Strength |
|---|---|---|
| Idea / topic first | Mostly no. MF DOOM: "I don't make up the idea first", "I choose the writing based on the instrumental" ([Spin](https://www.spinmagazine.com/2019/03/mf-doom-madvillain-interview-madvillainy-anniversary/)). Jay-Z starts from the beat ([Revolt](https://www.revolt.tv/article/jay-z-most-iconic-studio-habits-explained), third-party). Ca$his hears the beat first ([RapAnalysis](https://www.rapanalysis.com/2013/07/cahis-interview)). Exception: comic concept songs; Lonely Island settled the concept for ["Dick in a Box"](https://en.wikipedia.org/wiki/Dick_in_a_Box) first. Cadence Weapon wrote subjects first early on and thinks it made his albums feel [disconnected](https://cadenceweapon.substack.com/p/notes-on-process) | Medium, small sample |
| Hook first | No reliable evidence it is the norm; one how-to guide recommends it; DOOM wrote around choruses that came with the beat | Weak |
| Feel the flow | Supported, often before the words: Jay-Z mumbles flows in falsetto (via Revolt); Cadence Weapon "mumbling flows and ideas until something real had come together" | Medium |
| Work out the rhyme words | True for Eminem, but collected in advance, not per song: rhyme lists on paper, 99% never used ([Rubin account](https://rockthebells.com/articles/rick-rubin-joe-rogan-eminem-jay-z), [Hess](https://jillianhess.substack.com/p/re-noted-eminems-boxes-of-notes), [Rolling Stone via Portigal](https://portigal.com/tag/eminem/)) | Medium |
| Fill gaps / revise | Overproduce, then cut by ear: Cadence Weapon ~50 songs kept 12; DOOM ~5 songs per batch of 50 beats; Skinner reportedly up to 100 versions (profile claim, unverified) | Medium |

Common threads: sound or groove arrives first or alongside; meaning is found inside the sound and often fixed late; loaded rhyme material is collected independently of any one song; most of what is written is discarded by ear. Concept-first holds for comic concept songs like this one. Artists differ (Jay-Z memorises and discards, Eminem hoards on paper, Cadence Weapon composes in the studio).

## 3. Where the repo's writer differs (ranked)
D1. Loaded words come from a commonest-first menu, and the model cannot hear the grid. `carpet.py` keeps the 150 most common words per bar (line 317) and the top 40 (line 439); `versebank._menu` offers the first 30. For V2 1-8 that is "new, two, through, use, used, school, group". Mean zipf offered 4.8-5.4 across the eight open slots against the original hook's 4.04. Sound-first itself is not the fault: DOOM, Jay-Z and Ca$his do it.
D2. Retelling instead of claiming: `versebank.writer_request` tells the model each verse "must tell or boast this story's core". v17 opens 34 of 76 bars in the first person.
D3. One voice: no mates, partners or swears in v17; someone other than the narrator appears in 5 of 76 bars.
D4. The `#cash` tags count an idiom being present, not being literalised: v17 reports 15, and 1 of those phrases is in the repo's own 7,235-phrase bank (the writer self-reports the `idiom` field).
D5. More candidates did not help when the selector was weak (STATE 14 Oct).
D6. The signals that discriminated (supply, repetition, characters) are not in `versebank.grade`; five other instruments failed labelled-set tests.

## 4. Built so far (all report-only; nothing validated against Joe's ear)
`toolkit/craft_readouts.py` (voice, company, rhyme-slot stock phrases) and `toolkit/reservoir.py` (loaded-word offer; opt-in `WW_RESERVOIR=1` in `versebank._menu`). Offer mean zipf 4.2-4.4 against today's 4.8-5.4. Not built: claim cards, staged payoff-first writing with a deterministic flow fit, the cold-read selector. Those need an API key, Joe's private stories and the private original, none of which exist in the cloud clone.
