"""Absorption cross section of a triangular rod: QMEM with M = 5, 10, 50 modes against the full-wave reference.

Data extracted from Fig. 7 of Vial et al., Phys. Rev. A 89, 023829 (2014).
"""

import os

import numpy as np
import matplotlib.pyplot as plt

import style

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fig-qmem-convergence.npz")


def main():
    style.use()
    # Mona Sans (latin subset) has no µ: fall back per glyph.
    plt.rcParams["font.family"] = ["Mona Sans", "DejaVu Sans"]
    d = np.load(DATA)
    fig, ax = plt.subplots(figsize=(6.2, 3.3))

    ax.plot(d["ref_lam"], d["ref_sigma"], color=style.INK, lw=2.0, zorder=2, label="Full-wave reference")
    series = [  # key, label, colour, marker, size, filled
        ("m5", "QMEM, $M = 5$", style.INK3, "s", 4.2, False),
        ("m10", "QMEM, $M = 10$", style.COOL, "v", 4.4, True),
        ("m50", "QMEM, $M = 50$", style.WARM, "o", 5.0, False),
    ]
    for key, label, c, m, ms, filled in series:
        lam, sig = d[f"{key}_lam"], d[f"{key}_sigma"]
        ax.plot(lam, sig, m, ls=(0, (2, 2)) if key == "m5" else "none", lw=0.8, color=c, ms=ms,
                mfc=c if filled else "white", mec=c, mew=1.1, zorder=4 if key == "m50" else 3, label=label)
    ax.legend(loc="upper left", handlelength=2.2, borderaxespad=0.2, labelspacing=0.35)

    ax.set_xlim(8.97, 11.03)
    ax.set_ylim(0.62, 2.0)
    ax.set_xticks(np.arange(9, 11.01, 0.5))
    ax.set_xlabel(r"Wavelength $\lambda$ ($\mathrm{\mu}$m)")
    ax.set_ylabel("Absorption cross section (µm)")
    style.save(fig, "fig-qmem-convergence")


if __name__ == "__main__":
    main()
