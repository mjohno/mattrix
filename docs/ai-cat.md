---
type: tool
title: AI Context XML Export
---

# AI Context XML Export

`scripts/ai-cat.py` combines selected project content into one XML document for
upload to a web-based AI chat model.

Run the command from the project root. It writes XML to standard output and
writes diagnostics to standard error.

## Usage

Export selected files and directories:

```sh
python scripts/ai-cat.py README.md src > ai-context.xml
```

Add the Git diff for the current directory:

```sh
python scripts/ai-cat.py SPEC-ai-cat.md PLAN-ai-cat.md RUBRIC-ai-cat.md --git-diff > ai-context.xml
```

Add the Git diff from another work directory:

```sh
python scripts/ai-cat.py src --git-diff ../other-project > ai-context.xml
```

Preview the selected entries without exporting file or diff content:

```sh
python scripts/ai-cat.py src --git-diff --dry-run
```

Run `python scripts/ai-cat.py` with no arguments to print command help. Use
`python scripts/ai-cat.py --help` for the same result.

## Collection Rules

- A named regular file is included, even when Git ignores it.
- A named directory is collected recursively.
- Recursive collection omits Git-ignored files.
- Symlinks are not followed or included.
- Repeated inputs produce one entry per file.
- Paths in the XML are relative to the current working directory.

Git must be available for recursive directory inputs and `--git-diff`.

## XML Output

The command writes one `ai-cat` root element. Each selected input is a `file`
element with `path` and `status` attributes. A Git diff also has
`source="gitdiff"`.

```xml
<ai-cat>
  <file path="src/example.py" status="text"><![CDATA[
print("Hello")
]]></file>
  <file path="assets/logo.png" status="binary" />
  <file path="docs/empty.md" status="empty" />
  <file path="." status="text" source="gitdiff"><![CDATA[
diff --git a/src/example.py b/src/example.py
]]></file>
</ai-cat>
```

Text content is wrapped in CDATA. The command safely handles CDATA terminator
sequences so that output remains valid XML.

## Status Values

| Status | Meaning | Content included |
| --- | --- | --- |
| `text` | Valid UTF-8 content that XML 1.0 can represent. | Yes, except during dry-run. |
| `empty` | A zero-byte file or empty Git diff. | No. |
| `binary` | A file with NUL bytes or content that is not valid UTF-8. | No. |
| `invalid-data` | UTF-8 content with characters invalid in XML 1.0. | No. |
| `unread` | A requested Git diff during dry-run. | No. |

Dry-run sets `dry-run="true"` on the root element. It classifies selected
files but omits all file content. It does not run `git diff`; Git ignore checks
still apply when collecting directories.

## Failures

Invalid paths, inaccessible files, Git failures, and invalid arguments produce
a diagnostic on standard error and exit with status `2`.
