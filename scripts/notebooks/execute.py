"""Execute a live notebook and store it, with its outputs, in src/data/notebooks/.

    python scripts/notebooks/execute.py ../gyptis-binder/gyptis.ipynb

Run it in the notebook's own environment (for gyptis: the environment.yml of
github.com/benvial/gyptis-binder, with PKG_CONFIG_PATH=$CONDA_PREFIX/lib/pkgconfig
so dolfin finds its pkg-config file). The page shows these outputs until a
reader starts a live kernel. FEniCS JIT chatter is dropped and PNG figures are
re-encoded as WebP to keep the page light.
"""

import base64
import io
import os
import sys

import nbformat
from nbclient import NotebookClient
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "src", "data", "notebooks")

NOISE = ("Calling FFC just-in-time (JIT) compiler",)


def clean(nb):
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        outputs = []
        for out in cell.outputs:
            if out.output_type == "stream":
                lines = [ln for ln in out.text.splitlines(True) if not ln.startswith(NOISE)]
                if not "".join(lines).strip():
                    continue
                out.text = "".join(lines)
            data = out.get("data", {})
            if "image/png" in data:
                img = Image.open(io.BytesIO(base64.b64decode(data["image/png"])))
                buf = io.BytesIO()
                img.save(buf, "webp", quality=88, method=6)
                del data["image/png"]
                data["image/webp"] = base64.b64encode(buf.getvalue()).decode()
            outputs.append(out)
        cell.outputs = outputs
        cell.execution_count = None
    return nb


if __name__ == "__main__":
    src = sys.argv[1]
    nb = nbformat.read(src, as_version=4)
    NotebookClient(nb, timeout=1200, resources={"metadata": {"path": os.path.dirname(src)}}).execute()
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, os.path.basename(src))
    nbformat.write(clean(nb), dst)
    print(f"wrote {os.path.relpath(dst)} ({os.path.getsize(dst) / 1024:.0f} kB)")
