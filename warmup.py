"""Compile, at image build time, the FEniCS forms the gyptis notebooks use.

FFC compiles each form once and dijitso caches the result, keyed by the form's
structure (elements, degrees, subdomain ids, coefficient shapes) rather than by
the mesh or the values of constants. So one solve per model on a coarse mesh
fills the cache for the whole notebook. Keep the calls below in step with the
notebooks in src/data/notebooks/: same models, degrees, geometry topology and
post-processing. A form left out costs a live reader one compilation, nothing
more.
"""

from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")

import numpy as np

import gyptis as gy
from gyptis.plot import plot


def warm_gyptis():
    # gyptis.ipynb: TM and TE scattering by a rod, cross sections.
    wl, R = 500, 300
    eps_rod = (4.2992 - 0.070425j) ** 2
    geom = gy.BoxPML(dim=2, box_size=(5 * wl, 5 * wl), pml_width=(wl, wl), Rcalc=0.9 * 3 * wl / 2)
    rod = geom.add_circle(0, 0, 0, R)
    rod, *bg = geom.fragment(rod, geom.box)
    geom.add_physical(bg, "box")
    geom.add_physical(rod, "rod")
    for pml in geom.pmls:
        geom.set_size(pml, wl / 2)
    geom.set_size("box", wl / 2)
    geom.set_size("rod", wl / 4)
    geom.build()
    pw = gy.PlaneWave(wavelength=wl, angle=0, dim=2, domain=geom.mesh, degree=2)
    plot(gy.utils.project_iterative(pw.expression.real, gy.dolfin.FunctionSpace(geom.mesh, "CG", 2)))
    for polarization in ("TM", "TE"):
        s = gy.Scattering(geom, dict(box=1, rod=eps_rod), dict(box=1, rod=1), pw, degree=2, polarization=polarization)
        s.solve()
        s.plot_field()
        s.get_cross_sections()
        s.extinction_cross_section()


def warm_waveguide():
    # anisotropic-waveguide.ipynb: modes of a uniaxial core, linear and quadratic elements.
    t, L, pml = 1, 3, 2
    geom = gy.geometry.LayeredBoxPML2D(
        t + 2 * L, thicknesses=OrderedDict(substrate=L, superstrate=L + t), pml_width=(pml, pml)
    )
    core = geom.add_rectangle(-t / 2, geom.y_position["superstrate"], 0, t, t)
    core, sup, sub = geom.fragment(core, [geom.layers["superstrate"], geom.layers["substrate"]])
    geom.add_physical(core, "core")
    geom.add_physical(sub, "substrate")
    geom.add_physical(sup, "superstrate")
    for p in geom.pmls:
        geom.set_size(p, 2)
    geom.set_size("substrate", 1)
    geom.set_size("superstrate", 1)
    geom.set_size("core", t / 4)
    geom.build()
    dx = geom.measure["dx"]
    dx_phys = dx("core") + dx("substrate") + dx("superstrate")
    V = gy.dolfin.FunctionSpace(geom.mesh, "CG", 1)
    epsilon = dict(core=2.31 * np.eye(3) - 0.12 * np.diag([1, 0, 0]), substrate=2.05, superstrate=2.05)
    for degree in ((1, 1), (2, 2)):
        simu = gy.Waveguide(geom, epsilon=epsilon, wavenumber=10, degree=degree)
        simu.eigensolve(n_eig=2, target=1.02 * 10 * 2.31**0.5, tol=1e-6, maximum_iterations=30)
        E = simu.solution["eigenvectors"][0]
        if degree == (1, 1):
            for i in range(2):
                for j in range(2):
                    gy.dolfin.assemble((E[i].real * E[j].real + E[i].imag * E[j].imag) * dx_phys)
                gy.utils.project_iterative(E[i].real, V)
                gy.utils.project_iterative(E[i].imag, V)


if __name__ == "__main__":
    warm_gyptis()
    warm_waveguide()
