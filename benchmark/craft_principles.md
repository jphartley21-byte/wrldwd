# What makes lyrics actually good — craft principles, and the checks that catch their absence

Written 11 Oct 2026, after Joe's verdict on the first rebuilt hook: *"Parts still don't make sense. It doesn't seamlessly flow as a whole or feel like a coherent thought or character. It doesn't say anything and there's no payoff."*

He was right, and the diagnosis is now measured rather than felt. This file records (1) what the craft sources say, (2) which of those principles can be checked by machine, and (3) which cannot — so we stop pretending a metric-based pass means the writing is good.

## 1. The finding that matters most
Our checks measured **form**: rhyme scheme, syllable spread, internal rhyme, alliteration, density of devices. Form is necessary and blind. A section can beat the original on every mechanical criterion and still be 16 unrelated observations — which is exactly what the first rebuilt hook was.

**The unit of craft is not the bar. It is the RUN and the ARGUMENT.**
- The repo's own analysis (`benchmark/comedy_theory.md`, from 81 annotated lines) already said it: the original's character lines are *"a 2-4 line run with a bland setup line and a bathetic closer on the rhyme beat"*, and *"the cashed-in word sits in the RHYME SLOT ... the payoff often lands on the next line across the bar break."*
- An automated gate can never verify an argument. What it *can* do is verify the fingerprints an argument leaves behind: a cashed idiom, a resolvable reference, a concrete image, a callback. Those are the checks below.

## 2. Principles, sources, and how to test them
| # | Principle | What it means | Test | Source |
|---|---|---|---|---|
| P2 | Script opposition + logical mechanism | A payoff works when the line forces one frame and then the ending flips it. | Does the section cash a stock phrase literally, with the payoff word in the rhyme slot? (the original cashes 4 in its 16-bar hook) | GTVH (Attardo & Raskin); see `comedy_theory.md` |
| P3 | The turn (volta) | A line that changes the direction of the thought. | Can you point at the bar where the meaning turns? If not, there is no turn. | poetry craft |
| P7 | Bathos | The drop from big to small is the comic engine. | Is the biggest claim followed by the smallest object? | `comedy_theory.md` |
| P8 | Through-line / supertask | Stanislavski: every unit of action serves one objective. | State the section's one-sentence goal. Any bar that does not advance it is an orphan and is cut. | Stanislavski's system |
| P9 | Cohesion devices | Lines are held together by reference, ellipsis, substitution, lexical repetition, conjunction. | For each bar, name its link to the previous one. | Halliday & Hasan, *Cohesion in English* |
| P10 | No exophoric reference | A pronoun or generic that never points to anything identified does not create cohesion. | Does every pronoun resolve inside the section? Is any "a place / a day / another week" left unpictured? | as P9 |
| P11 | Topic–comment / given-new | Each bar should start from the established and add one new thing. | Does a bar introduce two unrelated new topics? | Information structure |
| P12 | Motif, callback, bookend | A recurring concrete element ties a section; a late line pointing back is a callback. | Does anything return? | narrative motif; callback |
| P13 | Non sequitur | A line that does not follow is either a device *in voice* or an accident. | Can you state a "therefore / because" link to the previous bar? | non sequitur (literary device) |
| P19–P22 | Idiom literalisation | A dead metaphor taken literally, figurative first and literal last, payoff word last in the bar. | Is there a cashed idiom, and is the literal word in the rhyme slot? | `comedy_theory.md`; zeugma craft |
| P14 | Consistent register | One voice held throughout; a break in register is a character break. | Does any bar drop or raise the register without intent? | register (sociolinguistics) |
| P1/P5 | Three-part build; rule of three vs two-line payoff | Setup → development → payoff; a triple is a device, a two-line payoff is a turn. | Does the run build, or just list? | joke structure; *Comedy Writing Secrets* |
| X2 | Deepity: "sounds meaningful, asserts nothing" | A line that only seems profound. | **Paraphrase the bar as a plain checkable claim. If it collapses to nothing, cut it.** | Dennett, "deepity" |
| X3 | Abstract/referentless nouns | Orwell's "meaningless words" point to no discoverable object. | Every content noun should be something you could point at. | Orwell, *Politics and the English Language* |
| X4 | Forced rhyme | The end word chosen for sound, not sense, warps the meaning. | Swap the end word for a non-rhyming synonym: if the meaning moves, the rhyme was driving. | Robin Frederick |
| X5 | Unrelated-image lists / scene-hopping | A run of images from unrelated scenes with no causal link reads as a checklist. | Count distinct scenes per 4 bars; require a cause→effect chain. | `authenticity_guide.md` |
| X6 | Telegraphy | Dropped subjects and verbs to fit the metre: nobody talks like that. | Is the bar a clause or a picture? A fragment is fine **only if it has an image**. | `authenticity_guide.md` |
| X8 | AI-slop banality | Lacking effort, quality or meaning; banal and generic. | Combine X1–X5 plus the explained-joke and moralising-ending bans (rubric 24). | AI slop |

Not found: "ESKIL" is not a real lyric-evaluation framework under any spelling. If Joe saw it somewhere, we need the source.

## 3. What is now checked by machine
`toolkit/coherence_gate.py` (run it with `--goal "the section's one sentence"`):
- **X2/P10 bare indefinites** — "a place he cannot pronounce", "another week": nothing to picture.
- **X6 imageless fragments** — a verbless bar with no object, place or person in it. (A fragment *with* an image is fine: a line in the original built on one repeated word (the same nationality adjective three times) passes; the opening bar and non-English bars are exempt.)
- **X2 generic-only content** — a bar whose content words are all abstractions.
- **P9/P13 orphan bars** and **P8 frames** — reported with the named link per bar (repeated word, reference, conjunction, repeated frame).
- **X5 scene-hopping** — consecutive unrelated places.
- **P10 dangling plural** — "they/them" with no antecedent in the preceding bars.
- **P2 payoff** — cashed idioms present and counted against the requirement for the section length.
- **P12 callback** — whether the closing bar echoes the first half.

Calibration is the whole point, and it is asserted in the selftest:
| Sample | Verdict |
|---|---|
| the original's 16-bar hook | **PASS** |
| a scrapbook stanza | **NOT YET** (caught) |
| our first rebuilt hook (Q120) | **NOT YET** — 3 fails: two bare indefinites, no cashed idiom |

## 4. What can never be mechanised, and must be written down instead
1. **The argument.** Before writing a section, write its supertask in one sentence (P8) and the bar that pays it off (P2/P3). If the payoff bar is not named in advance, there will not be one.
2. **The turn.** Where the thought changes direction. A human has to point at it.
3. **Voice.** Whether the whole section is one man talking. The tool can count register words; it cannot hear a person.
4. **The paraphrase test (X2) at scale.** The tool screens for the generic and the unpictured; only a human can paraphrase a line and see it collapse.
5. **Whether the joke is in the character.** Joe's definition: the comedy comes from the character and the wordplay, not from gags. Character is a human judgement.

## 5. The rule that follows
Before any section is written: **state the argument in one sentence, name the run structure (2-4 bars per run, bland setup, bathetic closer cashing an idiom on the rhyme beat), and name the payoff bar.** Then write. A section with no named payoff is not written yet, whatever its metrics say.
