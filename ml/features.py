"""features: one numeric vector per bar, built from the EXISTING toolkit.

Nothing here re-implements a check. Every feature is a call into a module the project already
trusts (toolkit/meaning_gate.py, craft_scan.py, rubric_score.py, sense_checks.py, flow_check.py,
rhyme_tools.py), so the judge can never measure anything the gates do not already measure. What the
judge adds is the ARCHITECTURE: the 17 human gates have no rule, so instead of a rule we learn a
probability from Joe's own verdicts plus a rule prior that encodes his stated reasons (ml/domain.py).

Feature groups, and the human gate each stands in for:
  form      -> FORM   (syllables, stress clash, bursts, band)                       [toolkit-measured]
  meaning   -> G1/G3  (clause runs off the end, no content, filler frames)
  flat      -> G12/G37(nonchalance: intensifiers and exclamation are the anti-tell)
  wordplay  -> G13/G28/G38 (cashed idiom, payoff in the rhyme slot, internal rhyme, homophones)
  image     -> G15/G36(lexical-field spread, proper nouns, domestic anchors)
  cringe    -> G34/G39(banned/AI-tell words, joke markers, rule-of-three, announced pun)
  character -> G40    (a named person, a domestic anchor, one scene)
  block     -> chain  (carpet share, scheme, duplicate end words) - stanza context per bar

The rule prior (`rule_prior`) is a single weighted score over the lexicons. It carries the domain
knowledge directly, so the judge is useful before the label set is large enough to learn from text.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TK = os.path.join(ROOT, "toolkit")
for p in (TK, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import rhyme_tools as rt          # noqa: E402
import meaning_gate as mg         # noqa: E402
import craft_scan as cs           # noqa: E402
import rubric_score as rs         # noqa: E402
import sense_checks as sc         # noqa: E402
from flow_check import bar_profile  # noqa: E402
import domain as dom              # noqa: E402

WORD_RE = re.compile(r"[A-Za-z']+")
BULLET_RE = re.compile(r"^\s*(?:#|[-*|>\[\]]|```)")   # incl. the repo's own "[Verse 1, Block A: ...]"
#                                                        structure lines and "[tool]" annotations, which
#                                                        check_all's reader also treats as non-bars
# A short LABEL at the start of the line ("quad:", "Alt 8:", "Verse 1:") is a notes line, not a bar.
LABEL_RE = re.compile(r"^\s*[A-Za-z][A-Za-z' _-]{0,18}:")
# A parenthetical carrying project ANNOTATION, not lyric: "(Porto 2023 true; timeshares invented; ...)",
# "(was 8)", "(invented)". The bar text is contaminated, so the line is dropped rather than cleaned.
ANNOT_RE = re.compile(
    r"\((?:[^()]*\b(?:invented|persona|callback|syllables?|exact|carpet|multisyl|notes?|quad|true"
    r"|hinge|rhyme|link)\b[^()]*)|\(\s*was\s+\d[^()]*\)", re.I)
# Shell commands and paths leak into the corpus from notes files; they are never lyric.
COMMAND_RE = re.compile(r"\bpython\b|\.py\b|toolkit/|writing/|[A-Za-z]:\\", re.I)
# Markers that appear in this project's PROSE (tool reports, pool notes, beat sheets) and in
# essentially no lyric bar. They stop a report file being silently scored as if it were bars.
PROSE_RE = re.compile(
    r"\bG[1-6]\b|\bfailed\b|\bStalled\b|\bcontender\)|\bWordplay\b|^\s*[A-Z][a-z]+:"
    r"|^\s*[A-Za-z]{2,}\s*\d+\s*:"                      # notes lines like "Alt 8:" / "Round 3:"
    r"|\bgate\b|\bmargin\b|\bmeasured\b|\bper-line\b|\bsyllable|\bpar\b|\boriginal\b"
    r"|\bblocks?\b|\bdraft\b|\bverified\b|\bTODO\b|\bPLACEHOLDER\b")


def clean_bars(lines):
    """Keep only lines that look like a LYRICAL BAR. Shared by the dataset builder and the judge so
    the two can never disagree about what counts as a bar (a prose note must not be scored as one)."""
    out = []
    for line in lines:
        s = line.strip()
        if not s or BULLET_RE.match(s):
            continue
        s = re.split(r"\s{2,}(?:CHANGED|NOTE)\b", s)[0].strip()
        s = re.sub(r"^(?:bar|line)\s*\d+\s*[:.)-]\s*", "", s, flags=re.I)   # "Bar 1: ..." from a model
        s = re.sub(r"^\d{1,2}\s*[:.)]\s+", "", s)          # "1. ..." / "2) ..."
        s = re.sub(r"^\d{1,2}\s+", "", s)                  # "5 Say hola..." from a transcript
        s = re.sub(r"\s*\((?:invented|persona|true|flagged)[^)]*\)\s*$", "", s, flags=re.I)
        words = s.split()
        if not 2 <= len(words) <= 20 or len(s) > 110:
            continue
        if s.endswith(":") or s.count("|") >= 2 or PROSE_RE.search(s):
            continue
        # bracket anywhere, a leading label, or an annotation parenthetical = a notes line, not a bar
        if "[" in s or "]" in s or LABEL_RE.match(s) or ANNOT_RE.search(s) or COMMAND_RE.search(s):
            continue
        # a bar is one clause: two sentences on a line, or a markdown/assignment artefact, is prose
        # from a draft's preamble (which the draft files wrap across several lines).
        if re.search(r"\.\s+[A-Z]", s) or "=" in s or "`" in s:
            continue
        if s.count("(") != s.count(")"):        # a report's parenthetical, not a lyric
            continue
        out.append(s)
    return out

# Feature order is fixed: the judge's explainer and the printed report rely on it.
NUMERIC_FEATURES = [
    # form
    "syl", "clash", "lapse", "pause", "cluster", "in_band", "soft_ending",
    # meaning
    "n_content", "end_dead", "end_enj", "end_tag", "n_filler", "mech_fails",
    # flat / nonchalance
    "intensifiers", "exclam", "caps_words", "shout_share",
    # wordplay
    "n_idioms", "payoff_slot", "internal_pairs", "redups", "homophone_pairs", "oov_ends",
    # image / truth
    "theme_hits", "field_spread", "n_places", "proper_nouns", "domestic", "n_named",
    # cringe / gag
    "banned", "ai_tell", "joke_markers", "list_fragment", "rule_of_three", "template_opener",
    # character
    "first_person", "mentions_person",
    # block context
    "pos_in_block", "block_bars", "carpet_share", "scheme_letters", "dup_end_words",
    "block_internal_share", "block_hops", "block_no_links",
    # the encoded prior
    "rule_prior",
]


def _words(text):
    return [w.lower() for w in WORD_RE.findall(text)]


def _ends_on(bar, kind):
    ws = WORD_RE.findall(bar)
    return 1 if ws and ws[-1].lower() in kind else 0


def _devices(bars):
    """Figures of speech per bar (toolkit/devices.py). Kept OUT of NUMERIC_FEATURES so the saved
    judge model keeps its input shape; the feature dict carries them for reporting."""
    try:
        import devices as dv
        return dv.inspect(bars)
    except Exception:
        return [{"bar": i + 1, "text": b, "devices": []} for i, b in enumerate(bars)]


def block_features(bars):
    """Stanza-level context, computed once and attached to every bar of the block."""
    letters, _reps, _detail = cs.families(bars)
    stats = rs.block_stats(bars)
    hops = sc.hops(bars)
    ends = [_words(b)[-1] for b in bars if _words(b)]
    dup = len(ends) - len(set(ends))
    return {
        "block_bars": len(bars),
        "devices": _devices(bars),
        "carpet_share": round(stats.get("carpet", 0.0), 3),
        "scheme_letters": len(set(letters)),
        "dup_end_words": dup,
        "block_internal_share": round(stats.get("internal", 0) / max(1, len(bars)), 3),
        "block_hops": len(hops),
        "block_no_links": 1 if len(hops) >= max(1, len(bars) - 1) else 0,
    }


def bar_features(bar, idx, block, blk):
    """Features for one bar; `blk` is block_features(bars) for its stanza."""
    ws = _words(bar)
    prof = bar_profile(bar)
    mech = mg.audit([bar], None)
    hard = mech["bars"][0][2] if mech["bars"] else []
    issues = mech["bars"][0][3] if mech["bars"] else []
    content = mg.content_words(bar)
    idioms = cs.idioms_in(bar)
    fields = sc.fields([bar])
    proper = sc.proper_nouns([bar])
    place_tokens = [w for w in ws if w in mg.PLACES]

    intens = sum(1 for w in ws if w in dom.SHOUT)
    caps = sum(1 for t in WORD_RE.findall(bar) if t.isupper() and len(t) > 1)
    exclam = bar.count("!")
    shout_share = (intens + exclam + caps) / max(1, len(ws))

    joke = sum(1 for w in ws if w in dom.JOKE)
    joke += sum(1 for p in dom.JOKE_PHRASES if re.search(p, bar.lower()))
    low = " " + bar.lower() + " "
    conj = len(re.findall(r"\b(and|or)\b", low))
    commas = bar.count(",") + bar.count(";")
    list_frag = 1 if idx in sc.list_fragments([bar]) else 0
    # rule of three: "x, y and z" or three parallel "and"s
    rule3 = 1 if (conj >= 2 and (commas >= 1 or bar.count(" and ") >= 2)) else 0
    template = 1 if ws and ws[0] in dom.TEMPLATE_OPENERS else 0

    banned = sum(1 for w in ws if w in rt.BANNED) + sum(1 for w in ws if w in dom.AI_TELL)
    oov = sum(1 for w in ws if rt.pron(w) is None and len(w) > 2)
    oov_ends = 1 if ws and rt.pron(ws[-1]) is None else 0

    domestic = sum(1 for w in ws if w in dom.DOMESTIC)
    named = sum(1 for w in ws if w in dom.CHARACTER_NAMES)
    first_person = 1 if re.search(r"\b(i|my|me|we|our|us)\b", low) else 0
    # a "domestic person mentioned not addressed": third-person reference to a person
    mentions_person = 1 if re.search(r"\b(he|she|his|her|the missus|the wife|in-laws|mate|bloke|"
                                     r"fella|lad|bird|geezer)\b", low) else 0

    n_idioms = len(idioms)
    payoff = 1 if cs.payoff_in_rhyme_slot(bar) else 0
    internal = len(cs.internal_pairs(bar))
    redups = len(re.findall(r"\b(\w+)-\1\b", bar.lower()))
    homophones = 0  # filled at block level below

    prior = 0.0
    prior += 3.0 * _ends_on(bar, mg.END_DEAD)
    prior += 2.0 * (1 if not content else 0)
    prior += 1.0 * (1 if len(content) == 1 else 0)
    prior += 2.0 * len([h for h in hard if "filler" in h])
    prior += 2.0 * banned
    prior += 1.5 * oov_ends
    prior += 1.0 * intens + 0.5 * exclam
    prior += 2.0 * joke + 1.5 * rule3
    prior += 1.5 * list_frag
    prior += 1.0 * template
    prior += 0.5 * (1 if (not place_tokens and not domestic and not named and not proper) else 0)
    prior -= 1.5 * (1 if (payoff and n_idioms) else 0)   # a cashed idiom in the rhyme slot is credit
    prior -= 1.0 * (1 if internal >= 1 else 0)
    prior -= 0.5 * min(2, len(fields))                    # image credit, capped
    prior -= 0.5 * (1 if domestic else 0)
    prior += 1.0 * (1 if prof["lapse"] >= 3 else 0)       # long unstressed run: hard to deliver

    zeros = {k: 0.0 for k in NUMERIC_FEATURES}
    zeros.update({
        "syl": prof["syl"], "clash": prof["clash"], "lapse": prof["lapse"],
        "pause": prof["pause"], "cluster": prof["cluster"],
        "in_band": 1 if 5 <= prof["syl"] <= 14 else 0,
        "soft_ending": 1 if (prof["grid"] and prof["syl"] > prof["grid"][-1]) else 0,
        "n_content": len(content),
        "end_dead": _ends_on(bar, mg.END_DEAD), "end_enj": _ends_on(bar, mg.END_ENJ),
        "end_tag": _ends_on(bar, mg.END_TAG),
        "n_filler": len([h for h in hard if "filler" in h]), "mech_fails": len(hard),
        "intensifiers": intens, "exclam": exclam, "caps_words": caps,
        "shout_share": round(shout_share, 3),
        "n_idioms": n_idioms, "payoff_slot": payoff, "internal_pairs": internal,
        "redups": redups, "oov_ends": oov + oov_ends,
        "theme_hits": 0, "field_spread": len(fields),
        "n_places": len(place_tokens), "proper_nouns": len(proper) - len(place_tokens),
        "domestic": domestic, "n_named": named,
        "banned": banned, "ai_tell": sum(1 for w in ws if w in dom.AI_TELL),
        "joke_markers": joke, "list_fragment": list_frag, "rule_of_three": rule3,
        "template_opener": template,
        "first_person": first_person, "mentions_person": mentions_person,
        "rule_prior": round(prior, 3),
    })

    # theme-set hits replace the placeholder above (needs the theme categories)
    cats = rt.theme_words()
    theme_hits = 0
    for _cat, words in cats.items():
        for term in words:
            if term in bar.lower():
                theme_hits += 1
    zeros["theme_hits"] = min(3, theme_hits)
    zeros["homophone_pairs"] = 0
    zeros["pos_in_block"] = idx
    zeros.update(blk)
    return zeros


def block_row(bars, source, label, provenance):
    """A full labelled stanza: block text, per-bar feature rows, block-level extras."""
    blk = block_features(bars)
    blk["homophone_pairs"] = 0  # placeholder, set below
    homos = cs.homophone_pairs(bars)
    rows = []
    for i, b in enumerate(bars, 1):
        f = bar_features(b, i, bars, blk)
        f["homophone_pairs"] = len(homos)
        rows.append({"bar": i, "text": b, "features": f})
    return {"source": source, "label": label, "provenance": provenance,
            "bars": rows, "homophones": len(homos)}


def vector(row):
    """Flat numeric vector for a bar row, in NUMERIC_FEATURES order."""
    return [float(row["features"].get(k, 0.0)) for k in NUMERIC_FEATURES]


if __name__ == "__main__":
    demo = ["Front row at the on-stage porno", "Money's pouring in this quarter"]
    br = block_row(demo, "demo", "accept", "hand-run")
    for r in br["bars"]:
        print(r["bar"], r["text"], "->", r["features"]["rule_prior"], "prior;",
              r["features"]["n_content"], "content words")
