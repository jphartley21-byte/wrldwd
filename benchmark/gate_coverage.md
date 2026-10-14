# Gate coverage: every aspect of what makes the original good, mapped to a check

Joe's rule (11 Oct 2026): *"the quality gates should be designed so that the original can only just pass"* and *"this only works as long as every aspect that makes the original lyrics so good is measured as accurately as possible."*

So: **no aspect may be silently unmeasured.** Each of the 41 rubric criteria is either MEASURED against the original's own value (so the original passes at exactly 0 margin) or listed as a HUMAN gate that **blocks a PASS** until Joe signs it off. `quality_gate.py` prints the human gates with every run.

## The threshold rule
Every threshold is the original's own measured value on the same bars (`python toolkit/quality_gate.py --original` proves it: all three levels MATCH, margin 0). Beating = positive margin. Matching = pass. Below = fail. This is what "the original can only just pass" means: it cannot beat itself.

## Three levels
| Level | Scope | Where |
|---|---|---|
| LINE | each bar's craft | `quality_gate.py --level line`, plus `meaning_gate.py` |
| VERSE | a section's runs, rhyme architecture, payoff | `quality_gate.py --level verse`, plus `coherence_gate.py` |
| SONG | the whole track: arc, bookend, motifs, no copying | `quality_gate.py --level song` |

## Coverage table
| # | Criterion | How it is checked | Accuracy note |
|---|---|---|---|
| 1 | Chain length and coverage | longest chain by ear (vsim ≥ .78 on the tail) + rhyme coverage share | accurate now; the old single-vowel version was wrong |
| 2 | Weak-syllable endings | soft-ending share vs the slot's | accurate |
| 3 | Breath/X lines | short bars whose end sound is unique in the section | approximate: "plain" is a judgement |
| 4 | Hinge line | does an end word rhyme across a section edge (song level) | accurate for rhymes; a thematic hinge is human |
| 5 | Line-length variance | spread, 5-14 band share, short-line share | accurate |
| 6 | Escalation arc + bookend | bookend: last section shares content with the first | the arc itself is HUMAN |
| 7 | Internal rhyme and vowel carpets | internal-rhyme share, carpet density | accurate |
| 8 | Cut-up, mosaic, homophone rhymes | mosaic + homophone counts | "none forced" is the human X4 test |
| 9 | Enjambed rhyme | pronoun-ended bar count | accurate |
| 10 | Reduplicated percussive words | reduplication count (hyphen/space repeats) | accurate |
| 11 | Names chosen for their vowel | carpet measured on place-ended bars | accurate |
| 12 | Nonchalance density | lexicon of flat-report markers (proxy) | **HUMAN** confirm; a proxy cannot hear deadpan |
| 13 | Echo with a twist | repeat detection + cashed idioms + pun pairs (`original_map.csv`: `idioms_named`, `pun_pair_with`) | map now NAMES each idiom with the register it signals and the bar it echoes; **HUMAN** confirm the repeat really changes sense |
| 14 | Number ladder | number-word count | accurate |
| 15 | Lexical-set metaphors | theme-set words per bar | **HUMAN** confirm the set describes another domain |
| 16 | Domestic anchors | domestic-object lexicon per 8 bars | accurate |
| 17 | Understated menace | euphemism/menace lexicon, zero swearing | partly; tone is human |
| 18 | Self-mockery | **HUMAN** (must be true, Joe confirms) | untestable |
| 19 | Roll-call hook with a local word per place | greeting count, place count, title withheld | accurate |
| 20 | Voice tics as rhythm | tic-word count per 8 bars | accurate |
| 21 | Two voices | **HUMAN** (delivery / Suno level) | untestable in text |
| 22 | Hook riff and beat | **HUMAN** (Suno level) | untestable in text |
| 23 | Breath-control bursts | 12-15 syllable bar count | accurate |
| 24 | No AI-tell words or shapes | BANNED lexicon, rule-of-three detection, filler frames | accurate |
| 25 | No copying | 4-gram overlap against the original (par is 0, not the original's self-count) | accurate |
| 26 | True or flagged | **HUMAN** — every fact from material/ or tagged | untestable |
| 27 | Signature set-piece | densest 8-bar window vs the rest | placement is HUMAN |
| 28 | Layers that reward a rewind | cut-ups + cashed idioms + repeats | **HUMAN** confirm the two readings |
| 29 | Handoff device | **HUMAN** (needs two voices) | untestable |
| 30 | Accuracy of the local layer | flag any proper noun not in material/ | **HUMAN** confirm with someone who has been there |
| 31 | Lived detail | bars naming a real place/number from material/ | **HUMAN** confirm the detail is earned |
| 32 | Scansion and speakability | stresses, clashes, pauses, clusters, band; flow_fit vs the audio | accurate for the counts; the ear is Joe's |
| 33 | Register | clause-or-image share (the original is 3rd person in places, so person is not forced) | partly; voice is HUMAN (40) |
| 34 | Cringe filter | **HUMAN**, fail level | untestable |
| 35 | Plain beats clever | **HUMAN** | untestable |
| 36 | Poster test | **HUMAN** | untestable |
| 37 | Nonchalance first | flat-register proxy; no shouting markers | **HUMAN** confirm |
| 38 | Wordplay carried by rhyme and flow | cashed idioms + cut-ups + `payoff_in_rhyme_slot` | placement now measured (is the key word the bar's last stressed syllable; bar 3 of the original = yes, and the pun partner in bar 4 is named); cleverness is HUMAN |
| 39 | No gag structure | **HUMAN** | untestable |
| 40 | Character carried by words alone | **HUMAN** | untestable |
| 41 | The scheme and flow sell it | the composite form measures at all three levels | partly; Joe's ear decides |

Craft principles from `craft_principles.md` are covered by `coherence_gate.py`: cashed idiom (P2/P19-P22), cohesion and orphan bars (P9/P13), exophoric reference (P10), bare indefinites and imageless fragments (X2/X3/X6), scene-hopping (X5), callback (P12), plus the supertask (P8) which the caller must state.

## Honest limits
- 17 criteria are HUMAN gates. The tool prints them on every run and refuses to call a section finished. A measured PASS is never a finish.
- Several measurable items are **proxies** (nonchalance, register, lexical sets, X lines). They are marked as such; they screen, they do not judge.
- The original's own thresholds give margin 0 on 34 measures at three levels. Anything we write must match or beat every one of them, and then still pass the 17 human gates.
