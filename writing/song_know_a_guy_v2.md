# V2 (15 Oct 2026, Joe: "Write a new version that passes all gates plus these new gates so I can see the difference"): the current draft
# rewritten to the Claude quality targets (match the original: first listen, rewind, clever >= the original's Haiku par; forced <= par;
# no bar at first listen 0; character 2/2). 32 bars changed. ww gate PASS (sense ON); targets 6/10 sections + character 2/2 (current
# draft 2/10, 1/2). Misses and why: writing/song_know_a_guy_v1_vs_v2.md. 'My crew' and 'Lone wolf / Solo' are gone. Assistant-authored.
# I KNOW A GUY: a new song written from scratch (15 Oct 2026) as a naive writer: premise (brief/premises.json know_a_guy),
# section argument, one rap move per bar, ingredients (material/ingredients.md), sentences, then fitted with toolkit/fitbar.py
# and held to `python -m ww.cli gate` until it exited 0. Nothing carried over from any earlier draft. Assistant-authored.
# RESULT: ww gate PASS (0 hard; sense read ON via Claude since 15 Oct, per slot against the original's count). fitbar 73/76 (bars 11, 37, 39: see the notes file). Notes and
# pipeline findings: writing/song_know_a_guy_notes.md.
# REWRITE 15 Oct 2026 (end rhymes, after Joe: "originals end rhymes are better rn" and the Lagos/favours/flavours/Vegas carpet):
# Hook 5-8 now rhymes all four bars on one ending (honest / solid / wallet / profit; Joe: "the original is AAAA"); cheap and identical rimes cut in 6 sections under the
# new rapfit rules (carpet, cheap, identical). The old blocks are kept as test cases in toolkit/tests/rhyme_complaints.txt.
# SENSE REWRITE 15 Oct 2026 (the sense gate came back on, on Claude): 12 bars in Hook 1-4, Hook 9-16, V1 25-32, V1 33-44 and V2 1-8 made
# plain sentences or tied to the guy (old bars in git history). Quality marks (report-only): python -m ww.write.qualityread.
# (persona) for Joe: every crime, bribe and luxury claim; the Prada suit; the boat in Palma; the
# Laxey bar tab; the crate, customs, Gardai and the trolley; the Barbour parka; the judge's lager; the top-thief list; the gold; the Spanish stop; the Whitsundays tinnie and the reef dive; the
# ute on K'gari. Named but not visited: Old Bailey, Canada, Saul. The East Coast is Australia's (2017, true). True places: material/travel_history.md.

== Hook 1-4
# argument: wherever I land, I know a guy. moves: shout_out, brag, flex_list, punchline
# one ending family on all four bars (venue / continue / cruise / news), as the original's Hook 1-4 shares one final vowel
Cheers to the venue
You left me for dead? I continue
Cops, bail, judge, jail, it's like a Greek cruise
In Bern, Zell, Crete, Nantes, I'm the bad news
#cash 4 | bad news | news

== Hook 5-8
# argument: my man in Rotterdam can get you a gnome by morning. moves: shout_out, brag, threat, punchline
Hoi hoi to the Dutch, they're honest
Their gnome's as tall as a house, rock solid
Cross my man and it's your wallet
Want one? Then I turn a profit
#cash 2 | rock solid | solid

== Hook 9-16
# argument: my people: the bloke with the torch, the brief, the doorman, the bike shop. moves: brag, name_drop, brag, threat, flex_list, punchline, brag, punchline
G'day there's a torch on call
My brief's a better call than Saul
Four-wheeler? Dead on arrival
My doorman will put you through the floor
Cash for Spain and it's cash for trains and cash for planes
Prost, and I don't buy
Hanoi bikes are getaway cars
If you're stuck I know a guy
#cash 2 | better call Saul | Saul
#cash 3 | dead on arrival | arrival
#cash 7 | getaway car | cars
#cash 8 | I know a guy | guy

== V1 1-8
# argument: the network is the business: worldwide, deniable, comfortable. moves: brag, brag, brag, name_drop, brag, brag, threat, punchline
One phone and a name, my reach is larger
Honesty box? I pay with good karma
In my suit head to toe Prada
My guy keeps a boat out in Palma
Stab vest? Nah, a parka
Clean hands and the judge gets lager
Try me and see what you get
Grazie grazie four weeks on the trains and no drama
#cash 2 | good karma | karma
#cash 8 | no drama | drama

== V1 9-16
# argument: I came from nothing and nobody; now I'm untouchable and too busy, so ring my guy. moves: brag, brag, deflate, brag, brag, brag, brag, punchline
Back then no one would know me
Broke, kipped on the floor, we
Now skip to the end
But the cops came round I walked out of it scot free
Nowadays my face goes round with all the athletes
Top floor, a sea view, I'm living the dream
Police have got a list and they've got me: top thief
I'm out so ring my main guy's guy he's discreet
#cash 4 | scot free | free
#cash 6 | living the dream | dream

== V1 17-24
# argument: my guy moves anything, anywhere, no questions (courier register). moves: brag, brag, brag, punchline, threat, threat, punchline, brag
# bars 5 and 7 end stressed-weak-weak, not the template's weak-only ending: only "him" makes that shape with a three-syllable
# rhyme, the original repeats it on both bars, and the draft rules forbid a repeated end word (listed to Joe).
Dublin, and my bar tab's in credit
No one sees my elephant
Customs won't open the crate it's medical
Gardaí come for the evidence? Chemical
Wrapped in a blanket, mate, just a passenger
And the guards at the gate? On salary
Where's the guy? Lying low in Canada
Pass it van to van, a real Marathon
#cash 1 | on credit | credit
#cash 5 | just a passenger | passenger

== V1 25-32
# argument: I've got a guy for every little luxury, in every country. moves: brag, brag, threat, shout_out, brag, brag, brag, punchline
Mozzarella and capers? It's my guy in Naples
Marrakesh when I'm able, my guy there, he sews a label
Barber's chair: cut-throat shave's on the house, cards on the table
Beer's dear in Bergen? Near fatal
And I own the whole fleet, Thai mainland
But the fags? That cheap it's dead cheeky
Forty a day? My guy is sorting me
Need me? Gone to my guy's guy down the road for a quick freebie
#cash 3 | cards on the table | table
#cash 6 | dead cheeky | cheeky

== V1 33-44
# argument: police, court, debt: nothing sticks, because my guy sorts it. moves: brag, deflate, brag, brag, threat, brag, brag, brag, threat, threat, brag, punchline
Sure the Spanish caught me
Officer? Who me? Seedy? Seedy?
Then my guy had the money
Cash in envelopes no one gets funny
My guy made you pay
Wanted posters, all Boomtown, front page
Never set foot in the dock Old Bailey
Back in the beer garden I'm saving face
Owe me? Then you've ten days' grace
You owe? Your head's a conker and that's fair game
Crown on top hat I'm king of Bristol
Dealers know that I know a guy, no names
#cash 5 | made you pay | pay
#cash 8 | saving face | face
#cash 9 | days' grace | grace
#cash 10 | fair game | game

== V2 1-8
# argument: the luxury life, all of it through a guy (monorhyme on the title's own vowel). moves: brag, brag, name_drop, brag, brag, threat, brag, punchline
The Whitsundays a tinnie? I've got a guy
Up K'gari in the ute where you do or die
Bangkok? My guy's van does the top fried rice
The reef? I dived, the sharks were in the crossfire
You wouldn't believe big boats and jets at night
You want it for free from my guy? So pigs can fly
I drive to his bay, dive in, I'm back by five
Name it, my mate: one call and it's mine
#cash 2 | do or die | die
#cash 6 | pigs can fly | fly

== V2 9-16
# argument: I don't need a guy any more: I am the guy (the knockout turns the hook's own line round). moves: brag, flex_list, brag, brag, brag, threat, threat, punchline
Well I've got my own boat
Christchurch Oslo Scotland Wales I'm in the photo
Famous now my face is on the East Coast
Pool hall? Hustled well and then I struck gold
Skip queues, walk in to the limelight
Don't need one 'cause I'm big now I take bribes
Seconds out no ref you get no bell
Each time you're stuck, I'm the guy and your last lifeline
#cash 4 | struck gold | gold
#cash 5 | in the limelight | limelight
