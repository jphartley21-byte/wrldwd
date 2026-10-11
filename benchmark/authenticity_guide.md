# Authenticity guide: what makes a bar sound like a real bloke said it (9 Oct 2026, from Joe's verdict on full draft v1)
Joe: "decent first draft ... but they need a better understanding of flow and sense making (the human element that makes it sound authentic)".

## The tells that made v1 sound machine-made
1. TELEGRAPHESE. Dropped subjects, verbs and articles to fit the rhyme: "Laruns gendarme said fine", "Branch in Bratislava, joint endeavour", "Black tie on the four-by-four safari", "Red dot on the host at the after-party". Nobody talks like a headline. The original's lines are full sentences with I/we/he, a verb and small linking words (V1 L37-42 read like pub chat).
2. PLACE CHECKLIST. Six places in eight bars reads like an itinerary. The original names about one place per four bars in the verses and lets the scene happen there.
3. SCENE HOPPING. A stanza is ONE scene with cause and effect (caught -> bribe -> cop changes tune -> pub). v1 jumped Pyrenees -> Boomtown -> Gloucester Road with the same copper. Each line must follow from the last; pronouns must be clear.
4. WRONG VOICE. Joe is from Reading, lives in Bristol: southern English. Not "nowt" (northern), not "esky" (Aussie). Tics: NOT ESTABLISHED. An earlier agent guess listed 'mate, proper, sound, swear down, sorted, can't lie'; Joe says he never says 'swear down' (11 Oct 2026). Use voice/quiz.md and voice/profile.md instead.
5. PHRASES NOBODY SAYS. "I'm sadly departing", "joint endeavour", "Odds-on I sign for it". Test: would Joe say it to a mate word for word? If you would only write it, cut it.
6. FALSE DETAIL. You ride off the ferry at Douglas, not Laxey. Details must be right or a mate will notice.

## What already sounds human in v1 (keep this register)
"Couldn't get a pint so it's mint tea and it's actually lovely" / "Mum tells her mates it's a gap year, partly" / "Swear down I've tried to stop buying rugs" / "Meet me in the caff at the top of Snowdon" / "And I'm a bit behind on this month's targets". Pattern: a full spoken sentence, a small honest reaction, the menace or flex slipped in as an aside.

## Flow (text cannot hear; do these)
- Say the bar in your head at 142 BPM, four beats: the stressed syllables must fall where they would in speech, not where the rhyme forces them.
- Run `flow_check.py` WITH the original slot lines as reference; fix every pause, clash and pile-up flag or justify it in one line.
- Syllables within ±1 of the original line, rhyme stress in the same position.
- One breath per bar: if it needs a comma to be sayable, rewrite it.
