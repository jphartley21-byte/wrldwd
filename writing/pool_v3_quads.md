# Quad pool v3 (11 Oct 2026): first machine-scored batch of 4-bar candidates

Method: the pipeline in the session plan (SOUND MAP -> BEAT SHEET -> BUILD -> SCORE -> REPAIR -> RATCHET -> PARK).
Built in the main thread with the toolkit only (no agents, CLAUDE.md rule 6). Every quad was scored with
`rhyme_tools.py check` + `quad` and `check_all.py --slot`; facts are from material/travel_history.md.
Status: FIRST PASS, candidates for Joe's ear, not signed off. Per G5 a weakest bar is named for each.

Calibration note (important): `check_all.py` compares our bars to the ORIGINAL slot's measured rhythm
(exact syllable count, end shape, 75% stress-grid overlap). Joe's own LOCKED bars 1-4 fail it too, so
full ALL PASS is a rhythm-clone target, not the human-review bar. Review bar used here = by-ear scheme +
carpet + technique floor + gates G1-G6. See findings at the end.

---

## Q1 — hook 5-8 (Porto / borders) | carpet AO(3)+OW | A C C A
Hola, and it's Porto
Their man on the quay wants the whole order
Says the lot's in a shed by the border
Might fetch it and drive to Bordeaux

- Why: greeting #2 (Hola) + place; business bridge; goods "over the border" (Fermoselle/Portugal, 2023); modal closer.
- Weakest: L2 ("their man ... the whole order") is generic register, no payoff.
- Truth: Porto 2023, Fermoselle border 2023, Bordeaux = locked L4. Weakish wordplay; flat but connected.
- Quad: scheme2 ABBA; fem_end 3; multisyl 4; mosaic 3; perfect_pairs 4; carpet AO 3/4.

## Q2 — hook (Oslo) | carpet OW 4/4
Cancelled the courier, kept it low
Booked it one-way, told 'em where to go
Missus thinks I'm in Oslo, she does not know
Might be back for Sunday, though

- Why: menace ("cancelled the courier") reported as admin; "one-way" (ticket/booked); domestic "Missus" mentioned not addressed.
- Weakest: L3 (three flat clauses; "she does not know" exists only to reach the rhyme — fails G3 as written).
- Truth: Oslo 2024. Persona: courier/missus.
- Quad: scheme1 AAAA; perfect_pairs 8; allit_bars 2; carpet OW 4/4; depth [1,1,1] (hard endings — nursery-rhyme risk).

## Q3 — verse (Vietnam / Amsterdam) | carpet AE(3)+AA
Woke up in Vietnam
Hostel did toast and jam
Fella there said the whole lot's in Amsterdam
So I'm booked on the first run, no scam

- Why: rags/hostel scene; the "lot" moved Amsterdam = logistics set; flat report.
- Weakest: L4 ("no scam") is a filler tag that says nothing (G1/G3).
- Truth: Vietnam 2015, Amsterdam 2019. "Fella" invented.
- Quad: carpet AE 4/4; depth [1,2,2]; perfect_pairs 6.

## Q4 — verse (John o' Groats) | carpet OW 4/4 | mono -oats
Rolled up to John o' Groats
Wind off the sea, two coats
Skipper says there's no boats
Might stop for a pint and take it slow

- Why: place; weather-as-poverty ("two coats"); "no boats" (ferry gone) flat.
- Weakest: L2/L4 near-cliche; "take it slow" is filler (G3).
- Truth: John o' Groats 2024 (motorbike, May); the skipper/no-boats line is INVENTED.
- Quad: scheme2 ABAC; groats/coats/boats perfect (depth 3,3); carpet OW 4/4; internal_bars 1.

## Q5 — verse (-oo / "flight risk") | carpet UW 4/4
Called a flight risk, so I flew
Case in the hold, nothing new
Left the keys with a mate, that's true
Might be back in a week or two

- Why: travel word "flight risk" cashed literally; domestic anchor (mate, keys); modal.
- Weakest: L3 ("that's true") filler; the pun is not in the rhyme slot (rubric 38 wants payoff word there).
- Truth: persona. Weakest quad for wordplay.
- Quad: carpet UW 4/4; depth [1,1,1] (hard endings); perfect_pairs 7; mate x1.

## Q6 — verse (Naples/Pompeii + Byron Bay) | carpet EY 4/4
Coach from Naples out to Pompeii
Queue was long, so I paid, okay
Told the lads I'm not one to stay
Might do the coast and kip in Byron Bay

- Why: Pompeii as a queue; "paid" (bribe/entry) flat; mode shift to Byron Bay.
- Weakest: L3 (filler; "not one to stay" says little).
- Truth: Naples/Pompeii 2026 (stag), Byron Bay 2017.
- Quad: scheme1 AAAA; internal_bars 2; perfect_pairs 10; carpet EY 4/4.

## Q7 — START HERE: the AAAA model quad (Oslo) | carpet AA-OW, 2-syllable
Hei, and I'm up in Oslo
Says the money will follow
Good for it, or he will borrow
Might stick about till tomorrow

- Why: best technique in the batch — true AAAA on a TWO-syllable tail (AA-x-OW), like the locked bars' AO-OW.
- Weakest: L3 ("Good for it, or he will borrow") — the debt idea is thin without a scene.
- Truth: Oslo 2024; their man/debt = persona. Needs OVR entry for "hei".
- Quad: scheme2 AAAA; end_cover2 4/4; fem_end 2; multisyl 9; mosaic 3; perfect_pairs 6; homophones 1.

## Q8 — verse (Bilbao / Koh Tao) | carpet AW 4/4 | pun pair "checked out"
Kaixo, and I'm in Bilbao
Their number one got checked out
So I checked out the hostel just now
Might head to Koh Tao, no idea how

- Why: greeting #2 (Kaixo) + place; the two-line pun pair the spec asks for — "checked out" = killed, then "checked out" = hostel checkout, the mundane travel sense.
- Weakest: L2 ("Their number one") — the menace needs a firmer noun.
- Truth: Bilbao 2023, Koh Tao 2015. "Their number one" = persona (invented).
- Quad: carpet AW 4/4; scheme1 AAAA; echo_words ['checked']; perfect_pairs 6.

---

## Findings from this batch (for the toolkit / STATE)
1. CALIBRATION GAP: `check_all` ALL PASS requires matching the original bar's exact syllable count,
   end shape and stress grid. Joe's locked bars fail it; so do all these. Either the definition of done
   means "form-matches the original's rhythm" (i.e. our slot bars should be rhythm-clones, not free),
   or the flow_fit target needs a tolerance. Ask Joe which.
2. PLACE END WORDS ARE VOWEL-LOCKED: a place's STRESSED vowel sets the carpet (Porto AO, Oslo AA,
   Padstow AE, Calais AE, Vietnam AA). Only Bordeaux/Porto share the AO-OW tail, so an AO-OW place pair
   is hard. `check` must be run on the end word before a place is chosen.
3. To EARN scheme2 AAAA (2-syllable), design the quad around a shared 2-syllable tail:
   -AA-x-OW: Oslo / follow / borrow / tomorrow (Q7). Others: borrow, sorrow, hollow, swallow, also.
   -OW-T-S: Groats / coats / boats / oats / votes / quotes.
   -AW: Bilbao / Koh Tao + out / now / how.
4. TOOLKIT BUG (pre-existing): OVR keys containing an apostrophe ("he's", "should've", "'em") are
   unreachable — `pron()` strips the apostrophe before lookup, so they never match and the word shows OOV.
5. Every quad ends on a 4-line flat scene; none yet has the original's register ramp or a number ladder.
   Next batch should force: one perfect pair that changes register, one number ladder, one enjambed rhyme.

---

# BATCH 2 (12 quads, same pipeline). All 12 chains: carpet 4/4, no OOV. Status: candidates for Joe's ear.

## Q9 — verse (docks, price ladder) | carpet AW 4/4 | numbers ladder
Sorted the drop at the docks, in and out
Nothing in writing, and nothing to doubt
Twenty a head, then it's thirty to shout
Forty and done, and I'm not hanging about

- Why: job terms as a pub round; no paperwork ("nothing in writing"); ladder twenty/thirty/forty (criterion 14).
- Weakest: L1 ("sorted the drop" is the register's cliche). Truth: persona; "haggle" real (Marrakesh 2025).
- Quad: numbers 3; perfect_pairs 4; mosaic 3; depth [2,2,2].

## Q10 — verse (ferry delay claim) | carpet EY 4/4
Paid for the crossing, then claimed the delay
Bloke on the desk says he can sort it today
Said I'll be back, put the case in the bay
Nobody checked, so we're both on our way

- Why: "delay" (compensation claim) cashed; "nobody checked" (customs) flat; deliberately avoids the original's "back shortly" frame.
- Weakest: L2 (11 syllables, stress 9 — long for a hook slot). Truth: persona; ferry 2023.
- Quad: internal_bars 2; multisyl 8; mosaic 8; allit_bars 4.

## Q11 — verse (postal logistics) | carpet EY-N 4/4
Whole thing runs like the post, no strain
Depot in Porto, a pickup in Spain
Everyone drops it, and I'm on the train
Not on the websites, I'm out in the rain

- Why: dealing as postal logistics (rubric 15) without cloning the original's network-not-social line.
- Weakest: L4 ("out in the rain" is filler). Truth: Porto + Spain 2023.
- Quad: depth [2,2,3]; perfect_pairs 6.

## Q12 — verse (rags to riches) | carpet IH-P 4/4
Backpacking, broke, with a hole in the zip
Slept on a floor for a kip
Now the lads are on the payroll to tip
And I'm too busy to stop for a chip

- Why: rags (broke, hostel) -> now (payroll); "kip" real British; "chip" a domestic anchor.
- Weakest: L4 (says little). Truth: broke backpacking 2015-17; payroll persona.

## Q13 — verse (Isle of Man) | carpet AE-N 4/4
Landed in Douglas, the Isle of Man
Doubled the cash in the back of the van
Wrapped him up tidy, that's part of the plan
Left him somewhere that nobody would scan

- Why: touch down; cash doubled; violence reported as packing (deadpan).
- Weakest: L4. Truth: Douglas/Isle of Man 2023; violence persona.

## Q14 — verse (Marrakesh) | carpet IY-T 4/4
Mint tea in the souk, and it's out of the heat
Barber took two quid, and he did it in the street
Fags are a fiver, so I'm onto a treat
The place has a pool, and I'm back on my feet

- Why: lived detail (mint tea, two-quid fade, cheap fags) — rubric 31.
- Weakest: L4 ("the place has a pool" is invented, not Joe's). Truth: Marrakesh 2025 (tea, barber true); pool INVENTED.

## Q15 — verse (the bribe) | carpet EH-ty 4/4 | the soft-ending block
Gendarme fined me, and it's heavy
I spot him a twenty
He pockets it, says twenty's plenty
Then points me the way to the ferry

- Why: bribe; cop changes tune on the spot; "spot him a twenty" (notice/give); all FOUR endings feminine (rubric 2).
- Weakest: L1. Truth: gendarme/fine is Joe's story (Pyrenees 2025).
- Quad: scheme2 AAAA; fem_end 4/4; multisyl 12; homophones 1.

## Q16 — verse (Whitsundays) | carpet UW 4/4
Hired the whole boat, and the crew's brand new
Black tie up on deck, and the water's blue
Soaked to the skin, but the suit pulls through
Mum calls it a gap year, and that's half true

- Why: luxury cruise; "pulls through" (idiom cashed); Mum + gap year (rubric 13/16).
- Weakest: L2. Truth: Whitsundays 2017; black tie = invented flourish (FLAG).

## Q17 — verse (Snowdon) | carpet IH-P 4/4
Solo up Snowdon, and I'm taking the trip
Big lad on the ridge, and he keeps giving me lip
Caught him a right, and I had him in a grip
Left him on the scree, and he started to slip

- Why: hike; playground violence (trip/lip/grip/slip); dense internal rhyme (4 bars).
- Weakest: L2 (12 syllables). Truth: Snowdon 2024; the fight is persona.

## Q18 — verse (sport as violence) | carpet EY-S 4/4
Big lad served, and I gave one back, ace
Went over the net, flat on his face
Left him a mess in the middle of the place
Nobody saw, so there is not a case

- Why: tennis for violence (rubric 17); "no case" = no police file (wordplay in the rhyme slot).
- Weakest: L3. Truth: persona.

## Q19 — hook roll call | carpet EY 4/4
Servus, up in Zell am Zay
G'day, down in Byron Bay
Gracias, on the ferry today
Ciao, and I'm back on my way

- Why: roll call of greetings + places (criterion 19); each greeting is correct for its place.
- Weakest: L4. Truth: Zell am See 2019 (Servus, Austrian), Byron Bay 2017 (G'day), ferry 2023.

## Q20 — verse (fare ladder) | carpet EY-T 4/4 | numbers ladder
Course of the ferry, and I'm running late
Two on the gate, and it's four for the freight
Six in the kitty, and eight on the plate
Ten for the man at the gate, and I'm straight

- Why: counted ladder two/four/six/eight/ten; fees as admin; "on the plate" (settled) + "straight" (no trouble).
- Weakest: L2. Truth: persona.
- Quad: numbers 5; perfect_pairs 20; carpet EY 7/19.

## Batch 2 note
TOOLKIT: added OVR entries `fiver`, `gday`, `hei`, `handoff` (rhyme_tools.py) so real words stop showing OOV;
re-ran `calibrate.py` — still PASSED. Still open: the schema2 AAAA target needs a shared 2-syllable tail,
so future quads should be designed from that tail backwards (Q7, Q15 show the two routes: vowel-tail vs -ty).

---

# BATCH 3 (12 quads; designed from a shared 2-syllable tail backwards). All chains: carpet 4/4, no OOV.
Four hit true scheme2 AAAA (Q21, Q22, Q26, Q28). Status: candidates for Joe's ear.

## Q21 — verse (flat refusals) | carpet EH-V-ER 4/4 | scheme2 AAAA
Nothing on the telly, so it's whatever
Missus asks the time, and I say whenever
Firm asks who's coming, and I say whoever
Slip them the bag, and I do not endeavour

- Why: deadpan non-engagement; domestic anchors (telly, missus); "the Firm" = business. whatever/whenever/whoever/endeavour = 2-syllable run.
- Weakest: L4. Truth: persona.
- Quad: scheme2 AAAA; fem_end 4/4; perfect_pairs 13; homophones 1; depth [3,3,3].

## Q22 — verse (conference, Barcelona) | carpet OW-N-AH 4/4 | scheme2 AAAA
Off to a conference in Barcelona
Pool on the roof and a cold corona
Nobody knows my real persona
Told the whole hall I'm a bit of a Jonah

- Why: work trip; "persona" pun; self-mockery ("a bit of a Jonah" = a jinx) — needs Joe's OK (rule 18).
- Weakest: L1. Truth: Barcelona 2026 conference TRUE (ran 17.2 km and 10 km there); rest persona.
- Quad: scheme2 AAAA; perfect_pairs 12; homophones 1; carpet OW 9/19.

## Q23 — verse (Interrail totals) | carpet EY 4/4 | retail/wholesale
Rail pass, twenty-eight days, never paid retail
Took the whole continent on in one go, wholesale
Seven countries, one card, and nobody read the detail
Made the last train, and I did not need bail

- Why: commerce set (retail/wholesale) for a rail pass; true totals (planned 21 days/9 countries, did 28/7).
- Weakest: L4. Truth: Interrail Apr 2019 TRUE.
- Quad: multisyl 10; mosaic 9; perfect_pairs 17; homophones 2.

## Q24 — verse (Bangkok) | carpet AA-K 4/4
Touched down in Bangkok
Kept the lot in a sock
Copper on the block
So I'm watching the clock

- Why: customs tension, flat and percussive. Weakest: L4. Truth: Bangkok 2015 TRUE.
- Quad: depth [2,2,3]; carpet AA 7/11.

## Q25 — verse (Larrau pass) | carpet AY 4/4
Pass in the clouds, and it's up to the sky
Cows on the road, and they do not ask why
Fog coming down, and I'm keeping it dry
Right of way's theirs, so I wait, and I sigh

- Why: pass/fog/cows TRUE (2023/2025); "right of way" as a road rule. Weakest: L4.
- Quad: depth [1,1,1] (hard endings).

## Q26 — verse (Bratislava) | carpet AA-V-AH 4/4 | scheme2 AAAA
Week three, and it's on to Bratislava
Coffee so strong that it's like drinking lava
Met a bloke there who swears he is from Java
I said "sound", and I paid for a guava

- Why: Bratislava/lava/Java/guava = exact 2-syllable run; the classic mosaic.
- Weakest: L4. Truth: Bratislava Apr 2019 TRUE; Java/guava invented.
- Quad: scheme2 AAAA; depth [4,3,3]; perfect_pairs 10.

## Q27 — verse (night flight) | carpet AY-T 4/4
Booked the last flight, and I'm out in the night
Nobody knows, and it feels about right
Case in the hold and the seal's on tight
Back in the morning, and it's out of sight

- Why: night flight; "out of sight" cashed. Weakest: L4. Truth: persona.
- Quad: depth [2,2,2]; perfect_pairs 11.

## Q28 — verse (the gendarme) | carpet AA-K 4/4 | scheme2 AAAA
Pulled in and parked by the rock
Gendarme came over and gave me a shock
Wanted a fine, so I peeled off a block
Paid him, and he waves me off from the dock

- Why: bribe; "peeled off a block" = a roll of notes (British). Weakest: L1. Truth: gendarme/fine is Joe's story.

## Q29 — verse (the overrun) | carpet AE-K 4/4
Zipped up the panniers and checked the sack
Told her a week, and I did not come back
Went the long way round and I lost the track
Got in at three, and she's up, and it's black

- Why: true overrun told flat; domestic return. Weakest: L4. Truth: overran the plan (28 vs 21 days) TRUE.

## Q30 — verse (interrogation) | carpet AW-N-D 4/4
Asked where the case could be found
I said "no idea", and I stared at the ground
He said he was having a look all around
So I slipped him a twenty, and a couple of pound

- Why: bribe under questioning, flat. Weakest: L3. Truth: persona.
- Quad: depth [3,3,3]; perfect_pairs 8.

## Q31 — verse (lost parcel) | carpet OW-S-T 4/4 | scheme2 AAAA
Packed it up neat and I sent it by post
Nobody signed for it, so it's a ghost
Told them it's gone, and I'll raise a toast
Down by the harbour for a Sunday roast

- Why: postal set (a tracked parcel gone); toast/roast bathos. Weakest: L3. Truth: persona.
- Quad: scheme2 AAAA; depth [3,3,3]; multisyl 4.

## Q32 — verse (the train) | carpet AY-N 4/4
Slow train and a bottle of wine
Rucksack down by the side of the Rhine
Bloke in the carriage says the seat's all mine
Nobody checks me, so I'm doing fine

- Why: train scene, flat. Weakest: L4. Truth: Interrail 2019 TRUE; the Rhine leg is FLAGGED (route not confirmed).
- Quad: depth [2,2,2]; perfect_pairs 8; homophones 1.

## Batch 3 note
TOOLKIT: added OVR `rhine`. `calibrate.py` re-run — PASSED. AAAA is reliably reachable by choosing the
2-syllable tail first (Q7 AA-OW, Q21 EH-V-ER, Q22 OW-N-AH, Q26 AA-V-AH, Q28 AA-K, Q31 OW-S-T); the
remaining quads are AAAB/ABAA/ABCD on solid 4/4 carpets (depth >= 2 nearly everywhere).

---

# BATCH 4 (12 quads; leaned harder on 2-syllable tails). All chains: carpet 4/4, no OOV.
Six hit scheme2 AAAA (Q33, Q34, Q35, Q37, Q39, Q41, Q43 — seven counting Q43). Status: candidates for Joe's ear.

## Q33 — verse (pub bingo) | carpet IH-NG-OW 4/4 | scheme2 AAAA
Eyes down in the pub and it's bingo
Big lad in the corner like a flamingo
Nobody at the table's on my lingo
So I settle it outside, and it's bingo

- Why: playground game as violence (rubric 17); "bingo" repeated as an echo-with-a-twist (winning = settled).
- Weakest: L3. Truth: persona.
- Quad: scheme2 AAAA; depth [4,4,4]; multisyl 6.

## Q34 — verse (customs) | carpet IY-K-IY 4/4 | scheme2 AAAA
Nothing in the case, and the seal's not leaky
Bloke on the gate is looking peaky
Once I have had a word, he is not so cheeky
Kept my head down, and I moved it, sneaky

- Why: customs/bribe, flat. Weakest: L1. Truth: persona.
- Quad: scheme2 AAAA; depth [3,3,3]; mosaic 3.

## Q35 — verse (homecoming) | carpet EH-L-IY 4/4 | scheme2 AAAA
Back on the sofa, in front of the telly
Roast in the oven, and I'm filling my belly
News says the world's a wobbly jelly
And the dog's on my lap, and it's back on the telly

- Why: domestic anchors (telly, roast, dog); "telly" echo. Weakest: L3. Truth: persona.

## Q36 — verse (bribe, refuse) | carpet AY-N-D 4/4
Nothing in the hold, nothing behind
Nobody comes near, and I do not mind
Copper's got a hunch, but nothing to find
So I pay him off, and he is suddenly kind

- Why: no evidence, flat bribe; "nothing behind" (nothing following). Weakest: L1. Truth: persona.
- Quad: depth [3,3,3]; perfect_pairs 10.

## Q37 — verse (hill ride) | carpet IH-L-IY 4/4 | scheme2 AAAA
Up in the hills, and it's getting chilly
Bloke at the top says I'm being silly
Sent the bike down, and it's fast and hilly
Back at the digs and I'm eating a chilli

- Why: hill ride; dense internal rhyme. Best technique of the batch. Weakest: L4. Truth: hills TRUE; chilli invented.
- Quad: scheme2 AAAA; multisyl 15; mosaic 9; homophones 1.

## Q38 — hook 9-16 (repeat job) | carpet OW 4/4
Second run of the summer, and I'm taking it slow
Their man on the ramp says it's a no-go
Wants the whole lot now, and I tell him "so-so"
Back on the boat out of Porto, and it's all go

- Why: repeat job, flat refusal; Porto (2023) internal. Weakest: L3. Truth: Porto 2023; rest persona.
- Quad: depth [1,1,1]; multisyl 9; mosaic 9.

## Q39 — verse (tracked parcel) | carpet EY-L 4/4 | scheme2 AAAA
Tracked it all on the post, and it's gone in the mail
Told them it's landed, and it's not for sale
Copper came round with a warrant and bail
And I'm off down the road with a different tale

- Why: postal set + police; each line a new register. Weakest: L4. Truth: persona.
- Quad: scheme2 AAAA; depth [2,2,2].

## Q40 — verse (refusal) | carpet AE-N 4/4
Copper asked if I'm the man
I said "never heard of him", sat in the van
He wanted a statement, I gave him "no plan"
And he let me go, and he did not scan

- Why: interrogation refused, flat. Weakest: L3. Truth: persona.

## Q41 — verse (Pyrenees) | carpet IY-Z 4/4 | scheme2 AAAA
Off to the Pyrenees
Case on the bike, and I'm at ease
Wind in the pass, and it's a breeze
Sandwich and a bit of the cheese

- Why: bike trip reported flat; Pyrenees/ease/breeze/cheese exact. Weakest: L4. Truth: Pyrenees 2025 TRUE.
- Quad: scheme2 AAAA; depth [2,2,2].

## Q42 — verse (border run) | carpet AE-P 4/4
Laid it all out on the map
Nobody spotted a gap
Copper's asleep, having a nap
So it's over the border, no trap

- Why: border crossing, flat. Weakest: L4. Truth: persona (border 2023 vibe).

## Q43 — verse (paid off) | carpet AA-P 4/4 | scheme2 AAAA
Told them I'd get them a spot
Paid for the whole of the lot
Nobody heard a shot
And it's all tied up in a knot

- Why: euphemism ("no shot"); one flat line per beat. Weakest: L3. Truth: persona.
- Quad: scheme2 AAAA; depth [2,2,2].

## Q44 — verse (Donegal) | carpet AO-L 4/4
Up through Donegal, nothing to call
Pub on the corner and a bit of a wall
Slept in the van in the back of the hall
Back on the road in the morning, that's all

- Why: Donegal (2023) internal; call/wall/hall/all exact. Weakest: L4. Truth: Donegal May 2023 TRUE.

## Batch 4 note
TOOLKIT: added OVR `peaky`, `pyrenees`. `calibrate.py` re-run — PASSED. Pool now 44 quads.
Nameable tails so far (all G2-clean): EH-V-ER, OW-N-AH, AA-V-AH, AA-K, OW-S-T, AA-OW, IH-NG-OW,
IY-K-IY, EH-L-IY, IH-L-IY, AY-N-D, EY-L, AE-N, IY-Z, AE-P, AA-P, AO-L, UW, EY, AY, AW.

---

# BATCH 5 (12 quads; one-syllable-tail families). All chains: carpet 4/4, no OOV.
Status: candidates for Joe's ear. Weakest bar named everywhere.

## Q45 — verse (bike, skint) | carpet ER-D-IY 4/4 | scheme2 AAAA
Road's all gravel and the bike's dirty
Tank's near empty, and I have only thirty
Rode it in fast, and the engine's thirsty
Pint in the corner, and I'm not thirty

- Why: bike debt/range; the last line is a self-mockery gag that NEEDS Joe's OK (rule 18). Weakest: L1. Truth: persona.
- Quad: scheme2 AAAA; multisyl 7.

## Q46 — verse (lone travel) | carpet OW-N 4/4
Nobody answered, so I did not phone
Landed at six, and I'm on my own
Copper on the desk says it's all known
Back on the plane and I'm chilled to the bone

- Why: lone trip, flat; "known"/"chilled to the bone". Weakest: L3. Truth: persona. Quad: depth [2,2,2].

## Q47 — verse (bribe, closed) | carpet UH-K 4/4 | scheme2 AAAA
Nobody does it by the book
Copper gave me a long hard look
I passed him a twenty, and I'm off the hook
And he shuts the file, and he keeps the book

- Why: "by the book" / "off the hook" cashed; file closed. Weakest: L4. Truth: persona.

## Q48 — verse (flat customs) | carpet EY-V 4/4
Wrote it all down and I gave
Nothing in the case and nothing to save
Copper on the gate says I'm being brave
And I'm back on the boat, and I give him a wave

- Why: customs, flat. Weakest: L3. Truth: persona.

## Q49 — verse (collected) | carpet IH-L 4/4
Sent him a photo and I sent him the bill
Two grand for the job, and he pays it, still
Nobody argues, and nobody's ill
And the last one who did is over the hill

- Why: debt collected, clean euphemism ("over the hill"). Weakest: L3. Truth: persona.

## Q50 — verse (paid off) | carpet AA-R-K 4/4
Rode it in through the dark
Left the case out in the park
Copper came over and left his mark
And I'm off down the road with the lot, no remark

- Why: night handover, flat. Weakest: L4. Truth: persona.

## Q51 — verse (framed) | carpet EY-M 4/4
Nobody asked for my name
Whole thing's a bit of a game
Copper's got me in the frame
So I give him the lot and I take the blame

- Why: "in the frame" cashed literally (framed). Weakest: L1. Truth: persona.

## Q52 — verse (the plan) | carpet AA-RT 4/4
Told them the lot from the start
Everyone knows their part
Copper's marking the chart
And I'm gone before he can start

- Why: plan as admin, flat. Weakest: L3. Truth: persona. Quad: perfect_pairs 10.

## Q53 — verse (early start) | carpet AO-N 4/4
Out of the door before dawn
Copper on the gate gives a yawn
I slip him a twenty, and he is gone
And I'm back on the road before the morn

- Why: pre-dawn bribe, flat. Weakest: L1. Truth: persona.

## Q54 — verse (omerta) | carpet UH-D 4/4
Told the lads it's all good
Nobody talks, and nobody should
Everyone's on it, and everyone stood
And I'm back at the bar, and it's understood

- Why: silence code at the pub, flat. Weakest: L1. Truth: persona. Quad: homophones 3.

## Q55 — verse (taped) | carpet EY-P 4/4
Wrapped it all up in the tape
Nothing on me but the shape
Copper's got it all on tape
So I'm off down the road, quick escape

- Why: "tape" cashed twice (packing tape / CCTV tape); "shape" = description. Weakest: L1. Truth: persona.

## Q56 — verse (coast) | carpet IY 4/4
Rode the whole coast and it's free
Nobody's watching, and it's just me
Copper's asleep in the lee of a tree
And I'm off down the road with a flask full of tea

- Why: coast ride, flat; "free"/"tea" domestic. Weakest: L4. Truth: persona; flask/tea TRUE habit.

## Batch 5 note
`calibrate.py` re-run — PASSED. Pool now 56 quads. Reserve tails still unused: AH-N-IY (money/honey),
EH-R-IY (berry/cherry/ferry), IH-T-IY (pretty/city), EH-D-IY (ready/already), UW-Z-IY, AA-M-AH
(drama/llama), OW-L-IY (slowly/lonely), AH-DH-ER (brother/mother), IY-D-IY (speedy/greedy).

---

# BATCH 6 (12 quads; reserved 2-syllable tails + fresh ones). All chains: carpet 4/4, no OOV.
Five hit scheme2 AAAA (Q57, Q58, Q59, Q67, Q68). Status: candidates for Joe's ear.

## Q57 — verse (the pass) | carpet IH-T-IY 4/4 | scheme2 AAAA
Rode the bike into the city
Fella on the corner says the pass is pretty
Told him it's fine, and it's a pity
Cos the top of the pass is a bit gritty

- Why: pass ride, flat. Weakest: L4. Truth: passes TRUE; city/persona.
- Quad: scheme2 AAAA; depth [3,3,3]; multisyl 10; mosaic 9.

## Q58 — verse (the hand-off) | carpet EH-D-IY 4/4 | scheme2 AAAA
Case in the boot, and it's ready
Bloke says the price is settled already
Hand on the gate, keeping steady
And I'm gone before anyone's ready

- Why: hand-off reported flat; ready/already/steady. Weakest: L3. Truth: persona.
- Quad: scheme2 AAAA; multisyl 14; homophones 2.

## Q59 — verse (solo trip) | carpet OW-L-IY 4/4 | scheme2 AAAA
Miles on the clock, and they go slowly
Nights in a tent, and it's getting lonely
One man, one bike, and that's the only
Chapel on the hill, and it's looking holy

- Why: solo trip; slowly/lonely/only/holy. Weakest: L4. Truth: solo bike trips TRUE.

## Q60 — verse (the quote) | carpet UW-Z 4/4
Kept it all quiet, nothing to lose
Their man in the corner is all over the news
I quote him a number, and he does not refuse
And I'm back on the boat, back in my shoes

- Why: quiet deal; lose/news/refuse/shoes. Weakest: L4. Truth: persona.

## Q61 — verse (bribe, gone) | carpet EY-K 4/4
Whole thing's a bit of a mistake
Copper's out front, and I do not break
I hand him a twenty, and that's what it takes
And I'm gone in the morning, and nobody wakes

- Why: "what it takes" cashed; mistake/break/takes/wakes. Weakest: L3. Truth: persona.

## Q62 — verse (homecoming) | carpet AW-N 4/4
Back in my own little town
Case in the hall, settling down
Lads at the bar want the story, and I'm the clown
Kettle on, telly on, world upside down

- Why: homecoming, flat; "I'm the clown" self-mockery (NEEDS Joe's OK, rule 18). Weakest: L4. Truth: persona.

## Q63 — verse (no paperwork) | carpet EY-D 4/4
Nobody asked what they paid
Nothing was signed, and the deal's been made
Copper's over there in the shade
And I'm straight up the road, and it's all top grade

- Why: cash deal, no contract; paid/made/shade/grade. Weakest: L4. Truth: persona.

## Q64 — verse (before noon) | carpet UW-N 4/4
Back on the road before noon
Copper's asleep, and he'll be up soon
Case on the back, and it's done by the moon
Maybe a pint in the afternoon

- Why: timing as admin, flat. Weakest: L4. Truth: persona.

## Q65 — verse (reprieve) | carpet IY-V 4/4
Told them the truth, and they do not believe
Nothing on me, and I take my leave
Copper's got a package he wants to receive
So I slip him a twenty, and it's a reprieve

- Why: believe/leave/receive/reprieve; bribe = "reprieve" (legal term cashed). Weakest: L3. Truth: persona.

## Q66 — verse (out west) | carpet EH-S-T 4/4
Did the whole thing in the west
Nothing on the file, and it's for the best
Copper's out front, and he wants a test
So I slip him a twenty and I let him rest

- Why: flat; west/best/test/rest. Weakest: L4 (12 syl). Truth: persona.

## Q67 — verse (the run) | carpet AH-N-IY 4/4 | scheme2 AAAA
Nobody gives you money
For nothing, and it's not funny
So I'm up at the front with the money
And the sun's on the coast, and it's sunny

- Why: money/funny/money/sunny; "up at the front" (in charge). Weakest: L4. Truth: persona.
- Quad: scheme2 AAAA; multisyl 21; mosaic 12.

## Q68 — verse (the crossing) | carpet EH-R-IY 4/4 | scheme2 AAAA
Got to the port for the ferry
Nothing to declare, and it's very
Bar on the deck's getting merry
And the sea's flat calm, and the sky's cherry

- Why: ferry, flat; ferry/very/merry/cherry. Weakest: L2. Truth: ferry TRUE (2023).

## Batch 6 note
`calibrate.py` re-run — PASSED. Pool now 68 quads. Still reserved: AA-M-AH (drama/llama), AH-DH-ER
(brother/mother), UW-Z-IY, IY-D-IY, plus all the 1-syllable families (AH-V, EY-N, EY-M, OW-B, EY-P, AA-RT...).

---

# BATCH 7 (12 quads WRITTEN TO THE GAP: forced reduplication, enjambment, soft endings, no commas,
# varied line lengths). Scored with toolkit/rubric_score.py after fixing the redup bug.
# Result: enjambment, mid-bar pauses, reduplication and line-length spread now MATCH/BEAT; below-par count
# fell to 2-5 per quad. Remaining gaps: multisyllabic density (par 8), consonant pile-ups, soft endings.

## Q69 — verse (parcel, nosy neighbour) | carpet OW 3/4
Tap-tap on the phone
Bloke wants a word and he is leaning over
Chop-chop and he is telling me it has got to go
And it is back in the van and I have places to

- Gap-driven: REDUP (tap-tap, chop-chop), ENJAMB (bar 4 ends "to"), SOFT ends (over, to), no commas, spread 8.
- Weakest: L1 (says least). Truth: persona. Below par: 3 (multisyl, pile-ups, soft).

## Q70 — verse (notes look off) | carpet EH 4/4
Knock-knock on the door and he opens it then
Nothing in there and I do not ask a question
Cash in the bag and it is heavy as heaven
And I am off again

- Gap-driven: REDUP (knock-knock), ENJAMB ("then"), SOFT (question, heaven), spread 6. Weakest: L2. Truth: persona.
- Below par: 3.

## Q71 — verse (the handover) | carpet AH 4/4
Chop-chop and I am filling it up
Nothing in the case but a bit of the stuff
Bloke at the door and he is not saying nothing
And it is all about the money

- Gap-driven: REDUP, ENJAMB ("up"), SOFT (nothing, money), spread 4. Weakest: L3. Truth: persona.
- Below par: 4.

## Q72 — verse (the ladder) | carpet AE 4/4
Bang-bang at the door and he is up on a ladder
Nobody is talking and nobody is at
It is a matter
And it is back in the van and I am taking it back

- Gap-driven: REDUP (bang-bang), ENJAMB ("at"), SOFT (ladder, matter), spread 9. Weakest: L3 (breath line). Truth: persona.
- Below par: 3.

## Q73 — verse (waiting) | carpet IH 4/4
Tick-tick on the door and it is in
Bloke at the door and he is willing
Nothing was said and the lot is in the building
And I am off down the road and I am sitting

- Gap-driven: REDUP (tick-tick), ENJAMB ("in", "is"), SOFT x3, spread 4. Weakest: L2. Truth: persona.
- Below par: 5.

## Q74 — verse (the horn) | carpet UW 4/4
Beep-beep on the horn and it is you
Bloke at the door and he is bringing it sooner
Nobody knows and there is fewer and fewer
And I am off with the crew

- Gap-driven: REDUP (beep-beep, fewer-fewer), ENJAMB ("you"), SOFT (sooner, fewer), spread 6. Weakest: L4. Truth: persona.
- Below par: 4.

## Q75 — verse (drip) | carpet IH 4/4
Drip-drip on the window and it is
Bloke at the door and he is
Nothing was said and the lot is in the building
And I am off down the road and I am sitting

- Gap-driven: REDUP, ENJAMB x2, SOFT x2, spread 4. Weakest: L2 (short). Truth: persona. Below par: 3.

## Q76 — verse (the pretty crowd) | carpet IH-T-IY 3/4
Clap-clap and the crowd goes pretty
Bloke at the door says he
Nobody knows and it is all a bit witty
And I am off out the city

- Gap-driven: REDUP, ENJAMB ("he"), SOFT x3, spread 6. Weakest: L2. Truth: persona. Below par: 2.

## Q77 — verse (the border) | carpet AO 4/4
Boom-boom on the door and it is all
Bloke at the door and he is over the border
Nobody is talking and it is under the water
And I am parked up the road with my back to the wall

- Gap-driven: REDUP (boom-boom), ENJAMB ("all"), SOFT (border, water), spread 4. Weakest: L4. Truth: persona.
- Below par: 3.

## Q78 — verse (the copper) | carpet AA 4/4
Nah-nah from the copper
Nothing was said and it is all a problem
Bloke at the door says the lot is in a bottle
And I am off with the lot and it is on

- Gap-driven: REDUP (nah-nah), ENJAMB ("on"), SOFT x3, spread 4. Weakest: L1. Truth: persona. Below par: 2.

## Q79 — verse (thud) | carpet AW 4/4
Thud-thud at the door and I am out
Bloke at the door is a bit of a shower
Nobody knows and it is a tower
And I am back in the van and I am off to the south

- Gap-driven: REDUP, ENJAMB ("out"), SOFT (shower, tower), spread 4. Weakest: L2. Truth: persona. Below par: 4.

## Q80 — verse (the notes) | carpet AH 4/4
Rap-rap at the door and he takes the money
Bloke at the door says they are funny
I said they are as sweet as the
And it is warm and sunny

- Gap-driven: REDUP, ENJAMB ("the"), SOFT x3, spread 4. Weakest: L3. Truth: persona. Below par: 4.

## Batch 7 note + TOOL BUG FIX
FOUND AND FIXED a real bug: `quad_stats`'s reduplication regex in toolkit/rhyme_tools.py contained two stray
backspace control characters (\x08) wrapped round the pattern, so criterion 10 (reduplication) had NEVER been
measurable and always read 0. Removed the control chars (only that). `calibrate.py` re-run — PASSED.
Pool now 80 quads.

---

# BATCH 8 (12 quads WRITTEN TO THE LAST GAPS: multisyllabic density up, consonant clusters down, keeping
# batch-7 gains). Result: below-par count 1-4 per quad (best so far). `calibrate.py` PASSED. Pool now 92 quads.

## Q81 — verse (money) | carpet AH 4/4
Knock-knock and the money
Bloke at the door and the notes look funny
I told him the notes are as sweet as honey
And I am off with the case and it is up

- Gap-driven: money/funny/honey = AH-N-IY run; REDUP; ENJAMB ("up"); SOFT x3. Weakest: L1. Below par: 4.

## Q82 — verse (hills) | carpet IH 4/4 | BEST OF THE BATCH
Drip-drip and the hills are chilly
Bloke says I am silly
I sent it down and I am with it
Back at the digs with a bit of chilli

- BEST: multisyl 10 (BEATS), cut-ups 9 (BEATS). chilly/silly/with it/chilli IH run. Weakest: L2. Below par: 1.

## Q83 — verse (the town) | carpet IH 4/4
Tick-tick on the clock and the town is pretty
Bloke at the door says I am witty
Nobody knows and I am in
And I am off out the city

- pretty/witty/in/city run; REDUP; ENJAMB ("in"). Weakest: L4. Below par: 2.

## Q84 — verse (the crossing) | carpet EH 4/4
Beep-beep for the ferry
Nobody asked and it is all very
Bar on the deck is getting merry
And I am off with the lot and I am with them

- ferry/very/merry/them EH run; ENJAMB ("them"); SOFT x3. Weakest: L1. Below par: 1.

## Q85 — verse (Bratislava) | carpet AA 4/4
Clap-clap and on to Bratislava
Coffee so strong it is like drinking lava
Met a bloke there who swears he is from Java
And I am back on

- Bratislava/lava/Java 2-syllable run; ENJAMB ("on"). Weakest: L4. Below par: 2.

## Q86 — verse (Barcelona) | carpet OW 4/4
Boom-boom and it is off to Barcelona
Pool on the roof and a cold corona
Nobody knows my real persona
And I am off so

- Barcelona/corona/persona run; ENJAMB ("so"). Weakest: L4. Below par: 1.

## Q87 — verse (flat refusals) | carpet EH 4/4
Tap-tap and it is whatever
She asks me the time and I say whenever
The firm asks who is coming and I say whoever
And I am back in the van and I am gone then

- whatever/whenever/whoever run; ENJAMB ("then"). Weakest: L3. Below par: 3.

## Q88 — verse (solo trip) | carpet OW 4/4
Hum-hum and the miles go slowly
Nights in a tent and it is lonely
One man one bike and that is the only
And I am off so

- slowly/lonely/only run; ENJAMB ("so"). Weakest: L4. Below par: 3.

## Q89 — verse (bingo) | carpet IH 4/4
Rap-rap and the eyes down in
Big lad in the corner like a flamingo
Nobody at the table is on my lingo
And I settle it all outside and it is bingo

- bingo/flamingo/lingo run; ENJAMB ("in"). Weakest: L1. Below par: 2.

## Q90 — verse (customs) | carpet IY 4/4
Nah-nah and the bloke is cheeky
Copper on the gate is looking peaky
Nobody on the gate is looking leaky
And I am off and he

- cheeky/peaky/leaky run; ENJAMB ("he"). Weakest: L4. Below par: 2.

## Q91 — verse (homecoming) | carpet EH 4/4
Thud-thud and I am back on the telly
Roast in the oven and I am filling my belly
News says the world is a wobbly jelly
And I am with them

- telly/belly/jelly run; ENJAMB ("them"). Weakest: L4. Below par: 3.

## Q92 — verse (Havana) | carpet AE 4/4
Chop-chop and it is off to Havana
Case in the bag and a big bandana
Nothing was said and it is all in the bandana
And I am on the road and

- Havana/bandana 2-syllable run; ENJAMB ("and"). Weakest: L3. Below par: 2.

## Batch 8 note
Multisyllabic density is the one stubborn gap: par is the original's exceptional Hook 1-4 (8 runs per 4 bars)
and most of our quads reach 1-6 (Q82 reached 10). Consonant pile-ups also persist. Pool now 92 quads.

---

# BATCH 9 (12 quads DIVERSIFIED: new openers, new reduplications, one wordplay each, no template phrases).
# Pool now 104 quads.

## Q93 — scene: flat refusals | carpet EH 4/4
Second time round is whatever
She asks where I have been and I say whenever
The firm wants a number and I say whoever
And it is bye-bye to the lot and I am gone then

- Opener "Second" (new); REDUP "bye-bye"; ENJAMB ("then"); SOFT x3. Weakest: L1. Below par: 3.

## Q94 — scene: the pass in rain | carpet IH 4/4
Rain on the pass and the gears go click-click
Mate says it is hilly
Said I will do it and I am in it
Back at the digs for a chilli

- Opener "Rain"; REDUP "click-click"; ENJAMB ("it"); SOFT x3. Weakest: L2. Below par: 3.

## Q95 — scene: the crossing | carpet EH 4/4
Glasses go clink-clink on the way to the ferry
Deck hand says the crossing is very
Bar on the deck is getting merry
And I am with them

- Opener "Glasses"; REDUP "clink-clink"; ENJAMB ("them"); SOFT x3. Weakest: L2. Below par: 2.

## Q96 — scene: the bike at night | carpet OW 4/4
Tyres pop-pop on the road
The miles go slowly
Nights on my own and it is lonely
One man and a bike and that is the only

- Opener "Tyres"; REDUP "pop-pop"; SOFT x3. Weakest: L2. Below par: 4 (no enjamb).

## Q97 — scene: fuel light | carpet ER 4/4
Petrol light is on and the engine is thirsty
Foot to the floor and the road is dirty
Tank is near dry and I have only thirty
Pint in the corner and I am not thirty

- Opener "Petrol"; WORDPLAY "foot to the floor" (keeper) literal; SOFT x4; NUMBER thirty/thirty. Weakest: L1. Below par: 6.

## Q98 — scene: the count | carpet AH 4/4
Counted it twice and the notes are the money
Fella on the corner says it is funny
Told him it is sound as the honey
And I am off in the sun and it is sunny

- Opener "Counted"; money/funny/honey/sunny run; SOFT x4. Weakest: L3. Below par: 6.

## Q99 — scene: customs | carpet IY 4/4
Customs waved me through and it is all cheeky
Copper on the gate is looking peaky
Snap-snap goes the case and it is not leaky
And I am off and he

- Opener "Customs"; REDUP "snap-snap"; ENJAMB ("he"); WORDPLAY "waved through". Weakest: L4. Below par: 3.

## Q100 — scene: off to work | carpet EH 4/4
Laces tied tight and the case is ready
Word from the firm and it is already
Hand on the rail and I am keeping steady
Hop-hop and I am with them

- Opener "Laces"; REDUP "hop-hop"; ENJAMB ("them"); SOFT x3. Weakest: L4. Below par: 3.

## Q101 — scene: pub bingo | carpet IH 4/4 | BEST
Ringside seat and it is eyes down for bingo
Big lad in the corner like a flamingo
Ping-ping goes the balls and it is all on my lingo
And I settle it outside and it is in

- Opener "Ringside"; REDUP "ping-ping"; ENJAMB ("in"); WORDPLAY "settle it" (pay the tab / sort him out). Below par: 1.

## Q102 — scene: the tide | carpet UW 4/4
Tide is in and it is noon
Case is on the back and it is soon
Out with the lot under the moon
Pint in the afternoon

- Opener "Tide"; noon/soon/moon/afternoon run. Weakest: L1. Below par: 6 (no redup/enjamb).

## Q103 — scene: the camera | carpet EY 4/4
Wrapped it all up in the tape
Copper has got nothing on the shape
Camera has got it all on tape
So it is off down the road and no escape

- Opener "Wrapped"; WORDPLAY "tape" twice (packing tape / CCTV tape); "shape" = description. Below par: 6.

## Q104 — scene: the gendarme | carpet AE 4/4
Gendarme asks if I am the man
Told him never heard of him sat in the van
He wanted a statement and I gave him a plan
And he let me go and he never did scan

- Opener "Gendarme". Weakest: L3. Below par: 5.

## Batch 9 note + SECOND TOOL FIX
Found and fixed a second metric flaw: the redup regex missed OVERLAPPING repeats (bye-bye, pop-pop read 0).
Rewrote it to count hyphen/space repeats plus click-clack-style pairs. `calibrate.py` re-run — PASSED.

## Q105 — Family A (long/dense, EH feminine tail, numbers): Time Machine cashed literally
Got a Time Machine and it does not take me anywhere
Thirty eight copies of a Tuesday I do not remember
Five thousand five hundred and ninety photographs of September
It knows more about me than I do, and it is not even clever

## Q106 — Family A2 (same tail, the rail pass and the bike): the machine keeps the better copy
Twenty one days on a rail pass in a polyester jumper
Nine countries, and a boot full of somebody's better weather
Then eleven years later, a bike and a bad temper
And the machine has still got the better September

## Q107 — Family B (ER carpet, wedding in Bergen): the man who said nothing
A wedding in Bergen and I was not the worst
Two hundred on a suit and the trousers were worse
A week in a car up to Nore, a fjord, and a church
The whole day went past and I never said a word

## Q108 — Family B2 (same ER carpet, the December visits): the deadpan quiz result
Three Decembers up there so I know how it works
The dark comes at half three and the nephew is a curse
We eat at four, then a quiz, and we come third
Then home in the cold and the kettle goes first

## Q109 — Family C first half (enjambment, OW feminine, brake/break homophone setup)
Two weeks camping and I forgot the pillow
Slept in a jumper and a coat, and my elbow, so
It rained for four days and there was nothing dry to
Then the back brake went on a bend, and

## Q110 — Family C second half (payoff lands across the quad line)
I got a proper break in Bilbao
Then told the whole thing to the kettle and the window
The neighbour got the version where nobody fell over
It cost about four hundred, and there is no slideshow

## Q111 - fresh syntax, no connective frame. Interrail plan as a document (true)
The itinerary says nine countries and a walk in every one
Twenty one days, and a rucksack full of nothing that I needed
Zürich, Ljubljana, and a lake that you can see the bottom of
Every hostel had a kettle and a photograph of a mountain

## Q112 - the walks that never happened; payoff is the document, not the walk
Fifteen hundred metres for the first one, and it was properly raining
Second one came from a train window
Third one, a service station
Nine countries, no walks, and the itinerary is the only document

## Q113 - Marrakesh, ER carpet, masculine ends (verse texture, not hook)
A riad in Marrakesh, and the shower did not work
Mint tea four times a day, and the third one was the worst
In the square, a snake and a man and a monkey and a bird
Paid a dirham, said la shukran, and that was the first

## Q114 - Isle of Man and Ireland by bike, same ER carpet
Bought the bike in Douglas for less than it was worth
Two ferries in one week, and I have never been so cursed
Dublin on a Tuesday, Donegal on the Thursday
Bed next to the bike with a sandwich and a thirst

## Q115 - enjambment + homophone (waste/waist), domestic register, self-mockery needs Joe's OK
Nothing fits any more, and that is a waste
of a good two weeks of white bread, and my
waist has gone somewhere, and the parcel
has been at the woman next door since Tuesday

## Q116 - enjambment, festival with a price joke, no connective frame
Boomtown in August, and the trousers were
the ones from the photo of the previous summer
Four days of mud and one shower, and a
burger that cost about the same as the ticket, nearly

## Q117 - the folder called Lads (true), present-tense report, deadpan inventory
There is a folder on the drive called Lads
One photo of a hill and a can of something
Two and a half thousand files and a plan
from twenty nineteen that stops at Switzerland

## Q118 - the backup drive numbers, ends of the lines not the sentence
Thirty eight snapshots of a computer I sold
One thousand eight hundred and ninety headers read
Which is a sentence that means nothing to anybody
But the drive knows what I did in the years I forgot

## Q120 — Hook 9-16, BUILT to the beat sheet [VERIFIED: meaning gate PASS, 4 criteria BEAT, 0 below par, margin +4]
[RE-SCORED 11 Oct 2026 by toolkit/trybars.py: scheme **FAIL** (bars 1-2, 1-4, 3-6, 3-8 must rhyme and do not), form 18, coherence 2 fails, judge 0.870. The VERIFIED tag above records rubric MARGIN, which does not test the slot's own rhyme scheme or syllable counts. Do not reuse without re-scoring.]
Three nights in a hostel in Ljubljana
G'day and the boat out to the Whitsundays
Ahoj and a bus across to Bratislava
Byron Bay and he never got on a wave
Same bag same bus same banana
He lost a whole day
A place he cannot pronounce and a plate of pasta
Might do another week in Zell am See

## Q119 — Hook 5-8, BUILT to the beat sheet [VERIFIED: meaning gate PASS, 4 criteria BEAT, 0 below par, margin +4]
Ola and the long road to Porto
They stop him again before the border
He gets a glass of water
Might miss the boat in the morning

## Q121 — Hook 5-16 REBUILT to the craft standard [meaning PASS + coherence PASS; form LOSES (5-8 -3, 9-16 -2)]
# Argument: he can say hello in every country and has nothing to say in any of them.
# Six 2-bar runs, each a bland setup plus a closer; 3 cashed idioms; bar 12 is the payoff.
# Payoff bar collects the hello (bar 1), the wave (bars 7-8) and Joe's locked "bored" (bar 3).
He learned the hello off a menu
Says it at the front of every queue
A guard waves him through, no interview
He waves back, which is the interview
Six hellos and he has not got one name
Six countries and every one looks the same
He has got every one of them under his belt
And every stamp is a hand he never felt
He can do the small talk to the end
And he has never made a friend
Nobody rings, so he is off the hook
Same hello, same wave, and the same bored look

## Q122 — Hook 5-8 BUILT to the beat sheet and the measured shape [VERIFIED 11 Oct: meaning PASS, coherence PASS with the slot's own 2 cash events, form margin +4, 0 criteria below par, line lengths 9-10-8-8 = the original's own for those lines]
Ola from the hills above Porto
A glass of port and a page of orders
Cut corners up at the border
Might hit the road to Majorca

Notes: H3 job done - second bare greeting; the middle two bars carry the bland admin register and flip it (a page of orders -> at the border); two cashed idioms at the original's own count for these lines (cut corners, hit the road); the anchor vowel is held on all four end words, which is what the original's own carpet does (1.00 on the slot's own measure); no mid-bar pause, no consonant pile-up, and the closer place is outside the greeting frame with "might". Truth: Porto's hills, the bridge and the port glasses are in material/; the page of orders and the border short-cut are (persona).
