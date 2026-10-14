# Gate architecture: what the original does at each level, and which gate belongs where

Written 12 Oct 2026 (Joe: "the gates we use need to work for the whole song too... different gates for
different levels"). Every threshold below is measured from the original's own 76 bars, so a gate that the
benchmark itself would fail is not in here. Lyrics are cited by line number and isolated words only.

## 1. The distillation, measured

| property | Hook (16 bars) | Verses (60 bars) | what it means |
|---|---|---|---|
| local / foreign words | **9** | **0** | code-switching is a HOOK device. Not one verse bar carries a local word |
| places named | 7 bars | 11 bars | places run through the whole song: ~1 bar in 4 |
| third-party people | 6 | 7 | present at every level, and sparse: not a gate |
| administrative words | 0 | **1** (cashed) | admin vocabulary is essentially absent. The one use is a deliberate tally gag, mid-bar |
| syllables per bar | **5-12**, mean 8.2 | **5-15**, mean 9.4 | the hook is tighter than the verse, by design |
| worst repeated content word | 3 (deliberate anaphora) | 4 | repetition ceiling is tighter in the hook |
| type/token, content words | 0.90-1.00 | 0.78-0.94 | the fastest verse block is the least varied, on purpose |
| lines reused outside the chorus | **0** | **0** | nothing is recycled: the chorus is the only repetition in the song |

Song level: the chorus returns **unchanged** (bar for bar), the title lands **once, in a verse**, and the
76 unique bars contain no duplicate line at all.

## 2. What makes it good, level by level

**LINE.** One bar is one event with one stamp. The rhyme word is almost always a *stamp* — a place, a
local word, a brand, or a concrete object — never an abstraction. Sentences are spoken, not written
(imperatives, asides, "come on then"). Rhythm is varied inside the line: a fast three-rhyme bar next to a
five-syllable one. Reduplication is the percussion ("dot-dot", "click-clack", "ping-pong").

**QUAD.** Four bars form a turn, not four statements: set-up, escalation, threat, punchline; or claim,
evidence, bathos, exit. The scheme is consistent across the quad and the quad usually ends short. The
fourth bar frequently hands off: it names the next thing or flips the register.

**VERSE.** A verse has a spine (the rise: broke, then broke down bricks, then Mr. Worldwide), a montage of
places as evidence, two lexical sets running through it (the trade, and the threat), and a bathos
counterweight (the pub, the cigarettes, the boots). One block goes double-time for length. The verse is
where the title lands. Nothing is repeated, and the last couplet steers back into the chorus.

**HOOK.** A roll call built on ONE vowel carpet, each bar carrying a place plus either a local greeting or
a concrete visual, the title withheld, and one perfect-rhyme pair that changes register. This is the only
level that code-switches, which is what makes it read as a world tour rather than a paragraph.

**SONG.** Build and release: tight hook, escalating verse, hook unchanged. The chorus is the only thing
repeated. The world grows (18 named places) while the register stays flat.

## 3. The gates, allocated by level

MEASURED = automated today. HUMAN = Joe's ear only; never pretend otherwise.

### LINE
| gate | threshold | evidence |
|---|---|---|
| syllables in the level's band | hook 5-12, verse 5-15 | hook mean 8.2, verse mean 9.4 |
| end word is not an administrative abstraction | 0 admin words in a rhyme slot | 0 in the original's 76 bars |
| no crutch repetition | hook <=3 of any content word, verse <=4 | max 3 (hook), 4 (verse) |
| the bar says something (image, action, or claim) | meaning gate + coherence P10 | meaning gate passes all 76 |
| MOVES: does the line land in the mouth | HUMAN | nothing automated has ever predicted it |

### QUAD
| gate | threshold | evidence |
|---|---|---|
| scheme holds inside the quad | pairs the by-ear scheme names must rhyme >=0.78 | 3 of 19 known pairs still mis-grade (documented) |
| at least one stamp in the quad | place, local word, or person | places in ~1 bar in 4 |
| internal rhyme density | >= 0.6 of the original's for that slot | measured per slot already |
| **sound device** (diagnostic, not a veto) | drum or echo in >= 40% of quads | the original: 10 of 19 quads (53%), and 3 quads lean on a repeat |
| **image chain** (diagnostic, not a veto) | a chain that LANDS on the rhyme, ~1 per 6 quads | the original: chains in 5 of 19 quads, landing in 3 |
| the quad turns | set-up then payoff, and the 4th bar is short or hands off | 4th-bar syllables run short in most quads |
| no word repeated across the quad | except a deliberate frame | the original's anaphora is flagged in its own doc |

**The drum, defined correctly (Joe, 12 Oct).** A drum is ONE syllable frame (nearest consonant either side of
a vowel) used three or more times with the vowels MOVING. Two wrong definitions came before it: a word-level
frame (which missed the first step of the couplet, because that word ends in a different consonant than the
others) and a strict syllabifier (which found no frame in a word whose medial consonant legitimately starts
the next syllable). The ear does neither: it pairs each vowel with its neighbours, and it lets a frame cross
a bar line. Measured on the couplet: one frame, four steps, vowels moving, spanning two bars, with the last
step sitting immediately before the rhyme word's stressed vowel.

### VERSE
| gate | threshold | evidence |
|---|---|---|
| spine | first two bars set a state, last two change it | HUMAN to judge, MEASURED to check it is not a repeat |
| place density | >= 1 named place per 4 bars | 11 places in 60 verse bars |
| no recycled lines | 0 lines reused anywhere but the chorus | 0 duplicates in 76 bars |
| one long block | at least one bar >=12 syllables per verse | 13, 15, 14, 15 all appear |
| lexical sets | the trade and the threat, named in the verse doc | two sets run through both verses |
| the title | lands once, in a verse, not in the hook | "Mr. Worldwide" appears once, V1 |

### HOOK
| gate | threshold | evidence |
|---|---|---|
| one vowel carpet | all bars rhyme inside the frame's family | measured per block |
| local words | >= 1 per 4 bars IN THE HOOK ONLY | 9 in the hook, 0 in the verses |
| places | >= 4 of 16 hook bars carry a place | 7 of 16 |
| the title is withheld | 0 occurrences | 0 in the hook |
| one perfect-rhyme pair that changes register | flagged in the hook doc | HUMAN to confirm it lands |

### SONG (new level, never checked before)
| gate | threshold | evidence |
|---|---|---|
| the chorus returns unchanged | bar-for-bar identical | the original repeats it exactly |
| nothing else is reused | 0 duplicate lines outside the chorus | 0 in 76 bars |
| the title lands once | exactly 1 occurrence, outside the hook | 1 occurrence |
| total world | >= 12 named places across the song | 18 |
| whole-song lexical variety | type/token >= 0.70 | 0.76 |
| build and release | hook, escalating verse, hook | the structure itself |

## 4. Why the old gate set could not see this

Every gate we had measured one thing: **sound**. Vowels, syllables, stress, rhyme strength, internal
density. That is why 5-16 could pass the sound gates and still be culturally empty: no local word, no
person, no place in a rhyme slot, and repetition used as filler to satisfy a density gate. The new level
architecture adds the missing axis — **what the bar is made of** — and puts each check at the level where
the original actually exhibits it. A hook gate at verse level would fail the original; that is how the
allocation above was tested, by running the gates against the 76 bars they came from.
