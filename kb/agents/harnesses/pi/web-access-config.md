---
type: configuration
title: Pi Web Access configuration
description: Defines the selected Pi Web Access search, fetching, content, and command settings.
tags:
  - pi
  - web-access
  - configuration
---

# Pi Web Access configuration

## Decisions

- Use DuckDuckGo as the default search provider.
- Do not configure search API keys or automatic provider fallback.
- Return raw results from normal searches. Do not use the curator workflow.
- Fetch web content through direct HTTP only. Do not use remote hosted fetch providers.
- Enable Gemini Web through the signed-in Chromium browser profile for explicit Gemini requests and supported media processing.
- Enable image, PDF, YouTube, and video support.
- Disable GitHub repository cloning and specialized GitHub pull request and issue processing.
- Keep `/websearch`, `/search`, and `/google-account` available. Disable `/curator`.

## Configuration file

Use `~/.pi/web-search.json`:

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

## Operation

Restart Pi after changes to command or feature enablement settings. Use `Ctrl+Shift+W` to inspect web-access requests.
