import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";

const infopages = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/infopages" }),
  schema: z.object({
    page: z.string(),
    pubDate: z.coerce.date(),
  }),
});

const postsCollection = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/posts" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional(),
    author: z.string().optional(),
    tags: z.array(z.string()),
    category: z.string().optional(),
    image: z
      .object({
        url: z.string(),
        alt: z.string(),
      })
      .optional(),
  }),
});

const research = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/research" }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      description: z.string(),
      pubDate: z.coerce.date(),
      image: z.object({
        url: image(),
        alt: z.string(),
      }),
      tags: z.array(z.string()),
    }),
});

const code = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/code" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    url: z.string().url(),
    language: z.string().optional(),
    stars: z.number().optional(),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = {
  infopages,
  posts: postsCollection,
  research,
  code,
};
