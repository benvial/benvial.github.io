"""Plate: a point source in a crystal of dispersive rods, at the band edge.

After Touboul et al., Multiscale Model. Simul. 22, 1136 (2024). A square
lattice (period a = 1) of rods whose permittivity follows a Lorentz law

    eps(k) = EPS_INF + D_EPS KR^2 / (KR^2 - k^2)

carries TM (E_z) waves. Two P1 FEM computations:

1. One cell with Bloch conditions: the first band tops out at the M point
   (k0, solved self-consistently in eps(k)); finite differences of the
   dispersive Bloch problem give the HFH coefficient T in
   k^2 ~ k0^2 + T |kappa|^2 (kappa measured from M).
2. A finite 16 x 12 crystal in air with PML, driven by a point source at a
   frequency just inside the band. The field is the M-point Bloch mode (a
   checkerboard, sign flip per cell) under a slow envelope, which HFH
   reduces to the effective equation T lap f + (k^2 - k0^2) f = source.
"""

import gmsh
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

import fem
import render

EPS_INF, D_EPS, KR = 6.0, 3.0, 2 * np.pi * 0.6
R_ROD = 0.3
NX, NY = 16, 12
ENV_CELLS = 8.0  # target envelope wavelength in cells


def eps(k):
    return EPS_INF + D_EPS * KR**2 / (KR**2 - k**2)


def cell_mesh(h):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    sq = occ.addRectangle(0, 0, 0, 1, 1)
    rod = occ.addDisk(0.5, 0.5, 0, R_ROD, R_ROD)
    occ.fragment([(2, sq)], [(2, rod)])
    occ.synchronize()
    surfs = [s for _, s in gmsh.model.getEntities(2)]
    inner = [s for s in surfs if abs(occ.getMass(2, s) - np.pi * R_ROD**2) < 1e-6]
    gmsh.model.addPhysicalGroup(2, inner, 1)
    gmsh.model.addPhysicalGroup(2, [s for s in surfs if s not in inner], 2)
    edges = {}
    for _, c in gmsh.model.getEntities(1):
        x0, y0, _, x1, y1, _ = gmsh.model.getBoundingBox(1, c)
        for name, ok in (("l", x1 < 1e-6), ("r", x0 > 1 - 1e-6), ("b", y1 < 1e-6), ("t", y0 > 1 - 1e-6)):
            if ok:
                edges[name] = c
    gmsh.model.mesh.setPeriodic(1, [edges["r"]], [edges["l"]], [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
    gmsh.model.mesh.setPeriodic(1, [edges["t"]], [edges["b"]], [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1])
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    gmsh.finalize()
    return m


def bloch_basis(m, kx, ky):
    """T maps free nodes to all nodes, u = T u_free, with u(x+1) = e^{ik} u(x)."""
    tol = 1e-8
    p = m.p
    key = {}
    for i, (x, y) in enumerate(p):
        if x < 1 - tol and y < 1 - tol:
            key[(round(x, 7), round(y, 7))] = i
    free = sorted(key.values())
    col = {n: j for j, n in enumerate(free)}
    rows, cols, vals = [], [], []
    for i, (x, y) in enumerate(p):
        ph = 1.0
        if x > 1 - tol:
            x -= 1
            ph *= np.exp(1j * kx)
        if y > 1 - tol:
            y -= 1
            ph *= np.exp(1j * ky)
        rows.append(i)
        cols.append(col[key[(round(x, 7), round(y, 7))]])
        vals.append(ph)
    return sp.csr_matrix((vals, (rows, cols)), shape=(m.n, len(free)))


def band1(m, kx, ky, k=2.0):
    """First TM band at Bloch vector (kx, ky), self-consistent in eps(k)."""
    T = bloch_basis(m, kx, ky)
    one = np.ones(len(m.t))
    K = fem.assemble(m, one, one, one, 0.0)
    rod = m.tag == 1
    for _ in range(50):
        w = np.where(rod, eps(k), 1.0)
        Kr = (T.conj().T @ K @ T).tocsc()
        Mr = (T.conj().T @ fem.mass(m, w) @ T).tocsc()
        lam, vec = spla.eigsh(Kr, k=1, M=Mr, sigma=0.5 * k**2, which="LM")
        k_new = np.sqrt(lam[0].real)
        if abs(k_new - k) < 1e-12:
            break
        k = k_new
    return k, T @ vec[:, 0]


def crystal_mesh(h_rod, h_air, pad, depth):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    X, Y = NX / 2 + pad, NY / 2 + pad
    box = occ.addRectangle(-X - depth, -Y - depth, 0, 2 * (X + depth), 2 * (Y + depth))
    rods = [(2, occ.addDisk(-NX / 2 + i + 0.5, -NY / 2 + j + 0.5, 0, R_ROD, R_ROD))
            for i in range(NX) for j in range(NY)]
    occ.fragment([(2, box)], rods)
    occ.synchronize()
    surfs = [s for _, s in gmsh.model.getEntities(2)]
    inner = [s for s in surfs if abs(occ.getMass(2, s) - np.pi * R_ROD**2) < 1e-6]
    gmsh.model.addPhysicalGroup(2, inner, 1)
    gmsh.model.addPhysicalGroup(2, [s for s in surfs if s not in inner], 2)
    f = gmsh.model.mesh.field
    b = f.add("Box")
    f.setNumber(b, "VIn", h_rod)
    f.setNumber(b, "VOut", h_air)
    f.setNumber(b, "XMin", -NX / 2 - 0.2)
    f.setNumber(b, "XMax", NX / 2 + 0.2)
    f.setNumber(b, "YMin", -NY / 2 - 0.2)
    f.setNumber(b, "YMax", NY / 2 + 0.2)
    f.setNumber(b, "Thickness", 1.0)
    f.setAsBackgroundMesh(b)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    gmsh.finalize()
    return m, (-X, X, -Y, Y)


def main(out):
    mc = cell_mesh(0.03)
    k0, u0 = band1(mc, np.pi, np.pi)
    d = 0.05
    kd, _ = band1(mc, np.pi - d, np.pi, k0)
    T = (kd**2 - k0**2) / d**2
    print(f"band edge (M): k0 a/2pi = {k0 / (2 * np.pi):.4f}  eps(k0) = {eps(k0):.3f}  HFH T = {T:.3f}")

    kappa = 2 * np.pi / ENV_CELLS
    k_hfh = np.sqrt(k0**2 + T * kappa**2)
    k_ex, _ = band1(mc, np.pi - kappa, np.pi, k_hfh)
    print(f"envelope {ENV_CELLS:.0f} cells: k a/2pi = {k_ex / (2 * np.pi):.4f} (Bloch), {k_hfh / (2 * np.pi):.4f} (HFH)")
    k = k_ex

    lam = 2 * np.pi / k
    m, box = crystal_mesh(lam / np.sqrt(eps(k)) / 12, lam / 10, 1.0, 1.5)
    print(f"mesh: {m.n} nodes, {len(m.t)} elements")
    epsel = np.where(m.tag == 1, eps(k), 1.0)
    axx, ayy, b = fem.pml_coefficients(m, epsel, np.ones(len(m.t)), box, 1.5, k)
    A = fem.assemble(m, axx, ayy, b, k)
    src = np.exp(-(m.c[:, 0] ** 2 + m.c[:, 1] ** 2) / (2 * 0.08**2))
    rhs = fem.mass(m, src) @ np.ones(m.n)
    u, _ = fem.solve(A, rhs)

    # mild compression so the 1/sqrt(r) decay keeps the envelope rings legible
    r = np.hypot(m.p[:, 0], m.p[:, 1])
    v = u * np.sqrt(np.maximum(r, 0.5))
    scale = np.percentile(np.abs(v[r < NY / 2]), 97)

    def draw(ax, pt):
        t = np.linspace(0, 2 * np.pi, 120)
        for i in range(NX):
            for j in range(NY):
                cx, cy = -NX / 2 + i + 0.5, -NY / 2 + j + 0.5
                ax.plot(cx + R_ROD * np.cos(t), cy + R_ROD * np.sin(t), color=render.INK, lw=1.6 * pt)
        s = 0.22
        ax.plot([-s, s], [0, 0], color=render.WARM, lw=1.6 * pt, solid_capstyle="butt")
        ax.plot([0, 0], [-s, s], color=render.WARM, lw=1.6 * pt, solid_capstyle="butt")

    hw = NX / 2 + 1.0
    render.plate(m, v, (-hw, hw, -hw * 0.75, hw * 0.75), out, scale=scale, intensity=0.9,
                 phase=0.0, edge_alpha=0.8, draw=draw)
    return k0, T, k


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "homog.png")
