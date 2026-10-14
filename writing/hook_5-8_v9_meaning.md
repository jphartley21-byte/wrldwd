# Hook 5-8 v9: written for meaning, not for the score (12 Oct 2026)

Ola and the lot on the dot
A grazie and a page of the orders
Names and numbers at the borders
Might do a week in Ljubljana

scheme PASS | form 10 | meaning 0 | coherence 1 | syllables 8/10/8/8 exactly on frame
rhyme-slot payload 3.91 (the original's hook is 4.04) | places 1 | loanword: grazie

## Why this exists
Joe rejected the block the sweep crowned -- "Hallo and the boat in Oslo / A page of the orders and
the corners / None of the names on the quarters" -- as meaningless gibberish, correctly. The cause
was not the search, it was the writer: after the sweep I kept editing by substituting words to satisfy
sound constraints (borders -> quarters for the rhyme) and never re-read the line. No gate caught it
because no gate tests whether words belong together; meaning_gate only tests for ABSENCE of content.

## The instrument that was supposed to catch this, and failed
toolkit/attest.py counts exact occurrences of a bar's head and tail four-word phrases on Wikipedia.
Measured on known material it does not discriminate:
  gibberish: "None of the names on the quarters" 0 hits, "A page of the orders and the corners" 0 hits
  good lines: Joe's approved "Front row at the on-stage porno" 0 hits, "Paid him by the weight" 0 hits,
              "Might take the ferry to Bergen" 0 hits
A bar's tail is a clause boundary, not an idiom, so real lines score zero. Kept as a negative result
and a by-hand CLI; explicitly NOT to be used as a gate.

## The trade, measured
                     scheme  form  meaning  coh  payload  places  sense
  swept (gibberish)  PASS     8     0        0    3.60     2       none
  this block         PASS    10     0        1    3.91     1       every bar
Two form points is what sense costs here. Sound and sense pull in opposite directions, and the only
defence against the first is a writer who reads the second.
