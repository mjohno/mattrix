# MKF Lookup Process

## Purpose

Find the best valid concept metadata matches for a query, then let the agent or user load selected files by path.

## Search Script

```sh
MKF_PATH=/knowledge/general python scripts/search_mkf.py --query "search terms" --limit 10
python scripts/search_mkf.py --query "search terms" --bundle /knowledge/general --limit 10
python scripts/search_mkf.py --query "stable" --advanced-field status:stable
```

Without `--bundle`, the script resolves roots from `MKF_PATH`. Each `--bundle` is an explicit bundle-root path and may be repeated. `--advanced-field` is explicit advanced-OKF intent.

## Search Order

1. Bundle roots in resolved `MKF_PATH` or explicit argument order.
2. Directory names, filenames, and concept IDs.
3. Core frontmatter metadata: `type`, `title`, `tags`, then `description`.
4. Markdown body content.

Higher-tier matches rank above lower-tier matches. Within a tier, stronger lexical matches rank first. `index.md` and `log.md` are reserved files and are excluded from concept candidates.

## Behavior

- Parse YAML frontmatter safely and require a non-empty `type` before returning a concept.
- Return partial valid-concept matches plus structured errors for unreadable, malformed, or non-conformant candidates.
- Search advanced fields only with explicit `--advanced-field` filters. Supported fields are `resource`, `status`, `stale_after`, `generated`, `verified`, and `sources`.
- Return metadata matches, not full synthesized answers.
- Load full files only after match selection.
- Do not write or repair concepts.
