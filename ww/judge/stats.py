"""Statistics for the acceptance battery (plan 5.4). Pure Python, no scipy. Everything here resamples CLUSTERS (quad / block /
poem), never bars or pairs, and prints its cluster count: synthetic degradations multiply pairs, not independent evidence.
"""
from __future__ import annotations

import math
import random
from typing import Iterable, Sequence


def _binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k), X ~ Bin(n, p), summed in log space (n up to a few thousand)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0
    lp, lq = math.log(p), math.log(1 - p)
    terms = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq for i in range(k + 1)]
    m = max(terms)
    return min(1.0, math.exp(m) * sum(math.exp(t - m) for t in terms))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """exact two-sided (1-alpha) interval for k successes in n trials."""
    if n <= 0:
        return 0.0, 1.0
    lo = 0.0
    if k > 0:  # largest p with P(X >= k | p) = alpha/2  <=>  smallest p with P(X<=k-1)=1-alpha/2
        a, b = 0.0, 1.0
        for _ in range(80):
            mid = (a + b) / 2
            if 1 - _binom_cdf(k - 1, n, mid) < alpha / 2:
                a = mid
            else:
                b = mid
        lo = (a + b) / 2
    hi = 1.0
    if k < n:
        a, b = 0.0, 1.0
        for _ in range(80):
            mid = (a + b) / 2
            if _binom_cdf(k, n, mid) > alpha / 2:
                a = mid
            else:
                b = mid
        hi = (a + b) / 2
    return lo, hi


def cluster_accuracy(units: Sequence[tuple[str, float, float]]) -> float:
    """units = (cluster, correct in [0,1], weight). weighted mean of PER-CLUSTER means (each cluster counts once)."""
    per: dict[str, list[tuple[float, float]]] = {}
    for c, y, w in units:
        per.setdefault(c, []).append((y, w))
    num = den = 0.0
    for vals in per.values():
        wsum = sum(w for _, w in vals) or 1e-12
        num += sum(y * w for y, w in vals) / wsum
        den += 1
    return num / den if den else 0.0


def cluster_bootstrap(units: Sequence[tuple[str, float, float]], B: int = 2000, seed: int = 0, alpha: float = 0.05) -> dict:
    """percentile CI of the cluster-mean accuracy, resampling clusters with replacement."""
    per: dict[str, list[tuple[str, float, float]]] = {}
    for u in units:
        per.setdefault(u[0], []).append(u)
    names = sorted(per)
    n = len(names)
    point = cluster_accuracy(units)
    if n == 0:
        return {"point": 0.0, "lo": 0.0, "hi": 1.0, "n_clusters": 0, "n_units": 0}
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        sample = [rng.choice(names) for _ in range(n)]
        means.append(sum(cluster_accuracy(per[c]) for c in sample) / n)
    means.sort()
    return {"point": point, "lo": means[int(alpha / 2 * B)], "hi": means[min(B - 1, int((1 - alpha / 2) * B))],
            "n_clusters": n, "n_units": len(units)}


def bradley_terry(wins: dict[tuple[str, str], float], iters: int = 200) -> dict[str, float]:
    """MM algorithm. wins[(a, b)] = number of times a beat b (ties count 0.5 each way). Returns log-strengths, mean 0."""
    items = sorted({x for ab in wins for x in ab})
    if not items:
        return {}
    w = {i: sum(v for (a, _), v in wins.items() if a == i) + 0.01 for i in items}
    s = {i: 1.0 for i in items}
    for _ in range(iters):
        new = {}
        for i in items:
            den = 0.0
            for j in items:
                if i == j:
                    continue
                n_ij = wins.get((i, j), 0.0) + wins.get((j, i), 0.0)
                if n_ij:
                    den += n_ij / (s[i] + s[j])
            new[i] = w[i] / den if den else s[i]
        z = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        s = {i: v / z for i, v in new.items()}
    return {i: math.log(v) for i, v in s.items()}


def holm(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """Holm-Bonferroni: which hypotheses are rejected."""
    order = sorted(pvals, key=lambda k: pvals[k])
    m = len(order)
    out, still = {}, True
    for rank, k in enumerate(order):
        still = still and pvals[k] <= alpha / (m - rank)
        out[k] = still
    return out


def sign_test_p(k: int, n: int) -> float:
    """one-sided exact p that >= k of n are successes under p=0.5."""
    return 1 - _binom_cdf(k - 1, n, 0.5) if n else 1.0


def selftest() -> tuple[bool, str]:
    problems: list[str] = []
    lo, hi = clopper_pearson(36, 40)
    if not (0.75 < lo < 0.78):
        problems.append(f"CP(36/40) lower should be ~0.763, got {lo:.3f}")
    if not (0.80 < clopper_pearson(19, 19)[0] < 0.86):
        problems.append(f"CP(19/19) lower should be ~0.82, got {clopper_pearson(19, 19)[0]:.3f}")
    if not (0.64 < clopper_pearson(17, 19)[0] < 0.70):
        problems.append(f"CP(17/19) lower should be ~0.67, got {clopper_pearson(17, 19)[0]:.3f}")
    if clopper_pearson(0, 10)[0] != 0.0 or clopper_pearson(10, 10)[1] != 1.0:
        problems.append("CP edge cases")
    # clustering: 3 clusters x 100 units that all agree must NOT look like n=300
    units = [(f"c{c}", 1.0, 1.0) for c in range(3) for _ in range(100)]
    bs = cluster_bootstrap(units, B=300)
    if bs["n_clusters"] != 3 or bs["point"] != 1.0:
        problems.append(f"cluster bootstrap bookkeeping: {bs}")
    mixed = [(f"c{c}", 1.0 if c % 5 else 0.0, 1.0) for c in range(20) for _ in range(10)]
    bm = cluster_bootstrap(mixed, B=400)
    if not (0.70 < bm["point"] < 0.90 and bm["lo"] < bm["point"] < bm["hi"]):
        problems.append(f"bootstrap interval should bracket the point estimate: {bm}")
    # Bradley-Terry recovers an ordering
    bt = bradley_terry({("a", "b"): 8, ("b", "a"): 2, ("b", "c"): 7, ("c", "b"): 3, ("a", "c"): 9, ("c", "a"): 1})
    if not (bt["a"] > bt["b"] > bt["c"]):
        problems.append(f"BT ordering wrong: {bt}")
    h = holm({"x": 0.001, "y": 0.04, "z": 0.2})
    if h != {"x": True, "y": False, "z": False}:
        problems.append(f"holm: {h}")
    if not (0.05 < sign_test_p(8, 10) < 0.06):
        problems.append(f"sign test p(8/10) ~0.055, got {sign_test_p(8, 10):.4f}")
    return (not problems, "; ".join(problems) if problems else "exact bounds match the reviewer's figures (36/40 -> 0.763, 19/19 -> 0.82), cluster bootstrap, BT, Holm")
