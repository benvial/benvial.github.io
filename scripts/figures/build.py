"""Redraw the research page figures into src/content/research/fig-*.webp.

    python scripts/figures/build.py [name ...]

Each figure script plots data extracted from the original paper figure
(stored in scripts/figures/data/), in the site style (style.py).
"""

import glob
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SKIP = {"build", "style"}

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(
        os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(HERE, "*.py"))
    )
    for name in names:
        if name in SKIP:
            continue
        print(f"== {name}")
        importlib.import_module(name).main()
