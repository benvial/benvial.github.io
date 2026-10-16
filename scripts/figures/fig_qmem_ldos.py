"""Local density of states around a triangular rod at 10.2 µm: direct computation against QMEM (M = 500).

Data extracted from Fig. 9 of Vial et al., Phys. Rev. A 89, 023829 (2014).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-qmem-ldos.npz")


def main():
    style.use()
    d = np.load(DATA)
    tri = np.vstack([d["triangle"], d["triangle"][:1]])
    vmin, vmax = 1.0, 9.6  # LDOS in units of 1e-4, common scale for both panels

    fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.35), sharey=True, gridspec_kw=dict(wspace=0.12))
    for ax, key, letter, label in zip(axes, "ab", "ab", ["direct computation", "QMEM, $M = 500$"]):
        im = ax.imshow(d[f"ldos_{key}"].astype(float), origin="lower", extent=d[f"extent_{key}"],
                       cmap=style.WARM_SEQ, vmin=vmin, vmax=vmax, interpolation="bilinear")
        ax.plot(*tri.T, color=style.INK, lw=1.0, solid_joinstyle="miter")
        ax.set_xlim(-2, 4)
        ax.set_ylim(-3, 4)
        ax.set_aspect("equal")
        ax.set_xticks([-2, 0, 2, 4])
        ax.set_xlabel(r"$x$ ($\mathrm{\mu}$m)")
        style.panel(ax, letter)
        ax.text(0.03, 1.02, label, transform=ax.transAxes, ha="left", va="bottom", color=style.INK2)
    axes[0].set_ylabel(r"$y$ ($\mathrm{\mu}$m)")
    cb = style.colorbar(fig, im, list(axes), label=r"LDOS ($10^{-4}$)")
    cb.set_ticks([2, 4, 6, 8])
    style.save(fig, "fig-qmem-ldos")


if __name__ == "__main__":
    main()
