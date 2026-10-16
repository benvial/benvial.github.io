"""Plate: a whispering-gallery quasinormal mode of a dielectric disk.

The complex resonance k R of the TM (E_z) mode with azimuthal order m is the
root of the exact dispersion relation

    n J_m'(n k R) H_m(k R) - J_m(n k R) H_m'(k R) = 0,

found by Newton iteration. The mode field (J_m inside, outgoing H_m outside,
times e^{i m theta}) is evaluated on a gmsh mesh refined at the rim. The
outside field grows with radius, as quasinormal modes do: the price of a
complex frequency.
"""

import gmsh
import numpy as np
from scipy.special import h1vp, hankel1, jv, jvp

import fem
import render

N_IN = 2.2  # refractive index of the disk
M = 7  # azimuthal order
R = 1.0


def dispersion(kR):
    return N_IN * jvp(M, N_IN * kR) * hankel1(M, kR) - jv(M, N_IN * kR) * h1vp(M, kR)


def find_root(z):
    for _ in range(60):
        h = 1e-7
        f = dispersion(z)
        df = (dispersion(z + h) - dispersion(z - h)) / (2 * h)
        dz = f / df
        z -= dz
        if abs(dz) < 1e-13:
            break
    return z


def mode(p, kR):
    r = np.hypot(p[:, 0], p[:, 1])
    th = np.arctan2(p[:, 1], p[:, 0])
    inside = r < R
    u = np.empty(len(p), complex)
    u[inside] = jv(M, N_IN * kR * r[inside] / R) / jv(M, N_IN * kR)
    u[~inside] = hankel1(M, kR * r[~inside] / R) / hankel1(M, kR)
    return u * np.exp(1j * M * th)


def main(out):
    guess = (M + 1.9) / N_IN  # WGM estimate
    kR = find_root(complex(guess, -0.01))
    Q = kR.real / (-2 * kR.imag)
    lam = 2 * np.pi * R / kR.real
    print(f"QNM m={M}: kR = {kR.real:.5f} {kR.imag:+.5f}i  Q = {Q:.0f}  lambda/R = {lam:.3f}")

    hw, hh = 4.0, 3.0  # view half sizes (4:3)
    cx = -0.9  # disk sits right of centre, spiral arms run left
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    box = occ.addRectangle(cx - hw - 0.5, -hh - 0.5, 0, 2 * hw + 1, 2 * hh + 1)
    disk = occ.addDisk(0, 0, 0, R, R)
    occ.fragment([(2, box)], [(2, disk)])
    occ.synchronize()
    surfs = [s for _, s in gmsh.model.getEntities(2)]
    inner = [s for s in surfs if abs(occ.getMass(2, s) - np.pi * R**2) < 1e-6]
    outer = [s for s in surfs if s not in inner]
    gmsh.model.addPhysicalGroup(2, inner, 1)
    gmsh.model.addPhysicalGroup(2, outer, 2)
    rim = [c for _, c in gmsh.model.getBoundary([(2, inner[0])], oriented=False)]
    f = gmsh.model.mesh.field
    d = f.add("Distance")
    f.setNumbers(d, "CurvesList", rim)
    f.setNumber(d, "Sampling", 400)
    th = f.add("Threshold")
    f.setNumber(th, "InField", d)
    f.setNumber(th, "SizeMin", lam / N_IN / 9)
    f.setNumber(th, "SizeMax", lam / 9)
    f.setNumber(th, "DistMin", 0.05)
    f.setNumber(th, "DistMax", 2.5)
    f.setAsBackgroundMesh(th)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    gmsh.finalize()
    print(f"mesh: {m.n} nodes, {len(m.t)} elements")

    u = mode(m.p, kR)
    # The outgoing field grows like exp(|Im k| r); compress so the rim
    # resonance and the radiating arms share the map.
    a = np.abs(u) / np.abs(u).max()
    v = u / np.maximum(np.abs(u), 1e-30) * np.tanh(3.0 * a)

    def draw(ax, pt):
        t = np.linspace(0, 2 * np.pi, 720)
        ax.plot(R * np.cos(t), R * np.sin(t), color=render.INK, lw=2.4 * pt, solid_capstyle="butt")

    render.plate(m, v, (cx - hw, cx + hw, -hh, hh), out, scale=1.0, intensity=0.92,
                 phase=0.35, edge_alpha=0.85, draw=draw)
    return kR, Q, m


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "qnm.png")
