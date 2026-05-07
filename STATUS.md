# STATUS.md — Project Progress

---

## Session 1 — Plan & Scaffold ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File / Directory | Description |
|---|---|
| `PLAN.md` | Architectural decisions: directory layout, vendored Serif theme, Pagefind search, Python scripts, CI strategy |
| `site/_data/schema.md` | Content schema documenting YAML front-matter fields for `_resources` collection |
| `site/_layouts/` | Empty scaffold (`.gitkeep`) |
| `site/_includes/` | Empty scaffold |
| `site/_sass/` | Empty scaffold |
| `site/_resources/{laboratory,zoonotic,epidemiology,training,software}/` | Empty scaffold — one subdir per category |
| `site/_search/cache/{local,external}/` | Empty scaffold for extracted-text cache |
| `site/assets/{css,js,images}/` | Empty scaffold |
| `site/pages/categories/` | Empty scaffold for category landing pages |
| `scripts/` | Empty scaffold for Python ingestion scripts |
| `.github/workflows/` | Empty scaffold for CI |
| `.gitignore` | Ignores for `_site/`, `.jekyll-cache/`, search cache contents, `__pycache__/`, `.DS_Store` |

### Decisions Recorded in PLAN.md

1. **Theme:** Vendored Jekyll Serif (not `remote_theme`, not gem-based) — full control, offline reproducibility.
2. **Content model:** `_resources` Jekyll collection with one `.md` per resource; subdirectories per category.
3. **Search:** Pagefind (primary), Lunr.js (fallback). Synthesised hidden HTML pages inject extracted text for full-corpus indexing.
4. **Scripts:** Python 3.10+ — `extract_local.py`, `fetch_external.py`, `build_search_pages.py`.
5. **CI:** GitHub Actions — Python + Ruby + Pagefind → deploy to GitHub Pages.

### Deferred to Session 2

- Vendor Serif theme files (layouts, includes, SCSS) at a pinned commit.
- `site/Gemfile` and `site/_config.yml`.
- Working `bundle exec jekyll serve`.
- Home page, sample category index, sample resource page with placeholder data.
- Navigation with five categories.

---

## Session 2 — Jekyll Site with Serif Theme
**Status:** Not started

## Session 3 — Content Model & Seed Entries
**Status:** Not started

## Session 4 — Ingestion Scripts
**Status:** Not started

## Session 5 — Search Index & UI
**Status:** Not started

## Session 6 — CI/CD, Docs, Polish
**Status:** Not started
