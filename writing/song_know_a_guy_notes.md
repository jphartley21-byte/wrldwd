# I Know a Guy: gate result, open notes and what the naive-writer run showed about the pipeline (15 Oct 2026)

## Result
- `python -m ww.cli gate writing/song_know_a_guy.md`: PASS, 0 hard issues, all 10 sections. Sense read OFF (no DEEPSEEK_API_KEY).
- fitbar per-bar fit: 74/76. Bars 37 and 39 fail on end shape only (see finding 2).
- recount 8% (original 20%); swagger hook 7/16, verses 22/60; meaning gate, phrase audit, songcheck, character cap: pass.

## Notes listed to Joe (rule 10: fixed or listed, never skipped)
- 114 FLOW/EAR notes (jammed stresses 27, reduced syllable on a downbeat 41, weak syllables on the beat 14, stress clash 29,
  "stress inverted" 25, pauses/commas 8, mouth-shape 3). NOT fixed: run on the original's own 76 bars the same notes fire as
  often or more (jammed 23, downbeat 39, beat 16, clash 24, inverted 30, mouth-shape 18). They do not separate the benchmark
  from a draft, so fixing them is not evidence of better flow. Your ear decides.
- 3 end-rhyme carpet notes (the original holds one sound family across the block; ours does not): Hook 5-8 2/6 (original 6/6),
  V1 17-24 10/28 (24/28), V1 25-32 9/28 (21/28). Real, not fixed: each needs the section re-rhymed on one vowel family.

## What the naive-writer run found in the pipeline (none of these were changed during the run)
1. fitbar and the gate disagree on end shape. slotcheck accepts a mid-word rhyme (~Sw) for |Sw and, in verses, checks only
   hard vs soft; fitbar demands the exact shape, and write.md says a mid-word rhyme cannot fill a |Sw slot (Majorca).
2. V1 17-24 bars 37/39: the template's weak-only ending (|w) with a three-syllable rhyme is only reachable with "him", the
   original ends both bars on it, and the draft rules forbid a repeated end word. A draft cannot satisfy fitbar and the gate here.
3. Bar 37's template has 4 weak syllables in a row; the weak-run rule fails any bar with 4. The template breaks its own rule.
4. characters.py counts "copper" but not "cops", "police", "Garda", "guards" or "customs": the police could be referenced 5
   times under a cap of 2. I held them to 2 by hand.
5. songcheck fails a rhyme pair on the OLD grader (match.best_end < 0.78) while fitbar prints that grader as a note only.
6. The local-word supply contains English words ("sea", "police", "yes", "part", "route", "mat"): 2 of the verses' 5
   counted local words are these. The gate can be passed without any real code-switching.
7. The cashed-idiom check can be gamed: the payoff only has to be the bar's last word, not part of the idiom
   ("#cash | top dog | nightlife" verified). I removed that declaration; the remaining declarations are real.
8. Punctuation changes spaCy's mid-bar restart count: deleting two commas from bar 76 turned a pass into a hard fail.
9. The stress model reads some words unexpectedly (gendarme SS, statue SS, speedy SS, radar SS, Rotterdam SwS, Hanoi Sw,
   Laos 2 syllables, "John o' Groats" SSS): a writer has to test every word, not every bar.
10. The pronoun-ending cap grows with song length (2 per 38 bars, 4 at 76), so partial drafts fail a check the song passes.

## Findings 11-12 (15 Oct 2026, after Joe: "originals end rhymes are better rn" and the Lagos/favours/flavours/Vegas carpet)
11. The gate passed cheap, samey end rhymes: rapfit's pair score rewards an identical, common rime with 1.0, and nothing measured
    rhyme quality. Now HARD (rapfit.quality_hard): cheap rimes and identical rimes per section, at most the original's count + 1.
12. The gate passed Hook 5-8 with two separate rhymes (people/sequel, solid/wallet) where the original rhymes all four bars: the
    by-ear letters (ABBA) mark closest partners, not families, and the carpet check had been a note since 13 Oct. I skipped that
    note when writing this song. Now HARD (carpet >= 85% of the original's).
This draft fails the gate in 7 sections under the new rules; the rewrite follows.

## Rewrite of the end rhymes (15 Oct 2026, same day): ww gate PASS again under the new rhyme rules
Changed bars only (everything else as before). Each bar re-fitted with fitbar; fitbar 74/76 (bars 37, 39 as before).
- Hook 5-8: posse / solid / wallet / copy: one family across all four bars (rapfit carpet 6/6; the old block was 2/6).
- Hook 9-16 bar 4: through the floor (was the wall: call/Saul/wall were three identical rimes).
- V1 1-8 bars 5-6: Barbour parka, the judge gets lager (four identical -arma rimes became one pair, karma/drama).
- V1 9-16 bars 6-8: living the dream, top thief, he's discreet (six bare -ee rimes became three: me / we / free).
- V1 33-44 bars 8-10, 12: saving face, ten days' grace, fair game, no names (pay/sway/day/play/okay became pay alone).
- V2 1-8 bars 3, 8: top fried rice, it's mine (six bare -eye rimes became four: guy / die / high / fly).
- V2 9-16 bars 1, 3, 4: my own code, the East Coast, struck gold (phone/known/home-grown were one common rime).
Song-level fixes found on the way: songcheck still judges scheme pairs with the old grader (posse ~ profit 0.76, so bar 8 became
"copy"); "weight" is on the admin-word list (bar 57 became "ten days' grace"); dropping "well known" lost the W-L drum in V2 9-16
(bar 69 now opens "Well,") and the device rate fell to 37% until it was back (8 of 19 quads, 42%).
HONEST READING: on cheap and identical rimes the song now sits AT the original's count or one over it in 7 sections, never better
than the original except Hook 5-8 (0 identical vs 2). The rules bound it at "no worse than the original + 1"; they do not make
the rhymes as good as the original's, and the original's rarer multi-syllable and mosaic endings are still not matched.
NOTES LISTED TO JOE (rule 10; 121, all from the unvalidated beat-grid / ear diagnostics): 28 "two stresses jammed together",
14 comma / pause placement, about 20 reduced syllables on a downbeat, 3 hard mouth-shape transitions (inside the par).
Suffix check: it counts "seed" as an -ed ending by spelling (seating / keyring / seed tripped it); worked around, not fixed.

## Finding 13 and the second rewrite (15 Oct 2026, Joe: "Why is hook 5-8 still ABBA when the original is AAAA?")
13. Two causes. The scheme letters still said ABBA (from the 9 Oct "A C C A" note, which marked closest partners), and the
    carpet I had just added counted a pair when rapfit's pair score reached 0.50, which a shared stressed vowel alone does
    (posse ~ solid 0.66). So posse / solid / wallet / copy passed as "6/6" while it was two pairs. Now: Hook 5-8 is AAAA in
    toolkit/match.MANUAL_SCHEME, and the carpet counts a pair only when the endings chain syllable by syllable from the end
    (the original's Hook 5-8: all six pairs two syllables deep). The same rule then failed Hook 1-4, V1 1-8, V1 9-16,
    V1 25-32 and V2 1-8 (each had a bar sharing the stressed vowel but not the ending).
Rewrite (bars changed): Hook 1-4 Cheers to the venue / Left out on the rocks? I continue / ... all on a day's cruise /
... there's a good few (one ending: venue / continue / cruise / few). Hook 5-8 honest / solid / wallet / profit (all six
pairs two syllables deep, as the original's). V1 1-8 bar 1 ... the rest is larger. V1 9-16 bar 5 ... with all the athletes.
V1 25-32 bar 4 My boots in Bergen? Dead fatal. V2 1-8 bar 4 ... the sharks were in the crossfire; bar 5 ... jets at night.
Pronoun endings held at the cap (4): "got it" and "than I" were tried and dropped for that reason.
ww gate PASS (0 hard, sense read OFF); fitbar 74/76 (bars 37, 39 as before).

## Finding 14 and the third rewrite (15 Oct 2026, Joe: "How is: Amsterdam or Koh Tao or Spain or Cairns or Wales / Prost and then you
## buy / The same flow as" the original's bars 13-14)
14. The gates matched syllables (12, 5), stress positions (11 of 12, 5 of 5), end shape and rhyme position, and missed three things:
    (a) "Koh Tao" put two stressed syllables on back-to-back 16ths of the original's audio where it runs weak syllables into a hit (the
    stress-run tolerance +1 hid it); (b) the original's bar repeats one cell three times with an internal rhyme, ours was a list of
    places joined by "or"; (c) the original's two bars are one sentence. Now HARD in toolkit/flow_par.py: fast_jam (no more stressed
    pairs on adjacent 16ths than the original's same bar) and cell (at the original's 5 repeated-cell bars, ours needs a repeated cell
    and internal rhyme >= the original's - 1). Bar 13 is in toolkit/tests/flow_flagged.txt. (c) is not gated: bar 14 passes every flow
    measure; it is a sense point, listed here.
Rewrite (bars changed): 3 ... and it's a day's cruise; 11 Four-wheeler? Dead on arrival (fitbar pattern 75%: the cash forces a stress
the frame does not have; a note, not a gate); 13 Cash for Spain and it's cash for Cairns and cash for Wales (same device as the
original's bar, a repeated cell, with different words and syntax; Joe to judge whether it is too close); 17 One phone and a name, the
rest is larger; 24 Grazie grazie four weeks on a pass and no drama; 28 ... walked out of it scot free; 40 Tape it, van to van, the
whole marathon; 48 Need me? Gone to my guy's guy down the road for a quick sneaky; 50 Officer? Never never seedy; 52 Cash in
envelopes, the deal's all sunny; 58 You owe? My crew will play conkers, it's fair game; 68 Name it, my mate: one call and it's mine.
Six commas dropped to keep comma bars at 22 of 76 (30%). ww gate PASS (0 hard, sense read OFF); fitbar 73/76 (11, 37, 39).

## Finding 15 (15 Oct 2026, Joe: "In the original lyrics these look like long bars but if you look closely there are end rhymes in the
## middle, so it's actually delivered over 8 bars ... See how we have end rhymes that don't rhyme?")
15. Measured on the audio template: 35 of the original's 74 timed lines run past one musical bar. In four of them (bars 13, 41, 42, 50) a
    word landing at the bar line has the same vowels, from its stress to the end, as the line's end word: an end rhyme delivered in the
    middle of the written line. Ours had none there (mozzarella / Naples, half the price / label). Now HARD (toolkit/flow_par.py
    barline): ours must land one within a syllable of the original's position. Re-cutting the original into musical bars would re-index
    every audio template, scheme letter and par table, so the rule works on the line as written. Old bars 41 and 42 are in
    toolkit/tests/flow_flagged.txt.
Rewrite: 13 Cash for Cairns and it's cash for Wales and cash for Spain (Wales / Spain); 41 Mozzarella? A stranger? It's my guy in Naples
(stranger / Naples); 42 Marrakesh, a fake trader, my guy there, so check the label (trader / label); 50 Officer? Who me? Seedy? Seedy?
(the repeat lands at the bar line, as the original's bar 50 does). ww gate PASS.
16. Joe: "Turkey and certi is same closeness as stranger and Naples?" No: the bar-line rule matched vowels only (stranger / Naples 0.69,
    trader / label 0.66, Wales / Spain 0.67 against the original's 0.81, 0.95, 1.0). Now the bar-line rhyme must score within 0.10 of the
    original's (rapfit pair score). Rewrite: 13 Cash for Spain and it's cash for scales and cash for Wales (scales / Wales 1.0);
    41 Mozzarella? The staples? It's my guy in Naples (staples / Naples 1.0); 42 Marrakesh when I'm able, my guy there, so check the label
    (able / label 1.0). ww gate PASS. The bar 41 "stranger" line is a flagged test case.
17. Joe: "Bars that as forced or don't make sense?" The sense gate was OFF (no DeepSeek key). Back on via Claude (no key): per bar it fails
    37/76 of the ORIGINAL's bars, so it gates per slot against the original's count + 1. Ours failed 5 sections (Hook 1-4 3 vs 0,
    V1 25-32 6 vs 3, V1 33-44 5 vs 2; across bars in Hook 9-16 and V2 1-8). 12 bars rewritten into plain sentences or tied to the guy:
    "Left out on the rocks? I continue" -> "You left me for dead? I continue"; "a good few" -> "a free brew" (the hook's cashed idiom is
    now "bad news"); "My boots in Bergen? Dead fatal" -> "Beer's dear in Bergen? Near fatal"; "a quick sneaky" (no noun) -> "a quick
    freebie"; "Bangkok, the roadside, and the top fried rice" -> "Bangkok? My guy's van does the top fried rice". ww gate PASS.
    Still open (report-only character read): bar 58 "My crew will play conkers" vs bar 72 "Lone wolf"; Joe's call.
18. Joe: "Write a new version that passes all gates plus these new gates so I can see the difference". writing/song_know_a_guy_v2.md: 32 bars
    rewritten against the quality targets ("match the original", Joe's choice). ww gate PASS; targets 6/10 sections + character 2/2 (the current
    draft: 2/10, 1/2). Side by side with scores: writing/song_know_a_guy_v1_vs_v2.md. Findings: (a) Haiku's "forced" flag fires on most rhymed
    endings, and the bar-line rhymes and cashed idioms are exactly what it flags, so V1 25-32 (par 6%) stayed at 31-50%; (b) the song-level place
    and swagger gates force a place list into the hook, which Haiku marks low on first listen, so Hook 1-4 met the quality targets only when it
    failed those gates; (c) re-reading one changed section moves unchanged bars by 0.5, so near-par passes are noise. The place counter does not
    know Perth or Hanoi (only Greek, Bern, Dutch and Spain count in the hook).
19. Joe (16 Oct) asked whether flow matching hears mouth shapes, transitions, pauses and syllable lengths, comparing v2 bar 76 with the
    original's. Stress, syllable counts, mouth-shape joins, closed-vowel runs and 16th jams were gated; pause position and a cell hidden
    inside one spelled-out word were not, and syllable length (weight) is still not measured (a crude heavy-syllable count did not separate
    the two lines). Now HARD in toolkit/flow_par.py: `pause` (break after the original's syllable) and spelled-out cells. v2 refit: 20 bars,
    e.g. 76 "Stuck? Need me? Call on me, call on me: last lifeline" (pause after 3, the repeated cell on the 16th run), 69 "A guy? Well, my
    own boat", 58 "Your head's a conker now. You owe me? Fair game". ww gate PASS; targets 7/10 + character 2/2.
20. Joe (16 Oct): gates for internal rhyme (amount, similarity between neighbours), sandwich rhymes, multis across words. Built as one
    section-level gate (toolkit/texture.py) against the original's same section. v2 failed it in 8 of 10 sections (thin multis in the hook
    and V1 1-8, too little internal rhyme in V1 1-8 and V1 33-44, no sandwich where the original has them in V1 17-24 and V2 9-16). v3 passes:
    e.g. "Got framed? Left for dead?" ~ "Cops, bail, dock, jail" (multis across words), "...it's medical / Chemical? Gardaí come for the
    evidence" (a link and a frame sandwich), "Pool hall? Hustled well and then I struck gold / Bold: I skip queues..." (link). Finding: the
    sense read and dense internal rhyme pull against each other; V1 33-44 needed plain sentences that still carry rhyme ("When you owe me
    I know: your head is fair game", "Who do I know? A guy. So I won't name names").
21. Joe (16 Oct) pasted the original's bars 46-52 against ours: the original holds one two-syllable ending (stressed 'or' + weak 'ee') for
    five bars across the V1 25-32 / V1 33-44 break, then moves once; ours shared only the weak 'ee'. The tools heard 'caught me' as
    rhyming on 'me' alone. Fixed (closing pronoun joins the tail in its weak form; depth no shallower than the original's same bar;
    rhymes across section breaks where the original has them). v4 bars 46-50: cheeky / greedy / freebies / speedy / Seedy, then
    money / chummy. Other bars the new rules caught: Hook 1-4 venue / continue (1 syllable where the original's pair is 2: now issue /
    continue), V1 17-24 'Salary' (no rhyme with its group where the original's bar is 3 deep: now Scavengers), V1 1-8 bar 7 (now 'wait
    and see', carried across the break into V1 9-16).
22. Joe (16 Oct) on v4 bar 46: the original's opener "is smoother than 'Fags? Cheap packs'". Two causes, both now HARD in flow_par
    against the original's same bar: two stresses on ONE 16th of the audio template (same_step), and a stop where the next syllable
    comes on the same or next 16th (run_breaks; Joe: "Yes hard gate those too"). run_breaks failed 25 of v4's bars, mostly the
    "Question? Answer" bars; 25 bars changed. The cost: the Q&A punctuation was one of the draft's few character tics, and some bars
    now read as run-ons on the page ("Officer who? Me? Seedy?" kept its stops only where the audio leaves room).
23. Joe (16 Oct) on bars 13-14: the original's pair works "because it's a sentence over 2 lines"; ours was "two sentences", and "Same
    here" on bars 67-68 (the original runs through the middle of a word there). No gate looked across a bar line for syntax. Now HARD
    (flow_par.carry): where the original's bar cannot end without the next (6 bar lines), ours must not end a sentence either. Four bars
    changed (14, 16, 32, 68). The cost: the per-bar sense read cannot see enjambment and marks every run-on half as a fragment.
24. Joe (16 Oct): "The sense check should take into account when sentences cross over a line." It now reads a sentence over the bar line
    as one item and counts failing sentences, not bars. Read whole, three of v4's run-on sentences still fail on their own faults
    (bars 25-27, 31-32, 13-14); the Hanoi pair passes. All slots stay within the original's par.
25. Joe (16 Oct) on seven v4 bars that "passed the sense/quality gates": five were flagged and absorbed by the per-slot allowance; two passed
    because the read only asked whether a bar can be restated. A new read (pointcheck: "did you have to work it out?") ranks bad bars above
    the original's (AUC 0.89) but cannot be cut into a gate, and web lookups of slang made it worse (0.84). It now lists 20 v4 bars to Joe.
