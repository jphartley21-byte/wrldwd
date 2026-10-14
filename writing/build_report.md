# build report (incumbent: (none: built from scratch))

spend on seeds this build: $0.0876 (block and ranking calls are in eval/ledger)

## Hook 5-8 -- BUILT, passes the plan gate
lore_allusion 'Beer garden': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: The council wants its gnome back and I am not sorry, because it came off the back of a lorry.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=4/4 frame problems=4 syllable misses=1
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 2: weak syllables on the beat: not(7), sorry(9) (put a stressed syllable on each downbeat)
  candidate frame fail: flow: 1.00 weak syllables per bar land on a downbeat, the original's slot average is 0.25 (cap 0.75); see the beat map in slotspec
  bar loop (1 calls): bar 2: 12 syllables for a target of 10; 0 variants tried -> repaired
    before: Hoi Rotterdam, gnome in my garden. / Council man wants gnome back, I read it, not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
    after:  Hoi Rotterdam, gnome in my garden. / Council wants gnome back, I'm not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
  bar loop (1 calls): bar 2: 12 syllables for a target of 10; 0 variants tried -> repaired
    before: Hoi Rotterdam, gnome in my garden. / Council man wants gnome back, I read it, not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
    after:  Hoi Rotterdam, gnome in my garden. / Council wants gnome back, I'm not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
  --- taken:
  1. Hoi Rotterdam, gnome in my garden.
  2. Council wants gnome back, I'm not sorry.
  3. Came off back of a lorry.
  4. Might lie low in Oslo, pardon.

## Hook 9-16 -- BUILT, passes the plan gate
lore_allusion 'Interest': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: A man who owes me bread had his page ruled in red biro, and I took him to Boomtown, where he lost his head.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/3 frame problems=10 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 2: 12 syl (need 9+-1)
  candidate frame fail: bar 3: 10 syl (need 8+-1)
  bar loop (5 calls): bar 1: verifier: grammar: unresolved_pronoun:his; 0 variants tried -> repaired | bar 2: 12 syllables for a target of 9; 11 variants tried -> no passing variant,  | bar 3: 10 syllables for a target of 8; 14 variants tried -> no passing variant,  | bar 4: verifier: grammar: unresolved_pronoun:he; 16 variants tried -> no passing | bar 5: 20 syllables for a target of 12; 6 variants tried -> repaired
    before: I ruled his page in biro, red. / I told him Friday was the deadline, as I said. / I took him and the lads to Boomtown, Fred. / At the guillotine prop he lost his head. / Nobody notices: the crowd claps, a steward asks about a wristband. / The blade came down. / I enter one head, less the fee. / A clean cut to the bread.
    after:  I ruled page in biro, red. / I told him Friday was the deadline, as I said. / I took him and the lads to Boomtown, Fred. / At the guillotine prop he lost his head. / Nobody looks; a steward asks about the band. / The blade came down. / I enter one head, less the fee. / A clean cut to the bread.
  bar loop (5 calls): bar 1: 9 syllables for a target of 7; 0 variants tried -> repaired | bar 2: ends |w, needs |S; 5 variants tried -> no passing variant, left as it was | bar 3: 10 syllables for a target of 8; 11 variants tried -> no passing variant,  | bar 4: ends |SwS, needs |S; 16 variants tried -> no passing variant, left as it  | bar 5: 17 syllables for a target of 12; 3 variants tried -> repaired
    before: His page got ruled in red biro, see. / I told him Friday, as I said to me. / We went to Boomtown with the lads, you see. / He lost his head at the guillotine. / Crowd claps, a steward asks about a wristband, nobody blinks. / The blade came down. / I post one head, less the fee. / A clean cut to the bread.
    after:  Page got ruled in red biro, see. / I told him Friday, as I said to me. / We went to Boomtown with the lads, you see. / He lost his head at the guillotine. / Crowd claps, steward asks about wristband, nobody looks. / The blade came down. / I post one head, less the fee. / A clean cut to the bread.
  --- taken:
  1. I ruled page in biro, red.
  2. I told him Friday was the deadline, as I said.
  3. I took him and the lads to Boomtown, Fred.
  4. At the guillotine prop he lost his head.
  5. Nobody looks; a steward asks about the band.
  6. The blade came down.
  7. I enter one head, less the fee.
  8. A clean cut to the bread.

## V1 1-8 -- BUILT, FAILS the plan gate
lore_allusion 'Portsmouth': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: The boat waits for me, the hosts thank me, and Mum thinks I work in IT.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=3/5 frame problems=7 syllable misses=2
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: perry
  candidate frame fail: bar 5: 10 syl (need 6+-1)
  candidate frame fail: bar 6: 12 syl (need 8+-1)
  bar loop (7 calls): bar 1: ends |S, needs |Sw; 0 variants tried -> repaired | bar 2: end word 'perry' is used more than once in this block; 0 variants tried - | bar 3: 13 syllables for a target of 8; 2 variants tried -> repaired | bar 4: 13 syllables for a target of 8; 3 variants tried -> repaired | bar 5: 10 syllables for a target of 6; 5 variants tried -> no passing variant, l | bar 6: 12 syllables for a target of 8; 9 variants tried -> no passing variant, l | bar 7: ends |Sw, needs |S; 5 variants tried -> no passing variant, left as it wa
    before: Boat waits, I turn up late, deckhand holds ramp / Deckhand holds the ramp, gets paid in pear perry / A host in Spain leaves a case of dry sherry / A host in Norway sets a place, warm cherry / Bergen says 'Takk', I answer 'ta', merry / Twelve stops, four weeks, one pass, validated bury / Mum thinks I work in perry / Conductors never asked what pass was for, twelve runs, Kerry
    after:  Boat waits, I turn up late, deckhand holds ready / Deckhand holds ramp, gets paid in pear perry / Host in Spain leaves sherry, very / Host in Norway sets place, warm cherry / Bergen says 'Takk', I answer 'ta', merry / Twelve stops, four weeks, one pass, validated bury / Mum thinks I work in perry / Conductors never asked what pass was for, twelve runs, Kerry
  bar loop (7 calls): bar 1: ends |S, needs |Sw; 0 variants tried -> repaired | bar 2: end word 'perry' is used more than once in this block; 0 variants tried - | bar 3: 13 syllables for a target of 8; 3 variants tried -> repaired | bar 4: 13 syllables for a target of 8; 3 variants tried -> repaired | bar 5: 10 syllables for a target of 6; 3 variants tried -> no passing variant, l | bar 6: 12 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 7: ends |Sw, needs |S; 5 variants tried -> no passing variant, left as it wa
    before: Boat waits, I turn up late, deckhand holds ramp / Deckhand holds the ramp, gets paid in pear perry / A host in Spain leaves a case of dry sherry / A host in Norway sets a place, warm cherry / Bergen says 'Takk', I answer 'ta', merry / Twelve stops, four weeks, one pass, validated bury / Mum thinks I work in perry / Conductors never asked what pass was for, twelve times, Derry
    after:  Boat waits, I turn up late, deckhand holds very / Deckhand holds ramp, gets paid in pear perry / A host in Spain leaves dry many / Host in Norway sets warm cherry / Bergen says 'Takk', I answer 'ta', merry / Twelve stops, four weeks, one pass, validated bury / Mum thinks I work in perry / Conductors never asked what pass was for, twelve times, Derry
  --- taken:
  1. Boat waits, I turn up late, deckhand holds ready
  2. Deckhand holds ramp, gets paid in pear perry
  3. Host in Spain leaves sherry, very
  4. Host in Norway sets place, warm cherry
  5. Bergen says 'Takk', I answer 'ta', merry
  6. Twelve stops, four weeks, one pass, validated bury
  7. Mum thinks I work in perry
  8. Conductors never asked what pass was for, twelve runs, Kerry

## V1 9-16 -- BUILT, passes the plan gate
lore_allusion 'Dial-a-ride': structurally OK | triggers in the bars: ['booking', 'bus', 'booked', 'bus pass'] | in a rhyme slot: False
argument: I came up with nothing but a bus pass, I own a quarry and I am known worldwide; thank you for applying, we know where you reside.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=5/5 frame problems=10 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: ends |S (need |w)
  candidate frame fail: bar 2: ends |S (need |w)
  bar loop (6 calls): bar 1: ends |S, needs |w; 17 variants tried -> no passing variant, left as it wa | bar 2: ends |S, needs |w; 9 variants tried -> no passing variant, left as it was | bar 3: 8 syllables for a target of 5; 2 variants tried -> repaired | bar 4: 9 syllables for a target of 12; 10 variants tried -> no passing variant,  | bar 5: 10 syllables for a target of 12; 15 variants tried -> no passing variant, | bar 8: 6 syllables for a target of 11; 11 variants tried -> no passing variant, 
    before: Booked a bus pass for the ride / Rail card, nothing else, just pride / Never laid a brick inside / Mayor's invoice made me known worldwide / Old mate applies, vacancy filled by bride / Your details on file at quarry slide / Interview's a rough ride in dumper, no guide / We know where you reside
    after:  Booked a bus pass for the ride / Rail card, nothing else, just pride / Never laid brick high / Mayor's invoice made me known worldwide / Old mate applies, vacancy filled by bride / Your details on file at quarry slide / Interview's a rough ride in dumper, no guide / We know where you reside
  bar loop (7 calls): bar 1: ends |S, needs |w; 11 variants tried -> no passing variant, left as it wa | bar 2: ends |S, needs |w; 7 variants tried -> no passing variant, left as it was | bar 3: 8 syllables for a target of 5; 2 variants tried -> repaired | bar 4: 9 syllables for a target of 12; 12 variants tried -> no passing variant,  | bar 5: 8 syllables for a target of 12; 25 variants tried -> no passing variant,  | bar 7: 10 syllables for a target of 12; 5 variants tried -> no passing variant,  | bar 8: 6 syllables for a target of 11; 4 variants tried -> no passing variant, l
    before: Left Reading with a booked ride / Rail card only, loads of pride / Never laid a brick beside / Mayor's drive is my cement, worldwide / Mate applies, but the post's for bride / Details kept on file at quarry slide / Interview's rough ride, dumper has no guide / We know where you reside
    after:  Left Reading with a booked ride / Rail card only, loads of pride / Never laid brick, right / Mayor's drive is my cement, worldwide / Mate applies, but the post's for bride / Details kept on file at quarry slide / Interview's rough ride, dumper has no guide / We know where you reside
  --- taken:
  1. Booked a bus pass for the ride
  2. Rail card, nothing else, just pride
  3. Never laid brick high
  4. Mayor's invoice made me known worldwide
  5. Old mate applies, vacancy filled by bride
  6. Your details on file at quarry slide
  7. Interview's a rough ride in dumper, no guide
  8. We know where you reside

## V1 17-24 -- BUILT, passes the plan gate
lore_allusion 'Broadchurch': structurally OK | triggers in the bars: ['harbour', 'the coast', 'coast', 'drama'] | in a rhyme slot: True
argument: A man from Dublin wanted what I owed him and chased me over the Irish Sea, and the island did the rest.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/3 frame problems=22 syllable misses=6
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 2: ends |S (need |Sww)
  candidate frame fail: bar 3: 15 syl (need 11+-1)
  bar loop (8 calls): bar 1: ends |w, needs |Sw; 2 variants tried -> repaired | bar 2: ends |S, needs |Sww; 5 variants tried -> no passing variant, left as it w | bar 3: 15 syllables for a target of 11; 23 variants tried -> no passing variant, | bar 4: 15 syllables for a target of 11; 12 variants tried -> no passing variant, | bar 5: 21 syllables for a target of 11; 10 variants tried -> no passing variant, | bar 6: 12 syllables for a target of 10; 17 variants tried -> no passing variant, | bar 7: 18 syllables for a target of 10; 13 variants tried -> no passing variant, | bar 8: ends ~S, needs |SwS; 15 variants tried -> no passing variant, left as it 
    before: Says I'm on his list; I clocked him. / Full Irish done, bike locked. / My boat leaves Douglas, his docks; he hires a car. Harbour. / He follows up the coast past Laxey Wheel, blocks me in. Parked up. / At Castletown I point him at slipway; hire car goes in, handbrake off. No drama. / He gets a lift off a stranger; karma. / I ride north into Donegal ignoring my phone; a farmer waves. / Quiet as bedroom before the alarm.
    after:  Says I'm on list; I clocked my partner. / Full Irish done, bike locked. / My boat leaves Douglas, his docks; he hires a car. Harbour. / He follows up the coast past Laxey Wheel, blocks me in. Parked up. / At Castletown I point him at slipway; hire car goes in, handbrake off. No drama. / He gets a lift off a stranger; karma. / I ride north into Donegal ignoring my phone; a farmer waves. / Quiet as bedroom before the alarm.
  bar loop (8 calls): bar 1: ends |w, needs |Sw; 2 variants tried -> repaired | bar 2: ends |S, needs |Sww; 5 variants tried -> no passing variant, left as it w | bar 3: 15 syllables for a target of 11; 23 variants tried -> no passing variant, | bar 4: 15 syllables for a target of 11; 13 variants tried -> no passing variant, | bar 5: 21 syllables for a target of 11; 9 variants tried -> no passing variant,  | bar 6: 12 syllables for a target of 10; 17 variants tried -> no passing variant, | bar 7: 18 syllables for a target of 10; 12 variants tried -> no passing variant, | bar 8: ends ~S, needs |SwS; 14 variants tried -> no passing variant, left as it 
    before: Says I'm on his list; I clocked him. / Full Irish done, bike locked. / My boat leaves Douglas, his docks; he hires a car. Harbour. / He follows up the coast past Laxey Wheel, blocks me in. Parked up. / At Castletown I point him at slipway; hire car goes in, handbrake off. No drama. / He gets a lift off a stranger; karma. / I ride north into Donegal ignoring my phone; a farmer waves. / Quiet as bedroom before the alarm.
    after:  Says I'm on list; I clocked the marker. / Full Irish done, bike locked. / My boat leaves Douglas, his docks; he hires a car. Harbour. / He follows up the coast past Laxey Wheel, blocks me in. Parked up. / At Castletown I point him at slipway; hire car goes in, handbrake off. No drama. / He gets a lift off a stranger; karma. / I ride north into Donegal ignoring my phone; a farmer waves. / Quiet as bedroom before the alarm.
  --- taken:
  1. Says I'm on list; I clocked my partner.
  2. Full Irish done, bike locked.
  3. My boat leaves Douglas, his docks; he hires a car. Harbour.
  4. He follows up the coast past Laxey Wheel, blocks me in. Parked up.
  5. At Castletown I point him at slipway; hire car goes in, handbrake off. No drama.
  6. He gets a lift off a stranger; karma.
  7. I ride north into Donegal ignoring my phone; a farmer waves.
  8. Quiet as bedroom before the alarm.

## V1 25-32 -- BUILT, FAILS the plan gate
argument: The stallholder gave me a special price just for me and I paid sixty, and in Bergen my slippers go by the door.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/4 frame problems=13 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: settle, special
  candidate frame fail: bar 3: 10 syl (need 14+-1)
  candidate frame fail: bar 5: 7 syl (need 9+-1)
  bar loop (7 calls): bar 1: 9 syllables for a target of 13; 0 variants tried -> repaired | bar 2: 12 syllables for a target of 15; 13 variants tried -> repaired | bar 3: 10 syllables for a target of 14; 10 variants tried -> no passing variant, | bar 5: 7 syllables for a target of 9; 9 variants tried -> no passing variant, le | bar 6: 13 syllables for a target of 9; 2 variants tried -> repaired | bar 7: ends |Sw, needs |w; 11 variants tried -> no passing variant, left as it w | bar 8: 10 syllables for a target of 15; 4 variants tried -> repaired
    before: Marrakesh souk, stall man says special. / Eighty dirhams for the leather, then he'll settle. / I pay sixty, he says ta, rose petal. / Mint tea kettle's on, my mate's kettle. / Bergen door, shoes off, footpath. / Leather slippers by the door, on the mat, no special. / Three Christmases, one trip, that's the level. / Koh Tao skipper says sixty, no settle.
    after:  At the souk the stall man says that price is special. / Eighty dirhams for the leather, he says, then he'll settle. / I pay sixty, he says ta, rose petal. / Mint tea kettle's on, my mate's kettle. / Bergen door, shoes off, footpath. / Slippers on the mat, no special. / Three Christmases, one trip, that's the level. / Koh Tao skipper says sixty, that's the final, no settle.
  bar loop (7 calls): bar 1: 8 syllables for a target of 13; 4 variants tried -> repaired | bar 2: 11 syllables for a target of 15; 4 variants tried -> no passing variant,  | bar 3: 9 syllables for a target of 14; 16 variants tried -> no passing variant,  | bar 5: 7 syllables for a target of 9; 9 variants tried -> no passing variant, le | bar 6: 11 syllables for a target of 9; 0 variants tried -> repaired | bar 7: ends |Sw, needs |w; 21 variants tried -> no passing variant, left as it w | bar 8: 10 syllables for a target of 15; 9 variants tried -> no passing variant, 
    before: Stall man in the souk says special. / Eighty dirhams for slippers, then he'll settle. / Sixty paid, he thanks me, rose petal. / Kettle's on, that's my mate's kettle. / Bergen door, shoes off, footpath. / Marrakesh slippers on the mat, no special. / Three Christmases, one trip, that's the level. / Koh Tao skipper says sixty, no settle.
    after:  The stall man in the souk says that's a special. / Eighty dirhams for slippers, then he'll settle. / Sixty paid, he thanks me, rose petal. / Kettle's on, that's my mate's kettle. / Bergen door, shoes off, footpath. / Marrakesh slippers on mat, no special. / Three Christmases, one trip, that's the level. / Koh Tao skipper says sixty, no settle.
  --- taken:
  1. At the souk the stall man says that price is special.
  2. Eighty dirhams for the leather, he says, then he'll settle.
  3. I pay sixty, he says ta, rose petal.
  4. Mint tea kettle's on, my mate's kettle.
  5. Bergen door, shoes off, footpath.
  6. Slippers on the mat, no special.
  7. Three Christmases, one trip, that's the level.
  8. Koh Tao skipper says sixty, that's the final, no settle.

## V1 33-44 -- BUILT, FAILS the plan gate
lore_allusion 'Table service': structurally OK | triggers in the bars: ['order', 'waiter', 'tipping', 'waiter'] | in a rhyme slot: True
argument: Asked about a car in a harbour I treated the custody desk like a restaurant, my cousin forged the gnome's receipt, and the debtor keeps his head down.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=3/5 frame problems=26 syllable misses=9
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: adjust, dust, just
  candidate frame fail: bar 1: 10 syl (need 6+-1)
  candidate frame fail: bar 1: ends |S (need |w)
  bar loop (10 calls): bar 1: 10 syllables for a target of 6; 13 variants tried -> no passing variant,  | bar 2: 15 syllables for a target of 9; 8 variants tried -> repaired | bar 3: 11 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 4: 13 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 5: 13 syllables for a target of 5; 12 variants tried -> no passing variant,  | bar 6: 11 syllables for a target of 9; 0 variants tried -> repaired | bar 7: ends |S, needs ~w; 19 variants tried -> no passing variant, left as it wa | bar 8: 12 syllables for a target of 10; 0 variants tried -> repaired | bar 9: 13 syllables for a target of 7; 13 variants tried -> no passing variant,  | bar 10: ends ~S, needs |S; 22 variants tried -> no passing variant, left as it w | bar 11: not attempted (call budget 10 reached) | bar 12: not attempted (call budget 10 reached)
    before: At the desk they want my name, address, weight. / I treat the sergeant like a waiter bringing the menu. / He asks: anything to declare? I say just. / Vehicle in harbour reason: tidal. He writes bust. / My cousin knocks up receipt with stamp and Tipp-Ex, just. / Paper says the gnome went back. The gnome stays, dust. / The gnome stays in my garden gathering rust. / I keep his trust while the gnome sits and gathers dust. / The debtor went bust; I had the bust of his head, just. / The bust sits on the shelf; I give him adjust. / On Thursdays I tap him on the shoulder lightly, adjust. / He keeps his head down and I keep his trust.
    after:  At the desk they want my name, address, weight. / I treat the sergeant like waiter, order. / He asks: anything to declare? I say just. / Vehicle in harbour reason: tidal. He writes bust. / My cousin knocks up receipt with stamp and Tipp-Ex, just. / Paper says gnome went back. The gnome stays, dust. / The gnome stays in my garden gathering rust. / I keep trust while the gnome sits and gathers dust. / The debtor went bust; I had the bust of his head, just. / The bust sits on the shelf; I give him adjust. / On Thursdays I tap him on the shoulder lightly, adjust. / He keeps his head down and I keep his trust.
  bar loop (10 calls): bar 1: 10 syllables for a target of 6; 7 variants tried -> no passing variant, l | bar 2: 14 syllables for a target of 9; 5 variants tried -> repaired | bar 3: 12 syllables for a target of 7; 13 variants tried -> no passing variant,  | bar 4: 14 syllables for a target of 7; 7 variants tried -> no passing variant, l | bar 5: 14 syllables for a target of 5; 18 variants tried -> no passing variant,  | bar 6: 12 syllables for a target of 9; 4 variants tried -> repaired | bar 7: ends |S, needs ~w; 22 variants tried -> no passing variant, left as it wa | bar 8: verifier: grammar: unresolved_pronoun:his; 0 variants tried -> repaired | bar 9: 14 syllables for a target of 7; 13 variants tried -> no passing variant,  | bar 10: 14 syllables for a target of 11; 18 variants tried -> no passing variant | bar 11: not attempted (call budget 10 reached) | bar 12: not attempted (call budget 10 reached) | pass reverted: the section did not improve (frame 29 -> 32, cashed 3 -> 3)
  --- taken:
  1. At the desk they want my name, address, weight.
  2. I treat the sergeant like waiter, order.
  3. He asks: anything to declare? I say just.
  4. Vehicle in harbour reason: tidal. He writes bust.
  5. My cousin knocks up receipt with stamp and Tipp-Ex, just.
  6. Paper says gnome went back. The gnome stays, dust.
  7. The gnome stays in my garden gathering rust.
  8. I keep trust while the gnome sits and gathers dust.
  9. The debtor went bust; I had the bust of his head, just.
  10. The bust sits on the shelf; I give him adjust.
  11. On Thursdays I tap him on the shoulder lightly, adjust.
  12. He keeps his head down and I keep his trust.

## V2 1-8 -- BUILT, passes the plan gate
lore_allusion 'Fred Olsen': NOT met: only 1 distinct trigger(s) from the card (cruise, cruise); need >= 2 | triggers in the bars: ['cruise', 'cruise'] | in a rhyme slot: True
argument: My partners look like accountants because they are, the damage is done in a spreadsheet, and the gnome has the reception in Zurich.
generated 10 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=3/3 frame problems=10 syllable misses=6
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 4: ends |S (need |w)
  candidate frame fail: bar 7: 4 syl (need 11+-1)
  bar loop (5 calls): bar 1: 16 syllables for a target of 11; 4 variants tried -> repaired | bar 2: 14 syllables for a target of 11; 0 variants tried -> repaired | bar 4: 8 syllables for a target of 10; 7 variants tried -> no passing variant, l | bar 7: 4 syllables for a target of 11; 1 variants tried -> repaired | bar 8: 14 syllables for a target of 9; 12 variants tried -> no passing variant, 
    before: I have a partner in every stop and I pay my dues / Cardigans, lanyards, a calculator, none make news / The gnome on reception greets the queues / No weapon among them, no bruise / Nothing to call the police on, no clues / The annual audit is a booze cruise / Every Tues- / -day somebody gets audited, I wouldn't want his shoes
    after:  Partner at every stop, I pay my dues / Cardigans, lanyards, calculator, none make news / The gnome on reception greets the queues / No weapon among them, no bruise / Nothing to call the police on, no clues / The annual audit is a booze cruise / Every Tuesday, audit splits the word in two / -day somebody gets audited, I wouldn't want his shoes
  bar loop (5 calls): bar 1: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 3: 7 syllables for a target of 10; 2 variants tried -> repaired | bar 4: ends |S, needs |w; 11 variants tried -> no passing variant, left as it wa | bar 7: 4 syllables for a target of 11; 9 variants tried -> no passing variant, l | bar 8: 14 syllables for a target of 9; 8 variants tried -> no passing variant, l
    before: A partner in every stop, I pay my dues / Cardigans, lanyards, calculator, never news / The Zurich gnome greets the queues / No weapon among them, so no bruise / Nothing to call the police on, no clues / The annual audit is a booze cruise / Every Tues- / -day somebody gets audited, I wouldn't want his shoes
    after:  Partner in every stop, I pay my dues / Cardigans, lanyards, calculator, never news / The gnome in Zurich greets the queues true. / No weapon among them, so no bruise / Nothing to call the police on, no clues / The annual audit is a booze cruise / Every Tues- / -day somebody gets audited, I wouldn't want his shoes
  --- taken:
  1. Partner in every stop, I pay my dues
  2. Cardigans, lanyards, calculator, never news
  3. The gnome in Zurich greets the queues true.
  4. No weapon among them, so no bruise
  5. Nothing to call the police on, no clues
  6. The annual audit is a booze cruise
  7. Every Tues-
  8. -day somebody gets audited, I wouldn't want his shoes

## V2 9-16 -- BUILT, passes the plan gate
lore_allusion 'House of the Dead': NOT met: only 1 distinct trigger(s) from the card (shot); need >= 2 | triggers in the bars: ['shot'] | in a rhyme slot: False
argument: A rival came for the firm so I settled it at the snooker table, and he never left the baize.
generated 3 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=1/3 frame problems=27 syllable misses=7
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: 9 syl (need 6+-1)
  candidate frame fail: bar 2: 23 syl (need 12+-1)
  bar loop (8 calls): bar 1: 9 syllables for a target of 6; 1 variants tried -> no passing variant, le | bar 2: 23 syllables for a target of 12; 1 variants tried -> no passing variant,  | bar 3: 13 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 4: 13 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 5: 17 syllables for a target of 8; 1 variants tried -> no passing variant, l | bar 6: 15 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 7: 12 syllables for a target of 9; 1 variants tried -> repaired | bar 8: 16 syllables for a target of 12; 1 variants tried -> no passing variant, 
    before: Debtor chalks my cue, still in the plot. / The accountant keeps the score; I rack the balls and ask the rival to keep a steady hand. / I put the black on its spot and the rival goes dead. / I lay the rival out on the bed of the table. / A pot shot: a shot at the pot, a man in the pocket. / Potted the rival on the spot; the black goes down on its spot. / Mum rings mid-frame and thinks it is all a game. / The rival had a plot; I had one reserved, with a view.
    after:  Debtor chalks my cue, still in the plot. / The accountant keeps the score; I rack the balls and ask the rival to keep a steady hand. / I put the black on its spot and the rival goes dead. / I lay the rival out on the bed of the table. / A pot shot: a shot at the pot, a man in the pocket. / Potted the rival on the spot; the black goes down on its spot. / Mum rings mid-frame and thinks it is all game. / The rival had a plot; I had one reserved, with a view.
  bar loop (8 calls): bar 1: 9 syllables for a target of 6; 12 variants tried -> no passing variant, l | bar 2: 23 syllables for a target of 12; 26 variants tried -> no passing variant, | bar 3: 14 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 4: 14 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 5: 13 syllables for a target of 8; 1 variants tried -> no passing variant, l | bar 6: 17 syllables for a target of 10; 1 variants tried -> no passing variant,  | bar 7: 12 syllables for a target of 9; 1 variants tried -> repaired | bar 8: 16 syllables for a target of 12; 1 variants tried -> no passing variant, 
    before: Debtor chalks my cue, still in the shot. / The accountant keeps the score; I rack the balls and ask the rival to keep a steady hand. / I put the black on its spot and the rival goes dead still. / The dead ball: I put the black on its spot and he goes dead. / I lay the rival out on the bed of the table. / A pot shot: a shot at the pot, a man in the pocket. / Mum rings mid-frame and thinks it is all a game. / The rival had a plot; I had one reserved, with a view.
    after:  Debtor chalks my cue, still in the shot. / The accountant keeps the score; I rack the balls and ask the rival to keep a steady hand. / I put the black on its spot and the rival goes dead still. / The dead ball: I put the black on its spot and he goes dead. / I lay the rival out on the bed of the table. / A pot shot: a shot at the pot, a man in the pocket. / Mum rings mid-frame and thinks it is all game. / The rival had a plot; I had one reserved, with a view.
  stage errors: plot: n=3 RuntimeError: deepseek 402: {"error":{"message":"Insufficient Balance (request_id: 1eb1d3b2-8a27-44a
  stage errors: plot: n=1 RuntimeError: deepseek 402: {"error":{"message":"Insufficient Balance (request_id: 903885cf-666b-4d4
  stage errors: shot: n=3 RuntimeError: deepseek 402: {"error":{"message":"Insufficient Balance (request_id: d7e5f7d1-e911-430
  --- taken:
  1. Debtor chalks my cue, still in the plot.
  2. The accountant keeps the score; I rack the balls and ask the rival to keep a steady hand.
  3. I put the black on its spot and the rival goes dead.
  4. I lay the rival out on the bed of the table.
  5. A pot shot: a shot at the pot, a man in the pocket.
  6. Potted the rival on the spot; the black goes down on its spot.
  7. Mum rings mid-frame and thinks it is all game.
  8. The rival had a plot; I had one reserved, with a view.
