"""train_judge: fit the human-gate preference judge.

WHAT THIS LEARNS, AND WHAT IT HONESTLY CANNOT
The 17 human gates have no rule. A supervised judge needs labelled positives, and this project has
very few: exactly ONE accepted stanza (bars 1-4) plus the phrases Joe kept. So:

  * the judge is NOT validated as a classifier. With one positive GROUP, leave-one-block-out is
    degenerate (the fold that holds the positive out has a single class). This file says so and
    reports the honest numbers it CAN report: rank separation and a leave-one-positive-out test.
  * the judge IS useful now, because half its signal is the rule prior in ml/domain.py - domain
    knowledge transcribed from Joe's own rejections, not fitted. The fitted part is a diction model:
    which vocabulary and shapes Joe keeps vs rejects.
  * the flywheel is the point: every new verdict (a locked bar, a "not bad" contender, a rejection)
    adds a row to ml/data/dataset.jsonl and moves the judge from rules toward learning. The contract
    that must hold at all times is the CALIBRATION CONTRACT in ml/evaluate.py.

No pandas: numpy + scipy + sklearn only (the repo's environment).

Usage:
  python ml/train_judge.py                 # fit, save ml/models/judge.joblib, print honest metrics
  python ml/train_judge.py --no-weak       # strong labels only (accept/like/reject)
"""
import argparse
import json
import os
import sys

import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression          # noqa: E402
from sklearn.preprocessing import StandardScaler             # noqa: E402
import joblib                                               # noqa: E402

import features as F                                        # noqa: E402

DATA = os.path.join(HERE, "data", "dataset.jsonl")
MODEL = os.path.join(HERE, "models", "judge.joblib")
METRICS = os.path.join(HERE, "models", "metrics.json")

# How much each tier counts. "like" rows are fragments, not full bars, so they weigh less; a "park"
# stanza is deliberately excluded from training and used only as a held-out sanity case.
TIER_WEIGHT = {"accept": 1.0, "like": 0.5, "reject": 1.0, "weak_neg": 0.4}
POSITIVE = {"accept", "like"}
NEGATIVE = {"reject", "weak_neg"}


def load(path=DATA):
    rows = []
    with open(path, encoding="utf8") as fh:
        for line in fh:
            b = json.loads(line)
            for r in b["bars"]:
                rows.append({"text": r["text"], "features": r["features"], "label": b["label"],
                             "source": b["source"], "block": b["source"] + "#" + str(b["label"])})
    return rows


class JudgeModel:
    """Numeric feature block (scaled) hstacked with word/char TF-IDF of the bar -> logistic."""

    def __init__(self, c=1.0):
        self.num = StandardScaler()
        self.word = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1,
                                    sublinear_tf=True)
        self.lr = LogisticRegression(C=c, class_weight="balanced", max_iter=2000,
                                     solver="liblinear")
        self.numeric_features = list(F.NUMERIC_FEATURES)

    def _num(self, feats):
        return np.asarray([F.vector({"features": f}) for f in feats], dtype=float)

    def _design(self, texts, feats, fit=False):
        if fit:
            num = self.num.fit_transform(self._num(feats))
            w = self.word.fit_transform(texts)
            c = self.char.fit_transform(texts)
        else:
            num = self.num.transform(self._num(feats))
            w = self.word.transform(texts)
            c = self.char.transform(texts)
        return sp.hstack([sp.csr_matrix(num), w, c]).tocsr()

    def fit(self, texts, feats, y, sample_weight=None):
        X = self._design(list(texts), list(feats), fit=True)
        self.lr.fit(X, y, sample_weight=sample_weight)
        return self

    def predict_proba(self, texts, feats):
        """P(lands) - the positive class (accept / like)."""
        return self.lr.predict_proba(self._design(list(texts), list(feats)))[:, 1]

    def risk(self, texts, feats):
        """P(reject) - the negative class, whatever column sklearn put it in."""
        p = self.lr.predict_proba(self._design(list(texts), list(feats)))
        neg = list(self.lr.classes_).index(0)
        return p[:, neg]

    def save(self, path=MODEL):
        """Save the fitted components, not the class: a pickled instance would record the module it
        was defined in (__main__ when trained from the CLI) and fail to load elsewhere."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"num": self.num, "word": self.word, "char": self.char, "lr": self.lr,
                     "numeric_features": self.numeric_features}, path)
        return path

    @staticmethod
    def load(path=MODEL):
        d = joblib.load(path)
        m = JudgeModel()
        m.num, m.word, m.char, m.lr = d["num"], d["word"], d["char"], d["lr"]
        m.numeric_features = d.get("numeric_features", list(F.NUMERIC_FEATURES))
        return m


def build(rows, allow_weak=True):
    use = [r for r in rows if r["label"] in POSITIVE or r["label"] == "reject"
           or (allow_weak and r["label"] == "weak_neg")]
    texts = [r["text"] for r in use]
    feats = [r["features"] for r in use]
    y = np.asarray([1 if r["label"] in POSITIVE else 0 for r in use])
    w = np.asarray([TIER_WEIGHT[r["label"]] for r in use])
    return use, texts, feats, y, w


def rank_separation(rows, scores):
    """Mean risk per tier - the honest 'does it order Joe's verdicts' number."""
    per = {}
    for r, s in zip(rows, scores):
        per.setdefault(r["label"], []).append(float(s))
    return {k: round(float(np.mean(v)), 3) for k, v in sorted(per.items())}


def leave_one_positive_out(rows, texts, feats, y, w):
    """Train without one positive BLOCK, then check the held-out positive scores below the reject
    mean. The only honest generalisation test available while positive blocks are so few."""
    blocks = sorted({r["block"] for r in rows if r["label"] in POSITIVE})
    idx = {i for i, r in enumerate(rows)}
    detail, hits, folds = [], 0, 0
    for blk in blocks:
        held = [i for i, r in enumerate(rows) if r["block"] == blk and r["label"] in POSITIVE]
        if not held:
            continue
        folds += 1
        keep = sorted(idx - set(held))
        m = JudgeModel().fit([texts[j] for j in keep], [feats[j] for j in keep],
                             y[keep], sample_weight=w[keep])
        neg = [float(m.risk([texts[j]], [feats[j]])[0])
               for j in keep if rows[j]["label"] in NEGATIVE]
        thr = float(np.mean(neg))
        s = float(m.risk([texts[i] for i in held], [feats[i] for i in held]).mean())
        detail.append({"held_out_block": blk, "score": round(s, 3),
                       "reject_mean": round(thr, 3), "below": bool(s < thr)})
        hits += int(s < thr)
    return {"folds": folds, "held_out_positive_below_reject_mean": hits, "detail": detail}


def contract(rows, scores, thr=0.5):
    """The calibration-style contract: every reject block flagged, every accept block not."""
    blocks = {}
    for r, s in zip(rows, scores):
        blocks.setdefault(r["block"], []).append((r["label"], float(s)))
    failures = []
    for blk, items in blocks.items():
        label, n = items[0][0], len(items)
        if label not in ("reject", "accept") or n < 2:
            continue
        mean = float(np.mean([s for _l, s in items]))
        if label == "reject" and mean < thr:
            failures.append(f"{blk}: rejected stanza scored {mean:.2f} < {thr}")
        if label == "accept" and mean >= thr:
            failures.append(f"{blk}: accepted stanza scored {mean:.2f} >= {thr}")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-weak", action="store_true", help="drop the weak_neg tier")
    ap.add_argument("--c", type=float, default=1.0)
    a = ap.parse_args()

    rows = load()
    use, texts, feats, y, w = build(rows, allow_weak=not a.no_weak)
    counts = {}
    for r in use:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    pos_blocks = len({r["block"] for r in use if r["label"] in POSITIVE})

    print(f"training rows {len(use)}  tiers {counts}  positive blocks {pos_blocks}")
    if pos_blocks < 3:
        print(f"  NOTE: {pos_blocks} positive block(s). Cross-validated classification is "
              f"degenerate; reporting rank separation + leave-one-positive-out instead.\n")

    model = JudgeModel(c=a.c).fit(texts, feats, y, sample_weight=w)
    scores = model.risk(texts, feats)

    sep = rank_separation(use, scores)
    failures = contract(use, scores)
    lopo = leave_one_positive_out(use, texts, feats, y, w)

    print("tier        mean risk (0 = lands, 1 = reject)")
    for k, v in sep.items():
        print(f"  {k:10} {v:.3f}")
    print("\nCALIBRATION CONTRACT:", "PASSED" if not failures else f"FAILED ({len(failures)})")
    for f in failures:
        print("  x", f)
    print(f"\nleave-one-positive-out: {lopo['held_out_positive_below_reject_mean']}/{lopo['folds']} "
          f"held-out positives scored below the reject mean")

    model.save()
    json.dump({"rows": len(use), "tiers": counts, "positive_blocks": pos_blocks,
               "rank_separation": sep, "contract_failures": failures, "lopo": lopo},
              open(METRICS, "w", encoding="utf8"), indent=1)
    print(f"\nsaved {os.path.relpath(MODEL, ROOT)} and {os.path.relpath(METRICS, ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
