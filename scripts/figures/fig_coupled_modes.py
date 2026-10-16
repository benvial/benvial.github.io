"""Eigenfrequencies of the four coupled modes of a symmetric dimer versus gap: full-wave against the coupling model.

Data extracted from Fig. 2 of Vial and Hao, J. Opt. 18, 115004 (2016).
"""

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-coupled-modes.npz")


def main():
    style.use()
    d = np.load(DATA)
    modes = [("EQ", style.INK), ("EDy", style.WARM), ("EDx", style.COOL), ("MD", style.BLUE)]
    iso = style.oklch(0.68)  # lighter than COOL so the isolated-rod lines recede
    label_x = {"re": {"edy": 1.0, "md": 1.0}, "im": {"edy": 1.8, "md": 1.0}}

    fig, (ar, ai) = plt.subplots(2, 1, figsize=(6.2, 4.6), sharex=True, gridspec_kw=dict(hspace=0.12))
    for ax, part in [(ar, "re"), (ai, "im")]:
        for key, x0 in label_x[part].items():
            v = float(d[f"iso_{key}_{part}"])
            ax.axhline(v, xmin=0, xmax=0.88, color=iso, lw=0.9, ls=(0, (4, 3)), zorder=1)
            ax.text(x0, v, key, color=style.INK3, ha="center", va="bottom", fontsize=8.5,
                    bbox=dict(fc="white", ec="none", pad=0.6))
        for name, c in modes:
            line = d[f"{name}_{part}_line"]
            ax.plot(line[:, 0], line[:, 1], color=c, lw=1.5, zorder=2)
            ax.plot(d["d"], d[f"{name}_{part}_m4"], "o", ms=3.6, mfc="white", mec=c, mew=1.0, zorder=3)
            ax.text(2.17, line[-1, 1], name, color=c, ha="left", va="center", fontsize=9)
    ar.set_ylim(0.05, 0.32)
    ar.set_yticks([0.1, 0.2, 0.3])
    ai.set_ylim(-0.053, 0.0)
    ai.set_yticks([-0.05, -0.04, -0.03, -0.02, -0.01, 0])
    ai.set_xlim(0, 2.4)
    ai.set_xticks([0, 0.5, 1, 1.5, 2])
    ai.set_xlabel(r"Normalized gap $d/L_x$")
    ar.set_ylabel(r"$\mathrm{Re}\,\omega/\omega_0$")
    ai.set_ylabel(r"$\mathrm{Im}\,\omega/\omega_0$")
    fig.align_ylabels([ar, ai])

    g = style.INK2
    handles = [Line2D([], [], color=g, lw=1.5), Line2D([], [], ls="none", marker="o", ms=3.6, mfc="white", mec=g),
               Line2D([], [], color=iso, lw=0.9, ls=(0, (4, 3)))]
    ar.legend(handles, ["full-wave", "coupling model ($M = 4$)", "isolated rod"], loc="lower left",
              bbox_to_anchor=(0.0, 1.0), ncol=3, fontsize=8.5, handlelength=2.0, columnspacing=1.6,
              borderaxespad=0.1)
    style.panel(ar, "a", y=1.09)
    style.panel(ai, "b")
    style.save(fig, "fig-coupled-modes")


if __name__ == "__main__":
    main()
