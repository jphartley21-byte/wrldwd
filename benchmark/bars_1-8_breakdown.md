# Breakdown of the original's opening 8 bars (chorus lines 1-8), the benchmark for our version
Written 9 Oct 2026. Joe pasted these 8 lines in chat; the lyrics are NOT stored in this project (copyright). Lines are cited as Ch L1-L8 with isolated words only. Sources: Genius annotations (42 of 42 read), 6 reaction transcripts + an earlier pass of 17 videos, the rhyme toolkit's mechanical analysis. All reaction evidence is thin (n = 6 for line-level; auto-captions; laughter inferred).

## 1. Line by line
| L | Key words | Job in the chorus | Meaning layers | Sound | Genius note | Reaction evidence |
|---|---|---|---|---|---|---|
| 1 | "hasta luego" | 5-syllable opener, a hello/goodbye that starts the roll call | Spanish "see you later" | EH-G-OW | gloss only | not singled out |
| 2 | "Wagwan ... Tobago" | greeting frame #1: [local greeting] + to the boys in + [place] | Patois greeting; Tobago is Caribbean | EY-G-OW | gloss (4 votes for Wagwan) | UK reactor rewinds here ("take it back", four hold-ons); a second recognises Tobago and goes into a Trinidad aside; Caribbean commenters confirm accuracy |
| 3 | "plain clothes" | 1st half of a two-line pun pair; the nonchalant hazard | plain clothes = undercover police; "plain" sounds like "plane" (deliberate, per Genius) | OW-DH-Z | top-voted (5 votes) | the plane/plain pair is among the most-quoted opening moments |
| 4 | "leg room ... plane home" | 2nd half of the pair; the payoff and the bathos | "plane" lands the pun; "more leg room" = coming home with more bags (a haul), said as an airline gripe | OW-M | gloss: leg room = bags/haul | a mundane complaint inside a flex; one UK reactor's likely laugh ("what is wrong with these guys") |
| 5 | "Ese ... Lagos" | greeting frame #2, second language | Yoruba "ese" = thanks; Lagos | EY-G-AA-S | top-voted annotation (6 votes) | Nigerian commenters confirm accuracy; reactors exclaim at the shout-out; one US comic laughs at the English-sounding pronunciation (accent bit) |
| 6 | "hold it down ... the man need favours" | plain business-register bridge; the setup for the product word | "hold it down" = keep order locally; "the man" = the boss; "favours" = business obligation | EY-V-ER-Z | not annotated (filler/setup) | not singled out |
| 7 | "Transatlantic ... flavours" | the product word lands on a perfect rhyme with "favours" | flavours = drug strains or luxury goods (annotator hedges); "transatlantic" = a distribution network; favours/flavours: obligation becomes merchandise | EY-V-ER-Z | wordplay, hedged | not singled out |
| 8 | "chuck the chips down ... Vegas" | closer; a place from outside the greeting frame | gambling idiom ("chips down"); "might" = casual, not a boast | EY-G-AH-S | reference gloss | not singled out |

## 2. Mechanics (measured with toolkit/rhyme_tools.py check)
- Syllables per bar: 5, 9, 9, 9, 8, 10, 8, 8 (mean 8.2). CHORUS BARS ARE 5-10 SYLLABLES, shorter than the verse lines (mean 9.3, up to 15). Do not write 12-syllable bars for a hook.
- Rhyme scheme (corrected by Joe, 9 Oct 2026): L1-L4 are AAAA on a TWO-SYLLABLE vowel rhyme EY-OW (lu-EH-GO ~ to-BAY-GO ~ PLAIN CLOTHES ~ PLANE HOME); the tool missed it because `check` keys only from the last stressed vowel. L5-L8: A C C A (favours/flavours = C). Always test the last TWO syllables' vowels, not just the last stressed one.
- Vowel carpet of the end words (stressed vowel): EY x5 (Tobago, Lagos, favours, flavours, Vegas), OW x2 (clothes, home), EH x1 (luego). Genius: "the chorus places share the long 'ay' sound with plane and flavours": PLACES WERE CHOSEN FOR THEIR VOWEL.
- Consonant skeleton on the place lines: lines 1, 2, 5, 8 all end G + a soft vowel (+S): luego / Tobago / Lagos / Vegas. So the A-rhyme is a MOSAIC of the pattern "[stressed vowel] + G + soft ending", not a perfect rhyme.
- Only one perfect rhyme: favours/flavours (4 matching phones). Clothes/home is assonance (OW + a nasal/fricative coda).
- Alliteration/consonance (Joe, 9 Oct 2026): L2 'boys' + 'Tobago' on B, and the greeting itself repeats W (Wag-wan); L3-L4 'plain'/'plane' + 'clothes' share PL/KL clusters. Sound glue inside bars comes from consonants as much as vowels.
- Internal rhyme is sparse (open/clothes, Ese/Lagos); these bars get their strength from the carpet, the repeated frame and the pun pair, not from dense internal rhyme.
- The two greeting lines repeat a frame ("[greeting] to the boys in [place]") with a different language each time; the other lines break the frame.

## 3. What each element does (the recipe)
1. A chantable frame repeated twice with different local languages (accuracy is what earns trust: reactors from the places confirm it).
2. Places chosen by vowel so the whole sequence sits on one carpet (EY) with a G skeleton.
3. A two-line pun pair in adjacent bars: a danger/menace phrase (plain clothes) then its homophone in a mundane travel setting (plane home). The swap from menace to airline comfort is the nonchalance.
4. Bathos by a domestic complaint (leg room) standing in for a smuggling haul.
5. A register ramp: business ("hold it down", "the man", "favours") then product ("flavours") then leisure/gambling ("chips down"), each step one register further from the street, all flat.
6. A perfect-rhyme pair (favours/flavours) placed right after the register ramp so the word change IS the payoff.
7. Modal understatement ("might chuck the chips down") instead of a boast.
8. Opener at 5 syllables, then 8-10 for the rest: the first bar is the shortest, a breath before the chant.
9. Three languages in 8 bars (Spanish, Patois, Yoruba) plus British English; every foreign word is correct.

## 4. Spec for OUR 8 bars (match the quality, do not copy)
- 8 bars, 5-10 syllables each (mean about 8), one bar per line.
- Bars 1-4: AAAA on one two-syllable vowel pattern (like EY-OW), reached through mixed word shapes (one word, two words, a place name); bars 1-4 must contain a pun pair (L3-L4) and clever phrasing.
- Choose a vowel carpet first (about 5 of 8 end words on one stressed vowel) and a consonant skeleton for the place lines; use the toolkit's families/rhymes/mosaic to build the bank. Include one perfect-rhyme pair whose second word changes the register, one assonance pair that carries the two-line pun, and a short opener.
- A two-line pun pair of our own (a menace phrase, then its homophone or double sense in a mundane travel setting), fresh in subject. NOT plane/plain, not plain clothes, not legroom, not "to the boys in [place]", not Tobago/Lagos/Vegas, not "hasta luego".
- Two or three greetings or local words from Joe's real trips, each correct (candidates in material/place_sound_families.md: Mai pen rai (Thai), Servus (Austrian), Kaixo (Basque), Zivjo (Slovene), Ahoj (Slovak), Doe maar gewoon (Dutch), G'day/arvo (Aus), Kia ora (NZ), Salam (Moroccan Arabic), Hei (Norwegian), Ciao, Sawasdee, Xin chao). Mark any pronunciation Joe must confirm.
- Nonchalance: the narrator reports something big or illicit in an everyday British register; domestic person mentioned, not addressed; no gag structure; each bar must SAY something (a beat sheet agreed with Joe first).
- Truth: places and events from material/travel_history.md; anything else tagged (invented).
- Per-syllable discipline: every end word chosen from a toolkit bank; every bar run through `check`; record rejected words and why.
