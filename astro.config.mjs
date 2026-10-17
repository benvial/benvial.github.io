import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

import sitemap from "@astrojs/sitemap";
import mdx from "@astrojs/mdx";
import { CODE_THEME } from "./src/scripts/highlight.ts";

// https://astro.build/config
export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
  markdown: {
    drafts: true,
    shikiConfig: {
      theme: CODE_THEME
    }
  },
  shikiConfig: {
    wrap: true,
    skipInline: false,
    drafts: true
  },
  site: 'https://bvial.info',
  redirects: {
    '/blog/posts/2024-02-29-gyptis': '/code/notebooks/gyptis/',
  },
  integrations: [sitemap(), mdx()]
});