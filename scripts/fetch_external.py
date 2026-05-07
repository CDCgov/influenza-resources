#!/usr/bin/env python3
"""Fetch and extract text from external URLs referenced in _resources.

For each resource entry with a `source_url` front-matter field, fetches the
page (HTML or PDF), extracts readable text, and writes it to
site/_search/cache/external/<url_hash>.txt.

Maintains a manifest (manifest.json) with ETag / Last-Modified / timestamp
for incremental fetching.

Constraints:
- Respects robots.txt
- User-Agent: influenza-resources-indexer/1.0 (+https://github.com/CDCgov/influenza-resources)
- 30-second per-request timeout
- Supports --max-age (days, default 7)

Usage:
    python scripts/fetch_external.py [--max-age 7] [--force]
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
import yaml
from bs4 import BeautifulSoup

USER_AGENT = "influenza-resources-indexer/1.0 (+https://github.com/CDCgov/influenza-resources)"
REQUEST_TIMEOUT = 30  # seconds

# ---------------------------------------------------------------------------
# YAML front-matter parser (minimal)
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _parse_front_matter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


# ---------------------------------------------------------------------------
# robots.txt cache
# ---------------------------------------------------------------------------

_robots_cache: dict[str, RobotFileParser] = {}


def _can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in _robots_cache:
        rp = RobotFileParser()
        robots_url = f"{origin}/robots.txt"
        try:
            resp = requests.get(robots_url, timeout=10,
                                headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                # No robots.txt or error → allow
                rp.parse([])
        except Exception:
            rp.parse([])
        _robots_cache[origin] = rp
    return _robots_cache[origin].can_fetch(USER_AGENT, url)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_html(content: bytes, encoding: str | None = None) -> str:
    soup = BeautifulSoup(content, "html.parser")
    # Remove script/style
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _extract_pdf_bytes(content: bytes) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(BytesIO(content))


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

def _load_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_manifest(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-age", type=int, default=7,
                        help="Max age in days before re-fetching (default: 7)")
    parser.add_argument("--force", action="store_true",
                        help="Ignore cache and re-fetch everything")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    resources_dir = repo_root / "site" / "_resources"
    cache_dir = repo_root / "site" / "_search" / "cache" / "external"
    cache_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = cache_dir.parent / "manifest.json"
    manifest = _load_manifest(manifest_path)

    max_age_secs = args.max_age * 86400

    if not resources_dir.is_dir():
        print(f"ERROR: resources directory not found: {resources_dir}", file=sys.stderr)
        return 1

    fetched = 0
    skipped = 0
    errors = 0

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    for md_file in sorted(resources_dir.rglob("*.md")):
        fm = _parse_front_matter(md_file.read_text(encoding="utf-8"))
        source_url = fm.get("source_url")
        if not source_url:
            continue

        slug = md_file.stem
        url_key = _url_hash(source_url)
        cache_file = cache_dir / f"{url_key}.txt"

        # Check freshness
        entry = manifest.get(url_key, {})
        if not args.force and entry:
            last_fetched = entry.get("timestamp", 0)
            if time.time() - last_fetched < max_age_secs and cache_file.exists():
                skipped += 1
                continue

        # Check robots.txt
        if not _can_fetch(source_url):
            print(f"  BLOCKED by robots.txt: {source_url}", file=sys.stderr)
            skipped += 1
            continue

        # Build conditional request headers
        headers = {}
        if not args.force and entry:
            if entry.get("etag"):
                headers["If-None-Match"] = entry["etag"]
            if entry.get("last_modified"):
                headers["If-Modified-Since"] = entry["last_modified"]

        try:
            resp = session.get(source_url, timeout=REQUEST_TIMEOUT, headers=headers)
        except Exception as exc:
            print(f"  ERROR fetching {source_url}: {exc}", file=sys.stderr)
            errors += 1
            continue

        if resp.status_code == 304:
            # Not modified — update timestamp only
            entry["timestamp"] = time.time()
            manifest[url_key] = entry
            skipped += 1
            continue

        if resp.status_code != 200:
            print(f"  WARNING: HTTP {resp.status_code} for {source_url}", file=sys.stderr)
            errors += 1
            continue

        # Detect content type and extract text
        content_type = resp.headers.get("Content-Type", "").lower()
        try:
            if "pdf" in content_type or source_url.lower().endswith(".pdf"):
                text = _extract_pdf_bytes(resp.content)
            else:
                text = _extract_html(resp.content,
                                     resp.encoding if resp.encoding else None)

            cache_file.write_text(text, encoding="utf-8")
            manifest[url_key] = {
                "url": source_url,
                "slug": slug,
                "etag": resp.headers.get("ETag", ""),
                "last_modified": resp.headers.get("Last-Modified", ""),
                "timestamp": time.time(),
                "chars": len(text),
            }
            fetched += 1
            print(f"  fetched: {slug} ({len(text)} chars)")
        except Exception as exc:
            print(f"  ERROR extracting {source_url}: {exc}", file=sys.stderr)
            errors += 1

    _save_manifest(manifest_path, manifest)
    print(f"\nDone: {fetched} fetched, {skipped} skipped (cached), {errors} errors")
    return 1 if errors > 0 and fetched == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
