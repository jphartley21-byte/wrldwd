"""bank: exhaustive, scripted banks of rhymes + sound-alike wordplay, plus query and an offline HTML browser. ADVISORY.
  python toolkit/bank.py build            # (re)generate bank/rhymes.csv and bank/wordplay_soundalikes.csv from bank/seeds.csv
  python toolkit/bank.py stats            # row counts per bank file and type
  python toolkit/bank.py find [--q TEXT] [--type T] [--place P] [--rhymes WORD] [--joe y|n|blank] [--bank FILE] [--max N]
  python toolkit/bank.py export-html      # writes bank/index.html (offline, searchable, filterable)
Schema (all bank/*.csv): id,type,text,items,sound,places,tags,source,joe_says_it,status
 - text = the headword/phrase; items = '; '-separated candidates/explanation; joe_says_it = y/n/blank (voice/quiz.md)
Other banks (idioms, slang, names, places, events) are plain CSVs in the same schema, appended by /bank and /research.
"""
import argparse, collections, contextlib, csv, glob, html, io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
BANK = os.path.join(ROOT, "bank")
sys.path.insert(0, HERE)
FIELDS = ["id", "type", "text", "items", "sound", "places", "tags", "source", "joe_says_it", "status"]


def load_rt():
    import rhyme_tools as R
    for line in open(os.path.join(BANK, "ovr.txt"), encoding="utf8"):
        if line.strip() and not line.startswith("#"):
            w, p = line.rstrip("\n").split("\t")
            R.OVR[w] = p
    R._IDX.clear()
    return R


def common(words, zmin=3.0):
    from wordfreq import zipf_frequency
    return [w for w in words if zipf_frequency(w, "en") >= zmin]


def freq_sort(words):
    from wordfreq import zipf_frequency
    return sorted(set(words), key=lambda w: (-zipf_frequency(w, "en"), len(w), w))


def seeds():
    return list(csv.DictReader(open(os.path.join(BANK, "seeds.csv"), encoding="utf8")))


def write(name, rows):
    path = os.path.join(BANK, name)
    with open(path, "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            r = {k: r.get(k, "") for k in FIELDS}
            r["id"] = f"{os.path.splitext(name)[0][:3]}{i}"
            w.writerow(r)
    return len(rows)


def build():
    R = load_rt()
    rhyme_rows, play_rows = [], []
    for s in seeds():
        term, kind = s["term"], s["kind"]
        ph, bad = R.pron_phrase(term)
        if ph is None:
            print("skip (no pronunciation):", term, bad)
            continue
        tags = ";".join(x for x in (kind, s["region"], "trip" if s["joe_trip"] == "y" else "") if x)
        src = s["note"] or "seed"
        sound = "-".join(R.key(ph, 0) or [])
        for mode, n, typ in (("perfect", 0, "rhyme_perfect"), ("near", 0, "rhyme_near"), ("assonance", 2, "rhyme_assonance_2syl"), ("perfect", 2, "rhyme_multi_2syl"), ("perfect", 3, "rhyme_multi_3syl")):
            kk = R.key(ph, n, mode)
            if not kk:
                continue
            ws = [w for w in R.index(n, mode).get(kk, []) if w != term.lower().replace(" ", "")]
            ws = freq_sort(common(ws, 2.8 if typ != "rhyme_perfect" else 2.5))
            if ws:
                rhyme_rows.append(dict(type=typ, text=term, items="; ".join(ws[:60]), sound="-".join(kk), places=term if kind == "place" else "", tags=tags, source=src))
        # sound-alike cut-ups (mosaic) for 1-3 syllable tails
        for nsyl in (2, 3):
            if R.nsyl(ph) < nsyl:
                continue
            ns = argparse.Namespace(text=term.lower(), nsyl=nsyl, loose=False, words=3, max=40)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    R.cmd_mosaic(ns)
                except Exception as e:
                    print("ERR", e)
            out = buf.getvalue().splitlines()
            if len(out) > 1 and not out[1].startswith("ERR") and out[1].strip():
                cuts = [c.strip() for c in out[1].split(";") if c.strip()]
                cuts = [c for c in cuts if all(w in common([w], 2.3) or len(w) <= 2 for w in c.split())][:30]
                if cuts:
                    play_rows.append(dict(type=f"soundalike_{nsyl}syl", text=term, items="; ".join(cuts), sound=out[0][:60], places=term if kind == "place" else "", tags=tags, source="mosaic (check by ear)", status="to check"))
    print("rhymes.csv", write("rhymes.csv", rhyme_rows), "rows; wordplay_soundalikes.csv", write("wordplay_soundalikes.csv", play_rows), "rows")


def all_rows():
    for p in sorted(glob.glob(os.path.join(BANK, "*.csv"))):
        if os.path.basename(p) == "seeds.csv":
            continue
        for r in csv.DictReader(open(p, encoding="utf8")):
            r["bank"] = os.path.basename(p)
            yield r


def stats():
    c = collections.Counter()
    items = 0
    for r in all_rows():
        c[(r["bank"], r.get("type", ""))] += 1
        items += len([x for x in (r.get("items") or "").split(";") if x.strip()])
    for (b, t), n in sorted(c.items()):
        print(f"{b:34} {t:24} {n}")
    print("rows:", sum(c.values()), "| individual items (words/phrases inside rows):", items)


def find(a):
    n = 0
    for r in all_rows():
        blob = " ".join(str(r.get(k, "")) for k in FIELDS).lower()
        if a.q and a.q.lower() not in blob: continue
        if a.type and a.type not in r.get("type", ""): continue
        if a.place and a.place.lower() not in (r.get("places", "") + " " + r.get("text", "")).lower(): continue
        if a.rhymes and a.rhymes.lower() not in blob: continue
        if a.joe and (r.get("joe_says_it", "") or "blank") != a.joe: continue
        if a.bank and a.bank not in r["bank"]: continue
        print(f"[{r['bank']}] {r.get('type','')} | {r.get('text','')} | {(r.get('items') or '')[:200]} | {r.get('tags','')}")
        n += 1
        if n >= a.max: break
    print(f"({n} shown)")


def export_html():
    rows = list(all_rows())
    data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Worldwide bank</title>
<style>:root{--bg:#fff;--fg:#1b1b1b;--mu:#666;--bd:#ddd;--ac:#0b6;--st:#e8a200}@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mu:#9a9a9a;--bd:#333;--ac:#3c9;--st:#ffc43d}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif}header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--bd);padding:10px 16px}
input,select,button{font:inherit;padding:6px;margin:3px 4px 3px 0;border:1px solid var(--bd);border-radius:6px;background:var(--bg);color:var(--fg)}main{padding:8px 16px 60px}
.r{border-bottom:1px solid var(--bd);padding:8px 0}.t{font-weight:600}.m{color:var(--mu);font-size:12px}.i{margin-top:2px;overflow-wrap:anywhere}.s{cursor:pointer;color:var(--mu);border:0;background:none;font-size:18px}.s.on{color:var(--st)}
</style></head><body><header><b>Worldwide bank</b> <span class="m" id="n"></span><br>
<input id="q" placeholder="search any text, sound, place" size="26"> <select id="b"></select> <select id="ty"></select> <select id="j"><option value="">Joe says it? any</option><option>y</option><option>n</option><option>blank</option></select>
<label><input type="checkbox" id="st"> starred only</label> <button id="ex">Copy my stars</button></header><main id="o"></main>
<script>const D=__DATA__;let S={};try{S=JSON.parse(localStorage.getItem('stars')||'{}')}catch(e){}
const $=id=>document.getElementById(id);const uniq=k=>[...new Set(D.map(r=>r[k]))].sort();
function fill(id,k,lbl){$(id).innerHTML='<option value="">'+lbl+'</option>'+uniq(k).map(v=>'<option>'+v+'</option>').join('')}fill('b','bank','all banks');fill('ty','type','all types');
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function key(r){return r.bank+':'+r.id}
function draw(){const q=$('q').value.toLowerCase(),b=$('b').value,t=$('ty').value,j=$('j').value,so=$('st').checked;let n=0,h='';
for(const r of D){if(b&&r.bank!==b)continue;if(t&&r.type!==t)continue;if(j&&(r.joe_says_it||'blank')!==j)continue;if(so&&!S[key(r)])continue;
const blob=(r.text+' '+r.items+' '+r.sound+' '+r.places+' '+r.tags).toLowerCase();if(q&&!blob.includes(q))continue;n++;if(n>300)continue;
h+='<div class="r"><button class="s '+(S[key(r)]?'on':'')+'" data-k="'+key(r)+'">'+(S[key(r)]?'★':'☆')+'</button> <span class="t">'+esc(r.text)+'</span> <span class="m">'+esc(r.type)+' · '+esc(r.sound)+' · '+esc(r.tags)+(r.status?' · '+esc(r.status):'')+'</span><div class="i">'+esc(r.items)+'</div></div>'}
$('o').innerHTML=h;$('n').textContent=n+' matches'+(n>300?' (first 300 shown, refine search)':'')}
document.addEventListener('click',e=>{const k=e.target.dataset&&e.target.dataset.k;if(k){S[k]?delete S[k]:S[k]=1;try{localStorage.setItem('stars',JSON.stringify(S))}catch(x){}draw()}});
['q','b','ty','j','st'].forEach(i=>$(i).addEventListener('input',draw));
$('ex').onclick=()=>{const txt=D.filter(r=>S[key(r)]).map(r=>r.text+' | '+r.type+' | '+r.items).join('\\n');navigator.clipboard&&navigator.clipboard.writeText(txt);alert(Object.keys(S).length+' stars copied. Paste them into the chat.')};draw();</script></body></html>"""
    open(os.path.join(BANK, "index.html"), "w", encoding="utf8").write(page.replace("__DATA__", data))
    print("wrote bank/index.html with", len(rows), "rows")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd")
    sp.add_parser("build"); sp.add_parser("stats"); sp.add_parser("export-html")
    f = sp.add_parser("find")
    for x in ("q", "type", "place", "rhymes", "joe", "bank"):
        f.add_argument("--" + x)
    f.add_argument("--max", type=int, default=40)
    a = p.parse_args()
    {"build": build, "stats": stats, "export-html": export_html}.get(a.cmd, lambda: find(a) if a.cmd == "find" else p.print_help())()
