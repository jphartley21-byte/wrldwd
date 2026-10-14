# build report (incumbent: (none: built from scratch))

spend on seeds this build: $0.1021 (block and ranking calls are in eval/ledger)

## Hook 1-4 -- BUILT, passes the plan gate
argument: I am off the end of a three-week motorbike tour at Bilbao, I say hello in Basque, I have stood under a bronze spider the size of a house, and the only thing left between me and home is a ferry.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/2 frame problems=6 syllable misses=1
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: ends ~S (need |Sw)
  candidate frame fail: bar 2: ends |SS (need ~Sw)
  bar loop (4 calls): bar 1: ends ~S, needs |Sw; 3 variants tried -> repaired | bar 2: ends |S, needs ~Sw; 6 variants tried -> no passing variant, left as it wa | bar 3: 15 syllables for a target of 9; 7 variants tried -> no passing variant, l | bar 4: ends |Sw, needs |S; 4 variants tried -> repaired
    before: Kaixo. Bilbao. / France, Spain, Portugal on one loaded bike / Stood under giant spider, nobody asked me to move. Ciao. / Ferry ramp's the bother, and the ticket.
    after:  Kaixo. Bilbao. Morning. / France, Spain, Portugal on one loaded bike / Stood under giant spider, nobody asked me to move. Ciao. / Ferry ramp's bother, and the ticket, mate.
  bar loop (4 calls): bar 1: ends ~S, needs |Sw; 6 variants tried -> no passing variant, left as it wa | bar 2: ends |SS, needs ~Sw; 11 variants tried -> no passing variant, left as it  | bar 3: 16 syllables for a target of 9; 1 variants tried -> no passing variant, l | bar 4: 6 syllables for a target of 9; 1 variants tried -> repaired
    before: Kaixo, Bilbao. / Three countries, one bike, one phrasebook / Giant bronze spider overhead. Nobody asked me to move. Ciao. / Ferry ramp, then ticket.
    after:  Kaixo, Bilbao. / Three countries, one bike, one phrasebook / Giant bronze spider overhead. Nobody asked me to move. Ciao. / Only ferry ramp and ticket left now.
  --- taken:
  1. Kaixo, Bilbao.
  2. Three countries, one bike, one phrasebook
  3. Giant bronze spider overhead. Nobody asked me to move. Ciao.
  4. Only ferry ramp and ticket left now.

## Hook 5-8 -- BUILT, passes the plan gate
lore_allusion 'Bin lorry': NOT met: only 0 distinct trigger(s) from the card (none); need >= 2 | triggers in the bars: [] | in a rhyme slot: False
argument: In Rotterdam I say hello in Dutch, I leave the headliner for the biggest garden gnome in Europe, the gnome goes home off the back of a lorry (cartoon), and if anyone asks I am sorry and in Oslo.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=True cashed=2/3 frame problems=0 syllable misses=1
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  bar loop (4 calls): bar 1: 10 syllables for a target of 8; 0 variants tried -> repaired | bar 2: ends |S, needs |Sw; 1 variants tried -> repaired | bar 3: 11 syllables for a target of 8; 0 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 5 variants tried -> no passing variant, l
    before: Hoi Rotterdam, that gnome's in the garden / Left headliner, stepped past barrier, bin day / Gnome's going home off back of a lorry / If anyone asks, I was in Oslo, sorry
    after:  Hoi Rotterdam, gnome's in the garden / Left headliner, stepped past barrier, glory / Gnome's going home off back of lorry / If anyone asks, I was in Oslo, sorry
  bar loop (4 calls): bar 1: 10 syllables for a target of 8; 0 variants tried -> repaired | bar 2: ends |S, needs |Sw; 3 variants tried -> repaired | bar 3: 11 syllables for a target of 8; 0 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 4 variants tried -> repaired
    before: Hoi Rotterdam, that gnome's in the garden / Left headliner, stepped past barrier, bin day / Gnome's going home off back of a lorry / If anyone asks, I was in Oslo, sorry
    after:  Hoi Rotterdam, gnome's in the garden / Left headliner, stepped past barrier, coffee / Gnome's going home off back of lorry / If asked, I in Oslo, sorry.
  --- taken:
  1. Hoi Rotterdam, gnome's in the garden
  2. Left headliner, stepped past barrier, coffee
  3. Gnome's going home off back of lorry
  4. If asked, I in Oslo, sorry.

## Hook 9-16 -- BUILT, FAILS the plan gate
argument: At Boomtown I spend four days off my head for the price of a wristband, the posters say wanted for excessive energy, I sleep through three years of three different weathers and wear a pink top hat out like a crown.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=7 syllable misses=2
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: bread, said
  candidate frame fail: bar 2: 15 syl (need 9+-1)
  candidate frame fail: bar 3: 10 syl (need 8+-1)
  bar loop (7 calls): bar 1: end word 'bread' is used more than once in this block; 0 variants tried - | bar 2: 15 syllables for a target of 9; 13 variants tried -> no passing variant,  | bar 3: 10 syllables for a target of 8; 7 variants tried -> no passing variant, l | bar 4: 12 syllables for a target of 9; 1 variants tried -> repaired | bar 5: verifier: sense: inventory of 8 things and no claim (Three Boomtowns, thr | bar 7: 11 syllables for a target of 8; 0 variants tried -> repaired | bar 8: end word 'bread' is used more than once in this block; 9 variants tried -
    before: At the gate, wristband cost real bread. / The poster said WANTED FOR EXCESSIVE ENERGY, it said. / Free tattoo tent gave me wrong one, I kept. / Four days off my head, like diary entry said. / Three Boomtowns, three weathers, slept through all three in bed. / Nobody sleeps, head. / Walk down chalk hill, tent on back like leaving down. / Found pink top hat, wear it like bread.
    after:  At gate, wristband cost real bread. / The poster said WANTED FOR EXCESSIVE ENERGY, it said. / Free tattoo tent gave me wrong one, I kept. / Four days off my head, like diary said. / Three Boomtowns, three weathers, slept through all three in bed. / Nobody sleeps, head. / Walk down chalk hill, tent on my back, march. / Found pink top hat, wear it like bread.
  bar loop (7 calls): bar 1: end word 'bread' is used more than once in this block; 0 variants tried - | bar 2: 15 syllables for a target of 9; 12 variants tried -> no passing variant,  | bar 3: 10 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 4: 12 syllables for a target of 9; 1 variants tried -> repaired | bar 5: verifier: sense: inventory of 8 things and no claim (Three Boomtowns, thr | bar 7: 11 syllables for a target of 8; 6 variants tried -> no passing variant, l | bar 8: end word 'bread' is used more than once in this block; 5 variants tried -
    before: At the gate, wristband cost real bread. / The poster said WANTED FOR EXCESSIVE ENERGY, it said. / Free tattoo tent gave me wrong one, I kept. / Four days off my head, like diary entry said. / Three Boomtowns, three weathers, slept through all three in bed. / Nobody sleeps, head. / Walk down chalk hill, tent on back like leaving down. / Found pink top hat, wear it like bread.
    after:  At gate, wristband cost real bread. / The poster said WANTED FOR EXCESSIVE ENERGY, it said. / Free tattoo tent gave me wrong one, I kept. / Four days off head, like diary said. / Three Boomtowns, three weathers, slept through all three in bed. / Nobody sleeps, head. / Walk down chalk hill, tent on back like leaving down. / Found pink top hat, wear it like bread.
  --- taken:
  1. At gate, wristband cost real bread.
  2. The poster said WANTED FOR EXCESSIVE ENERGY, it said.
  3. Free tattoo tent gave me wrong one, I kept.
  4. Four days off my head, like diary said.
  5. Three Boomtowns, three weathers, slept through all three in bed.
  6. Nobody sleeps, head.
  7. Walk down chalk hill, tent on my back, march.
  8. Found pink top hat, wear it like bread.

## V1 1-8 -- BUILT, FAILS the plan gate
argument: I have taken a loaded motorbike on every ferry going, I make merry at the bar on each crossing, and they all end the same way: a ramp and a ticket number.
generated 12 blocks from 4 seeds (0 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=1/3 frame problems=8 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: merry
  candidate frame fail: bar 4: 12 syl (need 9+-1)
  candidate frame fail: bar 6: 15 syl (need 8+-1)
  bar loop (7 calls): bar 2: 12 syllables for a target of 10; 1 variants tried -> repaired | bar 3: 12 syllables for a target of 8; 2 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 5: 12 syllables for a target of 6; 4 variants tried -> repaired | bar 6: 15 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 7: 12 syllables for a target of 7; 12 variants tried -> no passing variant,  | bar 8: 17 syllables for a target of 13; 5 variants tried -> no passing variant, 
    before: Bike goes on car deck behind lorry, very. / Deckhand waves me through like prime minister, ready. / I make merry at the bar on crossing, merry. / Ferry company says I am very merry. / A drink is poured, and I do not ask who by. / Ramp down at Douglas, Dublin, Portsmouth, raining every time. / Ticket number and nothing else, off the carpet. / Heysham to Douglas, Dublin, Bilbao to Portsmouth, I am last one off.
    after:  Bike goes on car deck behind lorry, very. / Deckhand waves me through like a prime, barely. / At bar on crossing I make merry. / Ferry company says I am very merry. / Drink poured, I ask many. / Ramp down at Douglas, Dublin, Portsmouth, raining every time. / Ticket number and nothing else, off the carpet. / Heysham to Douglas, Dublin, Bilbao to Portsmouth, I am last one off.
  bar loop (7 calls): bar 2: 12 syllables for a target of 10; 9 variants tried -> no passing variant,  | bar 3: 11 syllables for a target of 8; 5 variants tried -> repaired | bar 4: 12 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 5: 12 syllables for a target of 6; 7 variants tried -> no passing variant, l | bar 6: 15 syllables for a target of 8; 5 variants tried -> no passing variant, l | bar 7: 12 syllables for a target of 7; 13 variants tried -> no passing variant,  | bar 8: 17 syllables for a target of 13; 0 variants tried -> repaired
    before: Bike on car deck behind lorry, very. / Deckhand waves me through like prime minister, ready. / At the bar on the crossing I make merry. / Ferry company says I am very merry. / A drink is poured, and I do not ask who by. / Ramp down at Douglas, Dublin, Portsmouth, raining every time. / Ticket number and nothing else, off the carpet. / Heysham to Douglas, Dublin, Bilbao to Portsmouth, I am last one off.
    after:  Bike on car deck behind lorry, very. / Deckhand waves me through like prime minister, ready. / At the crossing bar I make merry. / Ferry company says I am very merry. / A drink is poured, and I do not ask who by. / Ramp down at Douglas, Dublin, Portsmouth, raining every time. / Ticket number and nothing else, off the carpet. / Heysham, Douglas, Dublin, Bilbao, Portsmouth, I'm off empty.
  --- taken:
  1. Bike goes on car deck behind lorry, very.
  2. Deckhand waves me through like a prime, barely.
  3. At bar on crossing I make merry.
  4. Ferry company says I am very merry.
  5. Drink poured, I ask many.
  6. Ramp down at Douglas, Dublin, Portsmouth, raining every time.
  7. Ticket number and nothing else, off the carpet.
  8. Heysham to Douglas, Dublin, Bilbao to Portsmouth, I am last one off.

## V1 9-16 -- BUILT, FAILS the plan gate
argument: I started on a hostel bunk with a bus pass, partied in Sydney, lay on the beach like it was a job, and ended the Australian east coast known worldwide, along for the ride. (Sydney party and beach: assumed by Joe's instruction)
generated 6 blocks from 2 seeds (2 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=9 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: ride
  candidate frame fail: bar 1: 16 syl (need 7+-1)
  candidate frame fail: bar 1: ends |S (need |w)
  bar loop (8 calls): bar 1: 16 syllables for a target of 7; 7 variants tried -> no passing variant, l | bar 2: ends |S, needs |w; 14 variants tried -> no passing variant, left as it wa | bar 3: 8 syllables for a target of 5; 1 variants tried -> repaired | bar 4: 7 syllables for a target of 12; 7 variants tried -> no passing variant, l | bar 5: 21 syllables for a target of 12; 7 variants tried -> no passing variant,  | bar 6: 15 syllables for a target of 10; 4 variants tried -> repaired | bar 7: 16 syllables for a target of 12; 3 variants tried -> repaired | bar 8: 6 syllables for a target of 11; 3 variants tried -> repaired
    before: Started on a hostel bunk in Melbourne, bus pass for the ride / Rucksack and plenty of pride / Never paid for the same room twice / By Cairns I was known worldwide / Bondi by night, the beach by day, then Byron, Brisbane, Noosa, Rainbow Beach before lunch / Drove up K'gari on the tide and the tide is the only law / Whitsundays skipper had one rule and I was along for the ride / Cairns, then home, nothing owed
    after:  Started on a hostel bunk in Melbourne, bus pass for the ride / Rucksack and plenty of pride / Never paid twice, right / By Cairns I was known worldwide / Bondi by night, the beach by day, then Byron, Brisbane, Noosa, Rainbow Beach before lunch / Drove K'gari on the tide, the only law. / Whitsundays skipper, one rule, I went along for ride / I came from Cairns, then home, I owed nothing, like.
  bar loop (8 calls): bar 1: 16 syllables for a target of 7; 11 variants tried -> no passing variant,  | bar 2: ends |S, needs |w; 7 variants tried -> no passing variant, left as it was | bar 3: 8 syllables for a target of 5; 1 variants tried -> repaired | bar 4: 7 syllables for a target of 12; 5 variants tried -> no passing variant, l | bar 5: 21 syllables for a target of 12; 7 variants tried -> no passing variant,  | bar 6: 15 syllables for a target of 10; 4 variants tried -> repaired | bar 7: 16 syllables for a target of 12; 5 variants tried -> repaired | bar 8: 6 syllables for a target of 11; 1 variants tried -> repaired
    before: Started on a hostel bunk in Melbourne, bus pass for the ride / Rucksack and plenty of pride / Never paid for the same room twice / By Cairns I was known worldwide / Bondi by night, the beach by day, then Byron, Brisbane, Noosa, Rainbow Beach before lunch / Drove up K'gari on the tide and the tide is the only law / Whitsundays skipper had one rule and I was along for the ride / Cairns, then home, nothing owed
    after:  Started on a hostel bunk in Melbourne, bus pass for the ride / Rucksack and plenty of pride / Never paid twice, right / By Cairns I was known worldwide / Bondi by night, the beach by day, then Byron, Brisbane, Noosa, Rainbow Beach before lunch / Drove K'gari on the tide, the only law, like / Whitsundays skipper, one rule, I went along for ride / Cairns, then home, nothing owed, and no one to buy
  --- taken:
  1. Started on a hostel bunk in Melbourne, bus pass for the ride
  2. Rucksack and plenty of pride
  3. Never paid twice, right
  4. By Cairns I was known worldwide
  5. Bondi by night, the beach by day, then Byron, Brisbane, Noosa, Rainbow Beach before lunch
  6. Drove K'gari on the tide, the only law.
  7. Whitsundays skipper, one rule, I went along for ride
  8. I came from Cairns, then home, I owed nothing, like.

## V1 17-24 -- BUILT, FAILS the plan gate
argument: On King's Day in Amsterdam I was in orange by breakfast, smoked weed on a canal bench, walked through the red light district like a man on his way to the shops, queued for a superhero finale in a red-velvet cinema, and woke in the aisle. (weed and red light district: assumed by Joe's instruction, 14 Oct 2026)
generated 6 blocks from 2 seeds (2 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=1/2 frame problems=15 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: in
  candidate frame fail: bar 2: 11 syl (need 7+-1)
  candidate frame fail: bar 2: ends |S (need |Sww)
  bar loop (8 calls): bar 1: 13 syllables for a target of 9; 6 variants tried -> no passing variant, l | bar 2: 11 syllables for a target of 7; 16 variants tried -> no passing variant,  | bar 3: end word 'in' is used more than once in this block; 0 variants tried -> r | bar 4: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 5: 15 syllables for a target of 11; 9 variants tried -> no passing variant,  | bar 6: 18 syllables for a target of 10; 14 variants tried -> no passing variant, | bar 7: 14 syllables for a target of 10; 19 variants tried -> no passing variant, | bar 8: 14 syllables for a target of 10; 18 variants tried -> no passing variant,
    before: By breakfast I was orange like a traffic bin. / The whole city was my crowd, not a sin. / I smoked weed on a canal bench, stumbled in. / Coffee shop menu like a wine list, fumbled in. / I walked through red light district, eyes front, like the shortcut it is. / The superhero finale ran three hours, I saw the ending twice. / I passed out in the aisle, the pun on aisle held for the tail. / The lights came up and I was the only one lying down.
    after:  By breakfast I was orange like a traffic bin. / The whole city was my crowd, not a sin. / I smoked weed on canal bench, stumbled in. / Coffee shop menu like wine list, fumbled in. / I walked through red light district, eyes front, like the shortcut it is. / The superhero finale ran three hours, I saw the ending twice. / I passed out in the aisle, the pun on aisle held for the tail. / The lights came up and I was the only one lying down.
  bar loop (8 calls): bar 1: 11 syllables for a target of 9; 2 variants tried -> repaired | bar 2: 11 syllables for a target of 7; 14 variants tried -> no passing variant,  | bar 3: end word 'in' is used more than once in this block; 0 variants tried -> r | bar 4: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 5: 15 syllables for a target of 11; 11 variants tried -> no passing variant, | bar 6: 18 syllables for a target of 10; 9 variants tried -> no passing variant,  | bar 7: 14 syllables for a target of 10; 15 variants tried -> no passing variant, | bar 8: 14 syllables for a target of 10; 12 variants tried -> no passing variant,
    before: By breakfast I was orange like a bin. / The whole city was my crowd, not a sin. / I smoked weed on a canal bench, stumbled in. / Coffee shop menu like a wine list, fumbled in. / I walked through red light district, eyes front, like the shortcut it is. / The superhero finale ran three hours, I saw the ending twice. / I passed out in the aisle, the pun on aisle held for the tail. / The lights came up and I was the only one lying down.
    after:  Breakfast had me orange like little. / The whole city was my crowd, not a sin. / I smoked weed on canal bench, stumbled in. / Coffee shop menu like wine list, fumbled in. / I walked through red light district, eyes front, like the shortcut it is. / The superhero finale ran three hours, I saw the ending twice. / I passed out in the aisle, the pun on aisle held for the tail. / The lights came up and I was the only one lying down.
  --- taken:
  1. Breakfast had me orange like little.
  2. The whole city was my crowd, not a sin.
  3. I smoked weed on canal bench, stumbled in.
  4. Coffee shop menu like wine list, fumbled in.
  5. I walked through red light district, eyes front, like the shortcut it is.
  6. The superhero finale ran three hours, I saw the ending twice.
  7. I passed out in the aisle, the pun on aisle held for the tail.
  8. The lights came up and I was the only one lying down.

## V1 25-32 -- BUILT, passes the plan gate
lore_allusion 'Brasso': structurally OK | triggers in the bars: ['brass', 'metal'] | in a rhyme slot: True
argument: In Marrakesh I walk into the big square at four o'clock, am quoted a special price just for me at six stalls running, haggle like a man with a train to catch, and pay the first price anyway.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/2 frame problems=4 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 3: 20 syl (need 14+-1)
  candidate frame fail: bar 5: 20 syl (need 9+-1)
  bar loop (8 calls): bar 1: 22 syllables for a target of 13; 1 variants tried -> repaired | bar 2: 23 syllables for a target of 15; 5 variants tried -> repaired | bar 3: 20 syllables for a target of 14; 10 variants tried -> no passing variant, | bar 4: 5 syllables for a target of 8; 0 variants tried -> repaired | bar 5: 20 syllables for a target of 9; 12 variants tried -> no passing variant,  | bar 6: 20 syllables for a target of 9; 4 variants tried -> repaired | bar 7: 12 syllables for a target of 10; 12 variants tried -> no passing variant, | bar 8: 10 syllables for a target of 15; 18 variants tried -> repaired
    before: Jemaa el-Fna at four, juice stalls like orange pyramids, I walk in like I own the square. / Six stalls in a row each quote a special price just for me, then wait for me to settle. / I offer half, he says three-quarters, the lamp is brass, the rose is a petal. / Final price, said flat. / A resort pool with red-orange parasols and a drink with a straw. / A hammock in a bamboo grove, snow on the High Atlas behind the palms. / Scooters go through the square pedal to the metal. / I paid the first price all along and tipped.
    after:  At four, Jemaa el-Fna, juice stalls like a temple. / Six stalls in row each quote a price, then wait for me to settle. / I offer half, he says three-quarters, the lamp is brass, the rose is a petal. / The final price, said flat, is special. / A resort pool with red-orange parasols and a drink with a straw. / Bamboo grove, snow behind, hammock level. / Scooters go through the square pedal to the metal. / I paid the first price all along and left a medal.
  bar loop (8 calls): bar 1: 22 syllables for a target of 13; 3 variants tried -> repaired | bar 2: 23 syllables for a target of 15; 4 variants tried -> repaired | bar 3: 20 syllables for a target of 14; 10 variants tried -> no passing variant, | bar 4: 5 syllables for a target of 8; 0 variants tried -> repaired | bar 5: 20 syllables for a target of 9; 23 variants tried -> no passing variant,  | bar 6: 20 syllables for a target of 9; 11 variants tried -> repaired | bar 7: 12 syllables for a target of 10; 14 variants tried -> no passing variant, | bar 8: 10 syllables for a target of 15; 18 variants tried -> repaired
    before: Jemaa el-Fna at four, juice stalls like orange pyramids, I walk in like I own the square. / Six stalls in a row each quote a special price just for me, then wait for me to settle. / I offer half, he says three-quarters, the lamp is brass, the rose is a petal. / Final price, said flat. / A resort pool with red-orange parasols and a drink with a straw. / A hammock in a bamboo grove, snow on the High Atlas behind the palms. / Scooters go through the square pedal to the metal. / I paid the first price all along and tipped.
    after:  Four at Jemaa, I walk in like I own the temple. / Six stalls quote me a special price, then wait for me to settle. / I offer half, he says three-quarters, the lamp is brass, the rose is a petal. / Final price, said flat, central. / A resort pool with red-orange parasols and a drink with a straw. / Hammock in bamboo, snow behind petrol. / Scooters go through the square pedal to the metal. / I paid the very first price all along and tipped the vessel.
  --- taken:
  1. Four at Jemaa, I walk in like I own the temple.
  2. Six stalls quote me a special price, then wait for me to settle.
  3. I offer half, he says three-quarters, the lamp is brass, the rose is a petal.
  4. Final price, said flat, central.
  5. A resort pool with red-orange parasols and a drink with a straw.
  6. Hammock in bamboo, snow behind petrol.
  7. Scooters go through the square pedal to the metal.
  8. I paid the very first price all along and tipped the vessel.

## V1 33-44 -- BUILT, passes the plan gate
lore_allusion 'Cartier Santos': NOT met: only 1 distinct trigger(s) from the card (crown); need >= 2 | triggers in the bars: ['crown'] | in a rhyme slot: False
argument: On the 2019 Interrail I did twelve stops in four weeks, a walk in every country, counted one waterfall of the seventy-two, and took the honesty box on trust.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=True frame_ok=False cashed=2/3 frame problems=11 syllable misses=5
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate frame fail: bar 1: 9 syl (need 6+-1)
  candidate frame fail: bar 2: ends |S (need |Sw)
  bar loop (10 calls): bar 1: 9 syllables for a target of 6; 9 variants tried -> no passing variant, le | bar 2: ends |S, needs |Sw; 10 variants tried -> no passing variant, left as it w | bar 3: 9 syllables for a target of 7; 4 variants tried -> repaired | bar 4: 9 syllables for a target of 7; 5 variants tried -> repaired | bar 5: end word 'seen' is used more than once in this block; 1 variants tried -> | bar 7: 8 syllables for a target of 10; 11 variants tried -> no passing variant,  | bar 8: end word 'bridge' is used more than once in this block; 1 variants tried  | bar 9: end word 'train' is used more than once in this block; 0 variants tried - | bar 10: 7 syllables for a target of 11; 9 variants tried -> repaired | bar 11: ends |S, needs |Sw; 10 variants tried -> no passing variant, left as it  | bar 12: not attempted (call budget 10 reached)
    before: The pass validated, that's Zurich. / First stamp, then Bern, watch crown as you must. / Seventy-two falls, I counted one. / The valley of falls, I saw just one. / David in Florence, seen. / A walk in Fiesole, the pink church seen. / Ljubljana, dragons on the bridge. / Bratislava, the UFO bridge. / Vienna, Freud, before the train. / Zell am See, the lake, then train. / Black Forest drinks stall runs on trust. / Twelve stops, nine countries, home on a flight.
    after:  The pass validated, that's Zurich. / First stamp, then Bern, watch crown as you must. / Seventy-two falls, one story. / Valley falls, I saw one order. / David in Florence, saw. / A walk in Fiesole, the pink church seen. / Ljubljana, dragons on the bridge. / In Bratislava I saw the bridge they call. / Vienna, Freud, before train. / Zell am See, I saw lake before the train, you're sure. / Black Forest drinks stall runs on trust. / Twelve stops, nine countries, home on a flight.
  bar loop (10 calls): bar 1: 8 syllables for a target of 6; 10 variants tried -> no passing variant, l | bar 2: ends |S, needs |Sw; 5 variants tried -> no passing variant, left as it wa | bar 3: 9 syllables for a target of 7; 5 variants tried -> no passing variant, le | bar 4: ends |S, needs |Sw; 3 variants tried -> repaired | bar 5: end word 'seen' is used more than once in this block; 1 variants tried -> | bar 7: ends |S, needs ~w; 14 variants tried -> no passing variant, left as it wa | bar 8: end word 'bridge' is used more than once in this block; 2 variants tried  | bar 9: end word 'train' is used more than once in this block; 0 variants tried - | bar 10: 7 syllables for a target of 11; 17 variants tried -> no passing variant, | bar 11: ends |S, needs |Sw; 5 variants tried -> no passing variant, left as it w | bar 12: not attempted (call budget 10 reached)
    before: Zurich validated the pass. / First stamp in Bern, watch crown as you must. / Seventy-two falls, I counted one. / The valley of falls, I saw one. / David in Florence seen. / A walk in Fiesole, pink church seen. / Ljubljana, the dragons on the bridge. / Bratislava, the UFO bridge. / Vienna, Freud, before the train. / Zell am See, the lake, then train. / Black Forest drinks stall runs on trust. / Twelve stops, nine countries, home on a flight.
    after:  Zurich validated the pass. / First stamp in Bern, watch crown as you must. / Seventy-two falls, I counted one. / Valley of falls, saw one morning. / David in Florence, thought. / A walk in Fiesole, pink church seen. / Ljubljana, the dragons on the bridge. / Bratislava, I saw UFO bridge, course. / Vienna, Freud, before train. / Zell am See, the lake, then train. / Black Forest drinks stall runs on trust. / Twelve stops, nine countries, home on a flight.
  --- taken:
  1. The pass validated, that's Zurich.
  2. First stamp, then Bern, watch crown as you must.
  3. Seventy-two falls, one story.
  4. Valley falls, I saw one order.
  5. David in Florence, saw.
  6. A walk in Fiesole, the pink church seen.
  7. Ljubljana, dragons on the bridge.
  8. In Bratislava I saw the bridge they call.
  9. Vienna, Freud, before train.
  10. Zell am See, I saw lake before the train, you're sure.
  11. Black Forest drinks stall runs on trust.
  12. Twelve stops, nine countries, home on a flight.

## V2 1-8 -- BUILT, FAILS the plan gate
argument: Every walk of that Interrail was in the wrong shoes, the Swiss snow over my boots, and I would not wish them on anyone; I have been in my own shoes ever since.
generated 9 blocks from 3 seeds (1 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=2/3 frame problems=4 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: shoes
  candidate frame fail: bar 4: ends |S (need |w)
  candidate frame fail: end word 'sho' repeats on bars [1, 8] (no end word may repeat in a block)
  bar loop (7 calls): bar 1: end word 'shoes' is used more than once in this block; 0 variants tried - | bar 3: 12 syllables for a target of 10; 0 variants tried -> repaired | bar 4: ends |S, needs |w; 10 variants tried -> no passing variant, left as it wa | bar 5: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 6: 16 syllables for a target of 12; 3 variants tried -> repaired | bar 7: 15 syllables for a target of 11; 23 variants tried -> no passing variant, | bar 8: end word 'shoes' is used more than once in this block; 0 variants tried -
    before: The Swiss walk is knee-deep in snow, in these shoes / Florence is a climb to Fiesole for the views / Ljubljana is a rest day under tram queues / Zell am See is a turquoise lake with blues / Munich is a Bayern match with red and white dues / The Black Forest is a waterfall walk and grey lake with clues / Amsterdam is a bench, a coffee shop, a cruise / Back to the boots by the door, in my shoes
    after:  Swiss walk is knee-deep in snow, in these shoes / Florence is a climb to Fiesole for the views / Ljubljana is rest day under tram queues / Zell am See is a turquoise lake with blues / Munich is Bayern match with red and white dues / Black Forest waterfall walk and grey lake view / Amsterdam is a bench, a coffee shop, a cruise / Back to boots by the door, in my shoes
  bar loop (7 calls): bar 1: end word 'shoes' is used more than once in this block; 0 variants tried - | bar 3: 12 syllables for a target of 10; 0 variants tried -> repaired | bar 4: ends |S, needs |w; 11 variants tried -> no passing variant, left as it wa | bar 5: 13 syllables for a target of 11; 0 variants tried -> repaired | bar 6: 16 syllables for a target of 12; 4 variants tried -> repaired | bar 7: 15 syllables for a target of 11; 3 variants tried -> repaired | bar 8: end word 'shoes' is used more than once in this block; 0 variants tried -
    before: The Swiss walk is knee-deep in snow, in these shoes / Florence is a climb to Fiesole for the views / Ljubljana is a rest day under tram queues / Zell am See is a turquoise lake with blues / Munich is a Bayern match with red and white dues / The Black Forest is a waterfall walk and grey lake with clues / Amsterdam is a bench, a coffee shop, a booze / Back to the boots by the door, in my shoes
    after:  Swiss walk is knee-deep in snow, in these shoes / Florence is a climb to Fiesole for the views / Ljubljana is rest day under tram queues / Zell am See is a turquoise lake with blues / Munich is Bayern match with red and white dues / Black Forest is waterfall walk and grey lake view / Amsterdam is bench, coffee shop, old school / Back to boots by the door, in my shoes
  --- taken:
  1. Swiss walk is knee-deep in snow, in these shoes
  2. Florence is a climb to Fiesole for the views
  3. Ljubljana is rest day under tram queues
  4. Zell am See is a turquoise lake with blues
  5. Munich is Bayern match with red and white dues
  6. Black Forest is waterfall walk and grey lake view
  7. Amsterdam is bench, coffee shop, old school
  8. Back to boots by the door, in my shoes

## V2 9-16 -- BUILT, FAILS the plan gate
lore_allusion 'Hammerite': structurally OK | triggers in the bars: ['paint', 'rust', 'tin', 'direct', 'paint', 'rust'] | in a rhyme slot: False
argument: On the Naples stag weekend I paint the town red: three-euro cocktails in a stone alley, a shrine to Maradona, Pompeii in March sun, a shot in each hand, and I wake up with a Vespa key and no Vespa (cartoon).
generated 6 blocks from 2 seeds (2 rejected), 0 passed both gates
candidate: plan_ok=False frame_ok=False cashed=1/2 frame problems=11 syllable misses=4
incumbent: plan_ok=None frame_ok=None cashed=None/None frame problems=None syllable misses=None
  candidate plan fail: end word repeated inside the block: red
  candidate frame fail: bar 3: 15 syl (need 10+-1)
  candidate frame fail: bar 3: ends |Sw (need |S)
  bar loop (8 calls): bar 1: ends |Sw, needs |S; 0 variants tried -> repaired | bar 2: end word 'steady' is used more than once in this block; 0 variants tried  | bar 3: 15 syllables for a target of 10; 6 variants tried -> no passing variant,  | bar 4: 15 syllables for a target of 10; 1 variants tried -> repaired | bar 5: ends |S, needs |SS; 7 variants tried -> no passing variant, left as it wa | bar 6: verifier: sense: inventory of 7 things and no claim (Red shot in each han | bar 7: 12 syllables for a target of 9; 1 variants tried -> repaired | bar 8: ends |S, needs ~w; 10 variants tried -> no passing variant, left as it wa
    before: Stone alley, price board ready. / Tall blue cocktails, black straws, three euros, steady. / Maradona shrine, sky-blue shirt, I pay respects, steady. / Pompeii, Vesuvius, March sun, amphitheatre, all dead. / Stag in blue sash, I'm best man. / Red shot in each hand, one for photo, red. / Woke with Vespa key, no Vespa, nobody asked. / Tin of direct-to-rust, no recap, paint town red.
    after:  Stone alley bar, price board, done. / Tall blue cocktails, black straws, three euros going. / Maradona shrine, sky-blue shirt, I pay respects, steady. / Pompeii, Vesuvius, March sun, all run. / Stag in blue sash, I'm best man. / Red shot in each hand, one for photo, red. / Woke with Vespa key, no Vespa, ask much. / Tin of direct-to-rust, no recap, paint town red.
  bar loop (8 calls): bar 1: ends |Sw, needs |S; 1 variants tried -> repaired | bar 2: 10 syllables for a target of 12; 5 variants tried -> no passing variant,  | bar 3: 16 syllables for a target of 10; 5 variants tried -> no passing variant,  | bar 4: 12 syllables for a target of 10; 1 variants tried -> repaired | bar 5: ends |S, needs |SS; 9 variants tried -> no passing variant, left as it wa | bar 6: verifier: sense: inventory of 7 things and no claim (Red shot in each han | bar 7: 13 syllables for a target of 9; 1 variants tried -> repaired | bar 8: ends |S, needs ~w; 5 variants tried -> no passing variant, left as it was
    before: Alley bar, price board ready. / Blue cocktails, black straws, three euros, steady. / Maradona wall shrine, sky-blue shirt, I pay respects, steady. / Pompeii under Vesuvius, March sun, all dead. / Stag in blue sash, I'm best man. / Red shot in each hand, one for the photo, red. / Woke with Vespa key and no Vespa, nobody asked. / Tin of direct-to-rust, no recap, paint town red.
    after:  Alley bar, price board done. / Blue cocktails, black straws, three euros, steady. / Maradona wall shrine, sky-blue shirt, I pay respects, steady. / Pompeii, Vesuvius, March sun, all dead. / Stag in blue sash, I'm best man. / Red shot in each hand, one for the photo, red. / Woke up with key, no Vespa, no one asked. / Tin of direct-to-rust, no recap, paint town red.
  --- taken:
  1. Stone alley bar, price board, done.
  2. Tall blue cocktails, black straws, three euros going.
  3. Maradona shrine, sky-blue shirt, I pay respects, steady.
  4. Pompeii, Vesuvius, March sun, all run.
  5. Stag in blue sash, I'm best man.
  6. Red shot in each hand, one for photo, red.
  7. Woke with Vespa key, no Vespa, ask much.
  8. Tin of direct-to-rust, no recap, paint town red.
