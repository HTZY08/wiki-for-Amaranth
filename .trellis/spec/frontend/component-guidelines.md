# Component Guidelines

> How components are built in this project.

---

## Overview

This is a **content-only** Starlight site. There are no custom Astro/UI components — all pages are markdown files under `src/content/docs/`. The only "components" are:

1. **Markdown content files** (`.md`) — under `src/content/docs/`
2. **Starlight built-in components** — navigation, table of contents, search, etc.
3. **Astro configuration** — `astro.config.mjs` and `content.config.ts`

---

## Content File Structure

Each `.md` file is a Starlight content page:

```markdown
---
title: Page Title
description: Brief description for search/snippets
---

## Section Heading

Content here...

### Sub-section

More content...
```

---

## When to Add Custom Components

**Almost never.** This project intentionally uses Starlight defaults to keep maintenance low. Only add custom Astro/React components when:

1. Native markdown cannot express the required layout
2. Starlight doesn't provide the feature (unlikely for a doc site)

If you do add components, place them in `src/components/` (create the directory).

---

## Styling

All style customizations go in `src/styles/custom.css`:
- Starlight CSS variable overrides only
- Font stack, accent color, dark mode
- No component-specific stylesheets

---

## Deploy Configuration

The site deploys to Cloudflare Pages via GitHub Actions. Key files:
- `.github/workflows/deploy.yml` — CI/CD pipeline
- No manual build/deploy steps needed

---

## Accessibility

- Starlight provides built-in a11y (semantic HTML, keyboard nav, focus management)
- Markdown content should use proper heading hierarchy (h1 → h2 → h3, never skip levels)
- Alt text on images is strongly recommended
