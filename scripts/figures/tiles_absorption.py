"""Sound absorption of the ceramic metatile: analytical model, finite elements and measurement.

Data digitized from Fig. 6 of Tugut et al., Proc. R. Soc. A 482, 20260361 (2026).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-tiles-absorption.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig, ax = plt.subplots(figsize=(6.2, 3.0))

    # the measured curve leaves the axes below zero in a few places (NaN breaks), as in the source
    ax.plot(*d["experiment"].T, color=style.WARM, lw=1.0, label="Experiment", zorder=2)
    ax.plot(*d["fem"].T, color=style.COOL, lw=1.6, ls=(0, (1, 1.6)), dash_capstyle="round", label="FEM",
            zorder=3)
    ax.plot(*d["analytical"].T, color=style.INK, lw=1.5, label="Analytical", zorder=4)

    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1.03)
    ax.set_xticks([0, 500, 1000, 1500, 2000])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Absorption coefficient")
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="upper left", bbox_to_anchor=(0.01, 1.0), handlelength=1.6, handletextpad=0.5,
              borderaxespad=0.2, borderpad=0.2, labelspacing=0.4, fontsize=8.5)

    style.save(fig, "fig-tiles-absorption")


if __name__ == "__main__":
    main()
