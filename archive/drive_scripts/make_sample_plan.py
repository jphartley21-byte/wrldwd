"""Build sample_plan.csv: a short list of drive files to extract small preview images from.

Runs locally (no admin). Reads exif_results.csv (GPS, times) and drive_catalog.csv from the Desktop folder.
Picks a few files per place (GPS segments), plus evenly spaced clips from the 2015-16 videos (no GPS).
"""
import csv
import re
import datetime
import collections

import reverse_geocoder as rg

FOLDER = r"C:\Users\Joe\Desktop\seagate_probe"
EXIF = FOLDER + r"\exif_results.csv"
CAT = FOLDER + r"\drive_catalog.csv"
PLAN = FOLDER + r"\sample_plan.csv"

IMAGE = {".jpg", ".jpeg", ".heic", ".png"}
VIDEO = {".mov", ".mp4", ".m4v"}


def date_of(r):
    t = r.get("exif_time", "")
    m = re.match(r"(\d{4})[:\-](\d{2})[:\-](\d{2})", t or "")
    if m:
        return datetime.date(*map(int, m.groups()))
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", r["name"])
    if m:
        return datetime.date(*map(int, m.groups()))
    m = re.search(r"/Masters/(\d{4})/(\d{2})/(\d{2})/", r["path"])
    if m:
        return datetime.date(*map(int, m.groups()))
    return None


def pick_even(items, k):
    if len(items) <= k:
        return list(items)
    step = (len(items) - 1) / (k - 1) if k > 1 else 0
    return [items[round(i * step)] for i in range(k)]


def main():
    rows = list(csv.DictReader(open(EXIF, encoding="utf-8-sig")))
    plan = []

    # 1. GPS files grouped into place segments
    pts = []
    for r in rows:
        if r["lat"] in ("", None):
            continue
        d = date_of(r)
        if d:
            pts.append((d, r))
    geo = rg.search([(float(r["lat"]), float(r["lon"])) for _, r in pts], mode=1)
    by_day_place = collections.defaultdict(list)
    for (d, r), g in zip(pts, geo):
        by_day_place[(d, (g["name"], g["admin1"], g["cc"]))].append(r)
    per_day = collections.defaultdict(collections.Counter)
    for (d, place), lst in by_day_place.items():
        per_day[d][place] += len(lst)
    days = sorted(per_day)
    segs = []
    for d in days:
        place = per_day[d].most_common(1)[0][0]
        if segs and segs[-1]["place"] == place and (d - segs[-1]["end"]).days <= 6:
            segs[-1]["end"] = d
            segs[-1]["files"] += [(d, r) for (dd, p), lst in by_day_place.items() if dd == d and p == place for r in lst]
        else:
            segs.append({"place": place, "start": d, "end": d,
                         "files": [(d, r) for (dd, p), lst in by_day_place.items() if dd == d and p == place for r in lst]})
    wanted_uk = {"Dublin", "Palmerstown", "Sainte-Luce-sur-Loire", "Nantes", "Cambridge", "Norwich", "Nottingham", "Ryde",
                 "Camden Town", "Severn Beach"}
    for s in segs:
        name, region, cc = s["place"]
        in_aus = cc == "AU"
        if not in_aus and name not in wanted_uk:
            continue
        files = sorted(s["files"], key=lambda x: (x[0], x[1]["name"]))
        k = 4 if in_aus else 3
        if len(files) < 2 and in_aus is False:
            continue
        for d, r in pick_even(files, k):
            plan.append({"label": f"{name}, {region}, {cc}", "date": d.isoformat(), "path": r["path"], "ext": r["ext"],
                         "frames": 2 if r["ext"] in VIDEO else 1})

    # 2. Videos with no GPS: the 2015-16 "Movies" folder, evenly spaced across the dates
    movies = [r for r in rows if r["root"] == "Movies" and r["ext"] in VIDEO]
    movies.sort(key=lambda r: (date_of(r) or datetime.date(1970, 1, 1), r["name"]))
    for r in pick_even(movies, 34):
        d = date_of(r)
        plan.append({"label": "Movies 2015-16 (no GPS)", "date": d.isoformat() if d else "", "path": r["path"],
                     "ext": r["ext"], "frames": 2})

    # 3. GoPro "New Zealand 2015" clips and the few loose 2015 photos (no GPS)
    for r in rows:
        if r["root"] == "New Zealand 2015" and r["ext"] in VIDEO:
            plan.append({"label": "New Zealand 2015 GoPro (no GPS)", "date": "2015-10", "path": r["path"], "ext": r["ext"],
                         "frames": 1})
    cat = list(csv.DictReader(open(CAT, encoding="utf-8-sig")))
    for r in cat:
        if r["root"] == "Pictures" and "Photos Library" not in r["path"] and r["ext"] in IMAGE and r["name"].startswith("2015-"):
            plan.append({"label": "Loose 2015 photo", "date": r["name"][:10], "path": r["path"], "ext": r["ext"], "frames": 1})
        if r["root"] == "Pictures" and r["name"].lower().startswith("new zealand"):
            plan.append({"label": "Loose New Zealand photo", "date": "2015", "path": r["path"], "ext": r["ext"], "frames": 1})
    # 4. A few 2016 Bali-era clips are already inside the evenly spaced Movies sample

    seen = set()
    final = []
    for p in plan:
        if p["path"] in seen:
            continue
        seen.add(p["path"])
        final.append(p)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["label", "date", "path", "ext", "frames"])
        w.writeheader()
        w.writerows(final)
    print("planned files:", len(final))
    print(collections.Counter(p["label"].split(",")[0] for p in final).most_common(60))


if __name__ == "__main__":
    main()
