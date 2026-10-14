"""domain: the accumulated lessons of this project, as machine-readable lexicons.

The 17 HUMAN gates in toolkit/quality_gate.py cannot be decided by a rule (cringe, does the joke
land, plain-beats-clever, poster test...). But every time Joe rejected a stanza he named a REASON,
and those reasons recur. This module turns them into two things:

  * REASON_TO_GATE: the words Joe actually uses ("obscure", "lame", "makes no sense", "cringe")
    mapped to the human gate they mean, so a rejection can be labelled against the gate it broke.
  * lexicons (`SHOUT`, `JOKE`, `DOMESTIC`, ...) that give a *proxy* signal for those gates. A proxy
    screens; it never judges. That is the same contract as toolkit/gate_coverage.md: the tool prints
    the human gates and refuses to call a section finished.

Everything here is domain knowledge transcribed from CLAUDE.md rules 1, 5 and the rejections in
writing/iteration_log.md and STATE.md. No original lyric is stored here (CLAUDE.md rule 4).
"""

# --- why Joe rejected a stanza: his words -> the gate that broke ---------------------------
# Transcribed from writing/iteration_log.md ("Joe rejected v10 (Burton obscure, good grouse lame,
# L8 makes no sense)"), STATE.md ("Terrible flow and rhyme schemes and they say nothing"), and the
# review command's gate list G1-G6.
REASON_TO_GATE = [
    (r"\bobscure|\brare\b|\bunknown to a (british|uk)\b|\bneeds? .{0,24}known|g2 risk|\bdated\b",
     "G2", "recognisability: a mate in his 30s would not get it"),
    (r"\bmakes? no sense|\bdoes not make sense|\bno sense\b|\bblur\b|\bsays? (little|nothing)\b|"
     r"\bdoesn'?t say\b|\bneeds? explaining\b|\bg1 risk",
     "G1", "plain sense: it is not a sentence a mate would say in the pub"),
    (r"\bcringe|\bwince|\bembarrassing\b", "G34", "cringe filter: a mate would wince"),
    (r"\blame\b|\bweak\b|\bflat\b|\btechnique\b.*optimis|\brhyme-first|\bback-fill|\bno pun\b|"
     r"double meaning is light|\bdevice\b",
     "G3", "not a technique carrier: the bar exists only for its rhyme, pun or alliteration"),
    (r"\bpun\b.*(light|weak|faint)|only implied|\bnot landing\b",
     "G38", "wordplay carried by the rhyme slot: the payoff does not land"),
    (r"flow bad|\brhymes? off\b|\bdoes not hit\b|\bdoesn'?t hit\b|\bscheme\b|\bsyllable", "FORM",
     "form: rhyme scheme / rhythm (the toolkit measures this; not a human gate)"),
]

# Rewrite directions Joe accepted as the right fix, keyed to the gate. Used by judge.py to turn a
# flagged feature into advice rather than just a number.
GATE_ADVICE = {
    "G1": "give the bar a subject, verb and object; one connected thought per stanza",
    "G2": "swap the dated/obscure word for one a 30s southern-English mate gets instantly",
    "G3": "cut the bar that exists only to carry the rhyme; say something with it",
    "G34": "report it flat - drop the wink, the explanation and the intensifier",
    "G38": "move the payoff word into the rhyme slot (the bar's last stressed syllable)",
    "G39": "no setup-then-punchline shape; the joke is the literal reading of a stock phrase",
    "FORM": "fix length/rhythm via toolkit/check_all.py",
}

# --- proxies for the human gates ------------------------------------------------------------
# G12/G37 nonchalance: the narrator reports something big flat, never shouts. Intensifiers and
# exclamation marks are the tell that a bar is selling rather than reporting.
SHOUT = set("""very really absolutely totally literally insanely massive huge incredible amazing
unbelievable mental mad crazy insane enormous brilliant fantastic epic""".split())

# G39 no gag structure: markers that announce a joke instead of letting the literal reading land.
JOKE = set("""haha lol lmao joke joking punchline funny hilarious boom boom-boom ha-ha
knee-slapper nudge nudge""".split())
JOKE_PHRASES = [r"\bget it\b", r"\bif you know what i mean\b", r"\bso to speak\b",
                r"\bno pun intended\b", r"\bsorry,? not sorry\b"]

# G16/G40 domestic anchors: the original grounds the menace in an everyday British register
# (parcel delivery, pub, telling-off, prices). This is the lexicon of that register.
DOMESTIC = set("""kettle tea brew cuppa pub pint missus wife husband in-laws bath shower
sofa telly tele garage van parcel postie postman post office chip shop chippy takeaway
sunday shed mot insurance tax rent mortgage corner shop off-licence newsagent bus stop
roundabout service station m-way motorway lay-by car park trolley checkout receipt
washing up hoover bin day binman round tea-time dinner tea plate mug kitchen""".split())

# G40 character: a named person carried by the words (the group's mates appear by name).
# Names seen in the project's material and keepers: not a hard list, only a hint.
CHARACTER_NAMES = set("""gaz dave joe baz dean lee steve tony mark paul sean""".split())

# Rule 24: no AI-tell words or shapes (also enforced in toolkit/rhyme_tools.py BANNED).
AI_TELL = set("""delve tapestry realm embark myriad plethora vibrant testament
unwavering breathtaking effortlessly""".split())

# Rule 1: the payoff must be the literal thing a stock phrase names. These openers are the
# template shapes (G3 / G6) the reviews flag.
TEMPLATE_OPENERS = set("""and so then but nobody as i when the it's""".split())
