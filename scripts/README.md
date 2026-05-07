# Ingestion Scripts

Python scripts that extract text from local documents and external URLs to
build the full-text search corpus.

## Prerequisites

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Scripts

### `extract_local.py`

Extracts text from PDFs, DOCX, and PPTX files referenced by resource entries'
`local_path` front-matter field. Output goes to `site/_search/cache/local/<slug>.txt`.

```bash
python scripts/extract_local.py          # incremental (skips if cache is newer)
python scripts/extract_local.py --force  # re-extract everything
```

### `fetch_external.py`

Fetches and extracts text from external URLs referenced by resource entries'
`source_url` front-matter field. Output goes to `site/_search/cache/external/<hash>.txt`.

- Respects `robots.txt`
- Uses conditional requests (ETag / Last-Modified) for efficiency
- Maintains `site/_search/cache/manifest.json` for cache tracking
- 30-second per-request timeout

```bash
python scripts/fetch_external.py              # incremental (7-day max-age)
python scripts/fetch_external.py --max-age 1  # re-fetch if older than 1 day
python scripts/fetch_external.py --force      # ignore cache, re-fetch all
```

## Output

Extracted text files are written to `site/_search/cache/` and are gitignored.
They are consumed by the search index build step (Session 5).
