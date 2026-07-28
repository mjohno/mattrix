# Annotation Syntax

Choose the native comment style for the target file and local context. An annotation in code IS a comment — it uses the file's native comment syntax. The difference is that annotations are structured and actionable, not passive notes.

| File/context | Preferred syntax | Notes |
| --- | --- | --- |
| JavaScript/TypeScript/C/Go/Rust line note | `// ...` | Prefer for short local annotations. |
| JavaScript/TypeScript/C/CSS block note | `/* ... */` | Use for multi-line annotations where block comments are idiomatic. |
| Python/Ruby/Shell/YAML/TOML | `# ...` | Preserve indentation near the annotated line. |
| Markdown/HTML/XML | `<!-- ... -->` | Use hidden annotations when the note is for maintainers/agents, not readers. |
| SQL | `-- ...` | Prefer line annotations near the relevant query clause. |

Rules:
- Prefer the smallest annotation block that is clear.
- Preserve indentation and formatting.
- Do not change executable code unless explicitly asked.
- If the file already has a local comment convention, follow it.
- If no safe syntax is known, ask before editing.
