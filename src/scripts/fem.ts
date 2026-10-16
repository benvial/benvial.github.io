// Minimal P1 finite element Helmholtz solver for the mesh fields drawn on the site.
//
// Problem: -Δu - k²u = δ(x - xs) in the domain, u = 0 on obstacles (PEC),
// first-order absorbing condition ∂u/∂n - iku = 0 on the outer boundary.
// The mesh is a Delaunay triangulation of a size-graded point cloud that is
// refined around the obstacles (the text blocks of the page).

import Delaunator from "delaunator";

export interface Rect {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface Mesh {
  x: Float64Array;
  y: Float64Array;
  tri: Uint32Array; // 3 node indices per element
  boundary: Uint8Array; // 1 = obstacle node (Dirichlet), 2 = outer boundary node
  outerEdges: Uint32Array; // pairs of node indices on the outer boundary
}

export interface MeshOptions {
  width: number;
  height: number;
  obstacles: Rect[];
  hMin: number;
  hMax: number;
  seed?: number;
}

function rng(seed: number) {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13;
    s ^= s >>> 17;
    s ^= s << 5;
    return (s >>> 0) / 4294967296;
  };
}

function distToRect(px: number, py: number, r: Rect) {
  const dx = Math.max(r.x0 - px, 0, px - r.x1);
  const dy = Math.max(r.y0 - py, 0, py - r.y1);
  return Math.sqrt(dx * dx + dy * dy);
}

function inside(px: number, py: number, r: Rect, eps = 0) {
  return px > r.x0 + eps && px < r.x1 - eps && py > r.y0 + eps && py < r.y1 - eps;
}

export function buildMesh(o: MeshOptions): Mesh {
  const { width: W, height: H, obstacles, hMin, hMax } = o;
  const rand = rng(o.seed ?? 7);
  const grade = 0.35; // growth of element size with distance to an obstacle

  const size = (px: number, py: number) => {
    let d = Infinity;
    for (let q = 0; q < obstacles.length; q++) {
      const dq = distToRect(px, py, obstacles[q]);
      if (dq < d) d = dq;
    }
    if (!isFinite(d)) d = hMax / grade;
    return Math.min(hMax, hMin + grade * d);
  };

  const xs: number[] = [];
  const ys: number[] = [];
  const kind: number[] = [];

  // Spatial hash for the acceptance test: one linked list of points per cell.
  const cell = hMin * 0.7;
  const gw = Math.ceil(W / cell) + 1;
  const gh = Math.ceil(H / cell) + 1;
  const head = new Int32Array(gw * gh).fill(-1);
  const link: number[] = [];
  const add = (px: number, py: number, k: number) => {
    const id = xs.length;
    xs.push(px);
    ys.push(py);
    kind.push(k);
    const gi = Math.floor(px / cell) + gw * Math.floor(py / cell);
    link.push(head[gi]);
    head[gi] = id;
  };
  const free = (px: number, py: number, rad: number) => {
    const r = Math.ceil(rad / cell), r2 = rad * rad;
    const cx = Math.floor(px / cell);
    const cy = Math.floor(py / cell);
    const i0 = Math.max(0, cx - r), i1 = Math.min(gw - 1, cx + r);
    for (let j = Math.max(0, cy - r), j1 = Math.min(gh - 1, cy + r); j <= j1; j++) {
      for (let i = i0; i <= i1; i++) {
        for (let id = head[i + gw * j]; id >= 0; id = link[id]) {
          const dx = xs[id] - px, dy = ys[id] - py;
          if (dx * dx + dy * dy < r2) return false;
        }
      }
    }
    return true;
  };

  // Obstacle perimeters, sampled at the finest size.
  for (const r of obstacles) {
    const edges: [number, number, number, number][] = [
      [r.x0, r.y0, r.x1, r.y0],
      [r.x1, r.y0, r.x1, r.y1],
      [r.x1, r.y1, r.x0, r.y1],
      [r.x0, r.y1, r.x0, r.y0],
    ];
    for (const [ax, ay, bx, by] of edges) {
      const len = Math.hypot(bx - ax, by - ay);
      const n = Math.max(1, Math.round(len / hMin));
      for (let i = 0; i < n; i++) {
        const t = i / n;
        const px = ax + t * (bx - ax);
        const py = ay + t * (by - ay);
        if (px < 0 || px > W || py < 0 || py > H) continue;
        if (obstacles.some((q) => q !== r && inside(px, py, q))) continue;
        if (free(px, py, hMin * 0.5)) add(px, py, 1);
      }
    }
  }

  // Outer boundary, graded.
  const walk = (ax: number, ay: number, bx: number, by: number) => {
    const len = Math.hypot(bx - ax, by - ay);
    let t = 0;
    while (t < len) {
      const px = ax + ((bx - ax) * t) / len;
      const py = ay + ((by - ay) * t) / len;
      if (!obstacles.some((q) => inside(px, py, q, -1)) && free(px, py, size(px, py) * 0.6)) add(px, py, 2);
      t += size(px, py);
    }
  };
  walk(0, 0, W, 0);
  walk(W, 0, W, H);
  walk(W, H, 0, H);
  walk(0, H, 0, 0);

  // Interior: shuffled jittered candidates, accepted against the local size.
  const step = hMin * 0.6;
  let nc = 0;
  for (let py = step / 2; py < H; py += step) for (let px = step / 2; px < W; px += step) nc++;
  const cand = new Float64Array(2 * nc);
  nc = 0;
  for (let py = step / 2; py < H; py += step) {
    for (let px = step / 2; px < W; px += step) {
      cand[nc++] = px + (rand() - 0.5) * step;
      cand[nc++] = py + (rand() - 0.5) * step;
    }
  }
  const order = new Uint32Array(cand.length / 2);
  for (let i = 0; i < order.length; i++) order[i] = i;
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    const t = order[i];
    order[i] = order[j];
    order[j] = t;
  }
  for (const c of order) {
    const px = cand[2 * c];
    const py = cand[2 * c + 1];
    if (px <= 1 || py <= 1 || px >= W - 1 || py >= H - 1) continue;
    if (obstacles.some((q) => inside(px, py, q, -hMin * 0.4))) continue;
    const h = size(px, py);
    if (free(px, py, h * 0.85)) add(px, py, 0);
  }

  const pts = new Float64Array(xs.length * 2);
  for (let i = 0; i < xs.length; i++) {
    pts[2 * i] = xs[i];
    pts[2 * i + 1] = ys[i];
  }
  const del = new Delaunator(pts);
  const t = del.triangles;
  const keep: number[] = [];
  for (let e = 0; e < t.length; e += 3) {
    const a = t[e], b = t[e + 1], c = t[e + 2];
    const cx = (xs[a] + xs[b] + xs[c]) / 3;
    const cy = (ys[a] + ys[b] + ys[c]) / 3;
    if (obstacles.some((q) => inside(cx, cy, q))) continue;
    // Drop slivers that bridge across an obstacle corner.
    const area = Math.abs((xs[b] - xs[a]) * (ys[c] - ys[a]) - (xs[c] - xs[a]) * (ys[b] - ys[a])) / 2;
    if (area < 1e-6) continue;
    keep.push(a, b, c);
  }

  // Outer boundary edges = hull edges that survived.
  const hull = del.hull;
  const outer: number[] = [];
  for (let i = 0; i < hull.length; i++) {
    const a = hull[i];
    const b = hull[(i + 1) % hull.length];
    if (kind[a] === 1 || kind[b] === 1) continue;
    outer.push(a, b);
  }

  return {
    x: Float64Array.from(xs),
    y: Float64Array.from(ys),
    tri: Uint32Array.from(keep),
    boundary: Uint8Array.from(kind),
    outerEdges: Uint32Array.from(outer),
  };
}

// ---------------------------------------------------------------------------
// Assembly and complex symmetric sparse LDLᵀ factorisation.
//
// Unknowns are ordered by geometric nested dissection (the mesh is planar, so
// splitting at the median coordinate gives small separators), which keeps the
// fill of L near O(n log n) instead of the O(n^1.5) of a banded profile. The
// factorisation itself is the up-looking LDLᵀ of T. Davis's LDL package, in
// complex arithmetic without conjugation.

const LEAF = 16; // nodes per dissection leaf

export interface Factor {
  n: number; // number of unknowns
  dof: Int32Array; // mesh node -> unknown index (-1 for Dirichlet nodes)
  perm: Int32Array; // unknown index -> position in the elimination order
  lp: Int32Array; // column pointers of L (strictly lower, unit diagonal implied)
  li: Int32Array; // row indices of L
  lr: Float64Array; // L, real part
  lm: Float64Array; // L, imaginary part
  dr: Float64Array; // D, real part
  di: Float64Array;
}

/** Elimination order: perm[v] = position of unknown v. */
function dissect(n: number, adjP: Int32Array, adjI: Int32Array, px: Float64Array, py: Float64Array, leaf = LEAF): Int32Array {
  const perm = new Int32Array(n);
  const ids = Int32Array.from({ length: n }, (_, i) => i);
  const left = new Uint8Array(n); // 1 = node lies in the left half of the range being cut
  let next = 0;
  // Orders ids[lo, hi): both halves recursively, then the separator between them.
  const rec = (lo: number, hi: number) => {
    if (hi - lo <= leaf) {
      for (let i = lo; i < hi; i++) perm[ids[i]] = next++;
      return;
    }
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (let i = lo; i < hi; i++) {
      const v = ids[i];
      if (px[v] < x0) x0 = px[v];
      if (px[v] > x1) x1 = px[v];
      if (py[v] < y0) y0 = py[v];
      if (py[v] > y1) y1 = py[v];
    }
    const c = x1 - x0 >= y1 - y0 ? px : py;
    // Quickselect: ids[lo, mid) <= ids[mid, hi) along c.
    const mid = (lo + hi) >> 1;
    for (let a = lo, b = hi - 1; a < b; ) {
      const pivot = c[ids[(a + b) >> 1]];
      let i = a, j = b;
      while (i <= j) {
        while (c[ids[i]] < pivot) i++;
        while (c[ids[j]] > pivot) j--;
        if (i <= j) {
          const t = ids[i]; ids[i] = ids[j]; ids[j] = t;
          i++;
          j--;
        }
      }
      if (j < mid) a = i;
      if (mid < i) b = j;
    }
    for (let i = lo; i < mid; i++) left[ids[i]] = 1;
    // Separator: right-half nodes touching the left half, moved to the end of the range.
    let end = hi;
    for (let i = hi - 1; i >= mid; i--) {
      const v = ids[i];
      for (let p = adjP[v]; p < adjP[v + 1]; p++) {
        if (!left[adjI[p]]) continue;
        ids[i] = ids[--end];
        ids[end] = v;
        break;
      }
    }
    for (let i = lo; i < hi; i++) left[ids[i]] = 0;
    rec(lo, mid);
    rec(mid, end);
    for (let i = end; i < hi; i++) perm[ids[i]] = next++;
  };
  rec(0, n);
  return perm;
}

export function factorise(mesh: Mesh, k: number, loss = 0.01): Factor {
  const nn = mesh.x.length;
  const dof = new Int32Array(nn).fill(-1);
  let n = 0;
  for (let i = 0; i < nn; i++) if (mesh.boundary[i] !== 1) dof[i] = n++;
  const X = mesh.x, Y = mesh.y, T = mesh.tri;

  // Graph of the unknowns (CSR, no diagonal).
  const nbr: number[][] = Array.from({ length: n }, () => []);
  for (let e = 0; e < T.length; e += 3) {
    for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) {
      if (a === b) continue;
      const i = dof[T[e + a]], j = dof[T[e + b]];
      if (i >= 0 && j >= 0 && !nbr[i].includes(j)) nbr[i].push(j);
    }
  }
  const adjP = new Int32Array(n + 1);
  for (let i = 0; i < n; i++) adjP[i + 1] = adjP[i] + nbr[i].length;
  const adjI = new Int32Array(adjP[n]);
  for (let i = 0; i < n; i++) adjI.set(nbr[i], adjP[i]);
  const px = new Float64Array(n), py = new Float64Array(n);
  for (let v = 0; v < nn; v++) if (dof[v] >= 0) { px[dof[v]] = X[v]; py[dof[v]] = Y[v]; }
  const perm = dissect(n, adjP, adjI, px, py);

  // Upper triangle of the permuted matrix by columns: column k holds rows i < k.
  const ap = new Int32Array(n + 1);
  for (let v = 0; v < n; v++) for (let p = adjP[v]; p < adjP[v + 1]; p++) if (perm[adjI[p]] < perm[v]) ap[perm[v] + 1]++;
  for (let k = 0; k < n; k++) ap[k + 1] += ap[k];
  const ai = new Int32Array(ap[n]);
  const fill = ap.slice(0, n);
  for (let v = 0; v < n; v++) for (let p = adjP[v]; p < adjP[v + 1]; p++) {
    const i = perm[adjI[p]];
    if (i < perm[v]) ai[fill[perm[v]]++] = i;
  }
  const ar = new Float64Array(ap[n]), am = new Float64Array(ap[n]);
  const dr = new Float64Array(n), di = new Float64Array(n);

  // A = K - k²(1 + i·loss) M - ik B
  const k2r = k * k, k2i = k * k * loss;
  const put = (gi: number, gj: number, re: number, im: number) => {
    let i = perm[gi], j = perm[gj];
    if (i === j) {
      dr[i] += re;
      di[i] += im;
      return;
    }
    if (i > j) return; // symmetric: keep the upper entry only
    for (let p = ap[j]; p < ap[j + 1]; p++) if (ai[p] === i) {
      ar[p] += re;
      am[p] += im;
      return;
    }
  };
  for (let e = 0; e < T.length; e += 3) {
    const p = [T[e], T[e + 1], T[e + 2]];
    const x1 = X[p[0]], y1 = Y[p[0]], x2 = X[p[1]], y2 = Y[p[1]], x3 = X[p[2]], y3 = Y[p[2]];
    const det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1);
    const area = Math.abs(det) / 2;
    const bx = [y2 - y3, y3 - y1, y1 - y2];
    const by = [x3 - x2, x1 - x3, x2 - x1];
    for (let a = 0; a < 3; a++) {
      const i = dof[p[a]];
      if (i < 0) continue;
      for (let b = 0; b < 3; b++) {
        const j = dof[p[b]];
        if (j < 0) continue;
        const kab = (bx[a] * bx[b] + by[a] * by[b]) / (4 * area);
        const mab = (area / 12) * (a === b ? 2 : 1);
        put(i, j, kab - k2r * mab, -k2i * mab);
      }
    }
  }
  const O = mesh.outerEdges;
  for (let e = 0; e < O.length; e += 2) {
    const a = dof[O[e]], b = dof[O[e + 1]];
    if (a < 0 || b < 0) continue;
    const len = Math.hypot(X[O[e]] - X[O[e + 1]], Y[O[e]] - Y[O[e + 1]]);
    // -ik ∫ φa φb ds
    put(a, a, 0, (-k * len) / 3);
    put(b, b, 0, (-k * len) / 3);
    put(a, b, 0, (-k * len) / 6);
    put(b, a, 0, (-k * len) / 6);
  }

  // Symbolic: elimination tree and column counts of L.
  const parent = new Int32Array(n), flag = new Int32Array(n), lnz = new Int32Array(n);
  for (let kk = 0; kk < n; kk++) {
    parent[kk] = -1;
    flag[kk] = kk;
    for (let p = ap[kk]; p < ap[kk + 1]; p++) {
      for (let i = ai[p]; flag[i] !== kk; i = parent[i]) {
        if (parent[i] === -1) parent[i] = kk;
        lnz[i]++;
        flag[i] = kk;
      }
    }
  }
  const lp = new Int32Array(n + 1);
  for (let kk = 0; kk < n; kk++) lp[kk + 1] = lp[kk] + lnz[kk];
  const li = new Int32Array(lp[n]);
  const lr = new Float64Array(lp[n]), lm = new Float64Array(lp[n]);

  // Numeric: row k of L from a sparse triangular solve along the tree.
  const yr = new Float64Array(n), ym = new Float64Array(n);
  const pattern = new Int32Array(n);
  lnz.fill(0);
  for (let kk = 0; kk < n; kk++) {
    let top = n;
    flag[kk] = kk;
    for (let p = ap[kk]; p < ap[kk + 1]; p++) {
      let i = ai[p];
      yr[i] += ar[p];
      ym[i] += am[p];
      let len = 0;
      for (; flag[i] !== kk; i = parent[i]) {
        pattern[len++] = i;
        flag[i] = kk;
      }
      while (len > 0) pattern[--top] = pattern[--len];
    }
    let dkr = dr[kk], dki = di[kk];
    for (; top < n; top++) {
      const i = pattern[top];
      const vr = yr[i], vm = ym[i];
      yr[i] = 0;
      ym[i] = 0;
      const p2 = lp[i] + lnz[i];
      for (let p = lp[i]; p < p2; p++) {
        const r = li[p];
        yr[r] -= lr[p] * vr - lm[p] * vm;
        ym[r] -= lr[p] * vm + lm[p] * vr;
      }
      const ddr = dr[i], ddi = di[i], den = ddr * ddr + ddi * ddi;
      const lkr = (vr * ddr + vm * ddi) / den, lki = (vm * ddr - vr * ddi) / den;
      dkr -= lkr * vr - lki * vm;
      dki -= lkr * vm + lki * vr;
      li[p2] = kk;
      lr[p2] = lkr;
      lm[p2] = lki;
      lnz[i]++;
    }
    dr[kk] = dkr;
    di[kk] = dki;
  }
  return { n, dof, perm, lp, li, lr, lm, dr, di };
}

/** (x, y) when it lies in an element, otherwise the centroid of the nearest element. */
export function onMesh(mesh: Mesh, x: number, y: number) {
  const T = mesh.tri, X = mesh.x, Y = mesh.y;
  let best = Infinity, bx = x, by = y;
  for (let e = 0; e < T.length; e += 3) {
    const a = T[e], b = T[e + 1], c = T[e + 2];
    const det = (X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a]);
    const l1 = ((X[b] - x) * (Y[c] - y) - (X[c] - x) * (Y[b] - y)) / det;
    const l2 = ((X[c] - x) * (Y[a] - y) - (X[a] - x) * (Y[c] - y)) / det;
    if (l1 >= -1e-9 && l2 >= -1e-9 && 1 - l1 - l2 >= -1e-9) return { x, y };
    const cx = (X[a] + X[b] + X[c]) / 3, cy = (Y[a] + Y[b] + Y[c]) / 3;
    const d = (cx - x) ** 2 + (cy - y) ** 2;
    if (d < best) { best = d; bx = cx; by = cy; }
  }
  return { x: bx, y: by };
}

/** Solve for a unit point source at (sx, sy). Returns nodal values (re, im). */
export function solvePoint(mesh: Mesh, f: Factor, sx: number, sy: number) {
  const { n, dof, perm, lp, li, lr, lm, dr, di } = f;
  const br = new Float64Array(n);
  const bi = new Float64Array(n);
  const T = mesh.tri, X = mesh.x, Y = mesh.y;
  for (let e = 0; e < T.length; e += 3) {
    const a = T[e], b = T[e + 1], c = T[e + 2];
    const det = (X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a]);
    const l1 = ((X[b] - sx) * (Y[c] - sy) - (X[c] - sx) * (Y[b] - sy)) / det;
    const l2 = ((X[c] - sx) * (Y[a] - sy) - (X[a] - sx) * (Y[c] - sy)) / det;
    const l3 = 1 - l1 - l2;
    if (l1 < -1e-9 || l2 < -1e-9 || l3 < -1e-9) continue;
    const w = [l1, l2, l3];
    [a, b, c].forEach((node, q) => {
      if (dof[node] >= 0) br[perm[dof[node]]] += w[q];
    });
    break;
  }
  // L y = b
  for (let j = 0; j < n; j++) {
    const xr = br[j], xi = bi[j];
    for (let p = lp[j]; p < lp[j + 1]; p++) {
      const r = li[p];
      br[r] -= lr[p] * xr - lm[p] * xi;
      bi[r] -= lr[p] * xi + lm[p] * xr;
    }
  }
  // D z = y
  for (let i = 0; i < n; i++) {
    const den = dr[i] * dr[i] + di[i] * di[i];
    const r = (br[i] * dr[i] + bi[i] * di[i]) / den;
    const m = (bi[i] * dr[i] - br[i] * di[i]) / den;
    br[i] = r;
    bi[i] = m;
  }
  // Lᵀ x = z
  for (let j = n - 1; j >= 0; j--) {
    let xr = br[j], xi = bi[j];
    for (let p = lp[j]; p < lp[j + 1]; p++) {
      const r = li[p];
      xr -= lr[p] * br[r] - lm[p] * bi[r];
      xi -= lr[p] * bi[r] + lm[p] * br[r];
    }
    br[j] = xr;
    bi[j] = xi;
  }
  const ur = new Float64Array(mesh.x.length);
  const ui = new Float64Array(mesh.x.length);
  for (let v = 0; v < mesh.x.length; v++) {
    const d = dof[v];
    if (d < 0) continue;
    ur[v] = br[perm[d]];
    ui[v] = bi[perm[d]];
  }
  return { ur, ui };
}
