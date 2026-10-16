"""Regenerate the research cover plates into src/content/research/.

    python scripts/plates/build.py

Each plate is a real computation (see the module docstrings); the numbers it
prints are the ones quoted in the plate captions.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "..", "..", "src", "content", "research")

import flexural  # noqa: E402
import homog  # noqa: E402
import invisible  # noqa: E402
import mim  # noqa: E402
import qnm  # noqa: E402
import topopt  # noqa: E402

SLUG = {"qnm": "qnms", "invisible": "invisible", "mim": "meta", "topopt": "topopt",
        "flexural": "elastic", "homog": "homogenization"}  # research entry ids

if __name__ == "__main__":
    which = sys.argv[1:] or list(SLUG)
    for name in which:
        print(f"== {name}")
        mod = {"qnm": qnm, "invisible": invisible, "mim": mim, "topopt": topopt,
               "flexural": flexural, "homog": homog}[name]
        mod.main(os.path.join(OUT, f"plate-{SLUG[name]}.webp"))
