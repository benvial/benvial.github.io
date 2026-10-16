"""Invisible graded profile with mu = A^2 (80 % field damping at the centre): mu, eps(r) and Re Ez.

Data extracted from Fig. 1 of Vial et al., Phys. Rev. B 94, 245119 (2016).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-invisible-profile.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig = plt.figure(figsize=(6.2, 2.75))
    W, H = fig.get_size_inches()

    def axes(x, y, w, h):
        return fig.add_axes([x / W, y / H, w / W, h / H])

    ax_mu = axes(0.5, 1.66, 2.35, 1.0)
    ax_eps = axes(0.5, 0.42, 2.35, 1.07)
    ax_f = axes(3.55, 0.42, 2.23, 2.23)
    cax = axes(5.86, 0.42, 0.07, 2.23)

    # permeability: specified mu = A^2 (line) and computed |Ez|^2 (open markers)
    ax_mu.plot(*d["mu_spec"].T, color=style.INK, lw=1.2, zorder=1)
    ax_mu.plot(*d["mu_comp"].T, "o", mfc="white", mec=style.WARM, mew=1.2, ms=4.6, zorder=2)
    ax_mu.text(1.15, 0.36, r"$\mu = A^2$ specified", color=style.INK, ha="left", va="center", fontsize=8.5)
    ax_mu.text(0.08, 0.8, r"$|E_z|^2$ computed", color=style.WARM, ha="left", va="center", fontsize=8.5)
    ax_mu.set_ylim(-0.03, 1.08)
    ax_mu.set_yticks([0, 0.5, 1], ["0", "0.5", "1"])
    ax_mu.set_ylabel(r"$\mu$", rotation=0, ha="right", va="center")
    ax_mu.tick_params(labelbottom=False)

    # permittivity for four wavelengths; lambda0/R = 1 is the case mapped on the right
    # drawn in the source order: where the curves merge (r > R) the later ones cover the earlier ones
    series = [("0.1", style.INK3, (0, (1.2, 1.6)), 1.4), ("1", style.WARM, "-", 1.3),
              ("2", style.COOL, (0, (4, 2)), 1.3), ("3", style.INK, "-", 1.3)]
    for lam, c, ls, lw in series:
        ax_eps.plot(*d[f"eps_{lam}"].T, color=c, ls=ls, lw=lw, label=lam)
    ax_eps.legend(title=r"$\lambda_0/R$", loc="lower right", ncol=2, handlelength=1.8, fontsize=8.5,
                  title_fontsize=8.5, labelspacing=0.3, columnspacing=1.2, borderaxespad=0.2)
    ax_eps.set_ylim(-70, 32)
    ax_eps.set_yticks([-60, -30, 0, 30])
    ax_eps.set_ylabel(r"$\varepsilon$", rotation=0, ha="right", va="center")
    ax_eps.set_xlabel(r"$r/R$")
    for ax in (ax_mu, ax_eps):
        ax.set_xlim(0, 2.65)
        ax.set_xticks([0, 1, 2])
        ax.yaxis.set_label_coords(-0.15, 0.5)
    style.panel(ax_mu, "a", x=-0.2)
    style.panel(ax_eps, "b", x=-0.2)

    # Re Ez for lambda0/R = 1: plane wave from the left, no scattered field outside
    x, y = d["field_x"], d["field_y"]
    half = 3.6
    ix = np.abs(x) <= half
    iy = np.abs(y) <= half
    f = d["field"].astype(float)[np.ix_(iy, ix)]
    im = ax_f.imshow(f, cmap=style.FIELD, vmin=-1, vmax=1, origin="upper", interpolation="bilinear",
                     extent=[x[ix][0], x[ix][-1], y[iy][-1], y[iy][0]])
    ax_f.set_xlim(-half, half)
    ax_f.set_ylim(-half, half)
    ax_f.set_xticks([-3, 0, 3])
    ax_f.set_yticks([-3, 0, 3])
    ax_f.set_xlabel(r"$x/R$")
    ax_f.set_ylabel(r"$y/R$", labelpad=1)
    for s in ax_f.spines.values():
        s.set_visible(False)
    style.panel(ax_f, "c", x=-0.12)
    cb = fig.colorbar(im, cax=cax, ticks=[-1, 0, 1])
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, width=0.6, labelsize=8.5)
    cb.set_label(r"Re $E_z$", labelpad=2)

    style.save(fig, "fig-invisible-profile")


if __name__ == "__main__":
    main()
