"""calibrate: run BEFORE trusting match.py / flow_fit.py after any change.
  python toolkit/calibrate.py ORIG_LINES_TXT   (original lyric lines, kept outside the project)
Must show: the original passes its own form profile in every slot and >= 66/76 bars of its flow templates;
every Joe-rejected stanza in toolkit/tests/rejected_*.txt (first line '# SLOT START') FAILS.
"""
import glob, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
SECS = [("Hook 1-4", 0, 4), ("Hook 5-8", 4, 8), ("Hook 9-16", 8, 16), ("V1 1-8", 16, 24), ("V1 9-16", 24, 32), ("V1 17-24", 32, 40), ("V1 25-32", 40, 48), ("V1 33-44", 48, 60), ("V2 1-8", 60, 68), ("V2 9-16", 68, 76)]
run = lambda args, text: subprocess.run([sys.executable] + args, input=text, capture_output=True, text=True, encoding="utf8").stdout
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
locked = ["Oh, bonjourno", "Front row at the on-stage porno", "Damn good show but the dame look bored, though", "So boarded a plane out to Bordeaux"]
v = run([os.path.join(HERE, "match.py"), "--slot", "Hook 1-4", "-"], chr(10).join(locked))
good = "original rhyme scheme AAAA (by ear): PASS" in v
ok &= good
print(("ok  " if good else "BAD ") + "Joe's locked bars 1-4 pass the by-ear scheme")
print("CALIBRATION", "PASSED" if ok else "FAILED: fix the tools before using them")
