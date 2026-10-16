"""Non-magnetic invisible medium that writes a portrait of Maxwell into the field amplitude (A, |Ez|, eps, Re Ez).

Data extracted from Fig. 2 of Vial et al., Phys. Rev. B 94, 245119 (2016).
"""

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-invisible-maxwell.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig = plt.figure(figsize=(6.2, 4.6))
    W, H = fig.get_size_inches()
    s = 1.82  # panel side (in)
    cols, rows = (0.6, 3.5), (2.68, 0.42)

    def show(col, row, key, cmap, norm, half, ticks, label, bad=False, box=True):
        ax = fig.add_axes([cols[col] / W, rows[row] / H, s / W, s / H])
        x, y = d[f"{key}_x"], d[f"{key}_y"]
        v = d[key].astype(float)
        cm = cmap.copy()
        if bad:  # the source's in-panel label boxes are masked: show them at the background level
            cm.set_bad(cm(norm(np.nanmedian(v[:8]))))
        im = ax.imshow(v, cmap=cm, norm=norm, origin="upper", interpolation="bilinear",
                       extent=[x[0], x[-1], y[-1], y[0]])
        ax.set_xlim(-half, half)
        ax.set_ylim(-half, half)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.text(0.035, 0.965, label, transform=ax.transAxes, ha="left", va="top", color=style.INK,
                bbox=dict(boxstyle="square,pad=0.25", fc=style.PAPER if box else "none", ec="none"))
        return ax, im, cm

    def bar(im, ax, ticks, label=None, extend="neither"):
        p = ax.get_position()
        cax = fig.add_axes([p.x1 + 0.07 / W, p.y0, 0.07 / W, p.height])
        cb = fig.colorbar(im, cax=cax, ticks=ticks, extend=extend, extendfrac=0.04)
        cb.outline.set_visible(False)
        cb.ax.tick_params(length=2, width=0.6, labelsize=8.5)
        if label:
            cb.set_label(label, labelpad=3)
        return cb

    # amplitude: target (portrait) and computed, same grey scale; |Ez| < 1 in the faint fringes is clipped.
    # Windows stop short of the source frames, whose tick marks sit inside the image.
    amp = Normalize(1.0, 1.5)
    ax_a, _, _ = show(0, 0, "A", style.GREY_SEQ, amp, 3.4, [-3, 0, 3], r"$A$", bad=True, box=False)
    ax_b, im, cm = show(1, 0, "absE", style.GREY_SEQ, amp, 3.4, [-3, 0, 3], r"$|E_z|$", bad=True, box=False)
    # a plain corner over the masked label box of the source panel, so it reads as a label area
    ax_b.add_patch(Rectangle((-3.7, 2.18), 1.99, 1.55, fc=cm.get_bad(), ec="none", zorder=2))
    bar(im, ax_b, [1, 1.25, 1.5], "Amplitude", extend="min")

    # permittivity on the diverging map centred on vacuum (eps = 1): grey below, vermilion above
    ax_c, im, _ = show(0, 1, "eps", style.FIELD, Normalize(0, 2), 5.25, [-5, 0, 5], r"$\varepsilon$")
    bar(im, ax_c, [0, 1, 2], extend="min")

    ax_d, im, _ = show(1, 1, "ReE", style.FIELD, Normalize(-1.45, 1.45), 8.25, [-5, 0, 5], r"Re $E_z$")
    bar(im, ax_d, [-1, 0, 1])

    for ax, letter in zip((ax_a, ax_b, ax_c, ax_d), "abcd"):
        style.panel(ax, letter, x=-0.03, y=1.01)
    for ax in (ax_a, ax_c):
        ax.set_ylabel(r"$y/\lambda_0$", labelpad=1)
    for ax in (ax_c, ax_d):
        ax.set_xlabel(r"$x/\lambda_0$")

    style.save(fig, "fig-invisible-maxwell")


if __name__ == "__main__":
    main()
