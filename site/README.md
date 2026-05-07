# Influenza Division Resources — Site Developer Guide

This directory contains the Jekyll source for the CDC Influenza Division Resource Site.

## Prerequisites

- **Ruby** 3.1+ with Bundler
- **Python** 3.10+ with pip/venv
- **Node.js** 18+ (for Pagefind via npx)

## Quick Start

```bash
# From the repository root:

# 1. Create and activate a Python virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install Python dependencies
pip install -r scripts/requirements.txt

# 3. Install Ruby gems
cd site && bundle install && cd ..

# 4. Full build (extract text → Jekyll → search pages → Pagefind)
./scripts/build.sh

# 5. Build and serve locally
./scripts/build.sh --serve
# Site available at http://127.0.0.1:4000
```

## How the Build Works

The `scripts/build.sh` pipeline runs these steps in order:

1. **`scripts/extract_local.py`** — Extracts text from PDFs in `docs/` using pdfminer.six. Outputs are cached by file modification time.
2. **`scripts/fetch_external.py`** — Fetches external URLs from resource entries, respects robots.txt, caches with ETag/Last-Modified.
3. **`bundle exec jekyll build`** — Builds the Jekyll site into `site/_site/`.
4. **`scripts/build_search_pages.py`** — Generates hidden HTML pages in `_site/_search_pages/` containing full extracted text, annotated with `data-pagefind-*` attributes.
5. **`npx pagefind@1.5.2 --site site/_site`** — Builds the Pagefind client-side search index.

## Adding a Resource

### Option A: GitHub Issue Form

Open a new issue using the **"Add Resource"** template. Fill in the fields and a pull request will be created automatically.

### Option B: Manual

1. Create a new Markdown file under `site/_resources/<category>/`:

   ```markdown
   ---
   title: "Your Resource Title"
   category: laboratory
   summary: >-
     A short 1-3 sentence description.
   source_url: "https://example.com/document"
   local_path: "docs/laboratory/filename.pdf"
   pub_date: 2025-01-15
   tags:
     - pcr
     - protocol
   ---
   ```

2. If adding a local file, place the PDF/DOCX/PPTX in the appropriate `docs/` subdirectory.
3. Run `./scripts/build.sh` to rebuild and verify.
4. Commit and open a pull request.

### Resource Front-Matter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Human-readable title |
| `category` | Yes | One of: `laboratory`, `zoonotic`, `epidemiology`, `training`, `software` |
| `summary` | Yes | 1–3 sentence plain-text description |
| `source_url` | No | Canonical URL (e.g. on cdc.gov) |
| `local_path` | No | Repo-relative path to a committed file |
| `pub_date` | No | ISO 8601 date (YYYY-MM-DD) |
| `tags` | No | List of keyword tags |
| `authors` | No | List of author names |
| `revision` | No | Document revision identifier |
| `supersedes` | No | Slug of the resource this replaces |

## Directory Structure

```
site/
├── _config.yml          # Jekyll configuration
├── _data/menus.yml      # Navigation menus
├── _includes/           # Header, footer, nav partials
├── _layouts/            # Page layouts (home, resource, resources, category)
├── _resources/          # Resource entries (one .md per resource)
│   └── laboratory/      # Category subdirectory
├── _sass/               # SCSS source (Bootstrap + custom)
├── images/              # Site images and category icons
├── pages/               # Static pages (search, submit, categories)
└── docs -> ../docs      # Symlink to repo-level docs for PDF access

scripts/
├── build.sh             # Full build pipeline
├── build_search_pages.py
├── extract_local.py
├── fetch_external.py
└── requirements.txt
```

## Search

The site uses [Pagefind](https://pagefind.app/) for client-side full-text search. The search index includes:

- All resource page content (titles, summaries, metadata)
- Full text extracted from local PDFs
- Text fetched from external URLs

Search is available via the header search bar (redirects to `/search/` with query) and the dedicated `/search/` page.

## CI/CD

- **`.github/workflows/build-site.yml`** — Builds and deploys to GitHub Pages on push to `main`.
- **`.github/workflows/check-links.yml`** — Weekly link checker (Monday 06:30 UTC). Creates an issue if broken links are found.
- **`.github/workflows/add-resource.yml`** — Auto-creates a PR from an "Add Resource" issue.
