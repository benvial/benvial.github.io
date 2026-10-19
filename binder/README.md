# Binder environment

mybinder.org builds this folder into the kernel image for the live notebooks in
`src/data/notebooks/` (see `src/components/prose/Notebook.astro`).

- `environment.yml`: gyptis, nannos, protis and plotly from conda-forge, pinned, shared by all notebooks. CPU builds only: nannos pulls jax and VTK, whose CUDA variants would add about 500 MB.
- `postBuild`: runs `warmup.py` at build time, which compiles the FEniCS forms of the gyptis notebooks (one coarse solve per model) so the JIT cache ships with the image. Keep it in step with those notebooks: a form it misses costs a live reader one compilation.
- `start`: points live kernels at that cache and matches BLAS/OpenMP threads to the CPU quota.

mybinder.org builds one image per commit, and a build takes about ten minutes.
So pages launch from the `binder` branch rather than `main`: the Binder workflow
(`.github/workflows/binder.yml`) copies this folder there whenever it changes on
main, builds the image, and only then moves the branch. Edits to the site or the
notebook leave the branch, and the image, alone. Don't commit to `binder` by hand.
