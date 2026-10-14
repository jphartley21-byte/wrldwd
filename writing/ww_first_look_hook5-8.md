# ww first look: Hook 5-8 candidates (13 Oct 2026)

FIRST LOOK ONLY. Written by the new pipeline (seed stage -> block writer -> deterministic checks -> reader -> comparative ranker). The judge is validated on dev for *sense* (87-100% pairwise against damaged text); it is NOT validated for *funny*. Nothing here is endorsed by me as good; the ranking says only which of these six is the cleanest.

Funnel: 8 real facts -> 64 seeds -> 16 kept -> 90 candidate blocks -> 12 pass the deterministic checks -> 6 pass the reader floor -> ranked. Cost about $0.30.


## #1  (fact: interrail_pass; mechanism: one_word_two_senses; rank score 6.589)

    Bonjour from Paris Nord, not Bristol.    [9 syl, ends |Sw]
    This seat is reserved, in the middle.    [9 syl, ends |Sw]
    Four weeks, twelve stops, just a single.    [8 syl, ends |Sw]
    Guard at Cologne might blow a whistle.    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 4 of 4.


## #2  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score 3.053)

    Hei, Bergen, frost on the mirrors    [8 syl, ends |Sw]
    The screen says now serving, check the filters    [10 syl, ends |Sw]
    The order's just a pair of slippers    [9 syl, ends |Sw]
    Might keep the ticket for the builders    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 4 of 4.


## #3  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score -1.737)

    Hei, Bergen, Christmas with the sisters    [9 syl, ends |Sw]
    Please bring photo ID, cross the fingers    [9 syl, ends |Sw]
    The order is a pair of slippers    [9 syl, ends |Sw]
    Might post the ticket to the winners    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 4 of 4.


## #4  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score -2.38)

    Hei, Bergen, frost on the rivers    [8 syl, ends |Sw]
    Ready for collection, check the figures    [10 syl, ends |Sw]
    The collection point is slippers    [8 syl, ends |Sw]
    Might keep the ticket with the pictures    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 1 of 4.


## #5  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score -2.653)

    Hei, Bergen, Christmas in the prisons    [9 syl, ends |Sw]
    Your order is ready, count the chickens    [10 syl, ends |Sw]
    The order is a pair of slippers    [9 syl, ends |Sw]
    Might keep the ticket for the misses    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 4 of 4.


## #6  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score -2.872)

    Hei, Bergen, Christmas for the millions    [9 syl, ends |Sw]
    Your order is ready, check the billions    [10 syl, ends |Sw]
    The pickup point is just slippers    [8 syl, ends |Sw]
    Might keep the ticket for the missions    [9 syl, ends |Sw]

End-rhyme carpet 6/6 (min 1.0); persona-less bars: 4 of 4.


## My honest read

- **#1 is the only one I would keep working on.** It is coherent British English, specific (Paris Nord, Cologne, a reserved seat), and its four end words (Bristol / middle / single / whistle) form a genuine perfect carpet. It is not yet *funny*: it is travel talk with no menace, no persona and no payoff (the reader found no persona in any bar).
- **#2-#6 are the old failure again**: the words were bent to fit the rhyme ("Christmas in the prisons", "count the chickens", "check the billions"). The reader passed them, because it is too charitable in absolute terms; only the ranker separated them (6.6 vs 3.0 vs -1.7 and lower).
- **The best seeds never reached this list.** The strongest ideas (take the guillotine out with the bins on Sunday; a live badger in the honesty box; "wanted for excessive energy") were killed by the hard sound filters: 65 candidate blocks failed on syllable count alone, 30 on a stress-second ending, and a dozen on words the pronouncer could not read (Noord, layby, dirham). The filter funnel is selecting for bland content that happens to fit, which is the same trap as before.

## What I am changing next
1. Syllable tolerance +-2 on bars 1, 3, 4 (the audio frame is a guide, rule R9) and treat primary+secondary compounds (footpath, wristband) as acceptable weak endings.
2. Heal pronunciations for place names and compounds before rejecting.
3. Require persona in at least two bars, so a clean-but-characterless block cannot win.
4. Re-run with the best seeds forced into the candidate pool.


---

# Run 2 (same day): loosened filters, persona required, low-effort writer

Funnel: 16 seeds -> 54 candidate blocks -> 31 pass the deterministic checks (run 1: 12 of 90) -> 14 pass the reader floor -> 22 have a persona in at least 2 bars -> 12 ranked. Cost about $0.18.

Shortlist after a diversity cap (one block per payoff word, two per fact; without it five of the top eight were variants of the Interrail 'single' joke):


## R2 #1  (fact: interrail_pass; mechanism: one_word_two_senses; rank score 3.433)

    Zurich April, the pass came from Bristol.    [10 syl, ends |Sw]
    Seat reserved, second class, in the middle.    [10 syl, ends |Sw]
    Man asks return; I ask for a single.    [10 syl, ends |Sw]
    Munich might get a better signal.    [9 syl, ends |Sw]


## R2 #2  (fact: moto_ferry; mechanism: euphemism_as_logistics; rank score 2.81)

    Portsmouth check-in opens without warning    [10 syl, ends |Sw]
    The bike and tent are checked in, no calling    [10 syl, ends |Sw]
    Offence goes as hand luggage for boarding    [10 syl, ends |Sw]
    The car deck might take some scoring    [8 syl, ends |Sw]


## R2 #3  (fact: bf_honesty; mechanism: one_word_two_senses; rank score 2.734)

    Baden-Baden's key safe is standard.    [9 syl, ends |Sw]
    The host has left the lockbox; code captured.    [10 syl, ends |Sw]
    The manual says badger is password.    [10 syl, ends |SS]
    The drinks are left out, so coins are gathered.    [10 syl, ends |Sw]


## R2 #4  (fact: bergen_shoes; mechanism: euphemism_as_logistics; rank score -2.227)

    In Bergen, the boot room's got the nippers.    [10 syl, ends |Sw]
    Now serving order four three two, skippers.    [10 syl, ends |Sw]
    The catalogue says collect the slippers.    [10 syl, ends |Sw]
    Might check the screen for the flippers.    [8 syl, ends |Sw]


## Read of run 2
- Mechanics improved (57% of candidates now pass the sound checks, up from 13%), and every top block has a persona. #1 (Interrail 'single') is the cleanest: coherent, specific, one mild joke ("Man asks return; I ask for a single").
- Still not funny. The best idea in the pool is one line, "Offence goes as hand luggage for boarding" (#2): an extraordinary thing reported as an airport errand, which is the right mechanism, but the lines around it ("no calling", "might take some scoring") are filler.
- The ranker cannot tell clean-and-mild from funny; it keeps promoting the safest block.
- 21 candidates (the cola-can and Marrakesh seeds) died because the pronouncer could not read "Noord" and "dirham"; both are now fixed, along with a diversity cap, but not yet rerun (balance).
