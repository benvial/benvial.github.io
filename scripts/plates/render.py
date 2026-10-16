"""Render a solved field on its own mesh, in the site's field map.

Mirrors src/scripts/mesh-field.ts: element value = mean of nodal Re(u),
quantised into 96 bins of the --field-cmap diverging map (graphite, paper,
vermilion) faded towards the paper by `intensity`, with hairline mesh edges.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from PIL import Image

BINS = 96


def oklch(L, C=0.0, h=0.0):
    """oklch (L in 0-1) to sRGB 0-1."""
    a, b = C * np.cos(np.radians(h)), C * np.sin(np.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    rgb = np.array([
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    ])
    rgb = np.clip(rgb, 0, 1)
    return np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)


# --field-cmap in src/styles/global.css (cool pole first)
PAPER = oklch(0.985)
STOPS = [oklch(L) for L in (0.27, 0.42, 0.57, 0.73, 0.87)] + [PAPER] + [
    oklch(0.87, 0.066, 33), oklch(0.73, 0.133, 33), oklch(0.57, 0.180, 33),
    oklch(0.42, 0.154, 33), oklch(0.27, 0.098, 33)]
INK = oklch(0.20)
INK3 = oklch(0.50)
WARM = oklch(0.52, 0.19, 33)
MESH_EDGE = (*oklch(0.30), 0.24)


def lut(intensity):
    rgb = np.array([PAPER + intensity * (s - PAPER) for s in STOPS])
    t = np.linspace(0, 1, BINS) * (len(rgb) - 1)
    i = np.minimum(np.floor(t).astype(int), len(rgb) - 2)
    f = (t - i)[:, None]
    return rgb[i] + f * (rgb[i + 1] - rgb[i])


def element_values(m, u, phase=0.0):
    v = (u * np.exp(-1j * phase)).real
    return v[m.t].mean(axis=1)


def plate(m, u, view, out, size=(2400, 1800), scale=None, intensity=0.9,
          phase=0.0, edge_alpha=1.0, draw=None, mask=None, edge_lw=1.0, ss=2):
    """Draw the plate and save it as PNG.

    view: (xmin, xmax, ymin, ymax) in model units (aspect must match size).
    scale: field value mapped to the end of the map (default: 98th pct).
    draw: callback(ax) adding ink geometry on top of the field.
    mask: boolean per element; False elements are not drawn (holes).
    """
    v = element_values(m, u, phase)
    keep = np.ones(len(v), bool) if mask is None else mask
    x0, x1, y0, y1 = view
    inview = keep & (m.c[:, 0] > x0 - 0.2 * (x1 - x0)) & (m.c[:, 0] < x1 + 0.2 * (x1 - x0)) \
        & (m.c[:, 1] > y0 - 0.2 * (y1 - y0)) & (m.c[:, 1] < y1 + 0.2 * (y1 - y0))
    if scale is None:
        scale = np.percentile(np.abs(v[inview]), 98)
    b = np.round((np.clip(v / scale, -1, 1) + 1) / 2 * (BINS - 1)).astype(int)
    colors = lut(intensity)[b]

    W, H = size[0] * ss, size[1] * ss
    dpi = 100
    fig = plt.figure(figsize=(W / dpi, H / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)
    polys = m.p[m.t[inview]]
    px = ss * 0.5  # seam sealing like the site's 0.5px stroke
    ax.add_collection(PolyCollection(polys, facecolors=colors[inview], edgecolors=colors[inview],
                                     linewidths=px * 72 / dpi, antialiased=True))
    # fade edges where the mesh is refined so dense zones keep their tone
    h = np.sqrt(m.area()[inview])
    fade = np.clip(h / np.percentile(h, 70), 0.3, 1.0)
    ec = np.zeros((len(h), 4))
    ec[:, :3] = MESH_EDGE[:3]
    ec[:, 3] = MESH_EDGE[3] * edge_alpha * fade
    ax.add_collection(PolyCollection(polys, facecolors="none", edgecolors=ec,
                                     linewidths=edge_lw * ss * 72 / dpi, antialiased=True))
    if draw is not None:
        draw(ax, ss * 72 / dpi)
    fig.savefig(out + ".tmp.png", dpi=dpi, facecolor=PAPER)
    plt.close(fig)
    img = Image.open(out + ".tmp.png").convert("RGB").resize(size, Image.LANCZOS)
    if out.endswith(".webp"):
        img.save(out, quality=90, method=6)
    else:
        img.save(out, optimize=True)
    os.remove(out + ".tmp.png")
    return scale
