# Binder environment

mybinder.org builds this folder into the kernel image for the live notebooks in
`src/data/notebooks/` (see `src/components/prose/Notebook.astro`). Only this
folder is read: the site's `package.json` at the root is ignored.

- `environment.yml`: gyptis from conda-forge, pinned.
- `postBuild`: executes `gyptis.ipynb` once at build time to warm the FEniCS JIT cache.
- `start`: points live kernels at that cache and matches BLAS/OpenMP threads to the CPU quota.

mybinder.org builds one image per commit, so pages pin `ref` to a commit that
holds this folder rather than `main`: otherwise every push to the site would
trigger a rebuild. After changing anything here (or the notebook code that
`postBuild` warms up), commit, then point the `ref` of each `<Notebook>` at that
commit.
