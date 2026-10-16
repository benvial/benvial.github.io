// Source position for a page header, derived from the page path so each page
// gets its own field while staying stable across builds and reloads. The
// source stays in the right-hand band, clear of the title in the bottom left.
export function sourceFor(path: string): { sourceX: number; sourceY: number } {
  const key = path.replace(/\/+$/, "") || "/";
  let h = 2166136261;
  for (let i = 0; i < key.length; i++) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const u = (h >>> 0) / 2 ** 32;
  const v = (Math.imul(h, 2654435761) >>> 0) / 2 ** 32;
  return {
    sourceX: +(0.72 + 0.24 * u).toFixed(3),
    sourceY: +(0.2 + 0.6 * v).toFixed(3),
  };
}
