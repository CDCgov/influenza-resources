#!/usr/bin/env python3
"""Generate synthesised hidden HTML pages for Pagefind indexing.

After `jekyll build`, this script reads each resource's front-matter and its
corresponding extracted-text cache file, then writes a hidden HTML page into
_site/_search_pages/<slug>.html with Pagefind data attributes so the full
extracted text is indexed alongside the visible site content.

Usage:
    python scripts/build_search_pages.py
"""

import re
import sys
from html import escape
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# YAML front-matter parser
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _parse_front_matter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def _slug_to_url(rel_path: str, baseurl: str = "") -> str:
    """Build a resource URL from the file's path relative to _resources/.

    Jekyll's `permalink: /resources/:path/` uses the file's collection-relative
    path (without extension), so we mirror that here.
    """
    prefix = baseurl.rstrip("/")
    # rel_path is e.g. "laboratory/illumina-dna-prep-manual" (no .md)
    return f"{prefix}/resources/{rel_path}/"


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{title}</title></head>
<body>
<div data-pagefind-body
     data-pagefind-filter="category:{category}"
     style="display:none;">
<h1 data-pagefind-meta="title">{title}</h1>
<span data-pagefind-meta="url:{url}"></span>
<span data-pagefind-meta="category:{category}"></span>
<p data-pagefind-meta="summary">{summary}</p>
{text}
</div>
</body>
</html>
"""


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    resources_dir = repo_root / "site" / "_resources"
    cache_local = repo_root / "site" / "_search" / "cache" / "local"
    cache_external = repo_root / "site" / "_search" / "cache" / "external"
    site_dir = repo_root / "site" / "_site"
    output_dir = site_dir / "_search_pages"

    # Read baseurl from Jekyll config
    config_path = repo_root / "site" / "_config.yml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    baseurl = config.get("baseurl", "").rstrip("/")

    if not site_dir.is_dir():
        print("ERROR: _site/ not found — run `jekyll build` first", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    generated = 0

    for md_file in sorted(resources_dir.rglob("*.md")):
        fm = _parse_front_matter(md_file.read_text(encoding="utf-8"))

        # Skip archived (superseded) revisions — they must not appear in search.
        if fm.get("archived"):
            print(f"  skipped (archived): {md_file.stem}")
            continue

        title = fm.get("title", md_file.stem)
        summary = fm.get("summary", "")
        slug = md_file.stem

        # Derive category: prefer plural 'categories' list, fall back to singular
        categories = fm.get("categories", [])
        if categories and isinstance(categories, list):
            category = categories[0]
        else:
            category = fm.get("category", "uncategorized")

        # Derive URL from file path relative to _resources/ (mirrors Jekyll :path permalink)
        rel_path = md_file.relative_to(resources_dir).with_suffix("")
        source_url = fm.get("source_url", "")
        url = source_url if source_url else _slug_to_url(str(rel_path), baseurl)

        # Try to find cached extracted text
        extracted_text = ""
        local_cache = cache_local / f"{slug}.txt"
        if local_cache.exists():
            extracted_text = local_cache.read_text(encoding="utf-8")

        # Also check external cache (by scanning manifest or by slug naming)
        # For external, the filename is a URL hash — we read it via slug match
        # from manifest if available
        if not extracted_text:
            manifest_path = cache_external.parent / "manifest.json"
            if manifest_path.exists():
                import json
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                for _key, entry in manifest.items():
                    if entry.get("slug") == slug:
                        ext_cache = cache_external / f"{_key}.txt"
                        if ext_cache.exists():
                            extracted_text = ext_cache.read_text(encoding="utf-8")
                        break

        if not extracted_text:
            # No cached text — still generate a page with just metadata
            # so the resource's title/summary are searchable
            extracted_text = f"{title}\n{summary}"

        html = _PAGE_TEMPLATE.format(
            title=escape(title),
            category=escape(category),
            summary=escape(summary[:200]),
            url=escape(url),
            text=escape(extracted_text),
        )

        out_file = output_dir / f"{slug}.html"
        out_file.write_text(html, encoding="utf-8")
        generated += 1
        print(f"  generated: {slug}.html ({len(extracted_text)} chars)")

    print(f"\nDone: {generated} search pages generated in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
