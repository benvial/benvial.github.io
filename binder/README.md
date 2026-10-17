# Binder environment

mybinder.org builds this folder into the kernel image for the live notebooks in
`src/data/notebooks/` (see `src/components/prose/Notebook.astro`).

- `environment.yml`: gyptis from conda-forge, pinned.
- `postBuild`: executes `gyptis.ipynb` (fetched from main) once at build time to warm the FEniCS JIT cache.
- `start`: points live kernels at that cache and matches BLAS/OpenMP threads to the CPU quota.

mybinder.org builds one image per commit, and a build takes about ten minutes.
So pages launch from the `binder` branch rather than `main`: the Binder workflow
(`.github/workflows/binder.yml`) copies this folder there whenever it changes on
main, builds the image, and only then moves the branch. Edits to the site or the
notebook leave the branch, and the image, alone. Don't commit to `binder` by hand.
