# Content Development Guidelines

> Best practices for creating and maintaining wiki content.

---

## Overview

This directory contains guidelines for the wiki project. The project is a Starlight/Astro content site. Most templates (hooks, state management, type safety) are **Not Applicable** because this project has no custom UI components.

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Project layout and file naming | ✅ Filled |
| [Component Guidelines](./component-guidelines.md) | Content structure, styling, deployment | ✅ Filled |
| [Quality Guidelines](./quality-guidelines.md) | Content standards, frontmatter, build | ✅ Filled |
| [Hook Guidelines](./hook-guidelines.md) | — | N/A (no custom hooks) |
| [State Management](./state-management.md) | — | N/A (content-only site) |
| [Type Safety](./type-safety.md) | — | N/A (minimal TypeScript) |

---

## Key Rules

1. **Every .md file needs `title` + `description` frontmatter**
2. **Run `npm run build` before committing** — site must compile clean
3. **Keep sidebar in astro.config.mjs in sync with actual content**
4. **Don't manually edit ai-daily/ files** — they're cron-generated
