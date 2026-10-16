// Fetch the public contribution calendars (GitHub + GitLab) and merge them into
// src/data/activity.json for the activity graph on /code. Never fails the build:
// on a network error the previous file is kept, or an empty one is written.

import { existsSync, readFileSync, writeFileSync } from "node:fs";

const GITHUB_USER = "benvial";
const GITLAB_USER = "benvial";
const out = new URL("../src/data/activity.json", import.meta.url).pathname;

async function get(url) {
  const res = await fetch(url, {
    headers: { "User-Agent": "bvial.info build" },
    signal: AbortSignal.timeout(10000),
  });
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res;
}

// The calendar HTML pairs each day cell (id, data-date) with a tooltip
// (for=id) holding "N contributions on ..." or "No contributions on ...".
async function github() {
  const html = await (await get(`https://github.com/users/${GITHUB_USER}/contributions`)).text();
  const dates = new Map();
  for (const m of html.matchAll(/data-date="(\d{4}-\d{2}-\d{2})"\s+id="([^"]+)"/g)) dates.set(m[2], m[1]);
  const counts = {};
  for (const m of html.matchAll(/<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)<\/tool-tip>/g)) {
    const date = dates.get(m[1]);
    if (!date) continue;
    const n = m[2].match(/^(\d[\d,]*) contributions?/);
    counts[date] = n ? Number(n[1].replace(/,/g, "")) : 0;
  }
  if (!Object.keys(counts).length) throw new Error("GitHub calendar markup not recognised");
  return counts;
}

async function gitlab() {
  return (await get(`https://gitlab.com/users/${GITLAB_USER}/calendar.json`)).json();
}

const [gh, gl] = await Promise.allSettled([github(), gitlab()]);

if (gh.status === "rejected") {
  console.warn("Activity: GitHub fetch failed:", gh.reason.message);
  if (!existsSync(out)) writeFileSync(out, JSON.stringify({ updated: null, days: [] }));
  process.exit(0);
}
if (gl.status === "rejected") console.warn("Activity: GitLab fetch failed:", gl.reason.message);

// GitHub defines the window (one year, Sunday-aligned); GitLab counts add in.
const extra = gl.status === "fulfilled" ? gl.value : {};
const days = Object.entries(gh.value)
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([date, count]) => ({ date, count: count + (extra[date] ?? 0) }));

const data = { updated: new Date().toISOString().slice(0, 10), days };
if (existsSync(out) && readFileSync(out, "utf8") === JSON.stringify(data)) process.exit(0);
writeFileSync(out, JSON.stringify(data));
console.log(`Activity: ${days.length} days, ${days.reduce((s, d) => s + d.count, 0)} contributions`);
