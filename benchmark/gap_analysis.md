# Why the original is still ahead, measured (12 Oct 2026)

Both 16-bar hooks run through the same instruments. Four metrics separate them, two do not.

| metric | original hook | ours (hook_1-16_v5) |
|---|---|---|
| bars naming a proper noun | 9 of 16 | 4 of 16 |
| mean zipf of the end word (lower = rarer) | 4.04 | 4.58 |
| rarest end word (zipf) | 1.75 | 2.68 |
| words with zipf < 3.5 ("loaded") | 16 (15%) | 4 (3%) |
| figures of speech (devices.py, whole hook) | 0 per-bar; hedge 1 | 6 (litotes 2, hedge 2, hyperbole 1, bathos 1) |
| lexical variety (distinct content / content) | 0.84 | 0.87 |
| distinct words with a second reading (funny.py) | 26 | 32 |

The bottom two rows are the ones where ours "wins", and they are precisely the two that cannot see
the difference. Lexical variety and second-reading availability measure SUPPLY, not quality, exactly
like the judge (2/5 agreement with Joe's own rules, 3 inverted) and the pun proxy (89% base rate).
Do not manage to those numbers.

## The five gaps, in order of how much they explain

1. NO WORLD IN IT. 9 of 16 bars vs 4 of 16 name a place, and the original jumps country every
   couplet while ours stays inside one domestic day (Bordeaux/Porto/Majorca plus a delivery round).
2. NO CODE-SWITCHING -- AND NO SUPPLY FOR IT. The original's engine is a word in each place's own
   language or slang. Probing toolkit/phrases.txt, phrases_raw.txt and entities.txt for the words
   that engine runs on returns only ENGLISH slang (cheers, birds, quid, whip, chips); every
   non-English item is absent from the harvest. This is a build gap, not a taste gap.
3. STAKES TOO LOW. The original's register includes police awareness, a network holding things down,
   and goods that are either champagne or a weapon. Ours has beer on the house, a pint, drops, chips
   going cold and the same price. STATE.md's own rule ("menace must exceed the group's normal life")
   is currently violated by 12 of our 16 bars.
4. THE RHYME SLOT CARRIES NO PAYLOAD. Our end words are the most predictable words in their lines
   (car, far, late, bar, price, weight, cold, mate); the original's payoff words are places, brands
   and loanwords. That is the measured difference between 4.58 and 4.04 mean zipf.
5. ONE REGISTER FOR SIXTEEN BARS. Ours is monotone: flat understatement plus a cashed idiom, six
   figures of speech doing work the original does with vocabulary and code-switching. The original
   changes register every couplet without ever raising its voice. Adding more figures is not the fix;
   it widens the same gap.

## Plan

A. HARVEST THE MISSING SUPPLY (highest leverage). Extend toolkit/harvest.py with a `loanwords` mode:
   per country Joe has actually visited, pull greetings, thanks and a handful of everyday nouns from
   Wiktionary, plus regional English slang (Jamaican, Cockney, Irish, Australian). Every word needs
   an end sound so bank.py can serve it into the rhyme slot.
B. REBUILD THE HOOK as a roll-call (the pivot below): one place per couplet, keeping the courier
   frame, with each couplet carrying a local word, a claim, and a stake above normal life.
C. ADD THE TWO MISSING READOUTS to trybars: mean end-word zipf and bars naming a place. Report
   lines, not vetoes. They measure gaps 1 and 4 directly and cannot reject a line Joe likes.
D. DEVICE BUDGET: no two consecutive bars share a mechanism.

## The pivot (Joe's stuck rule, T2)

T2 fires: the same theme and register has now been through 12 versions of bars 5-8 and 6 of 9-16.
Parked as best: writing/hook_1-16_v5.md. Three fresh angles, each changing at least two of
theme / rhyme family / structure:

1. BY LANGUAGE (chosen). Each couplet is a place greeted in its own tongue or slang; the carpet is
   the open vowel the loanwords end on (-o / -a / -e). True places: Porto, Bilbao, Naples,
   Bratislava, Ljubljana, Marrakesh, Bergen, Byron Bay.
2. THE LEDGER. A haulage manifest, one country per couplet, each with customs, weight and favour
   stakes; carpet -e? (weight, plate, straight, freight, mate, late) -- a bank we already have.
3. THE ROUTE. A literal journey in order (Interrail 2019, the motorbike run), one leg per bar,
   carpet ?? / ??, a local word at each stop.

Judged by gaps: 1 closes gaps 1 and 2 together and is the only angle that does. 2 closes gap 3 well
and reuses the register we already have. The build is therefore 1's engine inside 2's frame.
