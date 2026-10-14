"""blockcheck: one compact line per bar so a block can be iterated quickly.

  python toolkit/blockcheck.py --slot "Hook 9-16" -        (stdin: our bars)
  python toolkit/blockcheck.py --slot "Hook 9-16" file.md

Prints, per bar: counted syllables vs the original's frame, our end word and end sound vs the frame's,
and whether the bar rhymes with every partner the BY-EAR scheme pairs it with. This is a VIEW over the
same counters check_all uses (flow_fit.sylls and the profile in benchmark/original_profile.json); it adds
no new measurement of its own, so it can never disagree with the gates.
"""
import json, os, subprocess, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forge                        # noqa: E402
import match as mt                  # noqa: E402
import rhyme_tools as rt            # noqa: E402

PROFILE = os.path.join(HERE, "..", "benchmark", "original_profile.json")


def main():
    slot = sys.argv[sys.argv.index("--slot") + 1]
    src = sys.argv[-1] if sys.argv[-1] != "--slot" else "-"
    text = sys.stdin.read() if src in ("-", "--slot") else open(src, encoding="utf8").read()
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith(("|", "#", "`", "=="))]
    fr = forge.slot_frame(slot)
    P = json.load(open(PROFILE, encoding="utf8"))[slot]
    ms = mt.MANUAL_SCHEME.get(slot, "")
    if len(lines) != fr["n"]:
        print(f"!! {len(lines)} bars but the slot has {fr['n']}")
        return
    keys, pairs = {}, {}
    for i, l in enumerate(lines):
        syl = len(forge.ff.sylls(l))
        want = fr["syls"][i]
        ends = mt._k(l)
        keys[i] = ends
        frame_end = "".join(P["keys"][i][0]) if P["keys"][i] else "?"
        shape = fr["shapes"][i]
        ours = "-".join(ends[0]) if ends else "?"
        flag = "" if want is None or abs(syl - want) <= 1 else "  <-- SYLLABLES"
        if want is not None and syl != want:
            flag += f" ({syl - want:+d})"
        print(f"{i + 1:>2}. {syl:>2}syl (frame {str(want):>4})  end {ours:<10} (frame {frame_end:<8}) {shape}  {l}{flag}")
    if ms:
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                if ms[i] != ms[j]:
                    continue
                sc = mt.best_end(lines[i], lines[j])
                ok = "ok " if sc >= 0.78 else "XX "
                pairs[f"{i + 1}-{j + 1}"] = sc
                print(f"   {ok}{ms[i]} pair {i + 1}-{j + 1}: {sc:.2f}")
    weak = [k for k, v in pairs.items() if v < 0.78]
    print(f"scheme {ms}: {'ALL PAIRS RHYME' if not weak else 'BROKEN: ' + ', '.join(weak)}")


if __name__ == "__main__":
    main()
