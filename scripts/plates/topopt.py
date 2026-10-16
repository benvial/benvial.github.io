"""Plate: a topology optimised all-dielectric cloak around a metal cylinder.

After Vial & Hao, Opt. Express 23, 23551 (2015). A PEC cylinder (radius
lambda/4) under plane wave illumination (E_z) is wrapped in a design annulus
whose element-wise permittivity eps = 1 + rho (EPS_MAX - 1) is optimised to
minimise the scattered field energy in a ring outside the device.

P1 FEM with PML, scattered-field formulation, adjoint gradient, density
filter and tanh projection with continuation, MMA (nlopt).
"""

import gmsh
import nlopt
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.spatial import cKDTree

import fem
import render

K = 2 * np.pi
R_PEC, R_DES = 0.25, 0.75
R_OBS = (0.85, 1.5)
EPS_MAX = 6.0
FILTER_R = 0.045
TAG_DES, TAG_AIR, TAG_PEC_EDGE, TAG_OUT = 1, 2, 10, 11
DESIGN_FILE = __file__.replace(".py", "-design.npy")  # optimised densities; pass as 2nd CLI arg to skip the optimisation


def build_mesh(X, Y, D):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    occ = gmsh.model.occ
    box = occ.addRectangle(-X - D, -Y - D, 0, 2 * (X + D), 2 * (Y + D))
    des = occ.addDisk(0, 0, 0, R_DES, R_DES)
    pec = occ.addDisk(0, 0, 0, R_PEC, R_PEC)
    ring = occ.cut([(2, des)], [(2, pec)], removeTool=False)[0]
    occ.cut([(2, box)], [(2, des), (2, pec)], removeTool=False)
    occ.remove([(2, pec)], recursive=True)
    occ.removeAllDuplicates()
    occ.synchronize()
    surfs = [s for _, s in gmsh.model.getEntities(2)]
    area_ring = np.pi * (R_DES**2 - R_PEC**2)
    ring_s = [s for s in surfs if abs(occ.getMass(2, s) - area_ring) < 1e-6]
    air_s = [s for s in surfs if s not in ring_s]
    gmsh.model.addPhysicalGroup(2, ring_s, TAG_DES)
    gmsh.model.addPhysicalGroup(2, air_s, TAG_AIR)
    curves = gmsh.model.getEntities(1)
    pec_c, out_c = [], []
    for _, c in curves:
        xmin, ymin, _, xmax, ymax, _ = gmsh.model.getBoundingBox(1, c)
        size = max(xmax - xmin, ymax - ymin)
        if abs(size - 2 * R_PEC) < 1e-3:
            pec_c.append(c)
        elif size > 2 * R_DES + 0.1:
            out_c.append(c)
    gmsh.model.addPhysicalGroup(1, pec_c, TAG_PEC_EDGE)
    gmsh.model.addPhysicalGroup(1, out_c, TAG_OUT)
    f = gmsh.model.mesh.field
    d = f.add("Distance")
    f.setNumbers(d, "CurvesList", [c for _, c in curves if c not in out_c])
    f.setNumber(d, "Sampling", 300)
    th = f.add("Threshold")
    f.setNumber(th, "InField", d)
    f.setNumber(th, "SizeMin", 1 / 50)
    f.setNumber(th, "SizeMax", 1 / 18)
    f.setNumber(th, "DistMin", 0.02)
    f.setNumber(th, "DistMax", 0.8)
    inner = f.add("Ball")
    f.setNumber(inner, "Radius", R_DES + 0.01)
    f.setNumber(inner, "VIn", 1 / 50)
    f.setNumber(inner, "VOut", 1)
    mn = f.add("Min")
    f.setNumbers(mn, "FieldsList", [th, inner])
    f.setAsBackgroundMesh(mn)
    for opt in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints"):
        gmsh.option.setNumber(opt, 0)
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.model.mesh.generate(2)
    m = fem.read_gmsh()
    pec_nodes = m.boundary_nodes(TAG_PEC_EDGE)
    out_nodes = m.boundary_nodes(TAG_OUT)
    gmsh.finalize()
    return m, pec_nodes, out_nodes


class Problem:
    def __init__(self, X=2.3, Y=1.75, D=0.6):
        self.m, pec, out = build_mesh(X, Y, D)
        m = self.m
        print(f"mesh: {m.n} nodes, {len(m.t)} elements")
        self.des = np.flatnonzero(m.tag == TAG_DES)
        self.box = (-X, X, -Y, Y)
        self.D = D
        self.uinc = np.exp(1j * K * m.p[:, 0])
        self.dir = np.concatenate([pec, out])
        self.g = np.concatenate([-self.uinc[pec], np.zeros(len(out))])
        fixed = np.zeros(m.n, bool)
        fixed[self.dir] = True
        self.free = np.flatnonzero(~fixed)
        r = np.hypot(m.c[:, 0], m.c[:, 1])
        self.Mobs = fem.mass(m, ((r > R_OBS[0]) & (r < R_OBS[1])).astype(float))
        # density filter (linear hat) on design element centroids
        c = m.c[self.des]
        a = m.area()[self.des]
        tree = cKDTree(c)
        pairs = tree.query_pairs(FILTER_R, output_type="ndarray")
        i = np.concatenate([pairs[:, 0], pairs[:, 1], np.arange(len(c))])
        j = np.concatenate([pairs[:, 1], pairs[:, 0], np.arange(len(c))])
        w = (FILTER_R - np.linalg.norm(c[i] - c[j], axis=1)) * a[j]
        H = sp.csr_matrix((w, (i, j)), shape=(len(c), len(c)))
        self.H = sp.diags(1 / np.asarray(H.sum(1)).ravel()) @ H
        # element mass matrices for the gradient
        self.Me = (m.area()[self.des])[:, None, None] * fem.MLOC[None]
        self.beta = 1.0

    def project(self, x):
        rt = self.H @ x
        b, eta = self.beta, 0.5
        den = np.tanh(b * eta) + np.tanh(b * (1 - eta))
        rp = (np.tanh(b * eta) + np.tanh(b * (rt - eta))) / den
        drp = b * (1 - np.tanh(b * (rt - eta)) ** 2) / den
        return rp, drp

    def solve(self, x):
        m = self.m
        rp, _ = self.project(x)
        eps = np.ones(len(m.t), complex)
        eps[self.des] = 1 + rp * (EPS_MAX - 1)
        one = np.ones(len(m.t))
        axx, ayy, b = fem.pml_coefficients(m, eps, one, self.box, self.D, K)
        A = fem.assemble(m, axx, ayy, b, K)
        a0x, a0y, b0 = fem.pml_coefficients(m, one, one, self.box, self.D, K)
        A0 = fem.assemble(m, a0x, a0y, b0, K)
        rhs = -(A - A0) @ self.uinc
        us, (lu, T) = fem.solve(A, rhs, dirichlet=self.dir, g=self.g)
        return us, eps, lu, T

    def objective(self, x, grad=None):
        us, eps, lu, T = self.solve(x)
        Mu = self.Mobs @ us
        J = np.real(np.vdot(us, Mu))
        if grad is not None and grad.size:
            # adjoint: Ared^H w = T^H Mobs us  (Ared = T^H A T is symmetric up to PML: use conj)
            rhs = T.conj().T @ Mu
            w = T @ np.conj(lu.solve(np.conj(rhs)))
            ut = us + self.uinc
            te = self.m.t[self.des]
            # dJ/deps_e = 2 k^2 Re(w_e^H M_e ut_e)
            loc = np.einsum("ei,eij,ej->e", np.conj(w[te]), self.Me, ut[te])
            dJ_deps = 2 * K**2 * np.real(loc)
            _, drp = self.project(x)
            grad[:] = self.H.T @ (dJ_deps * (EPS_MAX - 1) * drp)
        return J


def main(out, iters=(40, 30, 30, 30, 30, 40), design=None):
    P = Problem()
    nd = len(P.des)
    x = np.full(nd, 0.5)
    J0 = P.objective(np.zeros(nd))
    print(f"bare PEC: J0 = {J0:.4e}")
    if design is not None:
        P.beta = 32
        return finish(P, np.load(design), J0, out)
    # gradient check
    g = np.zeros(nd)
    P.objective(x, g)
    for e in np.random.default_rng(0).choice(nd, 3, replace=False):
        h = 1e-5
        xp, xm = x.copy(), x.copy()
        xp[e] += h
        xm[e] -= h
        fd = (P.objective(xp) - P.objective(xm)) / (2 * h)
        print(f"grad check e={e}: adjoint {g[e]:.4e}  fd {fd:.4e}")
    for beta, n in zip((1, 2, 4, 8, 16, 32), iters):
        P.beta = beta
        opt = nlopt.opt(nlopt.LD_MMA, nd)
        opt.set_lower_bounds(0.0)
        opt.set_upper_bounds(1.0)
        opt.set_min_objective(lambda xx, gg: P.objective(xx, gg) / J0)
        opt.set_maxeval(n)
        x = opt.optimize(x)
        print(f"beta={beta}: J/J0 = {opt.last_optimum_value():.4e}")
    np.save(DESIGN_FILE, x)
    return finish(P, x, J0, out)


def finish(P, x, J0, out):
    us, eps, _, _ = P.solve(x)
    rp, _ = P.project(x)
    J = np.real(np.vdot(us, P.Mobs @ us))
    print(f"final J/J0 = {J / J0:.4e} (scattered energy reduced {J0 / J:.0f}x)")
    m = P.m
    u = us + P.uinc

    hw, hh = 1.6, 1.2

    # nodal density for a smooth 0.5 iso-line of the projected design
    tri = m.t[P.des]
    acc = np.zeros(m.n)
    cnt = np.zeros(m.n)
    np.add.at(acc, tri, np.repeat(rp[:, None], 3, 1))
    np.add.at(cnt, tri, 1)
    used = np.unique(tri)
    rho_n = np.zeros(m.n)
    rho_n[used] = acc[used] / cnt[used]

    def draw(ax, pt):
        from matplotlib.patches import Circle
        from matplotlib.tri import Triangulation

        tr = Triangulation(m.p[:, 0], m.p[:, 1], tri)
        ax.tricontourf(tr, rho_n, levels=[0.5, 1.01], colors=[(*render.INK, 0.14)])
        ax.tricontour(tr, rho_n, levels=[0.5], colors=[render.INK], linewidths=1.6 * pt)
        ax.add_patch(Circle((0, 0), R_DES, facecolor="none", edgecolor=render.INK, lw=1.6 * pt))
        ax.add_patch(Circle((0, 0), R_PEC, facecolor=render.INK, edgecolor="none"))

    render.plate(m, u, (-hw, hw, -hh, hh), out, scale=1.6, intensity=0.85, edge_alpha=0.7, draw=draw)
    return J0 / J


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "topopt.png", design=sys.argv[2] if len(sys.argv) > 2 else None)
