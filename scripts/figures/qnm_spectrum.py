"""Schematic spectrum of an open resonator truncated by PML (after Vial et al., PRA 2014)."""

import numpy as np
import matplotlib.pyplot as plt

import style


def main():
    style.use()
    fig, ax = plt.subplots(figsize=(6.2, 3.9))
    ax.set_xlim(-0.35, 10.4)
    ax.set_ylim(-5.6, 1.1)
    ax.axis("off")

    arrow = dict(arrowstyle="-|>,head_length=0.5,head_width=0.22", color=style.INK, lw=0.8,
                 shrinkA=0, shrinkB=0)
    ax.annotate("", xy=(10.3, 0), xytext=(-0.3, 0), arrowprops=arrow)
    ax.annotate("", xy=(0, 1.05), xytext=(0, -5.5), arrowprops=arrow)
    ax.text(10.3, 0.28, r"$\mathrm{Re}\,\omega$", ha="right", va="bottom")
    ax.text(0.18, 1.0, r"$\mathrm{Im}\,\omega$", ha="left", va="top")

    # continuous spectrum on the real axis, rotated by the PML stretch
    phi = np.radians(32)
    L = 9.4
    ax.plot([0, 9.9], [0, 0], color=style.INK3, lw=1.0, ls=(0, (4, 3)))
    ax.plot([0, L * np.cos(phi)], [0, -L * np.sin(phi)], color=style.INK, lw=1.4)
    t = np.linspace(0, phi, 30)
    ax.plot(1.6 * np.cos(t), -1.6 * np.sin(t), color=style.INK, lw=0.7)
    ax.text(1.85 * np.cos(phi / 2), -1.85 * np.sin(phi / 2), r"$\phi$", ha="left", va="center")
    ax.text(L * np.cos(phi) - 0.1, -L * np.sin(phi) - 0.15,
            "continuous spectrum\nrotated by the PML", ha="right", va="top", color=style.INK2)

    # guided modes: real eigenfrequencies
    gx = [1.3, 2.4, 3.3, 4.7, 5.0]
    ax.plot(gx, np.zeros_like(gx), "x", color=style.INK, ms=6, mew=1.3)
    ax.text(1.3, 0.3, "guided modes", ha="left", va="bottom", color=style.INK2)

    # leaky modes above the rotated line are revealed, those below stay hidden
    tan = np.tan(phi)
    leaky = np.array([[3.2, -0.95], [5.3, -1.0], [8.6, -0.5], [5.0, -2.1], [6.6, -2.3],
                      [2.6, -3.0], [4.6, -3.5], [3.5, -4.6], [7.4, -4.2]])
    shown = leaky[:, 1] > -tan * leaky[:, 0]
    ax.plot(*leaky[shown].T, "o", color=style.WARM, ms=6.5)
    ax.plot(*leaky[~shown].T, "o", mfc="white", mec=style.INK3, mew=1.1, ms=6.5)
    ax.text(9.9, -1.35, "leaky modes revealed\n(quasi-normal modes)", ha="right", va="top", color=style.WARM)
    ax.text(0.4, -4.05, "leaky modes\nstill hidden", ha="left", va="top", color=style.INK3)

    style.save(fig, "fig-qnm-spectrum")


if __name__ == "__main__":
    main()
