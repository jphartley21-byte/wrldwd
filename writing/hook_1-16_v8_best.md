# Hook 1-16 v8: the best the system can currently produce (12 Oct 2026)

Chosen by measurement, not by taste: for each block, the best result the search produced.

```
Yo, bonjourno
Said damn at the on-stage porno
Front row on my phone, so bored, though
So I boarded a plane out to Bordeaux
Hallo and the boat in Oslo
A page of the orders and the corners
None of the names on the quarters
Might take the train to Ljubljana
First drop done back to the car
Not the worst run I have had by far
Slate for the path and never late
Half the load and a laugh in the bar
Same box same box same box and it's all the same price
Paid him by the weight
Loaded up the van, chips go cold
Might do the same again mate
```

| block | scheme | form | meaning | coh | syllables = frame | payload | places |
|---|---|---|---|---|---|---|---|
| Hook 1-4 | PASS | 6 | 0 | 0 | [4, 8, 8, 10] vs [5, 9, 9, 9] | 4.07 | 1 |
| Hook 5-8 | PASS | 8 | 0 | 0 | [8, 10, 8, 8] vs [8, 10, 8, 8] | 3.60 | 2 |
| Hook 9-16 | PASS | 11 | 0 | 0 | [7, 9, 8, 9, 12, 5, 8, 7] vs [7, None, 8, 9, 12, 5, 8, 7] | 5.13 | 0 |

Whole hook: **25 form problems** (Joe's own bars 1-4 account for 6 of them).

## Where the limitations are (12 Oct 2026)

1. BARS 9-16 DEFEATED THE SEARCH. 6,480 combinations swept against that slot's frame, zero passed
   the scheme. The reason is now clear and it is not a supply problem: the slot's by-ear scheme
   (AABACBDB) rhymes on the STRESSED SYLLABLE INSIDE the end word -- its own bars link a place name,
   a short place and a country by their stressed syllable, not their final vowel. Every generated
   pool rhymes on the final vowel, so bars 11/14/16 never linked. The generator cannot see
   stressed-tail rhymes yet. That is the single biggest missing capability.

2. THE FRAME IS A GUIDE, NOT A LAW. Joe's approved bars 1-4 measure [4, 8, 8, 10] syllables against
   the frame's [5, 9, 9, 9] -- off on every bar, including one a whole syllable short -- and they are
   the benchmark every other block is judged against. The sweeps optimise frame-exactness; that may
   be optimising something the ear does not hear.

3. THE POOLS ARE STILL HAND-WRITTEN. The supply is queryable (bank.py: 260 loanwords, phrases by
   payoff sound, places by end sound) but every candidate phrasing in those sweeps was mine. The
   search space is therefore bounded by my templates, and the thing that makes a bar good -- the
   phrasing -- is the part with no generator and no measure behind it.

4. THE INSTRUMENTS DISAGREE, AND NONE OF THEM IS JOE'S EAR. Form says this hook is 25 problems;
   payload says block 5-8 (3.60) is better than the original's own hook (4.04); the judge ranks
   differently again and is known to be inverted on 3 of 5 of Joe's own documented rules. Every
   rejection so far has come from Joe, not from a number.

5. SUPPLY IS HALF-BUILT. 260 loanwords harvested, 77 pronounceable. 183 need an OVR entry before
   they can sit in a rhyme slot, and Jamaica and Morocco returned nothing (multi-word entries and
   Arabic script). The code-switching engine therefore runs on roughly a third of the vocabulary it
   should have.

