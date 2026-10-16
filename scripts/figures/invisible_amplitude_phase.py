"""Inverse design of amplitude and phase: specified versus computed Re Ez, amplitude A and phase psi.

Data extracted from Fig. 5 of Vial et al., Phys. Rev. B 94, 245119 (2016).
"""

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-invisible-amplitude-phase.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig = plt.figure(figsize=(6.2, 4.45))
    W, H = fig.get_size_inches()
    s, gap = 1.72, 0.1
    x0, y0 = 0.66, 0.42
    ext = list(d["extent"])

    columns = [
        ("ReE", r"Field Re $E_z$", Normalize(-1.35, 1.35), [-1, 0, 1]),
        ("A", r"Amplitude $A$", Normalize(0.6, 1.4), [0.7, 1, 1.3]),
        ("psi", r"Phase $\psi$ (rad)", Normalize(-2.65, 2.65), [-2, 0, 2]),
    ]
    rows = [("spec", "Specified"), ("comp", "Computed")]

    for j, (key, title, norm, ticks) in enumerate(columns):
        left = x0 + j * (s + gap)
        for i, (suffix, rowname) in enumerate(rows):
            bottom = y0 + (1 - i) * (s + gap)
            ax = fig.add_axes([left / W, bottom / H, s / W, s / H])
            im = ax.imshow(d[f"{key}_{suffix}"].astype(float), cmap=style.FIELD, norm=norm, origin="upper",
                           interpolation="bilinear", extent=ext)
            ax.set_xticks([-5, 0, 5])
            ax.set_yticks([-5, 0, 5])
            for sp in ax.spines.values():
                sp.set_visible(False)
            if i == 0:
                ax.tick_params(labelbottom=False)
            else:
                ax.set_xlabel(r"$x/\lambda_0$")
            if j == 0:
                ax.set_ylabel(r"$y/\lambda_0$", labelpad=1)
                ax.text(-0.36, 0.5, rowname, transform=ax.transAxes, rotation=90, ha="center", va="center",
                        fontweight=620, color=style.INK)
            else:
                ax.tick_params(labelleft=False)
        # one colorbar per column, above it, with the quantity as its title
        top = y0 + 2 * s + gap
        cax = fig.add_axes([(left + 0.15 * s) / W, (top + 0.16) / H, 0.7 * s / W, 0.07 / H])
        cb = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=ticks)
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=2, width=0.6, labelsize=8.5, top=True, bottom=False, labeltop=True,
                          labelbottom=False, pad=1.5)
        cb.ax.set_title(title, fontsize=9.5, fontweight=400, loc="center", pad=13)

    style.save(fig, "fig-invisible-amplitude-phase")


if __name__ == "__main__":
    main()
