---
title: "What is Astro?"
course: "astro-fundamentals"
section: "Content Collections"
duration: "03:42"
videoUrl: "/videos/intro2.mp4"
---


# What is Astro?

Astro is a modern static site generator that delivers lightning-fast performance by default by shipping less JavaScript to the browser. Its unique island architecture allows developers to build websites using their favorite components — whether from React, Vue, Svelte, or others — without sacrificing performance.

Unlike traditional SPA frameworks, Astro focuses on static-first delivery, meaning your pages render as HTML by default and only hydrate interactive components when needed. This makes it ideal for content-heavy websites like blogs, marketing sites, documentation, and portfolios.

## What You'll Learn

In this lesson, you'll learn:
- The core philosophy behind Astro
- Why Astro is different from other frontend tools
- The types of projects Astro is best suited for
- How Astro's performance model benefits the end user

## The Astro Philosophy

Astro is built around several key principles that distinguish it from other web frameworks:

### Less JavaScript, More Performance
Traditional single-page applications (SPAs) ship entire JavaScript bundles to the browser, even for static content. Astro takes a different approach by rendering pages to static HTML at build time and only adding JavaScript where it's actually needed. This results in faster page loads, better SEO, and improved user experience across all devices.

### Islands Architecture
Astro pioneered the "islands architecture" pattern, where interactive components exist as isolated islands of interactivity within a sea of static HTML. Each island can use different frameworks (React, Vue, Svelte) and only loads JavaScript when the component needs to be interactive. This means you can have a React component for your navigation, a Vue component for your contact form, and a Svelte component for your image gallery—all on the same page.
