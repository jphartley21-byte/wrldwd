# build report (incumbent: (none: built from scratch))

spend on seeds this build: $0.0991 (block and ranking calls are in eval/ledger)

## Hook 1-4 -- BUILT, passes the plan gate
lore_allusion 'Athletic Bilbao': structurally OK | triggers in the bars: ['badge', 'shirt'] | in a rhyme slot: True
argument: I touch down in a new port, greet it in its own language, deal with one petty bit of paperwork, and am gone again to the next place before the hook is over.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=1/2 frame problems=10 syllable misses=2
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 2: 12 syl (need 9+-1)
  candidate frame fail: bar 2: ends |S (need ~Sw)
  bar loop (3 calls): bar 1: ends ~S, needs |Sw; 3 variants tried -> repaired | bar 2: 12 syllables for a target of 9; 9 variants tried -> no passing variant, l | bar 3: 11 syllables for a target of 9; 0 variants tried -> repaired
    before: Kaixo, Bilbao / I'm here on tour to collect one lion badge shirt / The counter wants the form, and that's it for now / Next port, one channel ferry, standard fare
    after:  Kaixo, Bilbao city / I'm here on tour to collect one lion badge shirt / Counter wants the form, and that's it for now / Next port, one channel ferry, standard fare
  bar loop (2 calls): bar 1: ends ~S, needs |Sw; 5 variants tried -> no passing variant, left as it wa | bar 2: 11 syllables for a target of 9; 6 variants tried -> no passing variant, l
  --- taken:
  1. Kaixo, Bilbao city
  2. I'm here on tour to collect one lion badge shirt
  3. Counter wants the form, and that's it for now
  4. Next port, one channel ferry, standard fare

## Hook 5-8 -- BUILT, passes the plan gate
lore_allusion 'Take a Break': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: The council wants its gnome back and I am not sorry, because it came off the back of a lorry.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=3/4 frame problems=3 syllable misses=0
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: scheme ABBA: bars 1 & 4 must rhyme but score 0.0
  candidate frame fail: end-rhyme carpet 3/6 rhyme; the original holds 6/6 (need >= 5): too many bars fall off the rhyme family
  bar loop (1 calls): bar 2: 12 syllables for a target of 10; 0 variants tried -> repaired
    before: Hoi Rotterdam, gnome in my lobby. / Council man wants gnome back, I read it, not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
    after:  Hoi Rotterdam, gnome in my lobby. / Council wants gnome back, I read it, not sorry. / Came off back of a lorry. / Might lie low in Oslo, pardon.
  bar loop (1 calls): bar 2: 12 syllables for a target of 10; 5 variants tried -> no passing variant, 
  --- taken:
  1. Hoi Rotterdam, gnome in my lobby.
  2. Council wants gnome back, I read it, not sorry.
  3. Came off back of a lorry.
  4. Might lie low in Oslo, pardon.

## Hook 9-16 -- BUILT, FAILS the plan gate
lore_allusion 'Four in a Bed': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: A man who owes me bread had his page ruled in red biro, and I took him to Boomtown, where he lost his head.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=13 syllable misses=2
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: head
  candidate frame fail: bar 1: 9 syl (need 7+-1)
  candidate frame fail: bar 1: grammar unresolved_pronoun:his
  bar loop (6 calls): bar 1: 10 syllables for a target of 7; 11 variants tried -> no passing variant,  | bar 2: 11 syllables for a target of 9; 10 variants tried -> no passing variant,  | bar 3: ends |S, needs ~Sw; 17 variants tried -> no passing variant, left as it w | bar 4: 11 syllables for a target of 9; 16 variants tried -> no passing variant,  | bar 5: 16 syllables for a target of 12; 15 variants tried -> no passing variant, | bar 8: end word 'head' is used more than once in this block; 1 variants tried -> | pass reverted: the section did not improve (frame 16 -> 16, cashed 2 -> 2)
  bar loop (6 calls): bar 1: 9 syllables for a target of 7; 4 variants tried -> no passing variant, le | bar 2: verifier: grammar: unresolved_pronoun:him; 7 variants tried -> no passing | bar 3: ends |S, needs ~Sw; 14 variants tried -> no passing variant, left as it w | bar 4: 11 syllables for a target of 9; 17 variants tried -> no passing variant,  | bar 5: 16 syllables for a target of 12; 3 variants tried -> repaired | bar 8: end word 'head' is used more than once in this block; 1 variants tried ->
    before: His page in red biro, he owes bread. / I gave him till Friday, as I said. / Took him and the lads to Boomtown, head. / At the wooden guillotine, he lost his head. / Nobody noticed; a steward asked about a wristband. / The blade came down. / I entered one head, less the fee. / A clean cut to the head.
    after:  His page in red biro, he owes bread. / I gave him till Friday, as I said. / Took him and the lads to Boomtown, head. / At the wooden guillotine, he lost his head. / Nobody noticed; steward asked about the pass. / The blade came down. / I entered one head, less the fee. / A clean cut to head.
  --- taken:
  1. His page in red biro, he owes bread.
  2. I gave him till Friday, as I said.
  3. Took him and the lads to Boomtown, head.
  4. At the wooden guillotine, he lost his head.
  5. Nobody noticed; steward asked about the pass.
  6. The blade came down.
  7. I entered one head, less the fee.
  8. A clean cut to head.

## V1 1-8 -- BUILT, FAILS the plan gate
lore_allusion 'P&O': NOT met: only 1 distinct trigger(s) from the card (ferry); need >= 2 | triggers in the bars: ['ferry'] | in a rhyme slot: True
argument: The boat waits for me, the hosts thank me, and Mum thinks I work in IT.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/5 frame problems=11 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: perry
  candidate frame fail: bar 4: 12 syl (need 9+-1)
  candidate frame fail: bar 7: 12 syl (need 7+-1)
  bar loop (8 calls): bar 1: 12 syllables for a target of 10; 0 variants tried -> repaired | bar 2: end word 'perry' is used more than once in this block; 0 variants tried - | bar 3: 12 syllables for a target of 8; 2 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 17 variants tried -> no passing variant,  | bar 5: 8 syllables for a target of 6; 5 variants tried -> no passing variant, le | bar 6: 11 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 7: 12 syllables for a target of 7; 8 variants tried -> no passing variant, l | bar 8: 23 syllables for a target of 13; 18 variants tried -> no passing variant,
    before: I turn up late; the ferry waits for me, very. / The deckhand holds the ramp, paid in perry. / A host in Spain leaves a case of sherry. / In Norway, a host sets a place for me. / Bergen says 'Takk'; I answer 'ta'. / Twelve stops in four weeks, one pass validated. / Mum thinks I work in IT, but I work in perry. / The conductors never asked what the pass was for, any of the twelve times; it lands in Kerry.
    after:  I turn up late; ferry waits for me, very. / Deckhand holds the ramp, paid in perry. / A host in Spain leaves plenty. / In Norway, a host sets a place for me. / Bergen says 'Takk'; I answer 'ta'. / Twelve stops in four weeks, one pass validated. / Mum thinks I work in IT, but I work in perry. / The conductors never asked what the pass was for, any of the twelve times; it lands in Kerry.
  bar loop (6 calls): bar 2: end word 'perry' is used more than once in this block; 0 variants tried - | bar 3: 12 syllables for a target of 8; 3 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 20 variants tried -> no passing variant,  | bar 5: 8 syllables for a target of 6; 1 variants tried -> repaired | bar 7: 12 syllables for a target of 7; 6 variants tried -> no passing variant, l | bar 8: 23 syllables for a target of 13; 3 variants tried -> repaired
    before: The boat waits; I turn up late for the ferry. / The deckhand holds the ramp, paid in perry. / A host in Spain leaves a case of sherry. / In Norway, a host sets a place for me. / Bergen says 'Takk'; I answer 'ta'. / Twelve stops in four weeks, one pass buried. / Mum thinks I work in IT, but I work in perry. / The conductors never asked what the pass was for, any of the twelve times; it lands in Kerry.
    after:  The boat waits; I turn up late for the ferry. / Deckhand holds the ramp, paid in perry. / A host in Spain leaves my sherry. / In Norway, a host sets a place for me. / Bergen says takk; ta, ready. / Twelve stops in four weeks, one pass buried. / Mum thinks I work in IT, but I work in perry. / Conductors never checked the pass in twelve trips to Kerry.
  --- taken:
  1. The boat waits; I turn up late for the ferry.
  2. Deckhand holds the ramp, paid in perry.
  3. A host in Spain leaves my sherry.
  4. In Norway, a host sets a place for me.
  5. Bergen says takk; ta, ready.
  6. Twelve stops in four weeks, one pass buried.
  7. Mum thinks I work in IT, but I work in perry.
  8. Conductors never checked the pass in twelve trips to Kerry.

## V1 9-16 -- BUILT, passes the plan gate
lore_allusion 'Dial-a-ride': structurally OK | triggers in the bars: ['bus', 'bus pass'] | in a rhyme slot: False
argument: I came up with nothing but a bus pass, I own a quarry and I am known worldwide; thank you for applying, we know where you reside.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=5/5 frame problems=15 syllable misses=6
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: 14 syl (need 7+-1)
  candidate frame fail: bar 1: ends |S (need |w)
  bar loop (7 calls): bar 1: 14 syllables for a target of 7; 9 variants tried -> no passing variant, l | bar 2: 12 syllables for a target of 6; 4 variants tried -> no passing variant, l | bar 4: ends |SS, needs |S; 16 variants tried -> no passing variant, left as it w | bar 5: 17 syllables for a target of 12; 21 variants tried -> no passing variant, | bar 6: 15 syllables for a target of 10; 2 variants tried -> repaired | bar 7: 16 syllables for a target of 12; 5 variants tried -> repaired | bar 8: 6 syllables for a target of 11; 6 variants tried -> no passing variant, l
    before: Reading, rented room, and a bus pass for a ride / Nothing to my name, just a rail card and pride / Never laid a brick / The mayor's invoice made me known: the single worldwide / An old acquaintance applies; the vacancy is for the mayor's bride / Keep your details on file at the bottom of the quarry slide / Your interview is a rough ride, and the dumper has no guide / We know where you reside
    after:  Reading, rented room, and a bus pass for a ride / Nothing to my name, just a rail card and pride / Never laid a brick / The mayor's invoice made me known: the single worldwide / An old acquaintance applies; the vacancy is for the mayor's bride / Your details on file at the quarry slide / Your interview is a rough ride, no guide. / We know where you reside
  bar loop (7 calls): bar 1: 13 syllables for a target of 7; 8 variants tried -> no passing variant, l | bar 2: 12 syllables for a target of 6; 17 variants tried -> no passing variant,  | bar 4: ends |SS, needs |S; 13 variants tried -> no passing variant, left as it w | bar 5: 17 syllables for a target of 12; 23 variants tried -> no passing variant, | bar 6: 15 syllables for a target of 10; 12 variants tried -> no passing variant, | bar 7: 16 syllables for a target of 12; 3 variants tried -> repaired | bar 8: 6 syllables for a target of 11; 15 variants tried -> no passing variant, 
    before: Reading, rented room, and a bus pass for the ride / Nothing to my name, just a rail card and pride / Never laid a brick / The mayor's invoice made me known: the single worldwide / An old acquaintance applies; the vacancy is for the mayor's bride / Keep your details on file at the bottom of the quarry slide / Your interview is a rough ride, and the dumper has no guide / We know where you reside
    after:  Reading, rented room, and a bus pass for the ride / Nothing to my name, just a rail card and pride / Never laid a brick / The mayor's invoice made me known: the single worldwide / An old acquaintance applies; the vacancy is for the mayor's bride / Keep your details on file at the bottom of the quarry slide / Your interview is a rough ride, no guide. / We know where you reside
  --- taken:
  1. Reading, rented room, and a bus pass for a ride
  2. Nothing to my name, just a rail card and pride
  3. Never laid a brick
  4. The mayor's invoice made me known: the single worldwide
  5. An old acquaintance applies; the vacancy is for the mayor's bride
  6. Your details on file at the quarry slide
  7. Your interview is a rough ride, no guide.
  8. We know where you reside

## V1 17-24 -- BUILT, passes the plan gate
argument: A man from Dublin wanted what I owed him and chased me over the Irish Sea, and the island did the rest.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/3 frame problems=28 syllable misses=7
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: 12 syl (need 9+-1)
  candidate frame fail: bar 2: 10 syl (need 7+-1)
  bar loop (8 calls): bar 1: 12 syllables for a target of 9; 4 variants tried -> repaired | bar 2: 10 syllables for a target of 7; 6 variants tried -> no passing variant, l | bar 3: 15 syllables for a target of 11; 23 variants tried -> no passing variant, | bar 4: ends |ww, needs |Sww; 8 variants tried -> no passing variant, left as it  | bar 5: 15 syllables for a target of 11; 11 variants tried -> no passing variant, | bar 6: 19 syllables for a target of 10; 15 variants tried -> no passing variant, | bar 7: 18 syllables for a target of 10; 14 variants tried -> no passing variant, | bar 8: ends ~S, needs |SwS; 17 variants tried -> no passing variant, left as it  | pass reverted: the section did not improve (frame 28 -> 30, cashed 2 -> 2)
  bar loop (8 calls): bar 1: 12 syllables for a target of 9; 5 variants tried -> repaired | bar 2: 10 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 3: 15 syllables for a target of 11; 17 variants tried -> no passing variant, | bar 4: ends |ww, needs |Sww; 7 variants tried -> no passing variant, left as it  | bar 5: 15 syllables for a target of 11; 10 variants tried -> no passing variant, | bar 6: 19 syllables for a target of 10; 16 variants tried -> no passing variant, | bar 7: 18 syllables for a target of 10; 12 variants tried -> no passing variant, | bar 8: ends ~S, needs |SwS; 16 variants tried -> no passing variant, left as it  | pass reverted: the section did not improve (frame 28 -> 29, cashed 2 -> 2)
  --- taken:
  1. Dublin cafe, said I'm on his list, I clocked him.
  2. Full Irish finished, bike locked, no drama.
  3. My boat leaves Douglas on time, his docks, he hires a car.
  4. Follows up the coast past Laxey Wheel, blocks me in.
  5. Castletown harbour, I point him at the slipway, handbrake off.
  6. He gets a lift off a stranger, karma, customer service reply.
  7. I ride north into Donegal, ignoring my phone, a farmer waves.
  8. Quiet as the bedroom before the alarm.

## V1 25-32 -- BUILT, FAILS the plan gate
argument: The stallholder gave me a special price just for me and I paid sixty, and in Bergen my slippers go by the door.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/4 frame problems=19 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: kettle
  candidate frame fail: bar 2: 12 syl (need 15+-1)
  candidate frame fail: bar 3: 12 syl (need 14+-1)
  bar loop (8 calls): bar 1: end word 'kettle' is used more than once in this block; 0 variants tried  | bar 2: 12 syllables for a target of 15; 11 variants tried -> no passing variant, | bar 3: 12 syllables for a target of 14; 18 variants tried -> no passing variant, | bar 4: end word 'kettle' is used more than once in this block; 0 variants tried  | bar 5: 11 syllables for a target of 9; 12 variants tried -> no passing variant,  | bar 6: 12 syllables for a target of 9; 3 variants tried -> repaired | bar 7: ends |S, needs |w; 11 variants tried -> no passing variant, left as it wa | bar 8: 18 syllables for a target of 15; 2 variants tried -> repaired
    before: Stall man in the souk says special price just for kettle. / I say forty, he says sixty, and we settle. / I pay the sixty and he thanks me, rose petal. / My mate put in for a kettle. / Bergen, at the in-laws' door the shoes come off. / The leather slippers sit on the mat by the door. / Three Christmases, one trip a year. / Koh Tao, I ask the dive skipper the price of a day, he says sixty.
    after:  Stall man in souk says special price just for kettle. / I say forty, he says sixty, and we settle. / I pay the sixty and he thanks me, rose petal. / Mate put in for a kettle. / Bergen, at the in-laws' door the shoes come off. / Slippers sit at the door, on the level. / Three Christmases, one trip a year. / Koh Tao, I ask the dive skipper the price of day, he says sixty.
  bar loop (8 calls): bar 1: 11 syllables for a target of 13; 22 variants tried -> no passing variant, | bar 2: 13 syllables for a target of 15; 8 variants tried -> no passing variant,  | bar 3: 11 syllables for a target of 14; 18 variants tried -> no passing variant, | bar 4: end word 'kettle' is used more than once in this block; 0 variants tried  | bar 5: 11 syllables for a target of 9; 11 variants tried -> no passing variant,  | bar 6: 12 syllables for a target of 9; 15 variants tried -> no passing variant,  | bar 7: ends |S, needs |w; 6 variants tried -> no passing variant, left as it was | bar 8: 18 syllables for a target of 15; 2 variants tried -> repaired
    before: The stall man in the souk opens with kettle. / I say forty, he says sixty, final, we settle. / I pay sixty and he thanks me, rose petal. / My mate put in for a kettle. / Bergen, at the in-laws' door the shoes come off. / The leather slippers sit on the mat by the door. / Three Christmases, one trip a year. / Koh Tao, I ask the dive skipper the price of a day, he says sixty.
    after:  The stall man in the souk opens with kettle. / I say forty, he says sixty, final, we settle. / I pay sixty and he thanks me, rose petal. / Mate put in for a kettle. / Bergen, at the in-laws' door the shoes come off. / The leather slippers sit on the mat by the door. / Three Christmases, one trip a year. / Koh Tao, I ask the dive skipper the price of day, he says sixty.
  --- taken:
  1. Stall man in souk says special price just for kettle.
  2. I say forty, he says sixty, and we settle.
  3. I pay the sixty and he thanks me, rose petal.
  4. Mate put in for a kettle.
  5. Bergen, at the in-laws' door the shoes come off.
  6. Slippers sit at the door, on the level.
  7. Three Christmases, one trip a year.
  8. Koh Tao, I ask the dive skipper the price of day, he says sixty.

## V1 33-44 -- BUILT, FAILS the plan gate
argument: Asked about a car in a harbour I treated the custody desk like a restaurant, my cousin forged the gnome's receipt, and the debtor keeps his head down.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/5 frame problems=25 syllable misses=10
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: dust, just, trust
  candidate frame fail: bar 1: 10 syl (need 6+-1)
  candidate frame fail: bar 2: 11 syl (need 9+-1)
  bar loop (10 calls): bar 1: 10 syllables for a target of 6; 5 variants tried -> no passing variant, l | bar 2: 11 syllables for a target of 9; 5 variants tried -> no passing variant, l | bar 3: 9 syllables for a target of 7; 5 variants tried -> no passing variant, le | bar 4: 11 syllables for a target of 7; 0 variants tried -> repaired | bar 5: 3 syllables for a target of 5; 7 variants tried -> no passing variant, le | bar 6: 12 syllables for a target of 9; 2 variants tried -> repaired | bar 7: ends |S, needs ~w; 17 variants tried -> no passing variant, left as it wa | bar 8: 8 syllables for a target of 10; 8 variants tried -> repaired | bar 9: 5 syllables for a target of 7; 10 variants tried -> no passing variant, l | bar 10: ends ~S, needs |S; 12 variants tried -> no passing variant, left as it w | bar 11: not attempted (call budget 10 reached) | bar 12: not attempted (call budget 10 reached) | pass reverted: the section did not improve (frame 25 -> 32, cashed 2 -> 2)
  bar loop (10 calls): bar 1: 10 syllables for a target of 6; 5 variants tried -> no passing variant, l | bar 2: 11 syllables for a target of 9; 5 variants tried -> no passing variant, l | bar 3: 9 syllables for a target of 7; 5 variants tried -> no passing variant, le | bar 4: 11 syllables for a target of 7; 7 variants tried -> no passing variant, l | bar 5: 3 syllables for a target of 5; 5 variants tried -> no passing variant, le | bar 6: 12 syllables for a target of 9; 8 variants tried -> no passing variant, l | bar 7: ends |S, needs ~w; 17 variants tried -> no passing variant, left as it wa | bar 8: 8 syllables for a target of 10; 2 variants tried -> repaired | bar 9: 5 syllables for a target of 7; 5 variants tried -> no passing variant, le | bar 10: ends ~S, needs |S; 12 variants tried -> no passing variant, left as it w | bar 11: not attempted (call budget 10 reached) | bar 12: not attempted (call budget 10 reached) | pass reverted: the section did not improve (frame 25 -> 29, cashed 2 -> 2)
  --- taken:
  1. At Bristol desk, sergeant asks for data.
  2. He wants name, address, date of birth, weight, waiter.
  3. Anything to declare? He nods, just.
  4. Reason for vehicle in harbour: tidal.
  5. He writes dust.
  6. Cousin the signwriter knocks up receipt with rust.
  7. The paper says the gnome went back, trust.
  8. The gnome stays in my garden, dust.
  9. Debtor went bust, just.
  10. Had the bust of his head done, sits on shelf, adjust.
  11. On Thursdays I tap him on the shoulder, lightly.
  12. He keeps his head down and I keep his trust.

## V2 1-8 -- BUILT, passes the plan gate
argument: My partners look like accountants because they are, the damage is done in a spreadsheet, and the gnome has the reception in Zurich.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=1/3 frame problems=25 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 2: 27 syl (need 11+-1)
  candidate frame fail: bar 4: 31 syl (need 10+-1)
  bar loop (7 calls): bar 1: 20 syllables for a target of 11; 5 variants tried -> repaired | bar 2: 27 syllables for a target of 11; 9 variants tried -> no passing variant,  | bar 3: 19 syllables for a target of 10; 3 variants tried -> repaired | bar 4: 31 syllables for a target of 10; 15 variants tried -> no passing variant, | bar 6: 23 syllables for a target of 12; 5 variants tried -> repaired | bar 7: 4 syllables for a target of 11; 4 variants tried -> repaired | bar 8: 28 syllables for a target of 9; 10 variants tried -> no passing variant, 
    before: I have a partner in every stop on the rail pass, and I pay my dues. / Cardigans, lanyards, a calculator with a paper roll; none of them has ever been in the news. / The Zurich accountant keeps the stolen gnome on reception to greet the queues. / There is not a weapon among them: the damage is done in a spreadsheet, and nobody has ever shown a bruise. / There is nothing to call the police on; no clues. / The annual audit is a booze cruise: the firm's away day, with the ledgers in the hold. / Every Tues- / -day somebody gets audited and I wouldn't want to be in his shoes; the shoes are by the door, as in Bergen.
    after:  Partner in every stop, dues paid and used. / Cardigans, lanyards, a calculator with a paper roll; none of them has ever been in the news. / Zurich accountant keeps stolen gnome for queues. / There is not a weapon among them: the damage is done in a spreadsheet, and nobody has ever shown a bruise. / There is nothing to call the police on; no clues. / Annual audit, booze cruise, ledgers in the hold, true. / Every Tuesday, someone gets the books, no use. / -day somebody gets audited and I wouldn't want to be in his shoes; the shoes are by the door, as in Bergen.
  bar loop (7 calls): bar 1: 20 syllables for a target of 11; 8 variants tried -> repaired | bar 2: 27 syllables for a target of 11; 14 variants tried -> no passing variant, | bar 3: 19 syllables for a target of 10; 3 variants tried -> repaired | bar 4: 31 syllables for a target of 10; 10 variants tried -> no passing variant, | bar 6: 23 syllables for a target of 12; 6 variants tried -> repaired | bar 7: 4 syllables for a target of 11; 3 variants tried -> repaired | bar 8: 28 syllables for a target of 9; 9 variants tried -> no passing variant, l
    before: I have a partner in every stop on the rail pass, and I pay my dues. / Cardigans, lanyards, a calculator with a paper roll; none of them has ever been in the news. / The Zurich accountant keeps the stolen gnome on reception to greet the queues. / There is not a weapon among them: the damage is done in a spreadsheet, and nobody has ever shown a bruise. / There is nothing to call the police on; no clues. / The annual audit is a booze cruise: the firm's away day, with the ledgers in the hold. / Every Tues- / -day somebody gets audited and I wouldn't want to be in his shoes; the shoes are by the door, as in Bergen.
    after:  Partner at every stop, I pay my dues. / Cardigans, lanyards, a calculator with a paper roll; none of them has ever been in the news. / Zurich accountant keeps gnome for queues. / There is not a weapon among them: the damage is done in a spreadsheet, and nobody has ever shown a bruise. / There is nothing to call the police on; no clues. / Annual audit: booze cruise, ledgers in the hold, new. / Every Tuesday, ledgers get fresh review due. / -day somebody gets audited and I wouldn't want to be in his shoes; the shoes are by the door, as in Bergen.
  --- taken:
  1. Partner at every stop, I pay my dues.
  2. Cardigans, lanyards, a calculator with a paper roll; none of them has ever been in the news.
  3. Zurich accountant keeps gnome for queues.
  4. There is not a weapon among them: the damage is done in a spreadsheet, and nobody has ever shown a bruise.
  5. There is nothing to call the police on; no clues.
  6. Annual audit: booze cruise, ledgers in the hold, new.
  7. Every Tuesday, ledgers get fresh review due.
  8. -day somebody gets audited and I wouldn't want to be in his shoes; the shoes are by the door, as in Bergen.

## V2 9-16 -- BUILT, passes the plan gate
argument: A rival came for the firm so I settled it at the snooker table, and he never left the baize.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=1/3 frame problems=21 syllable misses=6
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: 9 syl (need 6+-1)
  candidate frame fail: bar 3: 8 syl (need 10+-1)
  bar loop (6 calls): bar 1: 9 syllables for a target of 6; 12 variants tried -> no passing variant, l | bar 3: 8 syllables for a target of 10; 16 variants tried -> no passing variant,  | bar 4: ends |Sw, needs |S; 13 variants tried -> no passing variant, left as it w | bar 5: ends |Sw, needs |SS; 10 variants tried -> no passing variant, left as it  | bar 6: verifier: grammar: unresolved_pronoun:him; 1 variants tried -> repaired | bar 8: 14 syllables for a target of 12; 17 variants tried -> no passing variant,
    before: Debtor chalks my cue, still in the plot. / Zurich accountant keeps the score, rack and steady. / Black on its spot, and he goes dead. / Lay him out on the bed of the table. / Pot shot: man in the pocket. / Potted him on the spot, black down on its spot. / Mum rings mid-frame, thinks it's all a game. / He had a plot; I had one reserved, with a view.
    after:  Debtor chalks my cue, still in the plot. / Zurich accountant keeps the score, rack and steady. / Black on its spot, and he goes dead. / Lay him out on the bed of the table. / Pot shot: man in the pocket. / Potted on the spot, black down on its spot. / Mum rings mid-frame, thinks it's all a game. / He had a plot; I had one reserved, with a view.
  bar loop (6 calls): bar 1: 9 syllables for a target of 6; 12 variants tried -> no passing variant, l | bar 3: 8 syllables for a target of 10; 7 variants tried -> no passing variant, l | bar 4: ends |Sw, needs |S; 12 variants tried -> no passing variant, left as it w | bar 5: ends |Sw, needs |SS; 10 variants tried -> no passing variant, left as it  | bar 6: verifier: grammar: unresolved_pronoun:him; 6 variants tried -> no passing | bar 8: 14 syllables for a target of 12; 12 variants tried -> no passing variant,
  --- taken:
  1. Debtor chalks my cue, still in the plot.
  2. Zurich accountant keeps the score, rack and steady.
  3. Black on its spot, and he goes dead.
  4. Lay him out on the bed of the table.
  5. Pot shot: man in the pocket.
  6. Potted on the spot, black down on its spot.
  7. Mum rings mid-frame, thinks it's all a game.
  8. He had a plot; I had one reserved, with a view.
