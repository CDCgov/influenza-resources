# Copilot Coding Agent Instructions

## Handling `add-resource` Issues

When assigned an issue with the `add-resource` label, follow these steps:

### 1. Parse the Issue

The issue body is generated from a GitHub issue form. It will render as markdown with
`### Label` headers followed by the user's input. Here is an example of what the raw
issue body looks like:

```
### Resource Title

RT-PCR Protocol for Influenza A Subtyping

### Category

laboratory

### Document

[LP-519Rev00D - Manual Procedure.pdf](https://github.com/user-attachments/files/12345678/LP-519Rev00D.-.Manual.Procedure.pdf)

### Source URL

https://www.cdc.gov/flu/professionals/laboratory/...
```

Extract these fields by finding the text after each `### <Label>` header:

| Field | Header in issue body | Required | Notes |
|-------|---------------------|----------|-------|
| Title | `### Resource Title` | Yes | Human-readable title |
| Category | `### Category` | Yes | One of: `laboratory`, `zoonotic`, `epidemiology`, `training`, `software` |
| Document | `### Document` | No | May contain a markdown link to an uploaded file attachment |
| Source URL | `### Source URL` | No | Canonical URL. Ignore if blank or `_No response_` |

**Parsing rules:**
- Fields appear in the order above, separated by `### ` headers
- Empty/blank fields or `_No response_` mean the field was not provided
- The Document field may contain a markdown link `[filename](url)` to a GitHub-uploaded file
- The Document field may also be plain text (ignore if no URL present)

If required fields are missing or the category is invalid, comment on the issue explaining what's needed and stop.

### 2. Create the Resource File

Create `site/_resources/<category>/<slug>.md` where `<slug>` is the title lowercased, non-alphanumeric characters replaced with hyphens, leading/trailing hyphens trimmed, max 80 characters.

Example: title `"RT-PCR Protocol for Influenza A Subtyping"` → slug `rt-pcr-protocol-for-influenza-a-subtyping`

Use this YAML front matter format (follow existing files in `site/_resources/` as examples):

```yaml
---
title: "<title>"
category: <category>
summary: >-
  <A concise 1-2 sentence summary of the resource>
source_url: "<url>"        # only if Source URL was provided
local_path: "<path>"       # only if a document was attached and downloaded
tags:
  - <relevant-tag>
authors:
  - "<author if known>"
---
```

**Summary generation:** Since the issue form does not have a dedicated summary field, generate
a concise 1-2 sentence summary based on:
- The resource title
- The document filename (if attached)
- The source URL context (if provided)

For example, for title "Manual Procedure Illumina DNA Prep Library SOP":
```yaml
summary: >-
  Manual procedure for Illumina DNA Prep library preparation, covering tagmentation,
  cleanup, and amplification steps for sequencing library construction.
```

### 3. Handle Attached Documents

If the issue body contains an attached file (GitHub uploads like `https://github.com/user-attachments/...`):

1. Download it to `docs/<category>/` with a descriptive filename
2. Set the `local_path` field in the front matter to `docs/<category>/<filename>`

### 4. Run the Build Pipeline

Run the full build to validate everything works:

```bash
python scripts/extract_local.py
python scripts/fetch_external.py
cd site && bundle exec jekyll build && cd ..
python scripts/build_search_pages.py
npx -y pagefind@1.5.2 --site site/_site
```

If any step fails, diagnose the issue, fix it, and retry.

### 5. Submit the Pull Request

- Commit message: `Add resource: <title> (closes #<issue-number>)`
- PR title: `Add resource: <title>`
- PR body should reference and close the issue, and summarize what was added

## General Notes

- Always follow the formatting conventions in existing `site/_resources/` files
- The `summary` field should be a concise 1-2 sentence description — generate one from the document content or title if not explicitly provided
- Only include `source_url`, `local_path`, `tags`, `authors`, `revision`, and `supersedes` fields when applicable

## End-to-End Example

Given this issue body:
```
### Resource Title

MiSeq NGS Run Setup Protocol

### Category

laboratory

### Document

[LP-601Rev01A - MiSeq Run.pdf](https://github.com/user-attachments/files/99999/LP-601Rev01A.-.MiSeq.Run.pdf)

### Source URL

_No response_
```

You would:
1. Download the PDF: `curl -L -o "docs/laboratory/LP-601Rev01A - MiSeq Run.pdf" "https://github.com/user-attachments/files/99999/LP-601Rev01A.-.MiSeq.Run.pdf"`
2. Create `site/_resources/laboratory/miseq-ngs-run-setup-protocol.md`:
   ```yaml
   ---
   title: "MiSeq NGS Run Setup Protocol"
   category: laboratory
   summary: >-
     Protocol for setting up and executing a sequencing run on the Illumina MiSeq
     instrument, including sample sheet configuration and flow cell loading.
   local_path: "docs/laboratory/LP-601Rev01A - MiSeq Run.pdf"
   tags:
     - miseq
     - ngs
     - sequencing
   authors:
     - "CDC Influenza Division"
   ---
   ```
3. Run the build pipeline to validate
4. Commit, push, and open a PR closing the issue
