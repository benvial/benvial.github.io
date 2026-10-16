"""Plate: a metal-insulator-metal metasurface absorber at resonance.

After Vial et al., J. Opt. Soc. Am. B 31, 1339 (2014). A grating of metal
strips over a lossy insulator on a metal ground plane (metals as perfect
conductors), lit at 30 degrees in TM polarisation (H_z). At the gap
resonance the incident power is trapped under the strips and absorbed, so the
reflected wave all but vanishes: the field above is the incoming plane wave
alone, and the energy piles up in the gaps.

P1 FEM on one period with Bloch quasi-periodic conditions, a line source
above the grating and a PML on top; the wavelength is swept to the
reflection minimum.
"""

import gmsh
import numpy as np
from scipy.optimize import minimize_scalar

import fem
import render

D = 1.0  # period
W = 0.5  # strip width
H_I, H_R = 0.09, 0.05  # insulator, strip thickness
EPS_I = 3.0 * (1 + 0.16j)  # loss tuned for critical coupling
THETA = np.radians(30)
Y_SRC, Y_TOP, PML = 2.3, 2.7, 0.9
TAG_INS, TAG_AIR, TAG_SRC = 1, 2, 20


def build_mesh(h_air):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    x0 = -D / 2
    ins = occ.addRectangle(x0, 0, 0, D, H_I)
    air = occ.addRectangle(x0, H_I, 0, D, Y_TOP + PML - H_I)
    strip = occ.addRectangle(-W / 2, H_I, 0, W, H_R)
    occ.cut([(2, air)], [(2, strip)])
    src = occ.addLine(occ.addPoint(x0, Y_SRC, 0), occ.addPoint(x0 + D, Y_SRC, 0))
    occ.fragment(occ.getEntities(2), [(1, src)])
    occ.synchronize()
    surfs = gmsh.model.getEntities(2)
    ins_s = [s for _, s in surfs if gmsh.model.getBoundingBox(2, s)[4] <= H_I + 1e-5]
    air_s = [s for _, s in surfs if s not in ins_s]
    gmsh.model.addPhysicalGroup(2, ins_s, TAG_INS)
    gmsh.model.addPhysicalGroup(2, air_s, TAG_AIR)
    src_c = [c for _, c in gmsh.model.getEntities(1)
             if abs(gmsh.model.getBoundingBox(1, c)[1] - Y_SRC) < 1e-5
             and abs(gmsh.model.getBoundingBox(1, c)[4] - Y_SRC) < 1e-5]
    gmsh.model.addPhysicalGroup(1, src_c, TAG_SRC)
    # periodic left/right
    left = [c for _, c in gmsh.model.getEntities(1)
            if abs(gmsh.model.getBoundingBox(1, c)[0] - x0) < 1e-5 and abs(gmsh.model.getBoundingBox(1, c)[3] - x0) < 1e-5]
    right = [c for _, c in gmsh.model.getEntities(1)
             if abs(gmsh.model.getBoundingBox(1, c)[0] - x0 - D) < 1e-5 and abs(gmsh.model.getBoundingBox(1, c)[3] - x0 - D) < 1e-5]
    left.sort(key=lambda c: gmsh.model.getBoundingBox(1, c)[1])
    right.sort(key=lambda c: gmsh.model.getBoundingBox(1, c)[1])
    tr = [1, 0, 0, D, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    gmsh.model.mesh.setPeriodic(1, right, left, tr)
    f = gmsh.model.mesh.field
    box = f.add("Box")
    f.setNumber(box, "VIn", 0.02)
    f.setNumber(box, "VOut", h_air)
    f.setNumber(box, "XMin", -1)
    f.setNumber(box, "XMax", 1)
    f.setNumber(box, "YMin", -1)
    f.setNumber(box, "YMax", H_I + H_R + 0.03)
    f.setNumber(box, "Thickness", 0.5)
    f.setAsBackgroundMesh(box)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints"):
        gmsh.option.setNumber(opt, 0)
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    # source line edges
    _, _, en = gmsh.model.mesh.getElements(1, src_c[0])
    m.src_edges = m.index[en[0].astype(int).reshape(-1, 2)]
    gmsh.finalize()
    # periodic node pairs by matching y
    xl, xr = m.p[:, 0] < x0 + 1e-9, m.p[:, 0] > x0 + D - 1e-9
    il, ir = np.flatnonzero(xl), np.flatnonzero(xr)
    il, ir = il[np.argsort(m.p[il, 1])], ir[np.argsort(m.p[ir, 1])]
    assert np.allclose(m.p[il, 1], m.p[ir, 1]), "non-matching periodic nodes"
    m.pairs = (il, ir)
    return m


def solve(m, lam):
    k = 2 * np.pi / lam
    alpha = k * np.sin(THETA)
    eps = np.where(m.tag == TAG_INS, EPS_I, 1.0 + 0j)
    one = np.ones(len(m.t))
    axx, ayy, b = fem.pml_coefficients(m, one, eps, (None, None, None, Y_TOP), PML, k)
    # H_z: div(1/eps grad H) + k^2 H  -> pml_coefficients(eps_like=1, mu_like=eps)
    A = fem.assemble(m, axx, ayy, b, k)
    rhs = np.zeros(m.n, complex)
    e = m.src_edges
    L = np.linalg.norm(m.p[e[:, 0]] - m.p[e[:, 1]], axis=1)
    f = np.exp(1j * alpha * m.p[:, 0])
    np.add.at(rhs, e[:, 0], L / 6 * (2 * f[e[:, 0]] + f[e[:, 1]]))
    np.add.at(rhs, e[:, 1], L / 6 * (f[e[:, 0]] + 2 * f[e[:, 1]]))
    il, ir = m.pairs
    top = np.flatnonzero(m.p[:, 1] > Y_TOP + PML - 1e-9)
    u, _ = fem.solve(A, rhs, dirichlet=top, g=np.zeros(len(top)),
                     periodic=(il, ir, np.exp(-1j * alpha * D) * np.ones(len(il))))
    return u, k, alpha


def reflection(m, u, k, alpha):
    """Fit u = a e^{-i beta y} + b e^{i beta y} (zeroth order) between grating and source."""
    beta = k * np.cos(THETA)
    sel = (m.p[:, 1] > 1.0) & (m.p[:, 1] < Y_SRC - 0.15)
    y = m.p[sel, 1]
    v = u[sel] * np.exp(-1j * alpha * m.p[sel, 0])
    M = np.stack([np.exp(-1j * beta * y), np.exp(1j * beta * y)], 1)
    (a, b), *_ = np.linalg.lstsq(M, v, rcond=None)
    return abs(b / a) ** 2, a


def tile(m, u, alpha, n=(-2, -1, 0, 1, 2)):
    ps, ts, us, tags = [], [], [], []
    for j, s in enumerate(n):
        ps.append(m.p + [s * D, 0])
        ts.append(m.t + j * m.n)
        us.append(u * np.exp(1j * alpha * s * D))
        tags.append(m.tag)
    return fem.Mesh(np.concatenate(ps), np.concatenate(ts), np.concatenate(tags)), np.concatenate(us)


def main(out):
    m0 = build_mesh(0.07)
    R_of = lambda lam: reflection(m0, *solve(m0, lam))[0]
    lams = np.linspace(1.55, 2.6, 43)
    Rs = np.array([R_of(l) for l in lams])
    i = int(np.argmin(Rs))
    res = minimize_scalar(R_of, bracket=(lams[max(i - 1, 0)], lams[i], lams[min(i + 1, len(lams) - 1)]),
                          tol=1e-6)
    lam = res.x
    m = build_mesh(lam / 22)
    u, k, alpha = solve(m, lam)
    R, a = reflection(m, u, k, alpha)
    print(f"mesh: {m.n} nodes, {len(m.t)} elements")
    print(f"sweep R min {Rs.min():.4f} at lambda/d={lams[i]:.3f}; refined lambda/d = {lam:.4f}, R = {R:.2e}, A = {1 - R:.4f}")
    u = u / a  # unit incident amplitude
    gap = np.abs(u[m.t[m.tag == TAG_INS]]).max()
    print(f"peak |H| in gap / incident = {gap:.1f}")
    mt, ut = tile(m, u, alpha)

    hw = 1.5
    y0 = -0.06
    view = (-hw, hw, y0, y0 + 2 * hw * 0.75)

    def draw(ax, pt):
        from matplotlib.patches import Rectangle

        ax.add_patch(Rectangle((-hw - 1, y0 - 1), 2 * hw + 2, 1 - y0 + 0.0, facecolor=render.INK, edgecolor="none"))
        for s in range(-3, 4):
            ax.add_patch(Rectangle((s * D - W / 2, H_I), W, H_R, facecolor=render.INK, edgecolor="none"))
        ax.plot([-hw - 1, hw + 1], [H_I, H_I], color=render.INK, lw=1.2 * pt)

    # gap fields reach ~9x the incident amplitude: compress the magnitude so
    # both the incoming wave and the gap resonance read on one map
    v = ut / np.maximum(np.abs(ut), 1e-30) * np.tanh(np.abs(ut) / 1.6)
    render.plate(mt, v, view, out, scale=1.0, intensity=0.88, phase=0.6, edge_alpha=0.8, draw=draw)
    return lam, R, gap


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "mim.png")
