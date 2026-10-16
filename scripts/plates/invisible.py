"""Plate: an invisible inhomogeneous medium that shapes field amplitude.

Following Vial, Liu, Horsley, Philbin & Hao, Phys. Rev. B 94, 245119 (2016):
for E_z polarisation, div(mu^-1 grad E) + k^2 eps E = 0 admits the
scattering-free solution E = A(x, y) exp(i k d.r) (any direction d) when

    mu  = A^2,
    eps = 1/A^2 - div(grad A / A^2) / (k^2 A).

We prescribe an amplitude A that dips to 0.2 in two lobes, build (eps, mu)
from it, then solve the full scattering problem with P1 FEM and PML (no
knowledge of the expected answer). The solve returns straight wavefronts,
the prescribed quiet zones, and no scattered wave.
"""

import gmsh
import numpy as np

import fem
import render

K = 2 * np.pi  # wavelength 1
THETA = np.radians(25)  # incidence; the invisibility condition holds for any direction
LOBES = [(-0.5, -0.05, 0.36, 0.85), (0.72, 0.18, 0.26, 0.75)]  # x, y, sigma, depth


def amplitude(x, y):
    """A, grad A, laplacian A (analytic)."""
    A = np.ones_like(x)
    Ax = np.zeros_like(x)
    Ay = np.zeros_like(x)
    lap = np.zeros_like(x)
    for x0, y0, s, d in LOBES:
        g = d * np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * s**2))
        gx = -(x - x0) / s**2 * g
        gy = -(y - y0) / s**2 * g
        A -= g
        Ax -= gx
        Ay -= gy
        lap -= g * (((x - x0) ** 2 + (y - y0) ** 2) / s**4 - 2 / s**2)
    return A, Ax, Ay, lap


def material(x, y):
    A, Ax, Ay, lap = amplitude(x, y)
    mu = A**2
    # div(grad A / A^2) = lap/A^2 - 2 |grad A|^2 / A^3
    div = lap / A**2 - 2 * (Ax**2 + Ay**2) / A**3
    eps = 1 / A**2 - div / (K**2 * A)
    return eps, mu


def main(out):
    hw, hh = 1.9, 1.425  # view (4:3)
    L, D = 0.4, 0.6  # margin to PML, PML depth
    X, Y = hw + L, hh + L
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    occ.addRectangle(-X - D, -Y - D, 0, 2 * (X + D), 2 * (Y + D))
    occ.synchronize()
    gmsh.model.addPhysicalGroup(2, [1], 1)
    gmsh.model.addPhysicalGroup(1, [c for _, c in gmsh.model.getEntities(1)], 9)
    # refine where the medium varies
    f = gmsh.model.mesh.field
    pts = [occ.addPoint(x0, y0, 0) for x0, y0, _, _ in LOBES]
    occ.synchronize()
    d = f.add("Distance")
    f.setNumbers(d, "PointsList", pts)
    th = f.add("Threshold")
    f.setNumber(th, "InField", d)
    f.setNumber(th, "SizeMin", 1 / 24)
    f.setNumber(th, "SizeMax", 1 / 15)
    f.setNumber(th, "DistMin", 0.35)
    f.setNumber(th, "DistMax", 1.4)
    f.setAsBackgroundMesh(th)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints"):
        gmsh.option.setNumber(opt, 0)
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    outer = m.boundary_nodes(9)
    gmsh.finalize()
    print(f"mesh: {m.n} nodes, {len(m.t)} elements")

    eps, mu = material(m.c[:, 0], m.c[:, 1])
    print(f"eps in [{eps.min():.2f}, {eps.max():.2f}], mu in [{mu.min():.3f}, {mu.max():.3f}]")
    box = (-X, X, -Y, Y)
    axx, ayy, b = fem.pml_coefficients(m, eps, mu, box, D, K)
    A = fem.assemble(m, axx, ayy, b, K)
    # scattered-field rhs: contrast operator acting on the incident wave
    one = np.ones(len(m.t))
    a0x, a0y, b0 = fem.pml_coefficients(m, one, one, box, D, K)
    A0 = fem.assemble(m, a0x, a0y, b0, K)
    uinc = np.exp(1j * K * (m.p[:, 0] * np.cos(THETA) + m.p[:, 1] * np.sin(THETA)))
    us, _ = fem.solve(A, -(A - A0) @ uinc, dirichlet=outer, g=np.zeros(len(outer)))
    u = uinc + us

    # check against the prescribed field
    Aex = amplitude(m.p[:, 0], m.p[:, 1])[0] * uinc
    phys = (np.abs(m.p[:, 0]) < X) & (np.abs(m.p[:, 1]) < Y)
    far = phys & (np.min([np.hypot(m.p[:, 0] - x0, m.p[:, 1] - y0) for x0, y0, _, _ in LOBES], 0) > 2.2)
    err = np.linalg.norm((u - Aex)[phys]) / np.linalg.norm(Aex[phys])
    print(f"relative error vs A e^{ik d.r}: {err:.3%}; max |u_s| far from medium: {np.abs((u - uinc)[far]).max():.3f}")

    def draw(ax, pt):
        # iso-lines of mu: the medium is there, the wave does not notice it
        gx, gy = np.meshgrid(np.linspace(-hw, hw, 800), np.linspace(-hh, hh, 600))
        _, mug = material(gx, gy)
        ax.contour(gx, gy, mug, levels=[0.12, 0.3, 0.55, 0.8], colors=[render.INK],
                   linewidths=1.7 * pt, linestyles="solid")

    render.plate(m, u, (-hw, hw, -hh, hh), out, scale=1.0, intensity=0.7, draw=draw)
    return err


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "invisible.png")
