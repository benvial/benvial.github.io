"""Specular transmission T_0,0 at normal incidence of four square coaxial aperture filters M1 to M4, simulated and measured.

Data extracted from Fig. 2 of Vial et al., Opt. Lett. 39, 4723 (2014).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-aaa-transmission.npz")
NAMES = ("M1", "M2", "M3", "M4")


def main():
    style.use()
    d = np.load(DATA)
    # greys to warm for increasing design wavelength
    colors = [style.oklch(0.72), style.oklch(0.45), style.oklch(0.55, 0.10, 33), style.WARM]
    fig, axes = plt.subplots(1, 2, figsize=(6.2, 2.75), sharey=True, gridspec_kw=dict(wspace=0.14))

    for ax, tag, letter, word in zip(axes, ("sim", "exp"), "ab", ("simulation", "measurement")):
        for i, n in enumerate(NAMES):
            lam, T = d[f"{tag}_{n}"].T
            ax.plot(lam, T, color=colors[i], lw=1.4)
            k = np.argmax(T)
            ax.text(lam[k], T[k] + 0.018, n, color=colors[i] if i else style.INK3, ha="center", va="bottom",
                    fontsize=8.5)
        ax.set_xlim(4, 18)
        ax.set_xticks([4, 6, 8, 10, 12, 14, 16, 18])
        ax.set_xlabel(r"Wavelength $\lambda$ ($\mathrm{\mu}$m)")
        style.panel(ax, letter, x=0.0, y=1.0)
        ax.text(0.06, 1.0, word, transform=ax.transAxes, ha="left", va="bottom", color=style.INK3, fontsize=9)

    a = axes[0]
    a.set_ylim(-0.025, 0.74)
    a.spines["left"].set_bounds(0, 0.7)
    a.set_yticks([0, 0.2, 0.4, 0.6], ["0", "0.2", "0.4", "0.6"])
    a.set_ylabel("Transmission $T_{0,0}$")
    axes[1].tick_params(axis="y", left=False)
    axes[1].spines["left"].set_visible(False)

    style.save(fig, "fig-aaa-transmission")


if __name__ == "__main__":
    main()
