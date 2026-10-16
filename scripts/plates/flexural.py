"""Plate: a topological interface quasinormal mode on a thin elastic plate.

After Vial et al., Phys. Rev. B 110, 174305 (2024) and Marti-Sabate et al.,
Phys. Rev. B 113, L140102 (2026). Point mass-spring resonators sit on an
infinite Kirchhoff plate (D = rho h = 1, so omega^2 = k^4). Each resonator
pushes on the plate with force t(k) w(r_j), t = M k^4 KR^4 / (KR^4 - k^4),
and the plate Green's function is

    G(r) = i / (8 k^2) [H0(k r) - H0(i k r)],   G(0) = i / (8 k^2).

Multiple scattering gives the nonlinear eigenvalue problem
(I / t(k) - G(k)) w = 0 whose complex roots k are the quasinormal modes.
The chain is an SSH array: dimers with short/long spacings swapped halfway,
so a domain wall sits in the middle and hosts an interface mode in the
Bragg gap. Its field radiates into the plate from the finite chain.
"""

import gmsh
import numpy as np
from scipy.special import hankel1

import fem
import render

KR = 2 * np.pi * 0.5  # resonator frequency in plate wavenumber units (period a = 1)
MASS = 0.6
N_CELL = 7  # dimers on each side of the wall
D_SHORT = 0.32


def positions():
    left = []
    x = 0.0
    for _ in range(N_CELL):  # walking left from the wall: long then short
        x -= 1 - D_SHORT
        left.append(x)
        x -= D_SHORT
        left.append(x)
    left = np.array(left[::-1])
    x = np.concatenate([left, [0.0], -left[::-1]])
    return np.stack([x, np.zeros_like(x)], 1)


def green(k, r):
    r = np.asarray(r, complex)
    out = np.full(r.shape, 1j / (8 * k**2), complex)
    nz = np.abs(r) > 1e-12
    out[nz] = 1j / (8 * k**2) * (hankel1(0, k * r[nz]) - hankel1(0, 1j * k * r[nz]))
    return out


def t_res(k):
    return MASS * k**4 * KR**4 / (KR**4 - k**4)


def matrix(k, P):
    d = np.hypot(*(P[:, None, :] - P[None, :, :]).transpose(2, 0, 1))
    return np.eye(len(P)) / t_res(k) - green(k, d)


def smallest(k, P):
    w, v = np.linalg.eig(matrix(k, P))
    i = np.argmin(np.abs(w))
    return w[i], v[:, i]


def newton(k, P):
    for _ in range(80):
        h = 1e-7
        f = smallest(k, P)[0]
        df = (smallest(k + h, P)[0] - smallest(k - h, P)[0]) / (2 * h)
        dk = f / df
        k -= dk
        if abs(dk) < 1e-12:
            break
    return k


def main(out):
    P = positions()
    # scan seeds across the band, keep converged roots, rank by localisation at the wall
    roots = []
    for kr in np.linspace(0.6 * KR, 1.2 * KR, 120):
        try:
            k = newton(complex(kr, -0.01), P)
        except (FloatingPointError, ZeroDivisionError):
            continue
        if k.real > 0 and -0.5 < k.imag < 0 and abs(smallest(k, P)[0]) < 1e-8:
            if all(abs(k - q) > 1e-6 for q in roots):
                roots.append(k)
    best, loc_best = None, -1
    for k in roots:
        w = smallest(k, P)[1]
        a = np.abs(w) ** 2
        loc = a[np.abs(P[:, 0]) < 1.6].sum() / a.sum()
        if loc > loc_best:
            best, loc_best = k, loc
    k = best
    w = smallest(k, P)[1]
    om = k**2  # omega = k^2 with D = rho h = 1
    Q = om.real / (-2 * om.imag)
    print(f"{len(roots)} QNMs found; interface mode k a = {k.real:.4f} {k.imag:+.5f}i  "
          f"omega = {(k**2).real:.4f} {(k**2).imag:+.5f}i  Q = {Q:.0f}  weight on wall = {loc_best:.2f}")

    hw, hh = 8.0, 6.0
    lam = 2 * np.pi / k.real
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    box = occ.addRectangle(-hw - 0.5, -hh - 0.5, 0, 2 * hw + 1, 2 * hh + 1)
    pts = [occ.addPoint(x, y, 0) for x, y in P]
    occ.synchronize()
    gmsh.model.mesh.embed(0, pts, 2, box)
    gmsh.model.addPhysicalGroup(2, [box], 1)
    f = gmsh.model.mesh.field
    d = f.add("Distance")
    f.setNumbers(d, "PointsList", pts)
    th = f.add("Threshold")
    f.setNumber(th, "InField", d)
    f.setNumber(th, "SizeMin", lam / 40)
    f.setNumber(th, "SizeMax", lam / 9)
    f.setNumber(th, "DistMin", 0.05)
    f.setNumber(th, "DistMax", 2.0)
    f.setAsBackgroundMesh(th)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    gmsh.finalize()
    print(f"mesh: {m.n} nodes, {len(m.t)} elements")

    tw = t_res(k) * w
    u = np.zeros(m.n, complex)
    for j, (x, y) in enumerate(P):
        u += tw[j] * green(k, np.hypot(m.p[:, 0] - x, m.p[:, 1] - y))
    # outgoing QNM fields grow with distance; compress like the QNM plate
    a = np.abs(u) / np.abs(u).max()
    v = u / np.maximum(np.abs(u), 1e-30) * np.tanh(3.0 * a)
    phase = np.angle(u[np.argmin(np.hypot(*m.p.T))])

    def draw(ax, pt):
        ax.plot(P[:, 0], P[:, 1], "o", ms=7.0 * pt, color=render.INK, mec=render.INK, lw=0)

    render.plate(m, v, (-hw, hw, -hh, hh), out, scale=1.0, intensity=0.9,
                 phase=phase, edge_alpha=0.85, draw=draw)
    return k, Q, m


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "flexural.png")
