"""Field of a point source in a finite dispersive stack, exact against the high-frequency homogenization envelope.

Data extracted from Fig. 10b (arXiv numbering) of Touboul et al., Multiscale Model. Simul. 22, 1136 (2024).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-hfh-field.npz")


def main():
    style.use()
    d = np.load(DATA)
    fig, ax = plt.subplots(figsize=(6.2, 2.4))

    ax.axhline(0, color=style.RULE, lw=0.7, zorder=0)
    ax.plot(*d["exact"].T, color=style.INK, lw=0.9)
    ax.plot(*d["envelope"].T, color=style.WARM, lw=1.7, ls=(0, (3.2, 2.2)))

    ax.set_xlim(0, 20)
    ax.set_ylim(-0.2, 1.08)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel(r"Position $\xi$ (periods)")
    ax.set_ylabel(r"Re $u$")

    ax.text(3.2, 0.62, "HFH envelope", color=style.WARM, ha="center", va="bottom")
    ax.text(16.2, 0.72, "exact field", color=style.INK, ha="left", va="bottom")

    style.save(fig, "fig-hfh-field")


if __name__ == "__main__":
    main()
