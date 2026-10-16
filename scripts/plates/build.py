"""Regenerate the four research cover plates into src/content/research/.

    python scripts/plates/build.py

Each plate is a real computation (see the module docstrings); the numbers it
prints are the ones quoted in the plate captions.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "..", "..", "src", "content", "research")

import invisible  # noqa: E402
import mim  # noqa: E402
import qnm  # noqa: E402
import topopt  # noqa: E402

SLUG = {"qnm": "qnms", "invisible": "invisible", "mim": "meta", "topopt": "topopt"}  # research entry ids

if __name__ == "__main__":
    which = sys.argv[1:] or ["qnm", "invisible", "mim", "topopt"]
    for name in which:
        print(f"== {name}")
        mod = {"qnm": qnm, "invisible": invisible, "mim": mim, "topopt": topopt}[name]
        mod.main(os.path.join(OUT, f"plate-{SLUG[name]}.webp"))
