"""Deterministic grammar / referent verifier (plan 4.3 a, b) on spaCy en_core_web_sm.

The two commonest v27 faults were ungrammatical word-strings (19) and unintroduced it/him/them (16); no gate caught either. This
checks, per bar and per RUN (pronouns need an antecedent inside the run):

  kind:  clause (finite verb) | elided (verb-initial: the genre drops "I") | participle (non-finite verb phrase) | list | fragment
  hard flags (block the bar, R13):  no_verb, list, bare_numeral_end, transitive_without_object, unresolved_pronoun:<w>
  weak flags (reported, never block):  weak_it, weak_parse (tagger unsure on a very short fragment)

It is a MEASURE and is subject to the registry: tuned on the dev split only, evaluated on the sealed split once, accepted or demoted by
the pre-registered rule (ww.eval.axes). Lyric fragments are hard for a parser trained on news prose, so the rules are deliberately few.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

THIRD = {"him", "her", "them", "they", "he", "she", "his", "their", "hers", "theirs", "himself", "herself", "themselves"}
TRANSITIVE = {"catch", "take", "give", "pay", "buy", "send", "put", "bring", "drop", "make", "win", "find", "hold", "show",
              "tell", "leave", "sell", "lose", "keep", "post", "pack", "book", "grab", "slip", "tape", "box", "strap"}
OBJECT_DEPS = {"dobj", "obj", "dative", "prt", "prep", "agent", "attr", "ccomp", "xcomp", "advcl", "acomp", "oprd", "npadvmod",
               "advmod", "conj", "pcomp", "intj", "relcl"}
FINITE_TAGS = {"VBD", "VBZ", "VBP", "MD"}
VERB_TAGS = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "MD"}
MOD_DEPS = {"amod", "compound", "nmod", "nummod"}
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty", "thirty",
                "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million"}
AUX = {"be", "is", "was", "were", "are", "am", "been", "being", "get", "got", "gets", "have", "has", "had", "having", "do", "did", "does"}
PERSON_WORDS = {"lad", "lads", "bloke", "blokes", "man", "men", "woman", "women", "mate", "mates", "boy", "boys", "girl", "girls", "wife",
                "husband", "mum", "mom", "dad", "brother", "sister", "boss", "copper", "coppers", "cop", "cops", "police", "plod", "officer",
                "driver", "dealer", "customer", "friend", "friends", "stranger", "guy", "guys", "crew", "gang", "family", "kid", "kids",
                "child", "people", "person", "waiter", "barman", "landlord", "landlady", "owner", "bouncer", "partner", "fella", "chap",
                "gentleman", "lady", "pal", "bird", "birds", "chick", "chicks", "federale", "rival", "victim", "uncle", "aunt", "nan",
                "grandad", "neighbour", "customs", "guard", "porter", "teacher", "doctor", "nurse", "king", "queen", "someone", "everyone"}
# the tagger reads a capitalised lyric opener ("Slept in the hostel") as a proper noun; these openers are verbs in this genre
IRREGULAR_PAST = {"slept", "ate", "went", "took", "gave", "paid", "bought", "sold", "sent", "ran", "got", "put", "made", "came", "saw",
                  "left", "lost", "won", "met", "said", "told", "found", "kept", "held", "drove", "rode", "flew", "wrote", "spent",
                  "stood", "sat", "slipped", "shipped", "stepped", "tipped", "grabbed", "dropped"}


@lru_cache(maxsize=1)
def nlp():
    import spacy
    return spacy.load("en_core_web_sm", disable=["ner"])


def _content(doc):
    return [t for t in doc if not t.is_punct and not t.is_space]


def analyse_doc(doc, known: set[str]) -> dict:
    toks = _content(doc)
    flags, weak = [], []
    if not toks:
        return {"kind": "empty", "flags": ["no_verb"], "weak": [], "nouns": [], "pronouns": []}
    verbs = [t for t in toks if t.tag_ in VERB_TAGS and t.dep_ not in MOD_DEPS]
    finite = [t for t in verbs if t.tag_ in FINITE_TAGS]
    first = toks[0]
    fl = first.text.lower()
    first_is_verb = first.tag_ in VERB_TAGS or fl in IRREGULAR_PAST or (fl.endswith("ed") and len(fl) > 3 and first.tag_ in ("NN", "NNP", "NNS", "JJ"))
    nouns = [t for t in toks if t.pos_ in ("NOUN", "PROPN")]
    head_nouns = [t for t in nouns if t.dep_ != "compound"]
    n_conj = sum(1 for t in toks if t.dep_ == "conj" or t.pos_ == "CCONJ")
    if finite:
        kind = "clause"
    elif first_is_verb:
        kind = "elided"
    elif verbs:
        kind = "participle"
    elif len(head_nouns) >= 3 and (n_conj >= 1 or any(t.text == "," for t in doc)):
        kind = "list"
    else:
        kind = "fragment"
    if kind == "list":
        weak.append("list")  # blocking lists is meaning_gate's inventory rule (calibrated on the original); here it is only reported
    if kind == "fragment":
        # a verbless noun phrase can be a picture (the genre allows it), so this is a report, not a block; lists ARE blocked above
        weak.append("verbless" if len(toks) >= 3 else "weak_parse")
    last = toks[-1]
    if last.pos_ == "NUM" or last.tag_ == "CD" or last.text.lower() in NUMBER_WORDS:
        weak.append("bare_numeral_end")  # idiomatic in real verse ("an aunt or two"); reported, not blocked
    run = 0
    for t in toks:  # "Paid packed gone the way": three verb forms in a row with no object, conjunction or auxiliary between
        run = run + 1 if (t.tag_ in ("VBD", "VBN", "VBG") and t.text.lower() not in AUX) else 0
        if run >= 3:
            flags.append("verb_string")
            break
    root = next((t for t in doc if t.dep_ == "ROOT"), None)
    if root is not None and root.tag_ in VERB_TAGS and root.lemma_.lower() in TRANSITIVE:
        passive = any(c.dep_ in ("auxpass", "aux") for c in root.children)
        if not passive and not any(c.dep_ in OBJECT_DEPS for c in root.children):
            flags.append("transitive_without_object")  # "Copper at the door caught"
    pronouns = []
    seen_here: set[str] = set()
    for t in doc:
        w = t.text.lower()
        if t.pos_ in ("NOUN", "PROPN"):
            seen_here.add(t.lemma_.lower())
        if t.pos_ == "PROPN" or w in PERSON_WORDS or t.lemma_.lower() in PERSON_WORDS or (t.pos_ == "NOUN" and re.search(r"(er|or|ist|man|men)$", w)):
            seen_here.add("person")
        if w in THIRD:
            pronouns.append(w)
            if "person" not in known and "person" not in seen_here:
                flags.append(f"unresolved_pronoun:{w}")
        elif w == "it" and t.dep_ in ("dobj", "obj", "nsubj") and not (known or (seen_here - {"person"})):
            weak.append("weak_it")
    persons = {"person"} if any(t.pos_ == "PROPN" or t.lemma_.lower() in PERSON_WORDS or t.text.lower() in PERSON_WORDS
                                 or (t.pos_ == "NOUN" and re.search(r"(er|or|ist|man|men)$", t.text.lower())) for t in toks) else set()
    return {"kind": kind, "flags": flags, "weak": weak, "nouns": [t.lemma_.lower() for t in nouns] + sorted(persons), "pronouns": pronouns}


def analyse_run(bars: Iterable[str], context: Iterable[str] = ()) -> list[dict]:
    """per bar analysis of `bars`; the antecedent registry accumulates across `context` (earlier bars of the same run/section)
    and then the bars themselves (plan: 'every pronoun needs an antecedent in the same run'). Only `bars` are returned."""
    context, bars = list(context), list(bars)
    docs = list(nlp().pipe(context + bars))
    known: set[str] = set()
    out = []
    for k, (text, doc) in enumerate(zip(context + bars, docs)):
        r = analyse_doc(doc, known)
        r["text"] = text
        known |= set(r["nouns"])
        if k >= len(context):
            out.append(r)
    return out


def passes(bars: Iterable[str]) -> bool:
    return not any(r["flags"] for r in analyse_run(bars))


def flagged_bars(bars: Iterable[str]) -> list[tuple[int, str, list[str]]]:
    return [(i, r["text"], r["flags"]) for i, r in enumerate(analyse_run(bars)) if r["flags"]]


def clause_share(bars: Iterable[str]) -> float:
    rs = analyse_run(bars)
    return sum(1 for r in rs if r["kind"] in ("clause", "elided", "participle")) / len(rs) if rs else 0.0


def selftest() -> tuple[bool, str]:
    problems: list[str] = []
    good = analyse_run(["I went to Rome on a plane", "Stepped out in Spanish leather", "Then he paid the man fifty quid"])
    if any(r["flags"] for r in good):
        problems.append(f"fluent bars flagged: {[(r['text'], r['flags']) for r in good if r['flags']]}")
    bad = analyse_run(["Money in the wallet and forty"]) + analyse_run(["Paid packed gone the way"]) + analyse_run(["Copper at the door caught"])         + analyse_run(["Taped him up and boxed him then strapped him in"])
    for r, need in zip(bad, ("(weak)", "verb_string", "transitive_without_object", "unresolved_pronoun")):
        if need == "(weak)":
            if "bare_numeral_end" not in r["weak"]:
                problems.append("bare numeral end should be reported as weak")
            continue
        if not any(f.startswith(need) for f in r["flags"]):
            problems.append(f"'{r['text']}' should raise {need}, got {r['flags']}")
    resolved = analyse_run(["The driver shut the van door", "Then he strapped him in"])
    if any(f.startswith("unresolved_pronoun") for r in resolved for f in r["flags"]):
        problems.append("pronoun with an antecedent in the run was flagged")
    return (not problems, "; ".join(problems) if problems else "fluent bars pass; noun stacks, bare numerals and unintroduced pronouns are flagged")
