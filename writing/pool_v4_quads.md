# Candidate quads v4 - built to the original's measured FLOW frames (11 Oct 2026)

Every quad here passed all four of these, re-verified at write time:
  1. meaning gate (full sentences, no scaffolding, no dead end words)
  2. coherence gate (argument, no orphans, cash events at the original's own count for that position)
  3. per-line FLOW fit against that original 4-bar block, measured from the audio: exact syllable
     count, the strong/weak frame, the end shape and the syllable the end rhyme starts on
  4. form margin >= 0 against the same block's own bars
Blocks 77-89 are the chorus repeat of blocks 1-13 in the original, so the same flow frames apply.

5	Cold beer on the house in Porto	Two glasses, cold lager, back road corners	Lager, chips, and the last orders	Might hit the road past the border
# block 5 (Hook 5-8) margin +1 syllables [8, 10, 8, 8] vs original [8, 10, 8, 8] scheme ABBA cash (2, 2) list-fragments 0 drift-pairs 0 gates PASS strict-flow PASS

## CONTENT-FIRST REBUILD (11 Oct) - border-stop scene, Joe's pick. NOT YET PASSING, kept for his ear.
Bom dia the road to Porto | Then stop him cash paid the man cut corners | Gets a glass of the cold water | Might hit the road up in Dorset
# what it says: bar 5 greeting + where he came in; bar 6 the routine stop, cash paid, the fixer cutting corners; bar 7 it ends in a glass of cold water; bar 8 might park up in Dorset.
# block 5 measured: margin +1 | syllables [8, 10, 8, 8] exact | all four audio flow frames exact | meaning PASS | coherence PASS
# cash (2, 2) AT PAR ("cut corners" with the payoff in the rhyme slot, "hit the road") | list-fragments 0 | drift-pairs 0 | places named 2 (Porto, Dorset) = par
# STILL SHORT: internal rhyme ours 0.0 vs the original's block 0.25 (needs 1 in 4 bars) | consonant pile-ups 0.5 vs 0.25 (2 rough junctions vs 1)
# OPEN: the block spec asks for one PERFECT-rhyme pair that flips register. Ours is corners/water (clean on the stressed vowel, not perfect); border/order is perfect but reads worse.

## QUAD A (11 Oct 2026) - FIRST QUAD TO PASS EVERY GATE. Hook 5-8.
5	Hey there boss the Bristol raiders	6	Under the radar the boss wrote papers	7	On the level with my payers	8	Might check Bordeaux haul to traders
# what it says: bar 5 roll-call (greeting + crew + Bristol); bar 6 the paperwork gets done off the radar; bar 7 straight with the people who pay in; bar 8 might run the Bordeaux haul past the traders.
# measured: repo check_all --slot "Hook 5-8" = ALL PASS. forge.clean(strict=True) True, margin +5. syllables [8, 10, 8, 8] exact.
# flow frames (audio): bar 5 87% / 6 90% / 7 87% / 8 100% strong-weak agreement, no beat mismatch, end rhyme on the original's step, end shape exact on all four.
# accents land on story words only (Bristol, raiders / Under, radar, boss, papers / level, payers / haul, traders) - no dead accent. accent mass 1/2/0/2 vs par 1/4/0/3.
# end carpet: raiders/papers/payers/traders, all EY + schwa + z, scheme AAAA. (6,7) papers/payers = the perfect pair that flips register (paperwork -> the people who pay).
# cash 2/2 AT PAR, both literal readings on: "under the radar", "on the level". places 2 = par (Bristol, Bordeaux). runs 5 vs par 2. internal rhyme 7 vs the original's 4. consonant pile-ups 0.0 vs 0.25. meaning + coherence PASS.
# WEAKEST BAR: bar 8 - "check ... to traders" is loose phrasing and the article is clipped; if Joe wants a cleaner sentence the replacements that also pass are "Might check Bordeaux stock to traders" / "Might check the Bordeaux to traders".

