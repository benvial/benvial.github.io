---
title: "Setting Up Your First Astro Project"
course: "astro-fundamentals"
section: "Getting Started"
duration: "05:18"
videoUrl: "/videos/intro2.mp4"
---

# Setting Up Your First Astro Project

Now that you understand what Astro is and why it's powerful, it's time to get your hands dirty and create your first Astro project. In this lesson, we'll walk through the entire setup process, explore the project structure, and make your first changes to see Astro in action.

## What You'll Learn

In this lesson, you'll learn:
- How to install Astro and create a new project
- Understanding Astro's project structure and key files
- Running the development server and making your first changes
- Basic configuration options and customization
- How to add your first page and component

## Prerequisites

Before we begin, make sure you have:
- Node.js version 18 or higher installed
- A code editor (VS Code recommended)
- Basic familiarity with the command line
- Understanding of HTML, CSS, and JavaScript fundamentals

## Creating Your First Astro Project

### Using the Astro CLI

The fastest way to create an Astro project is using the official create-astro command. This interactive tool will guide you through the setup process and let you choose from several starter templates.

```bash
npm create astro@latest
```

The CLI will ask you several questions:
- **Project name**: Choose a descriptive name for your project
- **Template**: Select from minimal, blog, portfolio, or other starter templates
- **TypeScript**: Whether to use TypeScript (recommended for larger projects)
- **Dependencies**: Whether to install dependencies automatically
- **Git repository**: Whether to initialize a Git repository

For your first project, we recommend starting with the "minimal" template to understand Astro's core concepts without additional complexity.

### Alternative Installation Methods

You can also specify options directly in the command:

```bash
# Create with specific template
npm create astro@latest my-astro-site -- --template minimal

# Create with TypeScript
npm create astro@latest my-astro-site -- --template minimal --typescript
```

### Installing Dependencies

If you didn't install dependencies during setup, navigate to your project folder and run:

```bash
cd my-astro-site
npm install
```

## Understanding the Project Structure

Once your project is created, you'll see a folder structure that looks like this:

```
my-astro-site/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   ├── layouts/
│   └── pages/
│       └── index.astro
├── astro.config.mjs
├── package.json
├── tsconfig.json
└── README.md
```

### Key Directories and Files

**`src/` Directory**
This is where all your source code lives. Everything in here gets processed by Astro during the build process.

**`src/pages/`**
This directory contains your website's pages. Astro uses file-based routing, meaning each file in this directory becomes a route on your website. The `index.astro` file becomes your homepage at `/`.

**`src/components/`**
Reusable Astro components go here. These are building blocks you can use across multiple pages to keep your code DRY (Don't Repeat Yourself).

**`src/layouts/`**
Layout components that wrap your pages go here. Layouts are perfect for shared elements like headers, footers, and navigation that appear across multiple pages.

**`public/` Directory**
Static assets that don't need processing go here. Files in this directory are served directly by the web server. This includes images, fonts, favicon, robots.txt, and other static files.

**`astro.config.mjs`**
The main configuration file for your Astro project. Here you can configure integrations, build options, server settings, and more.

**`package.json`**
Contains your project's metadata, dependencies, and npm scripts. This is standard for any Node.js project.

## Running Your Development Server

To start the development server and see your site in action:

```bash
npm run dev
```

This command starts a local development server, typically at `http://localhost:4321`. The server includes:
- **Hot Module Replacement (HMR)**: Changes you make are instantly reflected in the browser
- **Error Overlay**: Helpful error messages displayed directly in the browser
- **Fast Refresh**: Quick reloading without losing application state

### Available Scripts

Your `package.json` includes several useful scripts:

- `npm run dev`: Start the development server
- `npm run build`: Build your site for production
- `npm run preview`: Preview your production build locally
- `npm run astro`: Run Astro CLI commands directly

## Making Your First Changes

### Editing the Homepage

Open `src/pages/index.astro` in your code editor. You'll see an Astro component that looks similar to HTML but with some special features:

```astro
---
// Component frontmatter (JavaScript)
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width" />
    <meta name="generator" content={Astro.generator} />
    <title>Astro</title>
  </head>
  <body>
    <h1>Astro</h1>
  </body>
</html>
```

