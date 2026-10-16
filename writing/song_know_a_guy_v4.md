# V4 (16 Oct 2026, Joe on the original's bars 46-52 against ours: "Can you see the difference in quality? How did our version get past
# the gates?"): the end-rhyme tools now hear a closing pronoun as part of the rhyme ('caught me' = stressed 'or' + weak 'ee'), each bar
# must rhyme as deep as the original's same bar, and where the original carries one ending across a section break ours must too.
# 6 bars changed from v3; bars 46-50 now hold one ending (stressed 'ee' + weak 'ee': cheeky / greedy / freebies / speedy / Seedy)
# across the V1 25-32 / V1 33-44 break, then money / chummy, as the original holds one for five bars then moves once.
# ww gate PASS (sense ON). Quality targets (report-only) 3/10; character read 1/2 (past-tense runs at bars 25-28, 49-51).
# Later the same day (Joe: the original's bar 46 opener "is smoother than 'Fags? Cheap packs'"): bar 46 -> "But the baccy price is
# dead cheeky" and bar 31 -> "they got me" (both had two stresses on one 16th of the audio template; now a HARD flow measure).
# RUN-BREAK REFIT, same day (Joe: "Yes hard gate those too and refit"): a stop (? : , !) where the original's next syllable comes on the
# very next 16th is now HARD (toolkit/flow_par.py run_breaks, the original's same bar as par). 25 bars changed: mostly stops removed or moved
# to a real gap; bars 36, 47, 61 and 66 reworded; bars 21, 44 and 47 keep the internal rhymes the section needs. ww gate PASS (sense ON).
# ONE SENTENCE OVER THE BAR LINE, same day (Joe: the original's bars 13-14 work "because it's a sentence over 2 lines"; ours were "two
# sentences which messes up the flow"; "Same here" on bars 67-68): where the original's bar runs on into the next (6 bar lines: 13, 15, 25,
# 26, 31, 67), ours must too (toolkit/flow_par.carry, HARD). Bars 25-26 already did; bars 14, 16, 32 and 68 now finish the bar before:
# "For a servo pie", "'Cause by night I know a guy", "To be sprung by my main guy's guy who's discreet", "'Cause a call to my guy makes
# it mine". ww gate PASS (sense ON).
# JOE'S SEVEN, same day ("The other five flagged ones I agree should be flagged and fixed"; "The torch bar and servo pie bar have nothing to do
# with Australia"; "US specific slang should be flagged, but not UK"): bars 8, 9, 14, 17, 22, 34, 56 rewritten (toolkit/localfit.py, ww/write/
# slangcheck.py). ww gate: every section PASS; the hook is 1 short on two quotas (3 of 4 local words that fit, 6 of 7 stamps), open for Joe.
# BREAK AND TWIN, same day (Joe on V1 25-32: "have the lines and rhyme schemes got mixed up somehow?"): the original's bar 44 is a
# break that rhymes with nothing and its bars 45-46 are one line said twice with the end word changed, the rhyme flipping on that word;
# ours rhymed bar 44 with 41-43 (five bars of one rhyme) and made 45-46 two unrelated lines. Both are HARD now (rapfit.check_block).
# Bars 44-47 rewritten: a break bar ('hard bargain'), the twin 'Now the man I use buys Spain's mainland / ... is dead cheeky', and
# 'Fifty quid' (was 'Forty', the original's own word there). ww gate: every section PASS; the two hook quotas above are still open.
# ONE ENDING AND MULTI-WORD RHYMES, same day (Joe: 'mainland' does not rhyme with Naples / label; our rhymes rarely span words
# where the original's do: 'for me'). V1 25-32 rebuilt so both rhyme families close on 'ee' like the original's (pricey / nicely / icy /
# Riley / Kylie, then cheeky / cheats me / freebies). New song-level gate: >= 0.8 x the original's 7 real two-word rhymes; five here
# (cheats me, fund me, charge ya, flogged it, flatter ya). Every section PASS (sense ON); the song is one two-word rhyme short.
# UK RAP LEXICON, same day (Joe: 'build it'): toolkit/ukrap.py found the sixth two-word rhyme: bar 21 'Stab vests? Nah I charm 'em'
# (was 'Stab vest? Nah a parka'). ww gate: every section PASS (sense ON); the song-level two-word minimum passes (6); FAIL only on the two
# open hook quotas.
# V3 (16 Oct 2026, Joe: "Go for all 3, add the gates, verify them, then write the new draft to pass all gates and print it"): v2 rewritten to
# the new rhyme-texture gate (toolkit/texture.py: internal rhyme amount + strength, frame / link sandwiches, multisyllabic runs across
# words, each per section against the original's same section). v2 failed it in 8 of 10 sections; v3 passes all 10. ww gate PASS
# (sense ON). Quality targets (report-only) fell to 3/10 from v2's 7/10; character 2/2. Assistant-authored.
# V2 (15 Oct 2026, Joe: "Write a new version that passes all gates plus these new gates so I can see the difference"): the current draft
# rewritten to the Claude quality targets (match the original: first listen, rewind, clever >= the original's Haiku par; forced <= par;
# no bar at first listen 0; character 2/2). 32 bars changed. ww gate PASS (sense ON); targets 6/10 sections + character 2/2 (current
# draft 2/10, 1/2). Misses and why: writing/song_know_a_guy_v1_vs_v2.md. 'My crew' and 'Lone wolf / Solo' are gone. Assistant-authored.
# PAUSE REFIT 16 Oct 2026 (Joe on bar 76: "Flows very differently" from the original's): toolkit/flow_par.py now makes a bar pause
# after the same syllable as the original's bar (22 of 76 bars) and hears spelled-out acronyms as a repeated cell. 18 bars failed it;
# 20 bars changed (2 more for the cashed idiom and the sense read). ww gate PASS (sense ON); targets 7/10 + character 2/2.
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
# Laxey bar tab; the crate, customs, the chemist, the ferry crews and the trolley; the Barbour parka; the judge's lager; the top-thief list; the gold; the Spanish stop; the Whitsundays yacht and the reef dive; the
# ute on K'gari. Named but not visited: Old Bailey, Canada, Saul. The East Coast is Australia's (2017, true). True places: material/travel_history.md.

== Hook 1-4
# argument: wherever I land, I know a guy. moves: shout_out, brag, flex_list, punchline
# one ending family on all four bars (venue / continue / cruise / news), as the original's Hook 1-4 shares one final vowel
Cheers! Any issue?
Got framed? Left for dead? I continue
Cops, bail, dock? Jail is just a Greek cruise
In Bern, Zell, Melbourne, Perth I'm bad news
#cash 4 | bad news | news

== Hook 5-8
# argument: my man in Rotterdam can get you a gnome by morning. moves: shout_out, brag, threat, punchline
Hoi hoi to the Dutch, they're honest
Their gnome's as tall as a house, rock solid
Cross my man and it's your wallet
Got one off my hands: I flogged it
#cash 2 | rock solid | solid

== Hook 9-16
# argument: my people: the bloke with the torch, the brief, the doorman, the bike shop. moves: brag, name_drop, brag, threat, flex_list, punchline, brag, punchline
The law up in Bergen? Skal
My brief's a better call than Saul
Four-wheeler's dead on arrival
My doorman will put you through the floor
Cash for Spain and it's cash for trains and cash for planes
Like a private eye
Hanoi bikes are getaway cars
'Cause by night I know a guy
#cash 2 | better call Saul | Saul
#cash 3 | dead on arrival | arrival
#cash 7 | getaway car | cars
#cash 8 | I know a guy | guy

== V1 1-8
# argument: the network is the business: worldwide, deniable, comfortable. moves: brag, brag, brag, name_drop, brag, brag, threat, punchline
One black book and the numbers? I'll charge ya
Honesty box? Me? Paid in full: karma
In my suit? Man! It's good Prada
My guy's cruiser? Moored out in Palma
Stab vests? Nah I charm 'em
Cash? Yes! I bung the judge lager
Cross me? Just you wait and see
Grazie grazie train drivers! A month and no drama
#cash 7 | wait and see | see
#cash 8 | no drama | drama

== V1 9-16
# argument: I came from nothing and nobody; now I'm untouchable and too busy, so ring my guy. moves: brag, brag, deflate, brag, brag, brag, brag, punchline
Back then my bird was poor, she
Broke, kipped on the floor we
Skip on to the end
But the cops came round I walked out of it scot free
Nowadays my face goes round with all the athletes
Top floor's a mad scene I'm living the dream
Police have got a list and they got me: top thief
To be sprung by my main guy's guy who's discreet
#cash 4 | scot free | free
#cash 6 | living the dream | dream

== V1 17-24
# argument: my guy moves anything, anywhere, no questions (courier register). moves: brag, brag, brag, punchline, threat, threat, punchline, brag
# bars 5 and 7 end stressed-weak-weak, not the template's weak-only ending: only "him" makes that shape with a three-syllable
# rhyme, the original repeats it on both bars, and the draft rules forbid a repeated end word (listed to Joe).
Dublin's mine: my bar tab's in credit
My man pays for negligence
Customs won't open the crate it's medical
Chemist wiped it of all of the evidence
Who is that, lying down? Just a passenger
And the guards at the border? Flatter ya
Where's the guy? Lying low in Canada
Rode in van to van, a real Marathon
#cash 1 | on credit | credit
#cash 5 | just a passenger | passenger

== V1 25-32
# argument: I've got a guy for every little luxury, in every country. moves: brag, brag, threat, shout_out, brag, brag, brag, punchline
Mozzarella that's pricey? My guy does it nicely
In Marrakesh it's dicey? My guy's Rolexes are icy
Barber's cut-throat shave? Free: on the house, the life of Riley
These days I drive a hard bargain
Now the man I use has met Kylie
Now the man I use is dead cheeky
Fifty quid? Now don't say my guy cheats me
Where am I? Gone to my guy's guy, he's local, for more freebies
#cash 3 | the life of Riley | Riley
#cash 4 | drive a hard bargain | bargain
#cash 6 | dead cheeky | cheeky

== V1 33-44
# argument: police, court, debt: nothing sticks, because my guy sorts it. moves: brag, deflate, brag, brag, threat, brag, brag, brag, threat, threat, brag, punchline
Sure the cops were speedy
Officer who? Me? Seedy? Seedy?
Then my guy came to fund me
Cash in envelopes keeps the cops chummy
My guy said you pay
Wanted poster's ten grand! Full front page
I never once came to the Old Bailey
So the brass at the Met were saving face
Owe me and you've ten days' grace
When you owe me I know: your head is fair game
Top of town: I'm the boss of Bristol
Who do I know? A guy. So I won't name names
#cash 8 | saving face | face
#cash 9 | days' grace | grace
#cash 10 | fair game | game
#cash 12 | name names | names

== V2 1-8
# argument: the luxury life, all of it through a guy (monorhyme on the title's own vowel). moves: brag, brag, name_drop, brag, brag, threat, brag, punchline
On Whitsundays a yacht? Yeah I've got a guy
Up K'gari in the ute where you do or die
My guy's Bangkok van does the top fried rice
The reef? I dived, the sharks were in the crossfire
You wouldn't believe big boats and jets at night
You get it for free from my guy if pigs can fly
I drive to his bay, dive, and I'm back by five
'Cause a call to my guy makes it mine
#cash 2 | do or die | die
#cash 6 | pigs can fly | fly

== V2 9-16
# argument: I don't need a guy any more: I am the guy (the knockout turns the hook's own line round). moves: brag, flex_list, brag, brag, brag, threat, threat, punchline
A guy? Well, my own boat
Christchurch Oslo Scotland Wales I'm in the photo
Famous? Me? My face is on the East Coast
At pool I hustled well and then struck gold
Bold: I skip queues to the limelight
Don't need one 'cause I'm big now I take bribes
Seconds out no ref you get no bell
Stuck? Need me? Call on me call on me last lifeline
#cash 4 | struck gold | gold
#cash 5 | in the limelight | limelight
