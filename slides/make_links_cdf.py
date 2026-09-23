#!/usr/bin/env python3
"""Time-weighted CDF of the links a Nexus 5X actually held (churn-n8-1, hold arm).

Exposure comes from node_minutes, so the curve is "share of time at or below k links",
not a share of samples. Run: python3 make_links_cdf.py
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("churn_rate_by_degree.csv")
h = df[(df["arm"] == "hold") & (df["class"] == "nexus")].sort_values("links_up")
k, w = h["links_up"].to_numpy(), h["node_minutes"].to_numpy()
cdf = np.cumsum(w) / w.sum()
q = lambda p: int(k[np.searchsorted(cdf, p)])
stats = dict(p50=q(.50), p90=q(.90), kmin=int(k.min()), kmax=int(k.max()),
             mean=float((k * w).sum() / w.sum()), minutes=float(w.sum()),
             share7=float(w[k == 7].sum() / w.sum() * 100))

fig, ax = plt.subplots(figsize=(3.5, 2.4))
ax.step(np.r_[k[0] - 1, k], np.r_[0, cdf], where="post", color="#1f77b4", lw=1.8)
ax.plot(k, cdf, "o", color="#1f77b4", ms=4)
for p, lbl in ((.5, f"median {stats['p50']}"), (.9, f"p90 {stats['p90']}")):
    ax.axhline(p, color="0.55", ls=":", lw=.9)
    ax.annotate(lbl, xy=(k[0] - .9, p), va="bottom", ha="left", fontsize=7, color="0.35")
ax.set_xlabel("links held")
ax.set_ylabel("cumulative share of time")
ax.set_xlim(k[0] - 1, k[-1] + .3); ax.set_ylim(0, 1.02)
ax.set_xticks(k); ax.set_yticks(np.arange(0, 1.01, .2))
ax.grid(alpha=.3, lw=.6)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
fig.tight_layout(pad=.3)
fig.savefig("figures/churn_links_held_cdf.pdf")
print("wrote figures/churn_links_held_cdf.pdf")
for kk, vv in stats.items(): print(f"  {kk} = {vv:.4g}" if isinstance(vv, float) else f"  {kk} = {vv}")
print("  per-degree share of time:", ", ".join(f"k={a}: {b/w.sum()*100:.1f}%" for a, b in zip(k, w)))
import json; open("/tmp/links_stats.json", "w").write(json.dumps(stats))
