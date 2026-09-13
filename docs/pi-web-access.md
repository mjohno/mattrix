---
type: configuration
title: Pi Web Access
---

# Pi Web Access

## Purpose

This configuration enables direct web search and content access for Pi.

It does not enable search-result curation.

## Active Configuration

Path:

```text
~/.config/pi/web-search.json
```

The legacy configuration path was removed:

```text
~/.pi/web-search.json
```

## Search Policy

- Use DuckDuckGo as the search provider.
- Set `workflow` to `none`.
- Return raw search results.
- Do not open the curator.
- Do not generate a curator summary.
- Disable the `/curator` command.
- Enable `/websearch`, `/search`, and `/google-account`.

## Content Access Policy

- Allow browser cookies.
- Use direct HTTP content fetching only.
- Do not allow remote hosted fetch providers.
- Enable image, PDF, YouTube, and video handling.
- Disable GitHub repository cloning.
- Disable specialized GitHub pull-request and issue handling.

## Configuration

```json
{
  "provider": "duckduckgo",
  "workflow": "none",
  "allowBrowserCookies": true,
  "fetchRouting": {
    "providers": ["http"],
    "allowRemoteHostedProviders": false
  },
  "image": { "enabled": true },
  "pdf": { "enabled": true },
  "githubClone": { "enabled": false },
  "githubPrIssue": { "enabled": false },
  "youtube": { "enabled": true },
  "video": { "enabled": true },
  "commands": {
    "websearch": { "enabled": true },
    "curator": { "enabled": false },
    "search": { "enabled": true },
    "google-account": { "enabled": true }
  }
}
```

## Validation

Check these conditions:

1. `~/.config/pi/web-search.json` exists and contains valid JSON.
2. `workflow` is `none`.
3. `commands.curator.enabled` is `false`.
4. `~/.pi/web-search.json` does not exist.

## Open Questions

- None identified from the supplied configuration.

## Checklist

- [ ] Confirm `~/.config/pi/web-search.json` exists.
- [ ] Confirm the file contains valid JSON.
- [ ] Confirm `workflow` is `none`.
- [ ] Confirm `commands.curator.enabled` is `false`.
- [ ] Confirm `~/.pi/web-search.json` does not exist.
- [ ] Run one web search and confirm it returns raw results without opening the curator.
