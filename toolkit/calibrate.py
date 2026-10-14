"""calibrate: run BEFORE trusting match.py / flow_fit.py after any change.
  python toolkit/calibrate.py ORIG_LINES_TXT   (original lyric lines, kept outside the project)
Must show: the original passes its own form profile in every slot and >= 66/76 bars of its flow templates;
every Joe-rejected stanza in toolkit/tests/rejected_*.txt (first line '# SLOT START') FAILS.
"""
import glob, subprocess, sys, os
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # a failing check prints IPA; cp1252 would
#                                                           # crash the harness instead of reporting it
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fixtures  # noqa: E402
SECS = [("Hook 1-4", 0, 4), ("Hook 5-8", 4, 8), ("Hook 9-16", 8, 16), ("V1 1-8", 16, 24), ("V1 9-16", 24, 32), ("V1 17-24", 32, 40), ("V1 25-32", 40, 48), ("V1 33-44", 48, 60), ("V2 1-8", 60, 68), ("V2 9-16", 68, 76)]
run = lambda args, text: subprocess.run([sys.executable] + args, input=text, capture_output=True, text=True, encoding="utf8", errors="replace").stdout
orig = [l.strip() for l in open(sys.argv[1], encoding="utf8") if l.strip()][:76]
ok = True
for n, a, b in SECS:
    out = run([os.path.join(HERE, "match.py"), "--slot", n, "-"], chr(10).join(orig[a:b])).splitlines()
    bad = [l for l in out if "FAIL" in l and not l.startswith("original rhyme scheme")]; good = not bad; v = "ok (by-ear scheme is the spec)" if good else "; ".join(bad)[:120]
    ok &= good
    print(("ok  " if good else "BAD ") + f"original vs own profile {n}: {v}")
f = run([os.path.join(HERE, "flow_fit.py"), "1", "-"], "\n".join(orig))
passes = sum(1 for l in f.splitlines() if " PASS |" in l)
ok &= passes >= 66
print(("ok  " if passes >= 66 else "BAD ") + f"original vs own flow templates: {passes}/76")
for path in glob.glob(os.path.join(HERE, "tests", "rejected_*.txt")):
    lines = [l.strip() for l in open(path, encoding="utf8") if l.strip()]
    slot, start = lines[0][2:].rsplit(" ", 1)
    m = [l for l in run([os.path.join(HERE, "match.py"), "--slot", slot, "-"], "\n".join(lines[1:])).splitlines() if l.startswith("VERDICT")][0]
    fl = [l for l in run([os.path.join(HERE, "flow_fit.py"), start, "-"], "\n".join(lines[1:])).splitlines() if l.startswith("VERDICT")][0]
    caught = "NOT YET" in m or "NOT YET" in fl
    ok &= caught
    print(("ok  " if caught else "BAD ") + f"Joe-rejected {os.path.basename(path)} is caught: form {m[9:30]} / flow {fl[9:30]}")
# Joe-approved bars must pass the by-ear scheme
locked = fixtures.joe_bars()
v = run([os.path.join(HERE, "match.py"), "--slot", "Hook 1-4", "-"], chr(10).join(locked))
good = "original rhyme scheme AAAA (by ear): PASS" in v
ok &= good
print(("ok  " if good else "BAD ") + "Joe's locked bars 1-4 pass the by-ear scheme")
# the meaning gate must pass Joe's locked bars and catch a known-bad stanza
mg = run([os.path.join(HERE, "meaning_gate.py"), "--selftest"], "")
good = "PASSED" in mg
ok &= good
print(("ok  " if good else "BAD ") + "meaning_gate selftest: " +
      ("passes locked bars, catches a known-bad stanza" if good else mg.strip()[:110]))
# the rhyme verdicts measured by ear must still hold (12 cases, 1 documented metric limit)
rp = run([os.path.join(HERE, "match.py"), "--selftest"], "")
good = "PASSED" in rp
ok &= good
print(("ok  " if good else "BAD ") + "rhyme verdicts by ear: " +
      ("all 12 asserted pairs hold, 1 unspecified" if good else rp.strip().splitlines()[-1][:110]))
# the vocab ledger must separate common from obscure (gate G2) and upsert cleanly
vg = run([os.path.join(HERE, "vocab.py"), "--selftest"], "")
good = "PASSED" in vg
ok &= good
print(("ok  " if good else "BAD ") + "vocab ledger selftest: " +
      ("G2 separates common from obscure, upsert and filter hold" if good else vg.strip()[:110]))
# the fast inner loop must parse candidate blocks and memoise the form check
tb = run([os.path.join(HERE, "trybars.py"), "--selftest"], "")
good = "PASSED" in tb
ok &= good
print(("ok  " if good else "BAD ") + "trybars selftest: " +
      ("block parsing, tail families and the form memo hold" if good else tb.strip()[:110]))
# the search tool: pool parsing, the scheme test and the world counter (it must never silently pass)
tf = run([os.path.join(HERE, "tryforms.py"), "--selftest"], "")
good = "PASSED" in tf
ok &= good
print(("ok  " if good else "BAD ") + "tryforms selftest: " +
      ("pool parsing, scheme pairs and the wrong-length guard hold" if good else tf.strip()[:110]))
# the writer's supply: phrases must load and resolve to sounds, and the UK list must hold
bk = run([os.path.join(HERE, "bank.py"), "--selftest"], "")
good = "PASSED" in bk
ok &= good
print(("ok  " if good else "BAD ") + "bank selftest: " +
      ("phrases resolve to end sounds and the UK everyday list holds" if good else bk.strip()[:110]))
# Joe's character rule (13 Oct 2026): at most two references to any one character, partners and mates preferred over
# family. Deliberately NOT asserted against the original -- the original's largest count is 4 ("mate"), so the cap is
# stricter than the benchmark and is a rule, not a calibration. The tool's own selftest is asserted here.
ch = run([os.path.join(HERE, "characters.py"), "--selftest"], "")
good = "ok" in ch.strip()[:4]
ok &= good
print(("ok  " if good else "BAD ") + "characters selftest: " +
      ("cap of 2 per character, family preference, possessive and substring handling" if good else ch.strip()[:110]))
# the Phase-A end-word tool: grouping (a complete carpet is one group), the shape/budget filter and the
# clique search must all hold, because every section is written onto a set it proposes
cp = run([os.path.join(HERE, "carpet.py"), "--selftest"], "")
good = "PASSED" in cp
ok &= good
print(("ok  " if good else "BAD ") + "carpet selftest: " +
      ("grouping, shape/budget filtering and the clique search hold" if good else cp.strip()[-110:]))
# the SONG-level repetition guard: the assembled song came out with 8 bars opening "Might" and a repeated
# line because nothing looked across sections. Its thresholds are calibrated so the original PASSES
# (its chorus returns and it opens 12 bars with "I"), and its fixtures prove it still catches the crutches.
pa = run([os.path.join(HERE, "phrase_audit.py"), "--selftest"], "")
good = "PASSED" in pa
ok &= good
print(("ok  " if good else "BAD ") + "phrase_audit selftest: " +
      ("duplicates, repeated openers, repeated phrases and the comma rate are all caught"
       if good else pa.strip()[-110:]))
cal = run([os.path.join(HERE, "phrase_audit.py"), "--calibrate", sys.argv[1]], "")
good = "CALIBRATION: PASSED" in cal
ok &= good
print(("ok  " if good else "BAD ") + "phrase_audit vs the original: " +
      ("the original clears every repetition threshold (its chorus repeat is exempt by design)"
       if good else cal.strip()[-110:]))
# report-only craft readouts (voice, company, stock phrases in the rhyme slot). Selftest only: they rank nothing.
cr = run([os.path.join(HERE, "craft_readouts.py"), "--selftest"], "")
good = "PASSED" in cr
ok &= good
print(("ok  " if good else "BAD ") + "craft_readouts selftest: " +
      ("voice share, company per window and rhyme-slot stock phrases are counted" if good else cr.strip()[-110:]))
# the loaded-word reservoir's ranking rules (hermetic; the slot offers are a report, not a calibration)
rs = run([os.path.join(HERE, "reservoir.py"), "--selftest"], "")
good = "PASSED" in rs
ok &= good
print(("ok  " if good else "BAD ") + "reservoir selftest: " +
      ("loaded words lead, the commonest trail, rare words are held back" if good else rs.strip()[-110:]))
# the meaning judge's PARSER and VERDICT RULE only. The model call is deliberately not calibrated: a
# calibration that needs a GPU is not a calibration. The measured accuracy of the model lives in STATE.md.
mj = run([os.path.join(os.path.dirname(HERE), "ml", "meaning_judge.py"), "--selftest"], "")
good = "PASSED" in mj
ok &= good
print(("ok  " if good else "BAD ") + "meaning_judge selftest: " +
      ("the parser reads fenced, padded and string kinds and the verdict rule rejects lists"
       if good else mj.strip()[-110:]))
# the INVENTORY rule is the meaning gate's only claim-detector, so its quietness on the ORIGINAL is
# asserted every run: the 13 Oct 2026 tightening made it fire on two more of Joe's rejected bars, and
# this is the check that says it still fires on none of the original's.
mc = run([os.path.join(HERE, "meaning_gate.py"), "--calibrate", sys.argv[1]], "")
good = "CALIBRATION: PASSED" in mc
ok &= good
print(("ok  " if good else "BAD ") + "meaning_gate inventory rule vs the original: " +
      ("fires on none of the original's lines" if good else mc.strip()[-110:]))
# the figures of speech must fire on their own fixtures and stay quiet on plain reportage
dvc = run([os.path.join(HERE, "devices.py"), "--selftest"], "")
good = "PASSED" in dvc
ok &= good
print(("ok  " if good else "BAD ") + "devices selftest: " +
      ("simile/metaphor/bathos/litotes/hyperbole/anaphora fire on fixtures, quiet on reportage"
       if good else dvc.strip()[:110]))
# the regression gates must separate Joe's approved bars from the weak blocks (12 Oct): local word per
# four bars, no admin word in a rhyme slot, no content word used more than three times
rg = run([os.path.join(HERE, "regression.py"), "--selftest"], "")
good = "PASSED" in rg and "DISCRIMINATION: PASSED" in rg
ok &= good
print(("ok  " if good else "BAD ") + "regression gates selftest: " +
      ("approved bars pass all three, both weak blocks fail at least one" if good else rg.strip()[-110:]))
# the level-allocated song gates must be TRUE OF THE ORIGINAL: a gate the benchmark fails is a wrong gate.
# This is what corrected four gates on 12 Oct (local words moved to hook level, the cashed-tally exception,
# the place and long-bar tests moved off the section level, and the rhyme-pair demand now needs both the
# by-ear scheme and the original's own keys to agree).
sc = run([os.path.join(HERE, "songcheck.py"), "--original", sys.argv[1], "--title", "Mr. Worldwide"], "")
good = "SONGCHECK: PASS" in sc
ok &= good
print(("ok  " if good else "BAD ") + "level gates (line/quad/verse/hook/song) hold on the original: " +
      ("all levels PASS" if good else sc.strip().splitlines()[-1][:110]))
# the sound devices Joe hears (doctor 12 Oct): a pivot word and a consonant-frame drum must be detected, and
# a repeated word must be caught as a crutch rather than counted as a device
er = run([os.path.join(HERE, "ear.py"), "--selftest"], "")
good = "EAR SELFTEST: PASSED" in er
ok &= good
print(("ok  " if good else "BAD ") + "ear devices (pivot / drum / echo / crutch): " +
      ("the original's couplet fires both, Joe's bars carry a device and no crutch, our filler is caught"
       if good else er.strip()[-110:]))
# the image-chain detector must find a chain that lands on the rhyme, and must not fire on flat bars
im = run([os.path.join(HERE, "imagery.py"), "--selftest"], "")
good = "IMAGERY SELFTEST: PASSED" in im
ok &= good
print(("ok  " if good else "BAD ") + "image chains (develop + land on the rhyme, bridge words): " +
      ("a chain that lands is found, flat bars stay quiet, a two-field word reads as a bridge"
       if good else im.strip()[-110:]))
# the pun/wordplay proxy must load and must not overclaim (it prints its own base rate)
fn = run([os.path.join(HERE, "funny.py"), "--selftest"], "")
good = "PASSED" in fn
ok &= good
print(("ok  " if good else "BAD ") + "pun proxy selftest: " +
      ("unexpectedness and second-reading lookups hold" if good else fn.strip()[:110]))
print("CALIBRATION", "PASSED" if ok else "FAILED: fix the tools before using them")
