"""Execute a live notebook and store it, with its outputs, in src/data/notebooks/executed/.

    python scripts/notebooks/execute.py src/data/notebooks/gyptis.ipynb

The notebooks in src/data/notebooks/ are committed without outputs; the deploy
workflow runs this script whenever one of them (or the Binder environment)
changes. Run it locally only to preview outputs with `npm run dev`, in the
notebook's own environment (for gyptis: binder/environment.yml, with
PKG_CONFIG_PATH=$CONDA_PREFIX/lib/pkgconfig so dolfin finds its pkg-config
file). The page shows these outputs until a reader starts a live kernel. FEniCS
JIT chatter is dropped and PNG figures are re-encoded as WebP to keep the page
light.
"""

import base64
import io
import os
import sys

import nbformat
from nbclient import NotebookClient
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "src", "data", "notebooks", "executed")

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
            # A cell printing in a loop yields one stream output per flush: join them.
            prev = outputs[-1] if outputs else None
            if out.output_type == "stream" and prev and prev.output_type == "stream" and prev.name == out.name:
                prev.text += out.text
                continue
            outputs.append(out)
        cell.outputs = outputs
        cell.execution_count = None
    return nb


if __name__ == "__main__":
    src = sys.argv[1]
    nb = nbformat.read(src, as_version=4)
    NotebookClient(nb, timeout=1200, record_timing=False, resources={"metadata": {"path": os.path.dirname(src)}}).execute()
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, os.path.basename(src))
    nbformat.write(clean(nb), dst)
    print(f"wrote {os.path.relpath(dst)} ({os.path.getsize(dst) / 1024:.0f} kB)")
