# Project Brief: CDC Influenza Division Resource Site

## Role

You are Claude Opus 4.7 acting as a senior full-stack engineer with expertise in Jekyll, GitHub Pages, client-side search (Pagefind / Lunr.js), Ruby tooling, and Python scripting for content ingestion. Treat this brief as authoritative; ask clarifying questions only when a hard blocker is encountered.

## Repository Context

- Repo: `influenza-resources` (CDCgov template-based, public domain).
- Existing top-level files MUST be preserved unchanged these include: `README.md` (must remain the rendered landing page on github.com), `LICENSE`, `CONTRIBUTING.md`, `DISCLAIMER.md`, `code-of-conduct.md`, `open_practices.md`, `rules_of_behavior.md`, `thanks.md`.
- Existing folder: `docs/laboratory/` (contains laboratory pdf documents).
- The Jekyll site will be built and served from a separate folder (`site/`) so it does not interfere with the GitHub-rendered `README.md`. GitHub Pages will publish via a GitHub Actions workflow (preferred) or from `/site` based on a git tag change.

## Goal

Stand up a minimal, accessible bundle site using the **Jekyll Serif theme** (https://github.com/zerostaticthemes/jekyll-serif-theme) that serves as a curated index of **CDC-cleared documents and links from the CDC Influenza Division** (https://www.cdc.gov/flu/index.html). The site is a "dumping ground" with structure, summaries, and full-text search.

### Required content categories (extensible)
- `laboratory`
- `zoonotic`
- `epidemiology`
- `training`
- `software`

Each resource entry must include: title, source URL (or local file path), category (one or more tags), publication/clearance date if known, and a short summary (1–3 sentences).

### Required features
1. Themed Jekyll site (Serif theme) under `site/`, buildable locally and via GitHub Pages / GitHub Actions.
2. Category landing pages, individual resource pages, and a global index.
3. **Full-text search** that indexes:
   - All Markdown/HTML content authored in the repo.
   - Text extracted from local PDFs and Office documents committed to the repo.
   - Text extracted from linked external URLs (fetched and cached at build time).
4. Accessory build scripts (Python preferred) that produce the search corpus as a build step. Default search engine: **Pagefind**; fallback: **Lunr.js**. Index must work fully client-side.
5. CI workflow under `.github/workflows/` that runs ingestion + index build + Jekyll build + Pages deploy.
6. No modification of the root `README.md`.

### Non-goals
- No backend server, no auth, no database.
- No re-hosting of CDC content beyond what is necessary for search indexing; prefer linking with cached extracted text used only for the index.

## Constraints & Standards

- Public domain / CC0 — keep CDCgov template notices intact.
- Accessibility: target WCAG 2.1 AA; semantic HTML, alt text, sufficient contrast.
- Performance: static output; lazy-load search index; keep JS payload modest.
- Reproducible builds: pin Ruby gems (`Gemfile.lock`), pin Python deps (`requirements.txt` or `pyproject.toml`), pin Node deps if used.
- All scripts must be idempotent and safe to re-run.
- External URL fetching must respect `robots.txt`, set a descriptive User-Agent, cache responses (ETag/Last-Modified), have timeouts, and degrade gracefully on failure.

---

## Execution Plan — Distinct Sessions

Execute the following sessions **in order, one per conversation / context window**, to maximize accuracy. At the end of each session: (a) commit changes with clear messages prefixed with the session number (e.g. `S2: scaffold Jekyll Serif site`), (b) update a top-level `STATUS.md` summarizing what landed and what is deferred, (c) stop and wait for the user before starting the next session.

### Session 1 — Plan & Scaffold
**Inputs:** this file, current repo state.
**Deliverables:**
- `PLAN.md` at repo root capturing decisions: directory layout, theme integration approach (vendored vs. `remote_theme` vs. gem-based), search engine choice (Pagefind vs. Lunr) with rationale, list of accessory scripts to be written, CI strategy.
- A content schema doc (e.g. `site/_data/schema.md`) defining the YAML front-matter fields for each resource entry and the `_data/resources.yml` structure if used.
- Empty directory scaffold under `site/` matching the planned layout.
- No theme code yet. No content yet.
**Exit criteria:** A reviewer can read `PLAN.md` and understand exactly what subsequent sessions will produce.

### Session 2 — Jekyll Site with Serif Theme (no real content)
**Inputs:** `PLAN.md`.
**Deliverables:**
- `site/Gemfile`, `site/_config.yml`, layouts/includes/SCSS as needed to render the Serif theme. Prefer `remote_theme: zerostaticthemes/jekyll-serif-theme` if it works; otherwise vendor the theme files and document why.
- Working `bundle exec jekyll serve` from `site/`.
- Home page, a category index page, and a single sample resource page using placeholder data.
- Navigation listing the five required categories.
- `.gitignore` updates for `site/_site/`, `site/.jekyll-cache/`, `vendor/`, etc.
**Exit criteria:** `cd site && bundle install && bundle exec jekyll build` succeeds locally and produces `_site/` with the themed home page.

### Session 3 — Content Model & Seed Entries
**Inputs:** running site from Session 2.
**Deliverables:**
- Final content model: either a `_resources` Jekyll collection (preferred) with one Markdown file per entry, or `_data/resources.yml` with rendered list pages — pick one in `PLAN.md` and implement it.
- Category taxonomy implemented (tags or collections).
- laboratory docs from `docs/laboratory/*.pdf` referenced in place, with corresponding resource entries created.
- Category landing pages auto-generated from the collection/data.
- A "Submit a resource" stub page describing how to contribute (link to `CONTRIBUTING.md`).
**Exit criteria:** The built site shows populated categories with real CDC Influenza Division links and summaries.

### Session 4 — Ingestion Scripts (local files + external URLs)
**Inputs:** content model from Session 3.
**Deliverables:**
- `scripts/` directory with Python tooling:
  - `extract_local.py` — extracts text from PDFs/DOCX/PPTX under `site/assets/docs/` (and `docs/`) into `site/_search/cache/local/*.txt`.
  - `fetch_external.py` — for each entry's external URL, fetches HTML/PDF, extracts readable text, writes to `site/_search/cache/external/<hash>.txt`. Maintains a `cache/` with ETag/Last-Modified, supports a `--max-age` flag, respects `robots.txt`, sets User-Agent `influenza-resources-indexer/1.0 (+https://github.com/CDCgov/influenza-resources)`, and times out gracefully.
  - `requirements.txt` (or `pyproject.toml`) pinning `requests`, `beautifulsoup4`, `pdfminer.six` (or `pypdf`), `python-docx`, `python-pptx`, `pyyaml`, `tldextract`.
  - `scripts/README.md` explaining usage.
- Cache directory committed empty (with `.gitkeep`); cache contents gitignored.
**Exit criteria:** Running `python scripts/extract_local.py && python scripts/fetch_external.py` populates `site/_search/cache/` with extracted text for every committed/linked resource, and re-runs are incremental.

### Session 5 — Search Index & UI
**Inputs:** ingestion output from Session 4.
**Deliverables:**
- Integration of **Pagefind** (default) into the Jekyll build:
  - A build step that, after `jekyll build`, synthesizes hidden indexable pages from the cached extracted text (using `data-pagefind-body` and `data-pagefind-meta`) so Pagefind indexes the full corpus, not just the visible site.
  - A `/search/` page with a Pagefind UI input and result list.
  - Result entries show title, category, summary, and link to either the resource page or the external URL.
- If Pagefind is unsuitable, implement Lunr.js fallback with a generated `search-index.json`.
- Document the final choice and tradeoffs in `PLAN.md`.
**Exit criteria:** Searching for terms that appear only inside a linked external PDF or webpage returns the corresponding resource entry on the locally built site.

### Session 6 — CI/CD, Docs, Polish
**Inputs:** working site + search.
**Deliverables:**
- GitHub Actions workflow `.github/workflows/build-site.yml` that: sets up Ruby + Python, installs deps, runs `extract_local.py` and `fetch_external.py`, runs `jekyll build`, runs Pagefind, and deploys `site/_site/` to GitHub Pages.
- A scheduled link-checking workflow (or job).
- `site/README.md` with developer instructions (how to add a resource, how to build locally, how the index works). The repo-root `README.md` remains untouched.
- Accessibility pass: heading order, landmarks, alt text, color contrast against Serif theme defaults.
- Final `STATUS.md` summary.
**Exit criteria:** Tagging builds and deploys the site automatically; the deployed site has working full-text search across all entries and their linked content.

---

## Working Rules (apply to every session)

1. **Never modify** `README.md` at the repo root.
2. Keep all site code under `site/`; keep all helper scripts under `scripts/`; keep CI under `.github/workflows/`.
3. Prefer minimal, well-documented diffs. No speculative features.
4. Pin all dependency versions.
5. Do not commit fetched third-party content beyond what is necessary for search indexing; store only extracted text in a gitignored cache.
6. Use commit messages prefixed with the session number (e.g. `S2: ...`).
7. At the end of each session, list: files added/changed, commands to verify, and explicit deferrals to later sessions.
8. If a step is blocked (e.g. theme incompatibility with GitHub Pages `remote_theme`), document the blocker in `PLAN.md`, take the documented fallback, and proceed.

## Begin

When instructed to start, perform **Session 2 only** and stop.