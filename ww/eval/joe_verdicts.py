"""Joe's recorded verdicts as data (R11: his words verbatim in `joe_quote`). The only human labels there are.

Sources: STATE.md, writing/iteration_log.md, toolkit/tests/rejected_*.txt, writing/contenders.md, writing/hook_1-16_v5.md.
`axes` says which kind of failure the verdict is about, so a sound-only complaint (Joe: Ljubljana does not rhyme with
dot/orders) never counts as evidence about the SENSE axes. `quote_exact` is False where the repo records a paraphrase.

Bars here are Joe's own accepted text or OUR rejected drafts; none are the original's lines.
"""
from __future__ import annotations

# (id, label, bars, joe_quote, quote_exact, axes, source, strength)
# label: accept | reject | contender ; axes subset of {sense, sound, flow, stance, unspecified, pun_licensed}
VERDICTS = [
    ("joe_hook_1-4", "accept",
     ["Yo, bonjourno", "Said damn at the on-stage porno", "Front row on my phone, so bored, though",
      "So I boarded a plane out to Bordeaux"],
     "", False, ["pun_licensed"], "toolkit/tests/joe_hook_1-4.txt; STATE.md (Joe-authored)", "authored"),
    ("joe_hook_5-8_V-a", "accept",
     ["Cold beer on the house in Porto", "A glass of port and he knows the waters", "Not the worst pint and last orders",
      "Might hit the road to Majorca"],
     "(chose this variant over the rejected inventory Option 1)", False, ["sense"],
     "STATE.md 12 Oct 'FINAL HOOK'; writing/hook_1-16_v5.md", "preferred_over_rejected"),
    ("joe_majorca_v5", "contender",
     ["Hola to the whole of Majorca", "Met a fella, says he's an importer", "Moves the lot from over the water",
      "Might have to sign for it in Portsmouth"],
     "not bad, it's a contender", True, ["sense"], "writing/contenders.md; iteration_log 9 Oct v5", "contender"),

    ("rej_quad_a", "reject",
     ["Hey there boss the Bristol raiders", "Under the radar the boss wrote papers", "On the level with my payers",
      "Might check Bordeaux haul to traders"],
     "still lack cohesion and meaning and purpose", True, ["sense"], "STATE.md; iteration_log 11 Oct 'Joe REJECTS Quad A'", "rejected"),
    ("rej_hook_5-8_v11", "reject",
     ["Hey port and the road to Porto", "Two glasses cold lager then cut corners", "Lager chips and the last orders",
      "Might hit the road then the border"],
     "they don't make sense... flow is worse", True, ["sense", "flow"], "STATE.md 'VERDICT ON v11'", "rejected"),
    ("rej_q119_hook_5-8", "reject",
     ["Ola and the long road to Porto", "They stop him again before the border", "He gets a glass of water",
      "Might miss the boat in the morning"],
     "Parts still dont make sense. It doesnt seemlessly flow as a whole or feel like a coherent thought or character. "
     "It doesnt say anything and there's no payoff.", True, ["sense", "stance"], "iteration_log 11 Oct; writing/pool_v3_quads.md Q119", "rejected"),
    ("rej_q120_hook_9-16", "reject",
     ["Three nights in a hostel in Ljubljana", "G'day and the boat out to the Whitsundays", "Ahoj and a bus across to Bratislava",
      "Byron Bay and he never got on a wave", "Same bag same bus same banana", "He lost a whole day",
      "A place he cannot pronounce and a plate of pasta", "Might do another week in Zell am See"],
     "Parts still dont make sense. It doesnt seemlessly flow as a whole or feel like a coherent thought or character. "
     "It doesnt say anything and there's no payoff.", True, ["sense", "stance"], "iteration_log 11 Oct; writing/pool_v3_quads.md Q120", "rejected"),
    ("rej_hook_9-16_v2", "reject",
     ["Rain in Bergen, then the bar", "Skal from the in-laws, bizarre", "The coast is one road, all the way",
      "Took the ferry, tunnel, and the car", "Cash, cash, cash, and then we drive it half the night, right",
      "Skint the next day, mate", "Boomtown, the souk, three in a row", "Then back the same, anyway"],
     "Neither of these are good enough.", True, ["sense", "stance"], "STATE.md 11 Oct (late 12); writing/hook_9-16_v2.md", "rejected"),
    ("rej_forge2_hook_9-16", "reject",
     ["In Bergen it's always skal", "The in-laws say shoes off or it's war", "Next I tipped my Porto waiter",
      "Then rode back with a case maybe four", "Nordic pine with a Nordic nine and Nordic bride", "Then down Oslo way",
      "Stayed at some mate's mate's in his bath", "Fifty kroner happy days"],
     "Neither of these are good enough.", True, ["sense", "stance"], "STATE.md 11 Oct (late 12) forge #2", "rejected"),
    ("rej_inventory_bar_corners", "reject",
     ["Two glasses, cold lager, back road corners"],
     "a nothing line with shit flow and should not have got through", True, ["sense", "flow"], "STATE.md 12 Oct 'Joe rejected a line that passed every gate'", "rejected"),
    ("rej_inventory_bar_folders", "reject",
     ["No names just numbers on folders"],
     "unclear, and it does not flow (stacks three stresses)", False, ["sense", "flow"], "STATE.md 12 Oct 'how did it get through the gates?'", "rejected"),
    ("rej_gibberish_quarters", "reject",
     ["None of the names on the quarters"],
     "how is the writer still landing on lines that are meaningless gibberish?", True, ["sense"], "STATE.md 12 Oct 'meaningless gibberish'", "rejected"),
    ("rej_hook_5-8_v9_ljubljana", "reject",
     ["Ola and the lot on the dot", "A grazie and a page of the orders", "Names and numbers at the borders",
      "Might do a week in Ljubljana"],
     "how did Ljubljana get into a block whose scheme demands a rhyme", False, ["sound"], "STATE.md 12 Oct", "rejected"),
]

# the six 'inventory' bars the repo's meaning_judge labelled 'fail'. Joe called some of them nothing and others only
# read as nothing (STATE.md 13 Oct 5: two labels were the assistant's and were wrong), so weight is halved.
INVENTORY_BARS = [
    "Pass maps plans and the road the rail going",
    "A packed bag a long rail a whole month a road going",
    "Cash cards and paid the same day",
    "Nine countries four walks cash going",
    "Gave them the cash the cards and the pass",
]

# toolkit/tests/rejected_*.txt : (file stem, joe_quote, axes)
REJECTED_FILES = {
    "rejected_v14_majorca": ("rhyme sits mid-word in 'Majorca' where the original's 'in LA-gos' starts it at a word start", False, ["sound"]),
    "rejected_v12_hook915": ("the scheme and the rhyme do not work like the original's; 'fleece/piece/police' does not work", False, ["sound"]),
    "rejected_v7_iom": ("rejected, no reason recorded beyond rhyme and flow", False, ["unspecified"]),
    "rejected_v9_iom": ("rejected, no reason recorded beyond rhyme and flow", False, ["unspecified"]),
    "rejected_v10_iom": ("rejected, no reason recorded beyond rhyme and flow", False, ["unspecified"]),
    "rejected_v12_snowdon": ("rejected, no reason recorded", False, ["unspecified"]),
}
