# Content Schema — Resource Entries

> This document defines the YAML front-matter fields for resource entries in the
> `_resources` Jekyll collection and explains how they are used by layouts,
> category pages, and the search index.

---

## Collection: `_resources`

Each resource is a single Markdown file under `site/_resources/`. Files may be
organised into category subdirectories (e.g., `_resources/laboratory/`) for
convenience — subdirectory names do not affect output paths (controlled by
permalink config).

**Filename convention:** `<short-slug>.md`  
Example: `_resources/laboratory/miseq-library-loading.md`

---

## Front-Matter Fields

```yaml
---
# REQUIRED
title: "MiSeq Library Loading Preparation"       # Human-readable title
category: laboratory                               # Primary category (single value)
summary: >-                                        # 1–3 sentence description
  Standard operating procedure for preparing and loading
  libraries onto the Illumina MiSeq platform.

# RECOMMENDED
source_url: "https://www.cdc.gov/flu/..."          # Canonical external URL (omit if local-only)
local_path: "docs/laboratory/LP-309Rev02D - MiSeq Library Loading Preparation.pdf"
                                                    # Repo-relative path to committed file (omit if external-only)
pub_date: 2024-01-15                               # Publication or clearance date (YYYY-MM-DD)

# OPTIONAL
tags:                                              # Additional taxonomy tags
  - sequencing
  - illumina
  - miseq
authors:                                           # Author(s) or originating group
  - "CDC Influenza Division"
revision: "Rev02D"                                 # Document revision identifier
supersedes: ""                                     # Slug of the resource this replaces (if any)
---
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | **yes** | Display title of the resource. |
| `category` | string | **yes** | Exactly one of: `laboratory`, `zoonotic`, `epidemiology`, `training`, `software`. Used for category landing pages and filtering. |
| `summary` | string | **yes** | 1–3 sentence plain-text summary. Displayed in listings and search results. |
| `source_url` | string | recommended | Canonical URL on cdc.gov or other authoritative source. Omit only if the resource exists solely as a local file. |
| `local_path` | string | recommended | Repo-relative path to a committed PDF, DOCX, or PPTX. Used by `extract_local.py` to generate search text. |
| `pub_date` | date | recommended | ISO 8601 date of publication or CDC clearance. Used for sorting. |
| `tags` | list of strings | optional | Free-form tags for cross-cutting topics. |
| `authors` | list of strings | optional | Authoring person(s) or group(s). |
| `revision` | string | optional | Document revision string (mirrors the document's own revision label). |
| `supersedes` | string | optional | Slug (filename without `.md`) of the older resource this entry replaces. Allows UI to show "superseded" badges. |

---

## Allowed Categories

Categories are a **closed enumeration** maintained in `_config.yml` under
`collections.resources.categories`. To add a new category:

1. Add it to the list in `_config.yml`.
2. Create a corresponding landing page at `site/pages/categories/<name>.md`.
3. Begin adding resources with `category: <name>`.

Current categories:

| Slug | Display Name |
|---|---|
| `laboratory` | Laboratory |
| `zoonotic` | Zoonotic |
| `epidemiology` | Epidemiology |
| `training` | Training |
| `software` | Software |

---

## Body Content

The Markdown body below the front-matter is **optional**. If present, it renders
as the main content of the individual resource page. Typical uses:

- Extended description or context not suited for the short `summary`.
- Instructions for using or citing the resource.
- Changelog or revision notes.

If the body is empty, the resource page will render only the front-matter
metadata (title, summary, links, tags).

---

## Relationship to Search Index

| Front-matter field | Pagefind mapping |
|---|---|
| `title` | `data-pagefind-meta="title"` |
| `category` | `data-pagefind-filter="category"` |
| `summary` | `data-pagefind-meta="summary"` |
| `source_url` / page URL | `data-pagefind-meta="url"` |
| Extracted text (from `local_path` or `source_url`) | `data-pagefind-body` content in synthesised page |

The `build_search_pages.py` script (Session 5) combines front-matter metadata
with extracted text from `_search/cache/` to produce hidden HTML pages that
Pagefind indexes alongside the visible site content.
