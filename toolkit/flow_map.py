"""flow_map: measure the ORIGINAL's real flow from audio, bar by bar, on a 16-step grid.
Run in the 'flow' conda env (torch + demucs + whisperx + librosa):
  conda activate flow
  python toolkit/flow_map.py build AUDIO_FILE LYRICS_TXT     # LYRICS_TXT: original lines, one per bar, outside the project (e.g. Desktop); never saved here
  python toolkit/flow_map.py show                            # print the templates (positions only)
Output: benchmark/flow_template.json = per bar: syllable count, the 16th-note step of every syllable onset,
which steps fall on beats, and pauses. Numbers only, no lyric text (CLAUDE.md rule 4).
"""
import difflib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "benchmark", "flow_template.json")
WORK = os.path.join(os.environ.get("TEMP", "/tmp"), "flow_work")


def syl(word):
    sys.path.insert(0, HERE)
    from rhyme_tools import pron, is_v
    p = pron(re.sub(r"[^a-z']", "", word.lower()))
    if p:
        return max(1, sum(1 for x in p if is_v(x)))
    if word.isupper() and len(word) > 1:
        return sum(3 if c == "W" else 1 for c in word)
    return max(1, len(re.findall(r"[aeiouy]+", word.lower().rstrip("e"))))


def build(audio, lyrics_txt):
    import librosa, numpy as np, torch, whisperx
    os.makedirs(WORK, exist_ok=True)
    # 1. separate vocals
    stem = os.path.join(WORK, "htdemucs", os.path.splitext(os.path.basename(audio))[0])
    if not os.path.exists(os.path.join(stem, "vocals.wav")):
        subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-o", WORK, audio], check=True)
    vocals, band = os.path.join(stem, "vocals.wav"), os.path.join(stem, "no_vocals.wav")
    # 2. beat grid from the instrumental
    y, sr = librosa.load(band, sr=22050)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, bpm=140, tightness=1000, units="time")
    beats = np.asarray(beats)
    # 3. word timings from the vocal
    cache = os.path.join(stem, "words.json")
    if os.path.exists(cache):
        heard = json.load(open(cache))
    else:
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisperx.load_model("large-v3", dev, compute_type="float16" if dev == "cuda" else "int8", language="en")
        audio_v = librosa.load(vocals, sr=16000)[0].astype(np.float32)  # avoids whisperx's ffmpeg call
        res = model.transcribe(audio_v, batch_size=16, language="en")
        amodel, meta = whisperx.load_align_model(language_code="en", device=dev)
        res = whisperx.align(res["segments"], amodel, meta, audio_v, dev)
        heard = [(w["word"], w.get("start")) for s in res["segments"] for w in s.get("words", []) if w.get("start") is not None]
        json.dump(heard, open(cache, "w"))
    # 4. map heard words onto the known lyric lines
    lines = [l.strip() for l in open(lyrics_txt, encoding="utf8") if l.strip()]
    lw = [(i, w) for i, l in enumerate(lines) for w in re.findall(r"[A-Za-z']+", l)]
    norm = lambda w: re.sub(r"[^a-z]", "", w.lower())
    sm = difflib.SequenceMatcher(None, [norm(w) for _, w in lw], [norm(w) for w, _ in heard], autojunk=False)
    t_of = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            t_of[a + k] = heard[b + k][1]
    # 5. sixteenth grid and bar phase (4 beats per bar; phase = best fit for line starts)
    sixteenths = np.concatenate([np.linspace(beats[i], beats[i + 1], 5)[:-1] for i in range(len(beats) - 1)])
    first_t = {}
    for idx, (li, _) in enumerate(lw):
        if idx in t_of and li not in first_t:
            first_t[li] = t_of[idx]
    def bar_start_index(t, phase):
        bi = int(np.searchsorted(beats, t + 0.12)) - 1
        return bi - ((bi - phase) % 4)
    best = max(range(4), key=lambda ph: sum(1 for t in first_t.values() if abs(beats[bar_start_index(t, ph)] - t) < 0.6 * (beats[1] - beats[0]) * 4))
    out = []
    for li, line in enumerate(lines):
        idxs = [k for k, (l, _) in enumerate(lw) if l == li]
        times = [t_of.get(k) for k in idxs]
        known = [t for t in times if t is not None]
        if not known:
            out.append({"bar": li + 1, "missing": True}); continue
        b0 = bar_start_index(known[0] + 0.15, best)
        s0 = b0 * 4
        steps = []
        for k, t in zip(idxs, times):
            n = syl(lw[k][1])
            if t is None:
                steps += [None] * n; continue
            st = int(np.argmin(np.abs(sixteenths - t))) - s0
            steps += [st] + [None] * (n - 1)
        # fill multi-syllable gaps evenly up to the next known onset
        for i, s in enumerate(steps):
            if s is None:
                prev = next((steps[j] for j in range(i - 1, -1, -1) if steps[j] is not None), 0)
                nxt = next((steps[j] for j in range(i + 1, len(steps)) if steps[j] is not None), prev + 2)
                steps[i] = prev + max(1, (nxt - prev) // 2)
        out.append({"bar": li + 1, "syl": len(steps), "steps": steps, "on_beat": [s for s in steps if s % 4 == 0],
                    "bars_spanned": (max(steps) // 16) + 1, "pickup": min(steps) < 0})
    # the chorus repeats word for word: fill unheard chorus bars from the other chorus
    n = len(out)
    for i in range(16):
        a, b = i, n - 16 + i
        if out[a].get("missing") and not out[b].get("missing"):
            out[a] = dict(out[b], bar=a + 1, copied_from=b + 1)
        elif out[b].get("missing") and not out[a].get("missing"):
            out[b] = dict(out[a], bar=b + 1, copied_from=a + 1)
    json.dump({"tempo": float(np.atleast_1d(tempo)[0]), "phase": best, "bars": out}, open(OUT, "w"), indent=0)
    print("tempo", float(np.atleast_1d(tempo)[0]), "bars", len(out), "->", OUT)


def show():
    d = json.load(open(OUT))
    print("tempo", round(d["tempo"], 1))
    for b in d["bars"]:
        if b.get("missing"):
            print(f"{b['bar']:>2}. (not heard)"); continue
        grid = ["."] * 16 * b["bars_spanned"]
        for s in b["steps"]:
            if 0 <= s < len(grid):
                grid[s] = "X" if s % 4 == 0 else "x"
        print(f"{b['bar']:>2}. {b['syl']:>2}syl {''.join(grid)}{'  (pickup)' if b['pickup'] else ''}")


if __name__ == "__main__":
    {"build": lambda: build(sys.argv[2], sys.argv[3]), "show": show}[sys.argv[1]]()
