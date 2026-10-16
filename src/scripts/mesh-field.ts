// Draws a live finite element solution behind page content.
// Every element marked [data-obstacle] inside a [data-mesh-field] becomes a
// perfectly conducting hole in the mesh; the rest of the box is meshed and
// solved with a point source the visitor can move.

import { buildMesh, factorise, onMesh, solvePoint, type Mesh, type Factor, type Rect } from "./fem";

const BINS = 96;

// Resolves any CSS colour (oklch, var-substituted) to sRGB bytes.
let probe: CanvasRenderingContext2D | null = null;
function rgbOf(css: string): number[] {
  probe ??= document.createElement("canvas").getContext("2d", { willReadFrequently: true })!;
  probe.clearRect(0, 0, 1, 1);
  probe.fillStyle = "#000";
  probe.fillStyle = css;
  probe.fillRect(0, 0, 1, 1);
  return [...probe.getImageData(0, 0, 1, 1).data.slice(0, 3)];
}

// The diverging colormap comes from --field-cmap in global.css (cool pole
// first), faded towards the paper by `intensity`.
function lut(el: HTMLElement, intensity: number): string[] {
  const style = getComputedStyle(el);
  const paper = rgbOf(style.getPropertyValue("--color-paper").trim());
  const stops = style.getPropertyValue("--field-cmap").split(/,(?![^(]*\))/).map((c) => c.trim()).filter(Boolean);
  const rgb = stops.map(rgbOf).map((c) => c.map((v, q) => paper[q] + intensity * (v - paper[q])));
  const out: string[] = [];
  for (let b = 0; b < BINS; b++) {
    const t = (b / (BINS - 1)) * (rgb.length - 1);
    const i = Math.min(Math.floor(t), rgb.length - 2);
    const f = t - i;
    const c = rgb[i].map((v, q) => Math.round(v + f * (rgb[i + 1][q] - v)));
    out.push(`rgb(${c[0]},${c[1]},${c[2]})`);
  }
  return out;
}

const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const fmt = (n: number) => n.toLocaleString("en-GB").replace(/,/g, " ");

class MeshField {
  el: HTMLElement;
  field: HTMLCanvasElement;
  edges: HTMLCanvasElement;
  marker: HTMLElement;
  readouts: HTMLElement[];
  mesh!: Mesh;
  factor!: Factor;
  W = 0;
  H = 0;
  lambda = 0;
  src = { x: 0, y: 0 };
  obstacles: Rect[] = [];
  measured?: ReturnType<MeshField["measureObstacles"]>;
  avgR = new Float64Array(0);
  avgI = new Float64Array(0);
  scale = 1;
  animate: boolean;
  visible = true;
  phase = 0;
  last = 0;
  raf = 0;
  stats = { factorMs: 0 };
  colors: string[];

  constructor(el: HTMLElement) {
    this.el = el;
    this.animate = el.dataset.animate === "true";
    this.colors = lut(el, Number(el.dataset.intensity ?? 0.8));
    this.field = document.createElement("canvas");
    this.edges = document.createElement("canvas");
    for (const c of [this.edges, this.field]) {
      c.className = "mesh-canvas";
      c.setAttribute("aria-hidden", "true");
      el.prepend(c);
    }
    this.marker = document.createElement("span");
    this.marker.className = "mesh-source";
    this.marker.setAttribute("aria-hidden", "true");
    el.append(this.marker);
    this.readouts = [...el.querySelectorAll<HTMLElement>("[data-mesh-readout]")];

    el.addEventListener("click", (ev) => this.onClick(ev));
    el.addEventListener("keydown", (ev) => this.onKey(ev));
    new IntersectionObserver(([entry]) => {
      this.visible = entry.isIntersecting;
      if (this.visible) this.loop();
    }).observe(el);

    // Small height jitter (mobile URL bar) is ignored, but any shift of an
    // obstacle (text reflow, late font swap) re-cuts the mesh so the holes
    // always match the blocks on top.
    let lastW = 0, lastH = 0, timer = 0;
    const ro = new ResizeObserver(() => {
      const r = el.getBoundingClientRect();
      const moved = this.obstaclesMoved();
      if (!moved && Math.abs(r.width - lastW) < 24 && Math.abs(r.height - lastH) < 24) return;
      const first = lastW === 0;
      lastW = r.width;
      lastH = r.height;
      clearTimeout(timer);
      timer = window.setTimeout(() => this.build(), first ? 0 : 180);
    });
    ro.observe(el);
    el.querySelectorAll<HTMLElement>("[data-obstacle]").forEach((o) => ro.observe(o));
  }

  /** Obstacle rectangles relative to the field, before padding. */
  measureObstacles() {
    const box = this.el.getBoundingClientRect();
    return [...this.el.querySelectorAll<HTMLElement>("[data-obstacle]")].map((o) => {
      const r = o.getBoundingClientRect();
      return { o, x0: r.left - box.left, y0: r.top - box.top, x1: r.right - box.left, y1: r.bottom - box.top };
    });
  }

  obstaclesMoved() {
    const now = this.measureObstacles();
    const before = this.measured;
    if (!before || before.length !== now.length) return true;
    return now.some((a, i) => {
      const b = before[i];
      return Math.abs(a.x0 - b.x0) > 2 || Math.abs(a.y0 - b.y0) > 2 || Math.abs(a.x1 - b.x1) > 2 || Math.abs(a.y1 - b.y1) > 2;
    });
  }

  build() {
    const box = this.el.getBoundingClientRect();
    const W = Math.round(box.width), H = Math.round(box.height);
    if (W < 50 || H < 50) return;
    const first = this.W === 0;
    const fx = first ? Number(this.el.dataset.sourceX ?? 0.85) : this.src.x / this.W;
    const fy = first ? Number(this.el.dataset.sourceY ?? 0.8) : this.src.y / this.H;
    this.W = W;
    this.H = H;
    const pad = Number(this.el.dataset.pad ?? 12);
    this.measured = this.measureObstacles();
    this.obstacles = this.measured
      .filter((r) => r.x1 > r.x0 && r.y1 > r.y0)
      .map((r) => {
        const p = Number(r.o.dataset.obstaclePad ?? pad);
        return {
          x0: Math.max(0, r.x0 - p),
          y0: Math.max(0, r.y0 - p),
          x1: Math.min(W, r.x1 + p),
          y1: Math.min(H, r.y1 + p),
        };
      });
    const perWidth = Number(this.el.dataset.wavelengths ?? 8);
    this.lambda = Math.max(72, Math.min(170, W / perWidth));
    const t0 = performance.now();
    this.mesh = buildMesh({
      width: W,
      height: H,
      obstacles: this.obstacles,
      hMin: this.lambda / 20,
      hMax: this.lambda / 11,
    });
    this.factor = factorise(this.mesh, (2 * Math.PI) / this.lambda);
    this.stats.factorMs = performance.now() - t0;
    this.place(fx * W, fy * H, true);
    this.drawEdges();
    this.el.classList.add("is-solved");
  }

  free(x: number, y: number) {
    const m = this.lambda / 10;
    if (x < m || y < m || x > this.W - m || y > this.H - m) return false;
    return !this.obstacles.some((r) => x > r.x0 - m && x < r.x1 + m && y > r.y0 - m && y < r.y1 + m);
  }

  /** Nearest point to (x, y) on the mesh, a hair inside its outer edge and outside
   *  every hole. With a direction, a point inside a hole leaves it on that side. */
  snap(x: number, y: number, dir?: [number, number]) {
    const e = 2;
    for (let k = 0; k <= this.obstacles.length; k++) {
      x = Math.min(Math.max(x, e), this.W - e);
      y = Math.min(Math.max(y, e), this.H - e);
      const r = this.obstacles.find((r) => x > r.x0 - e && x < r.x1 + e && y > r.y0 - e && y < r.y1 + e);
      if (!r) return { x, y };
      const exits = [
        { x: r.x0 - e, y, d: x - r.x0, ok: dir ? dir[0] < 0 : true },
        { x: r.x1 + e, y, d: r.x1 - x, ok: dir ? dir[0] > 0 : true },
        { x, y: r.y0 - e, d: y - r.y0, ok: dir ? dir[1] < 0 : true },
        { x, y: r.y1 + e, d: r.y1 - y, ok: dir ? dir[1] > 0 : true },
      ].filter((p) => p.ok && p.x >= e && p.x <= this.W - e && p.y >= e && p.y <= this.H - e);
      if (!exits.length) return null;
      const p = exits.reduce((a, b) => (b.d < a.d ? b : a));
      x = p.x;
      y = p.y;
    }
    return null;
  }

  place(x: number, y: number, fallback = false, dir?: [number, number]) {
    if (!fallback) {
      const p = this.snap(x, y, dir);
      if (!p) return false;
      ({ x, y } = onMesh(this.mesh, p.x, p.y));
    } else if (!this.free(x, y)) {
      // Pick the free point farthest from every obstacle, nearest the preferred spot on ties.
      let best = -1, bx = x, by = y;
      const step = this.lambda / 6;
      for (let py = step; py < this.H - step / 2; py += step) {
        for (let px = step; px < this.W - step / 2; px += step) {
          if (!this.free(px, py)) continue;
          let d = Math.min(px, py, this.W - px, this.H - py);
          for (const r of this.obstacles) {
            const dx = Math.max(r.x0 - px, 0, px - r.x1), dy = Math.max(r.y0 - py, 0, py - r.y1);
            d = Math.min(d, Math.hypot(dx, dy));
          }
          const score = Math.min(d, this.lambda) - 1e-3 * Math.hypot(px - x, py - y);
          if (score > best) { best = score; bx = px; by = py; }
        }
      }
      x = bx;
      y = by;
    }
    this.src = { x, y };
    const { ur, ui } = solvePoint(this.mesh, this.factor, x, y);
    const T = this.mesh.tri, ne = T.length / 3;
    this.avgR = new Float64Array(ne);
    this.avgI = new Float64Array(ne);
    const mags: number[] = [];
    const near = (this.lambda / 2) ** 2;
    for (let e = 0; e < ne; e++) {
      const a = T[3 * e], b = T[3 * e + 1], c = T[3 * e + 2];
      const r = (ur[a] + ur[b] + ur[c]) / 3, i = (ui[a] + ui[b] + ui[c]) / 3;
      this.avgR[e] = r;
      this.avgI[e] = i;
      const cx = (this.mesh.x[a] + this.mesh.x[b] + this.mesh.x[c]) / 3 - x;
      const cy = (this.mesh.y[a] + this.mesh.y[b] + this.mesh.y[c]) / 3 - y;
      if (cx * cx + cy * cy > near) mags.push(Math.hypot(r, i));
    }
    mags.sort((p, q) => p - q);
    this.scale = mags[Math.floor(mags.length * 0.97)] || 1;
    this.marker.style.transform = `translate(${x}px, ${y}px)`;
    this.marker.classList.add("is-placed");
    this.writeReadout();
    this.draw();
    this.loop();
    return true;
  }

  writeReadout() {
    const set = (k: string, v: string) => {
      for (const r of this.readouts) r.querySelectorAll(`[data-k="${k}"]`).forEach((slot) => (slot.textContent = v));
    };
    set("nodes", fmt(this.mesh.x.length));
    set("elements", fmt(this.mesh.tri.length / 3));
    set("dofs", fmt(this.factor.n));
    set("lambda", `${Math.round(this.lambda)} px`);
    set("ms", `${Math.max(1, Math.round(this.stats.factorMs))} ms`);
    set("source", `(${Math.round(this.src.x)}, ${Math.round(this.src.y)})`);
  }

  sizeCanvas(c: HTMLCanvasElement) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    c.width = Math.round(this.W * dpr);
    c.height = Math.round(this.H * dpr);
    c.style.width = `${this.W}px`;
    c.style.height = `${this.H}px`;
    const ctx = c.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, dpr };
  }

  drawEdges() {
    const { ctx, dpr } = this.sizeCanvas(this.edges);
    const { x, y, tri } = this.mesh;
    const ink = getComputedStyle(this.el).getPropertyValue("--mesh-edge").trim() || "rgba(20,24,30,.16)";
    ctx.strokeStyle = ink;
    ctx.lineWidth = Math.max(0.5, 1 / dpr);
    ctx.lineJoin = "round";
    ctx.beginPath();
    for (let e = 0; e < tri.length; e += 3) {
      const a = tri[e], b = tri[e + 1], c = tri[e + 2];
      ctx.moveTo(x[a], y[a]);
      ctx.lineTo(x[b], y[b]);
      ctx.lineTo(x[c], y[c]);
      ctx.closePath();
    }
    ctx.stroke();
  }

  draw() {
    if (!this.mesh) return;
    const ctx = this.field.width === Math.round(this.W * Math.min(window.devicePixelRatio || 1, 2))
      ? this.field.getContext("2d")!
      : this.sizeCanvas(this.field).ctx;
    ctx.clearRect(0, 0, this.W, this.H);
    const { x, y, tri } = this.mesh;
    const cs = Math.cos(this.phase), sn = Math.sin(this.phase);
    const buckets: number[][] = Array.from({ length: BINS }, () => []);
    const inv = 1 / this.scale;
    for (let e = 0; e < tri.length / 3; e++) {
      let v = (this.avgR[e] * cs + this.avgI[e] * sn) * inv;
      v = Math.max(-1, Math.min(1, v));
      buckets[Math.round(((v + 1) / 2) * (BINS - 1))].push(e);
    }
    for (let b = 0; b < BINS; b++) {
      const list = buckets[b];
      if (!list.length) continue;
      ctx.fillStyle = this.colors[b];
      ctx.strokeStyle = this.colors[b];
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      for (const e of list) {
        const a = tri[3 * e], p = tri[3 * e + 1], c = tri[3 * e + 2];
        ctx.moveTo(x[a], y[a]);
        ctx.lineTo(x[p], y[p]);
        ctx.lineTo(x[c], y[c]);
        ctx.closePath();
      }
      ctx.fill();
      ctx.stroke(); // seals hairline gaps between flat-shaded elements
    }
  }

  loop() {
    if (!this.animate || reduceMotion() || this.raf) return;
    const tick = (t: number) => {
      this.raf = 0;
      if (!this.visible || !this.mesh) return;
      if (t - this.last > 1000 / 30) {
        const dt = this.last ? Math.min(t - this.last, 100) : 0;
        this.last = t;
        this.phase += (dt / 4000) * 2 * Math.PI; // Re(u e^{-iωt}) with ωt increasing: outgoing waves, one period every 4 s
        this.draw();
      }
      this.raf = requestAnimationFrame(tick);
    };
    this.raf = requestAnimationFrame(tick);
  }

  onClick(ev: MouseEvent) {
    const target = ev.target as HTMLElement;
    if (target.closest("a, button, input, [data-obstacle]")) return;
    const r = this.el.getBoundingClientRect();
    this.place(ev.clientX - r.left, ev.clientY - r.top);
  }

  onKey(ev: KeyboardEvent) {
    if (ev.target !== this.el) return;
    const step = this.lambda / 4;
    const d: Record<string, [number, number]> = {
      ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step],
    };
    const mv = d[ev.key];
    if (!mv) return;
    ev.preventDefault();
    this.place(this.src.x + mv[0], this.src.y + mv[1], false, mv);
  }
}

function boot() {
  document.querySelectorAll<HTMLElement>("[data-mesh-field]").forEach((el) => {
    if ((el as any).__mesh) return;
    (el as any).__mesh = true;
    const start = () => new MeshField(el);
    (document.fonts?.ready ?? Promise.resolve()).then(start);
  });
}

boot();
