# MKF Lookup Process

## Purpose

Find the best MKF metadata matches for a query, then let the agent or user load selected files by path.

## Search Script

Use `scripts/search_mkf.py`.

Recommended invocation shape:

```sh
python scripts/search_mkf.py --query "search terms" --bundle NAME=/path/to/bundle --limit 10
```

The script may also resolve bundles from the environment when no explicit `--bundle` is supplied.

## Search Order

1. Bundle roots in resolved MKF bundle path order.
2. Directory names, filenames, and concept IDs.
3. Frontmatter metadata: `type`, `title`, `tags`, then `description`.
4. Markdown body content.

Higher-tier matches rank above lower-tier matches. Within a tier, stronger lexical matches rank first.

## Result Shape

Return JSON records grouped by bundle:

```json
{
  "query": "checklist",
  "results": [
    {
      "bundle": "GENERAL",
      "bundle_root": "/knowledge/general",
      "concept_id": "quality/skill-checklist",
      "path": "/knowledge/general/quality/skill-checklist.md",
      "match_tier": "frontmatter",
      "matched_fields": ["type", "title"],
      "score": 120,
      "type": "checklist",
      "title": "Skill Checklist",
      "description": "Quality checklist for skills.",
      "tags": ["skills"],
      "excerpt": "..."
    }
  ]
}
```

## Behavior

- Return metadata matches, not full synthesized answers.
- Load full files only after match selection.
- Group or label results by bundle.
- Do not write or repair concepts.
- If no matches are found, report the searched bundles and query.
