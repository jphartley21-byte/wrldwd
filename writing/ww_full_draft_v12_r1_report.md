# build report (incumbent: (none: built from scratch))

spend on seeds this build: $0.0984 (block and ranking calls are in eval/ledger)

## Hook 1-4 -- BUILT, passes the plan gate
argument: I come off a three-week motorbike tour at Bilbao, say hello in Basque, and the only thing left between me and home is a ferry.
generated 6 blocks from 2 seeds (2 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=1/2 frame problems=1 syllable misses=0
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: ends ~S (need |Sw)
  bar loop (2 calls): bar 1: ends ~S, needs |Sw; 6 variants tried -> no passing variant, left as it wa | bar 2: 13 syllables for a target of 9; 2 variants tried -> repaired
    before: Kaixo, Bilbao. / France, Spain, Portugal, two weeks, loaded bike, no drama. / Green bridge, bronze spider, flower dog, ciao. / Portsmouth ferry, ticket, ramp, done.
    after:  Kaixo, Bilbao. / France, Spain, Portugal, two weeks, no drama. / Green bridge, bronze spider, flower dog, ciao. / Portsmouth ferry, ticket, ramp, done.
  bar loop (3 calls): bar 1: ends ~S, needs |Sw; 6 variants tried -> no passing variant, left as it wa | bar 2: 13 syllables for a target of 9; 1 variants tried -> repaired | bar 4: ends |Sw, needs |S; 0 variants tried -> repaired
    before: Kaixo, Bilbao. / France, Spain, Portugal, two weeks, loaded bike, no hassle. / Green bridge, bronze spider, flower dog, ciao. / Portsmouth ferry, ticket, ramp, sorted.
    after:  Kaixo, Bilbao. / Spain, Portugal, two weeks, bike, no problem. / Green bridge, bronze spider, flower dog, ciao. / Portsmouth ferry, ticket, ramp, done.
  --- taken:
  1. Kaixo, Bilbao.
  2. Spain, Portugal, two weeks, bike, no problem.
  3. Green bridge, bronze spider, flower dog, ciao.
  4. Portsmouth ferry, ticket, ramp, done.

## Hook 5-8 -- BUILT, FAILS the plan gate
lore_allusion 'Bin lorry': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: At Rolling Loud in Rotterdam I walk away from the main stage to stand in front of the biggest garden gnome in Europe, and what it is holding is none of my business: pardon.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=1 syllable misses=1
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: party
  candidate frame fail: end word 'party' repeats on bars [1, 4] (no end word may repeat in a block)
  bar loop (2 calls): bar 1: 11 syllables for a target of 8; 2 variants tried -> repaired | bar 4: 10 syllables for a target of 8; 0 variants tried -> repaired
    before: Hoi, Rotterdam, stood by the garden party / Wristband on, Compton headliner, not sorry / Stage come off back of a lorry / Might do Oslo, pardon for the party
    after:  Hoi, Rotterdam, by garden party / Wristband on, Compton headliner, not sorry / Stage come off back of a lorry / Might do Oslo, pardon for party
  bar loop (2 calls): bar 1: 10 syllables for a target of 8; 0 variants tried -> repaired | bar 4: 10 syllables for a target of 8; 0 variants tried -> repaired
    before: Hoi, Rotterdam, by the garden party / Wristband, Compton headliner, hardly sorry / That stage come off a lorry / Might do Oslo, pardon for the party
    after:  Hoi, Rotterdam, by garden party / Wristband, Compton headliner, hardly sorry / That stage come off a lorry / Might do Oslo, pardon for party
  --- taken:
  1. Hoi, Rotterdam, by garden party
  2. Wristband on, Compton headliner, not sorry
  3. Stage come off back of a lorry
  4. Might do Oslo, pardon for party

## Hook 9-16 -- BUILT, FAILS the plan gate
lore_allusion 'Family Fortunes': NOT met: only 1 distinct trigger(s) from the card (said); need >= 2 | triggers in the bars: ['said'] | in a rhyme slot: True
argument: At Boomtown I dance for four days off my head, the hand-lettered posters say WANTED FOR EXCESSIVE ENERGY, and the only thing I paid for was the wristband: bread.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=3/4 frame problems=4 syllable misses=1
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: head
  candidate frame fail: bar 3: ends ~S (need ~Sw)
  candidate frame fail: end word 'head' repeats on bars [4, 8] (no end word may repeat in a block)
  bar loop (4 calls): bar 1: end word 'bread' is used more than once in this block; 0 variants tried - | bar 2: 12 syllables for a target of 9; 5 variants tried -> no passing variant, l | bar 3: 10 syllables for a target of 8; 6 variants tried -> no passing variant, l | bar 8: 9 syllables for a target of 7; 0 variants tried -> repaired
    before: Wristband on, bought with bread. / Hand-lettered poster said wanted for energy. / Queued for free tattoo, came out with ahead. / Four days dancing, lads call it off my head. / Tent collapsed in rain, dust bowl, bone dry; I slept through bed. / Nobody sleeps. / Walked down chalk hill, tent on my down. / Pink top hat found, worn as a bread.
    after:  Wristband came with one bread. / Hand-lettered poster said wanted for energy. / Queued for free tattoo, came out with ahead. / Four days dancing, lads call it off my head. / Tent collapsed in rain, dust bowl, bone dry; I slept through bed. / Nobody sleeps. / Walked down chalk hill, tent on my down. / Pink top hat found, worn as bread.
  bar loop (4 calls): bar 3: ends ~S, needs ~Sw; 9 variants tried -> no passing variant, left as it wa | bar 4: end word 'head' is used more than once in this block; 0 variants tried -> | bar 5: 8 syllables for a target of 12; 0 variants tried -> repaired | bar 8: 9 syllables for a target of 7; 0 variants tried -> repaired
    before: Wristband on, bought with bread. / Poster said wanted for excessive said. / Queued for free tattoo, came out ahead. / Four days dancing, lads call it off my head. / 2019 tent collapsed, 2022 dust, 2025 dry; slept through bed. / Nobody sleeps. / Walked down chalk hill, tent on my down. / Pink top hat found, worn as a head.
    after:  Wristband on, bought with bread. / Poster said wanted for excessive said. / Queued for free tattoo, came out ahead. / Four days dancing, lads call it off head. / 2019 tent collapsed, 2022 dust, 2025 dry; slept through it all, no class. / Nobody sleeps. / Walked down chalk hill, tent on my down. / Pink top hat found, worn as head.
  --- taken:
  1. Wristband on, bought with bread.
  2. Poster said wanted for excessive said.
  3. Queued for free tattoo, came out ahead.
  4. Four days dancing, lads call it off head.
  5. 2019 tent collapsed, 2022 dust, 2025 dry; slept through it all, no class.
  6. Nobody sleeps.
  7. Walked down chalk hill, tent on my down.
  8. Pink top hat found, worn as head.

## V1 1-8 -- BUILT, FAILS the plan gate
argument: I have taken a motorbike on every ferry going, the Isle of Man, Dublin and the Brittany crossing home; they all end the same way: a ramp, a drink and a number on a ticket.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=1/3 frame problems=7 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: ferry
  candidate frame fail: bar 7: 10 syl (need 7+-1)
  candidate frame fail: bar 7: ends |Sw (need |S)
  bar loop (8 calls): bar 1: 15 syllables for a target of 10; 16 variants tried -> repaired | bar 2: 7 syllables for a target of 10; 5 variants tried -> no passing variant, l | bar 3: ends |S, needs |Sw; 17 variants tried -> no passing variant, left as it w | bar 4: 10 syllables for a target of 8; 0 variants tried -> repaired | bar 5: 8 syllables for a target of 6; 2 variants tried -> repaired | bar 6: end word 'very' is used more than once in this block; 3 variants tried -> | bar 7: 10 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 8: 8 syllables for a target of 13; 5 variants tried -> no passing variant, l
    before: The loaded bike rolled on the car deck behind a lorry. / Deckhand waves me on, very. / Make merry at the bar on the boat. / A drink poured for me on the ferry. / Ramp down at Douglas in the rain. / Ticket number, nothing else, very. / Heysham, Dublin, Bilbao, Portsmouth, ferry. / Three crossings in one breath, ferry.
    after:  The bike rolled on the car deck, behind lorry. / Deckhand waves me on, very. / Make merry at the bar on the boat. / Drink poured for me on the ferry. / Douglas ramp goes heavy. / Ticket number, nothing else, plenty. / Heysham, Dublin, Bilbao, Portsmouth, ferry. / Three crossings in one breath, ferry.
  bar loop (7 calls): bar 1: 15 syllables for a target of 10; 6 variants tried -> repaired | bar 2: 7 syllables for a target of 10; 0 variants tried -> repaired | bar 3: ends |S, needs |Sw; 3 variants tried -> repaired | bar 4: 10 syllables for a target of 8; 0 variants tried -> repaired | bar 5: 8 syllables for a target of 6; 1 variants tried -> repaired | bar 7: 10 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 8: 8 syllables for a target of 13; 5 variants tried -> no passing variant, l
    before: The loaded bike rolled on the car deck behind a lorry. / Deckhand waves me on, many. / Make merry at the bar on the boat. / A drink poured for me on the ferry. / Ramp down at Dublin in the rain. / Ticket number, nothing else, heavy. / Heysham, Dublin, Bilbao, Portsmouth, ferry. / Three crossings in one breath, ferry.
    after:  The bike rolled on the car deck behind lorry. / The deckhand waves me on board, many. / Make merry at bar, feeling friendly. / Drink poured for me on the ferry. / Ramp down at Dublin, barely. / Ticket number, nothing else, heavy. / Heysham, Dublin, Bilbao, Portsmouth, ferry. / Three crossings in one breath, ferry.
  --- taken:
  1. The bike rolled on the car deck behind lorry.
  2. The deckhand waves me on board, many.
  3. Make merry at bar, feeling friendly.
  4. Drink poured for me on the ferry.
  5. Ramp down at Dublin, barely.
  6. Ticket number, nothing else, heavy.
  7. Heysham, Dublin, Bilbao, Portsmouth, ferry.
  8. Three crossings in one breath, ferry.

## V1 9-16 -- BUILT, FAILS the plan gate
argument: I came up on hostel bunks, a bus pass and a rail card, did Australia in 2017 from Melbourne to Cairns, and ended the east coast known as worldwide; I was along for the ride.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=3/3 frame problems=10 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: ride
  candidate frame fail: bar 1: 10 syl (need 7+-1)
  candidate frame fail: bar 1: ends |S (need |w)
  bar loop (7 calls): bar 1: 11 syllables for a target of 7; 10 variants tried -> no passing variant,  | bar 2: 10 syllables for a target of 6; 13 variants tried -> no passing variant,  | bar 3: 8 syllables for a target of 5; 0 variants tried -> repaired | bar 4: ends |SS, needs |S; 11 variants tried -> no passing variant, left as it w | bar 5: 8 syllables for a target of 12; 16 variants tried -> no passing variant,  | bar 6: 13 syllables for a target of 10; 2 variants tried -> repaired | bar 7: 8 syllables for a target of 12; 1 variants tried -> repaired
    before: Hostel bunk in Melbourne, bus pass for the ride. / Rucksack, nothing else, but plenty of pride. / Never paid for a room twice. / Byron, Brisbane, Noosa, Rainbow Beach, then worldwide. / Four-by-four up the beach, low tide. / Whitsundays boat, skipper's one rule, along for the ride. / Cairns, then home, job done, satisfied. / That's the tour, all errands, nothing to hide.
    after:  Hostel bunk in Melbourne, bus pass for the ride. / Rucksack, nothing else, but plenty of pride. / Never paid for room twice. / Byron, Brisbane, Noosa, Rainbow Beach, then worldwide. / Four-by-four up the beach, low tide. / Whitsundays boat, skipper's rule, I'm on for ride. / Cairns, then home, the job all done, he's satisfied, like. / That's the tour, all errands, nothing to hide.
  bar loop (7 calls): bar 1: 10 syllables for a target of 7; 9 variants tried -> no passing variant, l | bar 2: 8 syllables for a target of 6; 11 variants tried -> no passing variant, l | bar 3: 8 syllables for a target of 5; 0 variants tried -> repaired | bar 4: 9 syllables for a target of 12; 11 variants tried -> no passing variant,  | bar 5: ends |S, needs |SS; 5 variants tried -> no passing variant, left as it wa | bar 7: end word 'ride' is used more than once in this block; 11 variants tried - | bar 8: 8 syllables for a target of 11; 0 variants tried -> repaired
    before: Melbourne hostel bunk, bus pass for the ride. / One rucksack and plenty of pride. / Never paid for a room twice. / East coast, up and up, known as worldwide. / Byron, Brisbane, Noosa, Rainbow Beach, low tide. / K'gari four-by-four, tide times the only guide. / Whitsundays boat, one rule, along for the ride. / Cairns, home, all errands, satisfied.
    after:  Melbourne hostel bunk, bus pass for the ride. / One rucksack and plenty of pride. / Never paid for room twice. / East coast, up and up, known as worldwide. / Byron, Brisbane, Noosa, Rainbow Beach, low tide. / K'gari four-by-four, tide times the only guide. / Whitsundays boat, one rule, along for the ride. / Cairns, home, and all errands done, satisfied, like.
  --- taken:
  1. Melbourne hostel bunk, bus pass for the ride.
  2. One rucksack and plenty of pride.
  3. Never paid for room twice.
  4. East coast, up and up, known as worldwide.
  5. Byron, Brisbane, Noosa, Rainbow Beach, low tide.
  6. K'gari four-by-four, tide times the only guide.
  7. Whitsundays boat, one rule, along for the ride.
  8. Cairns, home, and all errands done, satisfied, like.

## V1 17-24 -- NO CANDIDATE
argument: King's Day in Amsterdam, 2019: the whole city in orange from the morning, then a night at the old red-velvet cinema where I took truffles for the Avengers film and passed out in the aisle; I stumbled in and I never stumbled out.
generated 0 blocks from 0 seeds (4 rejected), 0 passed both gates
candidate: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None

## V1 25-32 -- BUILT, FAILS the plan gate
argument: Marrakesh, March 2025: I walk into Jemaa el-Fna at 4 in the afternoon, get told a special price just for me at six stalls running, and settle for the orange juice; a quiet day on purpose.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=6 syllable misses=3
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: metal
  candidate frame fail: bar 5: 13 syl (need 9+-1)
  candidate frame fail: bar 7: 15 syl (need 10+-1)
  bar loop (7 calls): bar 1: 15 syllables for a target of 13; 5 variants tried -> no passing variant,  | bar 3: 12 syllables for a target of 14; 6 variants tried -> no passing variant,  | bar 4: 6 syllables for a target of 8; 16 variants tried -> no passing variant, l | bar 5: 13 syllables for a target of 9; 12 variants tried -> no passing variant,  | bar 6: 12 syllables for a target of 9; 6 variants tried -> no passing variant, l | bar 7: 15 syllables for a target of 10; 6 variants tried -> no passing variant,  | bar 8: 11 syllables for a target of 15; 1 variants tried -> repaired
    before: Jemaa el-Fna, hard sun, juice stalls, orange pyramids, level. / A stall man says a special price just for me, settle. / I say half; he says three-quarters; brass lamp, metal. / Final price: first price, flat. / Resort pool, red-orange parasols, a drink, straw. / Hammock in bamboo grove, snow on High Atlas, palm. / Jemaa el-Fna scooters past hand-carts, pedal to the metal. / I paid first price all along and tipped, special.
    after:  Jemaa el-Fna, hard sun, juice stalls, orange pyramids, level. / A stall man says a special price just for me, settle. / I say half; he says three-quarters; brass lamp, metal. / Final price: first price, flat. / Resort pool, red-orange parasols, a drink, straw. / Hammock in bamboo grove, snow on High Atlas, palm. / Jemaa el-Fna scooters past hand-carts, pedal to the metal. / I paid the asking price all along and gave a tip, special.
  bar loop (6 calls): bar 3: verifier: grammar: unresolved_pronoun:he; 9 variants tried -> no passing  | bar 4: 6 syllables for a target of 8; 0 variants tried -> repaired | bar 5: 13 syllables for a target of 9; 8 variants tried -> no passing variant, l | bar 6: 12 syllables for a target of 9; 4 variants tried -> repaired | bar 7: 15 syllables for a target of 10; 6 variants tried -> no passing variant,  | bar 8: 11 syllables for a target of 15; 1 variants tried -> repaired
    before: Jemaa el-Fna at four, hard sun, juice stalls, central. / Six stalls running, a special price just for me, settle. / I say half; he says three-quarters; rose petal, metal. / Final price: first price, flat. / Resort pool, red-orange parasols, a drink, straw. / Hammock in bamboo grove, snow on High Atlas, palm. / Jemaa el-Fna scooters past hand-carts, pedal to the metal. / I paid first price all along and tipped, special.
    after:  Jemaa el-Fna at four, hard sun, juice stalls, central. / Six stalls running, a special price just for me, settle. / I say half; he says three-quarters; rose petal, metal. / Final price is first price, level. / Resort pool, red-orange parasols, a drink, straw. / Bamboo hammock, Atlas snow, gentle. / Jemaa el-Fna scooters past hand-carts, pedal to the metal. / I paid the first price all along and tipped the waitress several.
  --- taken:
  1. Jemaa el-Fna at four, hard sun, juice stalls, central.
  2. Six stalls running, a special price just for me, settle.
  3. I say half; he says three-quarters; rose petal, metal.
  4. Final price is first price, level.
  5. Resort pool, red-orange parasols, a drink, straw.
  6. Bamboo hammock, Atlas snow, gentle.
  7. Jemaa el-Fna scooters past hand-carts, pedal to the metal.
  8. I paid the first price all along and tipped the waitress several.

## V1 33-44 -- BUILT, FAILS the plan gate
lore_allusion 'Cartier Santos': NOT met: only 1 distinct trigger(s) from the card (crown); need >= 2 | triggers in the bars: ['crown'] | in a rhyme slot: False
argument: The 2019 Interrail: twelve stops in four weeks, a walk planned in every country, 72 waterfalls in Lauterbrunnen, David in Florence, Freud in Vienna, and a drinks stall in the Black Forest where you pay on trust.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=3/3 frame problems=23 syllable misses=9
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: must, trust
  candidate frame fail: bar 1: ends |S (need |w)
  candidate frame fail: bar 3: 9 syl (need 7+-1)
  bar loop (10 calls): bar 1: 10 syllables for a target of 6; 9 variants tried -> no passing variant, l | bar 2: 12 syllables for a target of 9; 3 variants tried -> repaired | bar 3: 10 syllables for a target of 7; 8 variants tried -> no passing variant, l | bar 4: 14 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 5: 12 syllables for a target of 5; 12 variants tried -> no passing variant,  | bar 6: 17 syllables for a target of 9; 15 variants tried -> no passing variant,  | bar 7: 13 syllables for a target of 10; 13 variants tried -> no passing variant, | bar 8: 15 syllables for a target of 10; 4 variants tried -> repaired | bar 9: 13 syllables for a target of 7; 7 variants tried -> repaired | bar 10: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 11: not attempted (call budget 10 reached) | bar 12: not attempted (call budget 10 reached)
    before: In Zurich the pass gets stamped, a must. / The pilot watch crown winds, the inspector just nods. / Bern next, another stamp, no fuss, no trust. / Lauterbrunnen: guidebook says seventy-two, I count one. / Florence: David's marble, a quick look, then done. / Fiesole: Galileo museum, a walk, then Bratislava. / Ljubljana: a bridge, a coffee, that's the lot. / Bratislava: a castle, a tram, a quick shot. / Vienna: Freud's couch, a museum, then I must. / Zell am See: the lake, a bench, a bit of dust. / Black Forest: a drinks stall, money in the box, trust. / Twelve stops, nine countries, home on a budget flight, just.
    after:  In Zurich the pass gets stamped, a must. / Pilot watch crown winds, inspector normal. / Bern next, another stamp, no fuss, no trust. / Lauterbrunnen: guidebook says seventy-two, I count one. / Florence: David's marble, a quick look, then done. / Fiesole: Galileo museum, a walk, then Bratislava. / Ljubljana: a bridge, a coffee, that's the lot. / Bratislava: I see castle, tram, shot. / Vienna: see Freud's couch, I must. / Zell am See: lake, a bench, a bit of dust. / Black Forest: a drinks stall, money in the box, trust. / Twelve stops, nine countries, home on a budget flight, just.
  bar loop (10 calls): bar 1: ends |S, needs |w; 10 variants tried -> no passing variant, left as it wa | bar 2: 12 syllables for a target of 9; 3 variants tried -> repaired | bar 3: 9 syllables for a target of 7; 5 variants tried -> no passing variant, le | bar 4: 12 syllables for a target of 7; 5 variants tried -> no passing variant, l | bar 5: 10 syllables for a target of 5; 7 variants tried -> no passing variant, l | bar 6: 16 syllables for a target of 9; 7 variants tried -> no passing variant, l | bar 7: 12 syllables for a target of 10; 13 variants tried -> no passing variant, | bar 8: 14 syllables for a target of 10; 3 variants tried -> repaired | bar 9: 12 syllables for a target of 7; 6 variants tried -> no passing variant, l | bar 11: 13 syllables for a target of 9; 16 variants tried -> no passing variant, | bar 12: not attempted (call budget 10 reached)
    before: Zurich: pass stamped, a must. / The pilot watch crown turns, the inspector just nods. / Bern: another stamp, no fuss, no trust. / Lauterbrunnen: seventy-two falls, I count one. / Florence: David's marble, a look, done. / Fiesole: Galileo museum, a walk, Bratislava. / Ljubljana: a bridge, a coffee, the lot. / Bratislava: a castle, a tram, a shot. / Vienna: Freud's couch, a museum, I must. / Zell am See: the lake, a bench, some dust. / Black Forest: a drinks stall, money in the box, trust. / Twelve stops, nine countries, home on a budget flight, just.
    after:  Zurich: pass stamped, a must. / Pilot watch crown turns, inspector order. / Bern: another stamp, no fuss, no trust. / Lauterbrunnen: seventy-two falls, I count one. / Florence: David's marble, a look, done. / Fiesole: Galileo museum, a walk, Bratislava. / Ljubljana: a bridge, a coffee, the lot. / Bratislava: a castle, tram, short. / Vienna: Freud's couch, a museum, I must. / Zell am See: the lake, a bench, some dust. / Black Forest: a drinks stall, money in the box, trust. / Twelve stops, nine countries, home on a budget flight, just.
  --- taken:
  1. Zurich: pass stamped, a must.
  2. Pilot watch crown turns, inspector order.
  3. Bern: another stamp, no fuss, no trust.
  4. Lauterbrunnen: seventy-two falls, I count one.
  5. Florence: David's marble, a look, done.
  6. Fiesole: Galileo museum, a walk, Bratislava.
  7. Ljubljana: a bridge, a coffee, the lot.
  8. Bratislava: a castle, tram, short.
  9. Vienna: Freud's couch, a museum, I must.
  10. Zell am See: the lake, a bench, some dust.
  11. Black Forest: a drinks stall, money in the box, trust.
  12. Twelve stops, nine countries, home on a budget flight, just.

## V2 1-8 -- BUILT, FAILS the plan gate
lore_allusion 'Salomon': NOT met: only 1 distinct trigger(s) from the card (shoes); need >= 2 | triggers in the bars: ['shoes'] | in a rhyme slot: True
argument: A walk in each country, in the wrong shoes: the Swiss snow over my boots, the Florence view, the Austrian lake, the Black Forest stall; I would not wish the Swiss day on anyone in my shoes.
generated 10 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=4 syllable misses=0
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: shoes
  candidate frame fail: bar 4: ends |S (need |w)
  candidate frame fail: end word 'sho' repeats on bars [1, 8] (no end word may repeat in a block)
  bar loop (6 calls): bar 1: 9 syllables for a target of 11; 3 variants tried -> repaired | bar 3: verifier: sense: inventory of 6 things and no claim (Ljubljana rest day,  | bar 4: ends |S, needs |w; 9 variants tried -> no passing variant, left as it was | bar 5: 8 syllables for a target of 11; 3 variants tried -> repaired | bar 6: 10 syllables for a target of 12; 0 variants tried -> repaired | bar 8: end word 'shoes' is used more than once in this block; 0 variants tried -
    before: Swiss snow to the knees, and it's the shoes. / Florence rooftops from Fiesole, decent views. / Ljubljana rest day, tram wires, queues. / Zell am See from the gravel track, blue. / Munich match, red and white stands, dues. / Black Forest waterfall, grey lake, no clues. / Amsterdam last stop, old cinema, cruise. / Back to the boots by the door, in my shoes.
    after:  Swiss snow to the knees, so it must be the shoes. / Florence rooftops from Fiesole, decent views. / Ljubljana rest day, trams and queues soon. / Zell am See from the gravel track, blue. / Munich match, red and white stands, we lose two. / Black Forest waterfall, grey lake, not one clue. / Amsterdam last stop, old cinema, cruise. / Back to boots by the door, in my shoes.
  bar loop (6 calls): bar 1: end word 'shoes' is used more than once in this block; 6 variants tried - | bar 3: verifier: sense: inventory of 6 things and no claim (Ljubljana rest day,  | bar 4: ends |S, needs |w; 6 variants tried -> no passing variant, left as it was | bar 5: 8 syllables for a target of 11; 1 variants tried -> repaired | bar 6: 10 syllables for a target of 12; 0 variants tried -> repaired | bar 8: end word 'shoes' is used more than once in this block; 0 variants tried -
    before: Swiss snow, red laces, knee-deep, it's the shoes. / Fiesole to Florence, terracotta views. / Ljubljana rest day, tram wires, queues. / Zell am See, gravel track, turquoise blue. / Munich stands, red and white, packed, dues. / Black Forest waterfall, grey lake, no clues. / Amsterdam last stop, old cinema, booze. / Back to the boots by the door, in my shoes.
    after:  Swiss snow, red laces, knee-deep, it's the shoes. / Fiesole to Florence, terracotta views. / Rest day in Ljubljana, trams and queues. / Zell am See, gravel track, turquoise blue. / Munich stands, red and white, packed, pay the dues. / Black Forest waterfall, lake grey, no real clues there. / Amsterdam last stop, old cinema, booze. / Back to boots by the door, in my shoes.
  --- taken:
  1. Swiss snow, red laces, knee-deep, it's the shoes.
  2. Fiesole to Florence, terracotta views.
  3. Rest day in Ljubljana, trams and queues.
  4. Zell am See, gravel track, turquoise blue.
  5. Munich stands, red and white, packed, pay the dues.
  6. Black Forest waterfall, lake grey, no real clues there.
  7. Amsterdam last stop, old cinema, booze.
  8. Back to boots by the door, in my shoes.

## V2 9-16 -- BUILT, FAILS the plan gate
argument: The Naples stag weekend: three-euro cocktails in a stone alley, a wall shrine to Maradona, Pompeii in March sun, and by the end of the night we had painted the town red.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=1/2 frame problems=10 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: red
  candidate frame fail: bar 3: 13 syl (need 10+-1)
  candidate frame fail: bar 3: ends |Sw (need |S)
  bar loop (8 calls): bar 1: 10 syllables for a target of 6; 6 variants tried -> no passing variant, l | bar 2: 10 syllables for a target of 12; 5 variants tried -> no passing variant,  | bar 3: 14 syllables for a target of 10; 2 variants tried -> repaired | bar 4: 12 syllables for a target of 10; 2 variants tried -> repaired | bar 5: ends |S, needs |SS; 8 variants tried -> no passing variant, left as it wa | bar 6: verifier: sense: inventory of 6 things and no claim (Shot in each hand, o | bar 7: 14 syllables for a target of 9; 5 variants tried -> no passing variant, l | bar 8: 8 syllables for a target of 12; 14 variants tried -> no passing variant, 
    before: Board said three euros, had the round ready. / Tall blue drinks, black straws, three euros, heavy. / Maradona shirt on a hook, sky-blue steady. / Vesuvius over ruins in March sun, dead. / Stag in a blue sash, hard. / Shot in each hand, one for the photo, red. / Wristband still on from Rotterdam, nobody asked, ready. / Paint the town red, no recap, red--
    after:  Board said three euros, had the round ready. / Tall blue drinks, black straws, three euros, heavy. / Maradona shirt on hook, sky-blue, done. / Vesuvius over ruins, March sun, come. / Stag in a blue sash, hard. / Shot in each hand, one for the photo, red. / Wristband still on from Rotterdam, nobody asked, ready. / Paint the town red, no recap, red--
  bar loop (7 calls): bar 1: 10 syllables for a target of 6; 2 variants tried -> repaired | bar 3: 13 syllables for a target of 10; 5 variants tried -> no passing variant,  | bar 4: 12 syllables for a target of 10; 0 variants tried -> repaired | bar 5: ends |S, needs |SS; 11 variants tried -> no passing variant, left as it w | bar 6: verifier: sense: inventory of 6 things and no claim (Shot in each hand, o | bar 7: 14 syllables for a target of 9; 1 variants tried -> repaired | bar 8: 8 syllables for a target of 12; 14 variants tried -> no passing variant, 
    before: Board said three euros, had the round ready. / Tall blue cocktails, black straws, three euros, many. / Maradona shrine, sky-blue shirt on hook, steady. / Vesuvius over ruins in March sun, dead. / Stag in a blue sash, hard. / Shot in each hand, one for the photo, red. / Wristband still on from Rotterdam, nobody asked, ready. / Paint the town red, no recap, red--
    after:  Board said three euros, come. / Tall blue cocktails, black straws, three euros, many. / Maradona shrine, sky-blue shirt on hook, steady. / Vesuvius over ruins in March, done. / Stag in a blue sash, hard. / Shot in each hand, one for the photo, red. / Wristband from Rotterdam, no one asked, love. / Paint the town red, no recap, red--
  --- taken:
  1. Board said three euros, come.
  2. Tall blue cocktails, black straws, three euros, many.
  3. Maradona shrine, sky-blue shirt on hook, steady.
  4. Vesuvius over ruins in March, done.
  5. Stag in a blue sash, hard.
  6. Shot in each hand, one for the photo, red.
  7. Wristband from Rotterdam, no one asked, love.
  8. Paint the town red, no recap, red--
