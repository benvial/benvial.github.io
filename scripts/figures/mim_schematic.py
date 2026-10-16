"""Cross-section of the metal-insulator-metal absorber: Cr rods on amorphous Si over a Cr film, on a Si substrate.

Geometry from Fig. 1a of Vial et al., J. Opt. Soc. Am. B 31, 1339 (2014) (d = 4.8 µm, D = d/2,
h_r = 100 nm, h_i = 530 nm, h_m = 200 nm); vertical scale exaggerated three times.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import style

D_PER = 4.8  # period d (µm)
D_ROD = 0.5 * D_PER  # rod diameter D
VS = 3.0  # vertical exaggeration
H_M, H_I, H_R = 0.2 * VS, 0.53 * VS, 0.1 * VS
H_SUB = 0.9


def dim(ax, x0, x1, y, label, below=False, **kw):
    """Horizontal dimension arrow with a centred label."""
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>,head_length=0.35,head_width=0.13", color=style.INK, lw=0.7,
                                shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + (-0.12 if below else 0.12), label, ha="center", va="top" if below else "bottom", **kw)


def vdim(ax, x, y0, y1, label):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="<|-|>,head_length=0.3,head_width=0.11", color=style.INK, lw=0.7,
                                shrinkA=0, shrinkB=0))
    ax.text(x - 0.15, (y0 + y1) / 2, label, ha="right", va="center")


def main():
    style.use()
    plt.rcParams["font.family"] = ["Mona Sans", "DejaVu Sans"]
    metal = style.oklch(0.30)
    insul = style.oklch(0.89)
    subst = style.oklch(0.955)
    W = 3 * D_PER
    y_i, y_r, y_t = H_M, H_M + H_I, H_M + H_I + H_R

    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    ax.set_aspect("equal")
    ax.axis("off")

    edge = dict(ec=style.INK, lw=0.8)
    ax.add_patch(Rectangle((0, -H_SUB), W, H_SUB, fc=subst, lw=0))
    ax.plot([0, 0], [-H_SUB, 0], color=style.INK, lw=0.8)
    ax.plot([W, W], [-H_SUB, 0], color=style.INK, lw=0.8)
    ax.add_patch(Rectangle((0, 0), W, H_M, fc=metal, **edge))
    ax.add_patch(Rectangle((0, y_i), W, H_I, fc=insul, **edge))
    for k in range(3):
        xc = D_PER / 2 + k * D_PER
        ax.add_patch(Rectangle((xc - D_ROD / 2, y_r), D_ROD, H_R, fc=metal, **edge))

    # material labels, right margin
    lab = dict(ha="left", va="center", color=style.INK2, fontsize=9)
    xl = W + 0.35
    ax.text(xl, y_r + H_R / 2 + 0.05, "Cr rods", **lab)
    ax.text(xl, y_i + H_I / 2, "amorphous Si", **lab)
    ax.text(xl, H_M / 2, "Cr", **lab)
    ax.text(xl, -H_SUB / 2, "Si substrate", **lab)

    # period d between cell boundaries, rod diameter D on the middle rod
    for x in (D_PER, 2 * D_PER):
        ax.plot([x, x], [y_r, y_t + 1.55], color=style.INK3, lw=0.6, ls=(0, (2, 2)))
    dim(ax, D_PER, 2 * D_PER, y_t + 1.3, "$d$")
    dim(ax, 1.5 * D_PER - D_ROD / 2, 1.5 * D_PER + D_ROD / 2, y_t + 0.35, "$D$")

    # insulator thickness, left margin
    vdim(ax, -0.4, y_i, y_r, "$h_\\mathrm{i}$")

    # incident plane wave on the left rod, angle theta_0 from the normal
    th = np.radians(30)
    x0, y0 = D_PER / 2, y_t + 0.08
    L = 3.3
    ax.plot([x0, x0], [y0, y0 + L * 0.95], color=style.INK3, lw=0.6, ls=(0, (2, 2)))
    ax.annotate("", xy=(x0, y0), xytext=(x0 - L * np.sin(th), y0 + L * np.cos(th)),
                arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.25", color=style.WARM, lw=1.6,
                                shrinkA=0, shrinkB=0))
    t = np.linspace(0, th, 30)
    r = 1.7
    ax.plot(x0 - r * np.sin(t), y0 + r * np.cos(t), color=style.INK, lw=0.6)
    ax.text(x0 - (r + 0.2) * np.sin(th / 2) + 0.05, y0 + (r + 0.2) * np.cos(th / 2), "$\\theta_0$",
            ha="right", va="bottom")
    ax.text(x0 - L * np.sin(th) - 0.1, y0 + L * np.cos(th), "incident", ha="right", va="center",
            color=style.WARM, fontsize=9)

    ax.set_xlim(-1.4, W + 3.4)
    ax.set_ylim(-H_SUB - 0.05, y_t + L * np.cos(th) + 0.6)
    style.save(fig, "fig-mim-schematic")


if __name__ == "__main__":
    main()
