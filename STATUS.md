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

## Session 3 — Content Model & Seed Entries ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File | Description |
|---|---|
| `site/_resources/laboratory/miseq-library-loading.md` | LP-309 Rev02D — MiSeq Library Loading Preparation |
| `site/_resources/laboratory/automated-rna-extraction-qiacube.md` | LP-381 Rev0D — Automated RNA Extraction using QIAcube HT |
| `site/_resources/laboratory/rt-pcr-sars-cov2-sgene.md` | LP-471 Rev03D — RT-PCR of SARS-CoV-2 S-gene |
| `site/_resources/laboratory/mrt-pcr-influenza-a-rev01.md` | LP-497 Rev01D — MRT-PCR of Influenza A (superseded) |
| `site/_resources/laboratory/mrt-pcr-influenza-a.md` | LP-497 Rev02D — MRT-PCR of Influenza A (current) |
| `site/_resources/laboratory/nanopore-sequencing-infa-sarscov2-rev00.md` | LP-512 Rev00D — Nanopore Sequencing InfA/SARS-CoV-2 (superseded) |
| `site/_resources/laboratory/nanopore-sequencing-infa-sarscov2.md` | LP-512 Rev01D — Nanopore Sequencing InfA/SARS-CoV-2 (current) |
| `site/_resources/laboratory/m-rtpcr-influenza-a-b.md` | LP-513 Rev00D — M-RTPCR of Influenza A and B |
| `site/_resources/laboratory/mrt-pcr-purification-exonuclease.md` | LP-514 Rev00D — MRT-PCR Purification using Exonuclease |
| `site/_resources/laboratory/dna-quantification-qubit.md` | LP-516 Rev00D — DNA Quantification with Qubit |
| `site/_resources/laboratory/miseq-ngs-run.md` | LP-517 Rev00D — Performing a MiSeq NGS Run |
| `site/_resources/laboratory/illumina-dna-prep-manual.md` | LP-519 Rev00D — Manual Illumina DNA Prep Library |
| `site/_resources/laboratory/qiaxcel-sample-prep-qc.md` | LP-520 Rev00D — QIAxcel Sample Prep and QC |

### Notes

- **13 resource entries** created, one per PDF in `docs/laboratory/`
- **Superseded relationships:** LP-497 Rev01→Rev02, LP-512 Rev00→Rev01 linked via `supersedes` front-matter
- **No external URLs added** — all entries reference only local PDFs committed in `docs/laboratory/`
- **Other categories** (zoonotic, epidemiology, training, software) remain empty — no docs exist for those yet

## Session 4 — Ingestion Scripts ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File | Description |
|---|---|
| `scripts/extract_local.py` | Extracts text from local PDFs/DOCX/PPTX referenced in resource `local_path`; writes to `site/_search/cache/local/<slug>.txt`; incremental (skips if cache newer than source) |
| `scripts/fetch_external.py` | Fetches external URLs from resource `source_url`; extracts HTML/PDF text; writes to `site/_search/cache/external/<hash>.txt`; respects robots.txt, conditional requests (ETag/Last-Modified), configurable `--max-age` |
| `scripts/requirements.txt` | Pinned Python deps: beautifulsoup4, pdfminer.six, python-docx, python-pptx, PyYAML, requests |
| `scripts/README.md` | Usage documentation for both scripts |

### Test Results

- `extract_local.py`: 13/13 PDFs extracted successfully (3,250–20,328 chars each)
- `extract_local.py` re-run: 0 extracted, 13 skipped (incremental caching works)
- `fetch_external.py`: runs cleanly with no external URLs (none in current resources)
- Cache files properly gitignored

## Session 5 — Search Index & UI ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File | Description |
|---|---|
| `scripts/build_search_pages.py` | Generates synthesised hidden HTML pages from cache + front-matter into `_site/_search_pages/` for Pagefind indexing |
| `site/pages/search.md` | `/search/` page with Pagefind UI (input, results, category filter) |
| `site/_layouts/resource.html` | Updated with `data-pagefind-body`, `data-pagefind-meta`, `data-pagefind-filter` attributes |

### Search Engine

- **Pagefind 1.5.2** — client-side, chunk-loaded index
- 26 pages indexed (13 visible resource pages + 13 synthesised full-text pages)
- 2,596 words indexed, 1 filter (category)
- Built-in `pagefind-ui.js` for search UI

### Pipeline

```bash
cd site && bundle exec jekyll build                    # 1. Jekyll build
cd .. && python scripts/build_search_pages.py          # 2. Inject synthesised pages
npx pagefind@1.5.2 --site site/_site                   # 3. Pagefind index
```

### Also Fixed

- All three scripts (`extract_local.py`, `fetch_external.py`, `build_search_pages.py`) now use PyYAML for front-matter parsing (fixes multi-line `summary` fields using YAML block scalars)

## Session 6 — CI/CD, Docs, Polish ✅

**Date:** 2026-05-07  
**Status:** Complete

### Delivered

| File | Description |
|---|---|
| `.github/workflows/build-site.yml` | CI/CD: Ruby + Python + Node setup → extract text → Jekyll build → Pagefind → deploy to GitHub Pages (on push to `main`) |
| `.github/workflows/check-links.yml` | Scheduled weekly link checker (lychee) — creates issue on broken links |
| `.github/workflows/add-resource.yml` | Issue-to-PR automation: "Add Resource" issue form auto-generates resource file + PR |
| `.github/ISSUE_TEMPLATE/add-resource.yml` | GitHub issue form template for submitting new resources |
| `site/README.md` | Developer guide: prerequisites, quick start, build pipeline, how to add resources, directory structure, search docs, CI/CD overview |

### Accessibility Fixes

- Added skip-to-content link (`<a href="#main-content">Skip to main content</a>`) visible on keyboard focus
- Replaced `<div class="header">` with `<header>` semantic element with `role="banner"`
- Replaced `<div class="footer">` with `<footer>` semantic element with `role="contentinfo"`
- Added `<main id="main-content">` landmark wrapping page content
- Added `aria-hidden="true"` to decorative SVG icon in header
- `lang="en"` already present on `<html>` element
- All form inputs have `aria-label` attributes
- All images have `alt` text

### UI Polish (pre-Session 6)

- Replaced category pills with large image card boxes with placeholder SVG icons
- Removed Jekyll Serif logo; centered and enlarged header search box
- Added home icon (house SVG) to left of search bar
- Added flu virion pencil drawing as hero image on homepage
- Updated category SVGs and enlarged card image area
