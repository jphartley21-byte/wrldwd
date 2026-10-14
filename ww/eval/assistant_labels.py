"""The assistant's strict bar-by-bar read of writing/full_draft_v27.md (12-13 Oct 2026). labelled_by = assistant, LOWEST weight,
dev split ONLY, never in the sealed test or any exit criterion (R14: assistant-made labels must not validate an assistant-built judge).

C = clear claim or event; F = fragment that still pictures something (neutral, not used for accuracy); L = list/inventory;
X = filler, ungrammatical or nonsense. Hook 1-4 is Joe's accepted block and is exempt (the earlier agent read called bar 2 nonsense
- a contradiction the plan resolves by tagging it pun-licensed, not by flagging Joe's own bars).
Strings are one letter per bar, in section order.
"""
V27_LABELS = {
    "Hook 5-8": "XCFC",
    "Hook 9-16": "FXFLLXCX",
    "V1 1-8": "XFXXFFCX",
    "V1 9-16": "CCFCXCFL",
    "V1 17-24": "XXCCCCXF",
    "V1 25-32": "LLXXXXCL",
    "V1 33-44": "XFCXFXFXFXFF",
    "V2 1-8": "FLFFLCXX",
    "V2 9-16": "FXFFFFXX",
}
NEGATIVE = {"X": "filler_or_nonsense", "L": "list_or_inventory"}
POSITIVE = {"C": "clear_claim_or_event"}
