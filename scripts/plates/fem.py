"""Minimal P1 finite element toolkit for the research cover plates.

Solves the scalar 2D Helmholtz problem

    div(a grad u) + k^2 b u = f

on gmsh triangulations, with element-wise constant (complex) coefficients,
Cartesian PML by complex coordinate stretching, Dirichlet nodes and
(Bloch) periodic node pairs.
"""

import gmsh
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


class Mesh:
    def __init__(self, nodes, tris, tags):
        self.p = nodes  # (n, 2)
        self.t = tris  # (m, 3)
        self.tag = tags  # (m,) physical tag of each element
        self.c = nodes[tris].mean(axis=1)  # centroids

    @property
    def n(self):
        return len(self.p)

    def area(self):
        p = self.p[self.t]
        d1, d2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
        return 0.5 * np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])

    def boundary_nodes(self, phys):
        """Nodes on gmsh physical curve(s) `phys`."""
        ids = []
        for tag in np.atleast_1d(phys):
            nt, _ = gmsh.model.mesh.getNodesForPhysicalGroup(1, int(tag))
            ids.append(nt)
        return np.unique(self.index[np.concatenate(ids).astype(int)])


def read_gmsh():
    """Read the current gmsh model's 2D mesh (physical surfaces only)."""
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    nt = nt.astype(int)
    index = np.full(nt.max() + 1, -1, dtype=int)
    index[nt] = np.arange(len(nt))
    nodes = xyz.reshape(-1, 3)[:, :2]
    tris, tags = [], []
    for dim, ptag in gmsh.model.getPhysicalGroups(2):
        for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, ptag):
            types, _, enodes = gmsh.model.mesh.getElements(dim, ent)
            for ty, en in zip(types, enodes):
                if ty == 2:
                    tris.append(index[en.astype(int).reshape(-1, 3)])
                    tags.append(np.full(len(tris[-1]), ptag))
    tris = np.concatenate(tris)
    # keep only nodes used by triangles, renumbered
    used = np.zeros(len(nodes), bool)
    used[tris] = True
    new = np.cumsum(used) - 1
    m = Mesh(nodes[used], new[tris], np.concatenate(tags))
    ok = index >= 0
    m.index = np.full_like(index, -1)
    m.index[ok] = np.where(used[index[ok]], new[index[ok]], -1)
    return m


def gradients(m):
    """P1 shape-function gradients per element: (m, 3, 2) and areas."""
    p = m.p[m.t]
    x, y = p[..., 0], p[..., 1]
    det = (x[:, 1] - x[:, 0]) * (y[:, 2] - y[:, 0]) - (x[:, 2] - x[:, 0]) * (y[:, 1] - y[:, 0])
    gx = np.stack([y[:, 1] - y[:, 2], y[:, 2] - y[:, 0], y[:, 0] - y[:, 1]], 1) / det[:, None]
    gy = np.stack([x[:, 2] - x[:, 1], x[:, 0] - x[:, 2], x[:, 1] - x[:, 0]], 1) / det[:, None]
    return np.stack([gx, gy], -1), 0.5 * np.abs(det)


MLOC = (np.ones((3, 3)) + np.eye(3)) / 12.0  # P1 mass matrix / area


def assemble(m, axx, ayy, b, k):
    """Matrix of -div(diag(axx, ayy) grad) - k^2 b with element constants."""
    G, A = gradients(m)
    Ke = (axx[:, None, None] * G[..., 0][:, :, None] * G[..., 0][:, None, :]
          + ayy[:, None, None] * G[..., 1][:, :, None] * G[..., 1][:, None, :]) * A[:, None, None]
    Me = (b * A)[:, None, None] * MLOC[None]
    Le = Ke - k**2 * Me
    rows = np.repeat(m.t, 3, axis=1).ravel()
    cols = np.tile(m.t, (1, 3)).ravel()
    return sp.csr_matrix((Le.ravel(), (rows, cols)), shape=(m.n, m.n))


def mass(m, w):
    """Weighted mass matrix with element weights w."""
    A = m.area()
    Me = (w * A)[:, None, None] * MLOC[None]
    rows = np.repeat(m.t, 3, axis=1).ravel()
    cols = np.tile(m.t, (1, 3)).ravel()
    return sp.csr_matrix((Me.ravel(), (rows, cols)), shape=(m.n, m.n))


def pml_stretch(c, box, depth, k, strength=4.0):
    """Complex stretch factors (sx, sy) at points c for a rectangular PML.

    `box` = (xmin, xmax, ymin, ymax) of the physical domain; the PML extends
    `depth` beyond it. Set a side to None to disable stretching there.
    """
    s = []
    for j, (lo, hi) in enumerate([(box[0], box[1]), (box[2], box[3])]):
        d = np.zeros(len(c))
        if lo is not None:
            d = np.maximum(d, (lo - c[:, j]) / depth)
        if hi is not None:
            d = np.maximum(d, (c[:, j] - hi) / depth)
        d = np.clip(d, 0, 1)
        s.append(1 + 1j * strength * d**2)
    return s


def pml_coefficients(m, eps_like, mu_like, box, depth, k):
    """Element coefficients for div(1/mu grad u) + k^2 eps u with PML.

    Returns axx, ayy, b for `assemble`. In the PML, material must be
    homogeneous (we use free space).
    """
    sx, sy = pml_stretch(m.c, box, depth, k)
    return sy / sx / mu_like, sx / sy / mu_like, sx * sy * eps_like


def solve(A, rhs, dirichlet=None, g=None, periodic=None):
    """Solve A u = rhs with optional Dirichlet values and periodic pairs.

    periodic: (slave, master, phase) arrays; u[slave] = phase * u[master].
    Returns the full nodal solution and the factorisation pieces.
    """
    n = A.shape[0]
    g_full = np.zeros(n, complex)
    fixed = np.zeros(n, bool)
    if dirichlet is not None:
        fixed[dirichlet] = True
        g_full[dirichlet] = g
    P = sp.identity(n, dtype=complex, format="csr")
    if periodic is not None:
        slave, master, phase = periodic
        P = sp.lil_matrix((n, n), dtype=complex)
        P.setdiag(1.0)
        P[slave, slave] = 0.0
        P[slave, master] = phase
        P = P.tocsr()
        fixed[slave] = True
    free = np.flatnonzero(~fixed)
    T = P[:, free]
    lift = A @ g_full
    Ared = (T.conj().T @ A @ T).tocsc()
    bred = T.conj().T @ (rhs - lift)
    lu = spla.splu(Ared)
    u = T @ lu.solve(bred) + g_full
    return u, (lu, T)
