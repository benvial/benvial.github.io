"""Effective permittivity and tunability of periodic ferroelectric composites against bias field, coupled and uncoupled models.

Data extracted from Fig. 3a,c of Vial and Hao, J. Appl. Phys. 126, 044102 (2019).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-ferro-tunability.npz")


def main():
    style.use()
    d = np.load(DATA)
    # greys to warm for increasing dielectric fraction f
    colors = [style.oklch(0.78), style.oklch(0.62), style.oklch(0.42), style.oklch(0.55, 0.10, 33), style.WARM]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.2, 2.6), gridspec_kw=dict(wspace=0.32))

    for i, f in enumerate(d["f"]):
        c = colors[i]
        for ax, key in ((a, "eps"), (b, "tun")):
            ax.plot(*d[f"{key}_uncpl_{i}"].T, color=c, lw=1.3, ls=(0, (3.5, 2)))
            ax.plot(*d[f"{key}_cpl_{i}"].T, color=c, lw=1.6)
        y0 = d[f"eps_cpl_{i}"][0, 1]
        a.text(0.05, y0 + 0.015, f"$f$ = {f:.1f}", color=c if i else style.INK3, ha="left", va="bottom",
               fontsize=8.5)

    b.axhline(1, color=style.INK3, lw=0.7, ls=(0, (1, 2)), zorder=0)
    b.text(1.98, 1.006, "bulk", color=style.INK3, ha="right", va="bottom", fontsize=8.5)
    b.text(1.02, 1.15, "coupled", color=style.INK, ha="center", va="bottom")
    b.text(0.72, 0.955, "uncoupled", color=style.INK, ha="center", va="top")

    for ax in (a, b):
        ax.set_xlim(0, 2)
        ax.set_xticks([0, 0.5, 1, 1.5, 2])
        ax.set_xlabel("Bias field (MV/m)")
    a.set_ylim(0.1, 0.9)
    b.set_ylim(0.9, 1.3)
    a.set_ylabel("Normalized permittivity")
    b.set_ylabel("Normalized tunability")
    style.panel(a, "a", x=-0.2)
    style.panel(b, "b", x=-0.2)

    style.save(fig, "fig-ferro-tunability")


if __name__ == "__main__":
    main()
