#!/usr/bin/env python3
"""Detect protocol version families and mark archived (superseded) revisions.

Protocols are revised over time, and several older revisions may live in
`site/_resources/` alongside the current one. This script groups documents that
look like multiple versions of the same protocol, asks which revision is the
current (latest) one, and records the decision in front-matter:

    Current version   ->  archived: false
                          superseded_by: ""

    Older versions    ->  archived: true
                          superseded_by: "<slug-of-current-version>"

Archived resources are excluded from the All Resources page, category pages,
the home page, and full-text search, and are listed on the Archive page
instead (see the Jekyll layouts).

Grouping signals (any is sufficient to link two documents):
  * an explicit `supersedes:` chain,
  * matching slugs after stripping a trailing `-rev<NN>` suffix,
  * matching titles after stripping a trailing "(Rev<NN>D)" suffix.

Usage:
    python scripts/detect_versions.py            # interactive selection
    python scripts/detect_versions.py --dry-run  # show the plan, write nothing
    python scripts/detect_versions.py --yes      # non-interactive; pick highest revision
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Front-matter helpers
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)

# Trailing "-rev01", "-rev00" style suffix on a slug.
_SLUG_REV_RE = re.compile(r"-rev\d+[a-z]?$", re.IGNORECASE)

# Trailing "(Rev01D)" style suffix on a title.
_TITLE_REV_RE = re.compile(r"\s*\(rev\s*\d+[a-z]?\)\s*$", re.IGNORECASE)

# Numeric portion of a revision label such as "Rev02D".
_REV_NUM_RE = re.compile(r"rev\s*(\d+)", re.IGNORECASE)


def _parse_front_matter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def _split_front_matter(text: str):
    """Return (fm_block, body) where fm_block excludes the `---` delimiters.

    Returns (None, text) when the file has no front-matter.
    """
    m = _FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def _set_fm_keys(fm_block: str, updates: dict) -> str:
    """Set top-level scalar keys in a front-matter block, preserving layout.

    Existing top-level keys are replaced in place; missing keys are inserted
    after `revision:`/`supersedes:` when present, otherwise appended.
    """
    lines = fm_block.split("\n")

    def _anchor_index() -> int:
        anchor = len(lines)
        for i, line in enumerate(lines):
            if re.match(r"^(supersedes|revision):", line):
                anchor = i + 1
        # Skip trailing empty element produced by the block's final newline.
        return min(anchor, len(lines) - 1 if lines and lines[-1] == "" else len(lines))

    for key, value in updates.items():
        pattern = re.compile(rf"^{re.escape(key)}:\s*.*$")
        new_line = f"{key}: {value}"
        for i, line in enumerate(lines):
            if pattern.match(line):
                lines[i] = new_line
                break
        else:
            lines.insert(_anchor_index(), new_line)

    return "\n".join(lines)


def _write_fm_updates(path: Path, updates: dict) -> None:
    text = path.read_text(encoding="utf-8")
    fm_block, body = _split_front_matter(text)
    if fm_block is None:
        raise ValueError(f"{path} has no YAML front-matter")
    new_fm = _set_fm_keys(fm_block, updates)
    path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")


# ---------------------------------------------------------------------------
# Version family detection
# ---------------------------------------------------------------------------

class Doc:
    def __init__(self, path: Path):
        self.path = path
        self.slug = path.stem
        fm = _parse_front_matter(path.read_text(encoding="utf-8"))
        self.title = str(fm.get("title", self.slug))
        self.revision = str(fm.get("revision", "") or "")
        self.supersedes = str(fm.get("supersedes", "") or "")
        self.archived = bool(fm.get("archived", False))

    @property
    def base_slug(self) -> str:
        return _SLUG_REV_RE.sub("", self.slug).lower()

    @property
    def base_title(self) -> str:
        return _TITLE_REV_RE.sub("", self.title).strip().lower()

    @property
    def rev_num(self) -> int:
        m = _REV_NUM_RE.search(self.revision)
        return int(m.group(1)) if m else -1


class _UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _group_families(docs: list) -> list:
    """Group documents into version families using slug/title/supersedes links."""
    by_slug = {d.slug: d for d in docs}
    uf = _UnionFind()
    for d in docs:
        uf.find(d.slug)

    # Link explicit supersedes chains.
    for d in docs:
        if d.supersedes and d.supersedes in by_slug:
            uf.union(d.slug, d.supersedes)

    # Link matching normalized slugs and titles.
    for key_fn in (lambda d: d.base_slug, lambda d: d.base_title):
        buckets = {}
        for d in docs:
            buckets.setdefault(key_fn(d), []).append(d)
        for members in buckets.values():
            for other in members[1:]:
                uf.union(members[0].slug, other.slug)

    families = {}
    for d in docs:
        families.setdefault(uf.find(d.slug), []).append(d)

    return [members for members in families.values() if len(members) > 1]


def _recommend_latest(members: list) -> "Doc":
    """Pick the most likely current version within a family."""
    superseded = {m.supersedes for m in members if m.supersedes}
    not_superseded = [m for m in members if m.slug not in superseded]
    candidates = not_superseded or members
    return max(candidates, key=lambda m: (m.rev_num, m.slug))


# ---------------------------------------------------------------------------
# Interactive selection
# ---------------------------------------------------------------------------

def _prompt_choice(members: list, recommended: "Doc", assume_yes: bool) -> "Doc":
    ordered = sorted(members, key=lambda m: (m.rev_num, m.slug))
    print("\nDetected a version family:")
    for i, m in enumerate(ordered, start=1):
        rec = "  <- recommended" if m is recommended else ""
        rev = m.revision or "(no revision)"
        print(f"  [{i}] {rev:>8}  {m.title}")
        print(f"       slug: {m.slug}{rec}")

    default_idx = ordered.index(recommended) + 1
    if assume_yes or not sys.stdin.isatty():
        print(f"  -> selecting current version: {recommended.slug}")
        return recommended

    while True:
        raw = input(f"Which is the current version? [1-{len(ordered)}, default {default_idx}]: ").strip()
        if not raw:
            return recommended
        if raw.isdigit() and 1 <= int(raw) <= len(ordered):
            return ordered[int(raw) - 1]
        print("  Please enter a valid number.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the plan without writing any files")
    parser.add_argument("--yes", action="store_true",
                        help="Non-interactive: always pick the recommended (highest) revision")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    resources_dir = repo_root / "site" / "_resources"
    if not resources_dir.is_dir():
        print(f"ERROR: {resources_dir} not found", file=sys.stderr)
        return 1

    docs = [Doc(p) for p in sorted(resources_dir.rglob("*.md"))]
    families = _group_families(docs)

    if not families:
        print("No multi-version protocol families detected. Nothing to do.")
        return 0

    print(f"Found {len(families)} version family/families.")
    changes = 0

    for members in families:
        latest = _prompt_choice(members, _recommend_latest(members), args.yes)
        for m in members:
            is_current = m.slug == latest.slug
            updates = {
                "archived": "true" if not is_current else "false",
                "superseded_by": f'"{latest.slug}"' if not is_current else '""',
            }
            label = "archive" if not is_current else "CURRENT"
            print(f"  {label:>7}: {m.slug}"
                  + (f"  -> {latest.slug}" if not is_current else ""))
            if not args.dry_run:
                _write_fm_updates(m.path, updates)
            changes += 1

    if args.dry_run:
        print(f"\nDry run: {changes} file(s) would be updated. No changes written.")
    else:
        print(f"\nDone: {changes} file(s) updated across {len(families)} family/families.")
        print("Rebuild the site (scripts/build.sh) to apply archive filtering.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
