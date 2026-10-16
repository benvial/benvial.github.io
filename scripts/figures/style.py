"""Matplotlib style for the figures redrawn on the research pages.

Same palette as the cover plates (scripts/plates/render.py, itself mirroring
src/styles/global.css): ink and greys for structure, one warm (vermilion)
accent, and the site's diverging field map. Type is Mona Sans, instanced
from the variable font shipped in node_modules into a local cache.
"""

import logging
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "plates"))
OUT = os.path.join(ROOT, "src", "content", "research")

import render  # noqa: E402


def oklch(*a):
    return tuple(float(c) for c in render.oklch(*a))


PAPER = tuple(float(c) for c in render.PAPER)
STOPS = [tuple(float(c) for c in s) for s in render.STOPS]
INK = oklch(0.20)
INK2 = oklch(0.40)
INK3 = oklch(0.50)
RULE = oklch(0.87)
COOL = oklch(0.45)
WARM = oklch(0.52, 0.19, 33)
WARM_PALE = oklch(0.80, 0.09, 33)
# A second, cool hue for the rare plot that needs two coloured series.
BLUE = oklch(0.50, 0.11, 245)

FIELD = LinearSegmentedColormap.from_list("field", STOPS)
# Sequential maps: paper to vermilion (magnitudes), paper to graphite.
WARM_SEQ = LinearSegmentedColormap.from_list("warm", [PAPER] + STOPS[6:])
GREY_SEQ = LinearSegmentedColormap.from_list("grey", [PAPER] + STOPS[4::-1])

FONTS = os.path.join(HERE, "__fontcache__")


def _instance(src, wght, name):
    """Static TTF of the Mona Sans variable font at width 100, weight `wght`."""
    path = os.path.join(FONTS, name)
    if not os.path.exists(path):
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont

        os.makedirs(FONTS, exist_ok=True)
        font = TTFont(os.path.join(ROOT, "node_modules", "@fontsource-variable", "mona-sans", "files", src))
        font.flavor = None
        instantiateVariableFont(font, {"wdth": 100, "wght": wght}, inplace=True)
        sub = "Italic" if "italic" in src else "Regular"
        for rec in list(font["name"].names):  # the default instance is named ExtraLight
            if rec.nameID in (1, 16):
                rec.string = "Mona Sans"
            elif rec.nameID in (2, 17):
                rec.string = sub
        font.save(path)
    font_manager.fontManager.addfont(path)


def use():
    """Apply the site style to matplotlib."""
    # The DejaVu / STIX fallbacks have no 620 weight or cursive face; Mona Sans is used regardless.
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    _instance("mona-sans-latin-standard-normal.woff2", 400, "MonaSans-Regular.ttf")
    _instance("mona-sans-latin-standard-normal.woff2", 620, "MonaSans-SemiBold.ttf")
    _instance("mona-sans-latin-standard-italic.woff2", 400, "MonaSans-Italic.ttf")
    plt.rcParams.update({
        "font.family": ["Mona Sans", "DejaVu Sans"],  # DejaVu supplies Greek (λ, µ)
        "font.size": 9.5,
        "font.weight": 400,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Mona Sans",
        "mathtext.it": "Mona Sans:italic",
        "mathtext.bf": "Mona Sans:weight=620",
        "mathtext.fallback": "stixsans",
        "text.color": INK,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 9.5,
        "axes.titleweight": 620,
        "axes.titlelocation": "left",
        "axes.labelsize": 9.5,
        "axes.prop_cycle": matplotlib.cycler(color=[WARM, INK, COOL, BLUE]),
        "xtick.color": INK2,
        "ytick.color": INK2,
        "xtick.labelcolor": INK3,
        "ytick.labelcolor": INK3,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "lines.linewidth": 1.6,
        "lines.markersize": 4,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "grid.color": RULE,
        "grid.linewidth": 0.6,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.dpi": 200,
        "image.cmap": "field",
    })
    for cmap in (FIELD, WARM_SEQ, GREY_SEQ):
        if cmap.name not in matplotlib.colormaps:
            matplotlib.colormaps.register(cmap)


def save(fig, name):
    """Write src/content/research/<name>.webp at a width that suits 40rem prose."""
    import io

    from PIL import Image

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    buf.seek(0)
    path = os.path.join(OUT, f"{name}.webp")
    Image.open(buf).convert("RGB").save(path, quality=92, method=6)
    print("wrote", os.path.relpath(path, ROOT))


def panel(ax, letter, x=-0.02, y=1.02):
    """Panel letter, set like the site's labels (semibold, lower case)."""
    ax.text(x, y, letter, transform=ax.transAxes, ha="right", va="bottom", fontsize=10.5, fontweight=620,
            color=INK)


def colorbar(fig, mappable, ax, label=None, **kw):
    """Thin colorbar without a frame."""
    cb = fig.colorbar(mappable, ax=ax, fraction=0.046, pad=0.03, **kw)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, width=0.6, labelsize=8.5)
    if label:
        cb.set_label(label)
    return cb
