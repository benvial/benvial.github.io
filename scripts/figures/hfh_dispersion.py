"""Dispersion diagram of a 1D dispersive layered medium, exact against high-frequency homogenization near the band edges.

Data extracted from Fig. 9a (arXiv numbering) of Touboul et al., Multiscale Model. Simul. 22, 1136 (2024).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-hfh-dispersion.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig, ax = plt.subplots(figsize=(6.2, 3.1))

    for k in sorted(k for k in d.files if k.startswith("band")):
        ax.plot(*d[k].T, color=style.INK, lw=1.3, solid_capstyle="butt")
    for k in sorted(k for k in d.files if k.startswith("hfh")):
        ax.plot(*d[k].T, color=style.WARM, lw=1.7, ls=(0, (3.2, 2.2)))

    ax.set_xlim(0, np.pi)
    ax.set_ylim(0, 4.3)
    ax.set_xticks([0, np.pi / 2, np.pi], ["0", r"$\pi/2$", r"$\pi$"])
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_xlabel(r"Bloch wavenumber $\kappa\delta$")
    ax.set_ylabel(r"Normalized frequency $\Omega$")

    ax.text(1.95, 1.8, "exact", color=style.INK, ha="left", va="top")
    ax.text(0.55, 1.62, r"HFH near" "\n" r"$\kappa\delta = 0$", color=style.WARM, ha="center", va="bottom", linespacing=1.1)
    ax.text(2.6, 1.55, r"HFH near" "\n" r"$\kappa\delta = \pi$", color=style.WARM, ha="center", va="top", linespacing=1.1)

    style.save(fig, "fig-hfh-dispersion")


if __name__ == "__main__":
    main()
