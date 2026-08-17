---
type: Convention
title: Exclude generated and temporary files from Git
description: Keep Git history limited to source and required project assets.
tags: [scm, git, hygiene]
status: stable
---

# Exclude generated and temporary files from Git

## Convention

Use `.gitignore` to exclude files that Git can reproduce, download, or does not need for project operation.

## Ignore

Ignore these file classes when they are not required source assets:

- Compiled artifacts and build output.
- Package archives and other generated archives.
- Temporary files and directories, including `tmp`.
- Tool caches.
- Local logs.
- Machine-specific configuration.
- Generated files that a documented command can reproduce.

## Rules

- Do not add files from an ignored directory.
- Do not use force-add to bypass an ignore rule unless the repository has an explicit exception for that file.
- Keep required source, configuration, and fixtures under version control.
- Add a narrow ignore pattern. Do not hide unrelated files.
- If a generated file must be versioned, document why it cannot be reproduced.
