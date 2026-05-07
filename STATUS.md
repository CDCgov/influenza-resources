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

### Deferred to Session 3

- Vendor Serif theme files (layouts, includes, SCSS) at a pinned commit.
- `site/Gemfile` and `site/_config.yml`.
- Working `bundle exec jekyll serve`.
- Home page, sample category index, sample resource page with placeholder data.
- Navigation with five categories.

---

## Session 2 — Jekyll Site with Serif Theme ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File / Directory | Description |
|---|---|
| `site/Gemfile` + `site/Gemfile.lock` | Pinned Ruby dependencies (Jekyll 4.3, webrick, jekyll-environment-variables) |
| `site/_config.yml` | Site configuration — `_resources` collection, category enumeration, Serif theme settings |
| `site/_layouts/` | Vendored Serif layouts (default, home, page) + custom layouts (resource, resources, category) |
| `site/_includes/` | Vendored Serif includes (header, footer, menus, hamburger, social, etc.) |
| `site/_sass/` | Vendored Serif SCSS (Bootstrap 5.3.2, components, pages) + custom `_resource.scss` |
| `site/assets/` | CSS entrypoint (`style.scss`), JS (`scripts.js`), fonts (Playfair Display woff2) |
| `site/images/` | Logo SVGs and favicon from Serif theme |
| `site/_data/menus.yml` | Navigation: 5 categories + Resources + Search in main menu; footer links |
| `site/_data/seo.yml` | Copyright text for footer |
| `site/_data/contact.yml` | Cleared contact data (empty email/phone) |
| `site/index.md` | Home page — category grid + recent resources |
| `site/pages/resources.md` | All-resources index page |
| `site/pages/search.md` | Search stub (placeholder for Pagefind in Session 5) |
| `site/pages/submit.md` | "Submit a Resource" contribution guide |
| `site/pages/categories/*.md` | 5 category landing pages (laboratory, zoonotic, epidemiology, training, software) |
| `site/_resources/laboratory/miseq-library-loading.md` | Sample resource entry with real metadata |

### Theme Vendoring Details

- **Source:** Jekyll Serif Theme v1.4 (commit `a323305ac59c537850ad35334df7a10124d4ca80`)
- **Reason:** Not published as a gem; `remote_theme` fragile; vendoring gives full control and offline reproducibility
- **Sass warnings:** Bootstrap 5.3.2 emits `@import` deprecation warnings (cosmetic, non-blocking)

### Verification

```bash
cd site && bundle install && bundle exec jekyll build
# Produces _site/ with themed pages at:
#   / (home), /resources/, /categories/{laboratory,zoonotic,epidemiology,training,software}/
#   /resources/laboratory/miseq-library-loading/, /search/, /submit/
```

## Session 3 — Content Model & Seed Entries
**Status:** Not started

## Session 4 — Ingestion Scripts
**Status:** Not started

## Session 5 — Search Index & UI
**Status:** Not started

## Session 6 — CI/CD, Docs, Polish
**Status:** Not started
