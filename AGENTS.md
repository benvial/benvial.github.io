# AGENTS.md — bvial.info

Personal website built with **Enlightr** (Astro theme). Source at repo root, output → `dist/`.

- original website: git@github.com:benvial/benvial.github.io.git
- template: git@github.com:benvial/enlightr.git

## Writting style

- Avoid using em dash — prefer brackets
- Prefer active voice over passive voice
- Use present tense for current work, past tense for completed projects




## Tech stack

| Area | Details |
|------|---------|
| Framework | **Astro ^7.0.0** (`type: "module"`) |
| CSS | **Tailwind CSS ^4.3** via **`@tailwindcss/vite`** |
| Content | **`@astrojs/mdx` ^7**; Markdown with **Shiki** theme `poimandres` |
| SEO / feed / sitemap | **`@lexingtonthemes/seo` ^0.4**; **`@astrojs/sitemap` ^3**; **`@astrojs/rss` ^4** |
| Aliases | `@/*` → `src/*` |

Site URL: `bvial.info` (set in `astro.config.mjs`)

## Folder map

| Path | Role |
|------|------|
| `src/pages/` | File-based routes |
| `src/layouts/` | `BaseLayout.astro`, feature layouts |
| `src/components/` | UI components |
| `src/content/` | Markdown collections (posts, courses, lessons, teachers, team, customers, infopages) |
| `src/styles/` | `global.css` — Tailwind entry, `@theme` tokens |
| `src/images/` | Images referenced from frontmatter |
| `public/` | Static assets served as-is |
| `scripts/` | Build/deploy scripts |

## Commands

| Command | Action |
|---------|--------|
| `npm install` | Install dependencies |
| `npm run dev` | Dev server |
| `npm run build` | Production build → `./dist/` |
| `npm run preview` | Preview production build |
| `npm run deploy` | Deploy to GitHub Pages |

## Content collections (`src/content.config.ts`)

All collections use `glob` loaders from `src/content/` with **Zod** schemas.

### `infopages` — legal-style pages (privacy, terms)
### `customers` — student stories/testimonials
### `team` — team members
### `posts` — blog posts
### `courses` — course definitions with sections/lessons
### `lessons` — per-lesson content (nested under course folder)
### `teachers` — teacher profiles

## Routing

| URL | Source |
|-----|--------|
| `/` | `src/pages/index.astro` |
| `/about`, `/pricing` | Matching `.astro` files |
| `/blog`, `/blog/posts/[...slug]` | `posts` collection |
| `/blog/tags`, `/blog/tags/[tag]` | Tag pages |
| `/courses`, `/courses/[course]`, `/courses/[course]/[lesson]` | Course pages |
| `/team/[...slug]`, `/teachers/[...slug]`, `/customers/[...slug]` | Collection pages |
| `/infopages/[...slug]` | Legal pages |
| `/forms/sign-in`, `sign-up`, `contact` | Form pages |
| `/system/*` | Design system |
| `/rss.xml` | RSS feed |
| `404` | `src/pages/404.astro` |

## Guardrails

- Do **not** rename `src/components/fundations/` — the spelling is intentional
- Avoid widening Zod schemas without updating all layouts that read those fields
- Prefer minimal diffs consistent with existing patterns (`@/` imports, collection names, layout props)
- `astro.config.mjs` and `src/content.config.ts` should change together if routing/collection shape changes

## Lexington Themes docs

- Documentation: https://lexingtonthemes.com/documentation
- Support: https://lexingtonthemes.com/legal/support/
- Theme specs: https://lexingtonthemes.com/templates/enlightr
- Changelog: https://lexingtonthemes.com/changelog/enlightr
