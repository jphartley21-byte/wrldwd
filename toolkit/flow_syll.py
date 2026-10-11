"""flow_syll: measure the original's SYLLABLE timings (letter-level alignment) on a 48-step bar grid
(12 steps per beat = sixteenths AND triplets), detect triplet runs, and add them to benchmark/flow_template.json.
Run in the 'flow' env:  python toolkit/flow_syll.py AUDIO LYRICS_TXT   (lyrics file kept outside the project)
"""
import difflib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "benchmark", "flow_template.json")
WORK = os.path.join(os.environ.get("TEMP", "/tmp"), "flow_work")


def main(audio, lyrics):
    import librosa, numpy as np, torch, whisperx
    stem = os.path.join(WORK, "htdemucs", os.path.splitext(os.path.basename(audio))[0])
    cache = os.path.join(stem, "chars.json")
    if os.path.exists(cache):
        words = json.load(open(cache))
    else:
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        a = librosa.load(os.path.join(stem, "vocals.wav"), sr=16000)[0].astype(np.float32)
        m = whisperx.load_model("large-v3", dev, compute_type="float16", language="en")
        res = m.transcribe(a, batch_size=16, language="en")
        am, meta = whisperx.load_align_model(language_code="en", device=dev)
        res = whisperx.align(res["segments"], am, meta, a, dev, return_char_alignments=True)
        words = []
        for s in res["segments"]:
            chars = s.get("chars", [])
            for w in s.get("words", []):
                if w.get("start") is None:
                    continue
                cs = [(c["char"], c.get("start")) for c in chars if c.get("start") is not None and w["start"] - 0.01 <= c["start"] <= w["end"] + 0.01]
                words.append({"w": w["word"], "start": w["start"], "end": w["end"], "chars": cs})
        json.dump(words, open(cache, "w"))
    y, sr = librosa.load(os.path.join(stem, "no_vocals.wav"), sr=22050)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, bpm=140, tightness=1000, units="time")
    beats = np.asarray(beats)
    T = json.load(open(OUT))
    phase = T["phase"]
    lines = [l.strip() for l in open(lyrics, encoding="utf8") if l.strip()]
    lw = [(i, w) for i, l in enumerate(lines) for w in re.findall(r"[A-Za-z']+", l)]
    norm = lambda w: re.sub(r"[^a-z]", "", w.lower())
    sm = difflib.SequenceMatcher(None, [norm(w) for _, w in lw], [norm(x["w"]) for x in words], autojunk=False)
    hit = {}
    for a0, b0, n in sm.get_matching_blocks():
        for k in range(n):
            hit[a0 + k] = words[b0 + k]
    def beat_pos(t):  # fractional beat index
        i = int(np.searchsorted(beats, t)) - 1
        i = max(0, min(i, len(beats) - 2))
        return i + (t - beats[i]) / (beats[i + 1] - beats[i])
    for li in range(len(lines)):
        onsets = []
        for k, (l, w) in enumerate(lw):
            if l != li or k not in hit:
                continue
            x = hit[k]
            # syllable onsets: first char of each vowel group in the heard word
            prev_v, got = False, []
            for ch, t in x["chars"]:
                v = ch.lower() in "aeiouy"
                if v and not prev_v:
                    got.append(t)
                prev_v = v
            onsets += got or [x["start"]]
        bar = T["bars"][li]
        if len(onsets) < 3 or bar.get("missing"):
            bar["triplets"] = []
            continue
        bp = [beat_pos(t) for t in onsets]
        b0 = int(bp[0]) - ((int(bp[0]) - phase) % 4)
        bar["steps48"] = [int(round((p - b0) * 12)) for p in bp]
        trip = []
        for i in range(len(bp) - 2):
            g1, g2 = bp[i + 1] - bp[i], bp[i + 2] - bp[i + 1]
            for unit in (1 / 3, 2 / 3):
                if abs(g1 - unit) < 0.07 and abs(g2 - unit) < 0.07:
                    trip.append(i)
        bar["triplets"] = sorted(set(trip))
    n = len(lines)
    for i in range(16):  # chorus 1 copied from chorus 2 if unheard
        a0, b0 = T["bars"][i], T["bars"][n - 16 + i]
        if not a0.get("triplets") and b0.get("triplets"):
            a0["triplets"], a0["steps48"] = b0["triplets"], b0.get("steps48")
    json.dump(T, open(OUT, "w"), indent=0)
    print("bars with triplets:", [b["bar"] for b in T["bars"] if b.get("triplets")])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
