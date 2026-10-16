"""Specular reflection R_0,0 at normal incidence of MIM absorbers for five periods d, simulated and measured.

Data extracted from Fig. 2 of Vial et al., J. Opt. Soc. Am. B 31, 1339 (2014).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-mim-reflection.npz")


def main():
    style.use()
    d = np.load(DATA)
    # greys to warm for increasing period d
    colors = [style.oklch(0.78), style.oklch(0.62), style.oklch(0.42), style.oklch(0.55, 0.10, 33), style.WARM]
    fig, axes = plt.subplots(1, 2, figsize=(6.2, 2.75), sharey=True, gridspec_kw=dict(wspace=0.14))

    for ax, tag, letter, word in zip(axes, ("sim", "exp"), "ab", ("simulation", "measurement")):
        dips = []
        for i, p in enumerate(d["d"]):
            lam, R = d[f"{tag}_{p:.1f}"].T
            ax.plot(lam, R, color=colors[i], lw=1.5)
            dips.append(lam[np.argmin(R)])
        # label each dip with its period, below the axis floor
        xs = np.array(dips)
        for j in range(1, len(xs)):  # keep labels at least 1.05 um apart
            xs[j] = max(xs[j], xs[j - 1] + 1.05)
        for i, (p, x) in enumerate(zip(d["d"], xs)):
            ax.text(x, -0.035, f"{p:.1f}", color=colors[i] if i else style.INK3, ha="center", va="top",
                    fontsize=8.5)
        ax.set_xlim(12, 24)
        ax.set_xticks([12, 14, 16, 18, 20, 22, 24])
        ax.set_xlabel(r"Wavelength $\lambda$ ($\mathrm{\mu}$m)")
        ax.spines["left"].set_bounds(0, 1)
        style.panel(ax, letter, x=0.0, y=1.0)
        ax.text(0.06, 1.0, word, transform=ax.transAxes, ha="left", va="bottom", color=style.INK3, fontsize=9)

    a = axes[0]
    a.set_ylim(-0.15, 1.02)
    a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1], ["0", "0.2", "0.4", "0.6", "0.8", "1"])
    a.set_ylabel("Reflection $R_{0,0}$")
    a.text(12.25, -0.035, r"$d$ ($\mathrm{\mu}$m)", color=style.INK3, ha="left", va="top", fontsize=8.5)
    axes[1].tick_params(axis="y", left=False)
    axes[1].spines["left"].set_visible(False)

    style.save(fig, "fig-mim-reflection")


if __name__ == "__main__":
    main()
