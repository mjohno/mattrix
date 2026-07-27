# Skill Taxonomy

This repository uses a role-based skill taxonomy. Each category defines the skill's primary role in the system.

## Mental Model

- **Nouns are interfaces** — artifact schemas, storage contracts, protocols, and canonical shapes.
- **Vocabulary is context** — human-loaded term definitions that shape interpretation without model invocation.
- **Specialized verbs are invocable skills** — skills that retrieve, transform, persist, or orchestrate work through a dedicated contract.
- **Protocols are governed interaction contracts** — stateful or approval-sensitive flows that agents follow through an authoritative interface.
- **Personas are lenses** — perspectives that modify how another skill evaluates or presents information.

## Metadata Model

Every package declares both type and category:

- `metadata.type` describes runtime treatment:
  - `interface` — passive contract provider selected and loaded for context
  - `vocabulary` — human-loadable context definitions with model invocation disabled
  - `skill` — invocable behavior that retrieves, transforms, writes, or orchestrates
  - `protocol` — governed interaction contract, usually map-category, that defines safe transitions between agent, user, tools, and state
  - `persona` — composable lens that changes evaluation or presentation
- `metadata.category` describes taxonomy placement and primary role.

Valid pairs:
- `type: interface`, `category: interface`
- `type: vocabulary`, `category: interface`
- `type: skill`, `category: input|transform|output|map`
- `type: protocol`, `category: map`, with top-level `disable_model_invocation: true`
- `type: persona`, `category: persona`

## Categories

### interface
Passive noun/domain contract packages that supply conventions, quality checks, templates, schemas, protocols, artifact shapes, vocabulary, or storage rules used by verb skills.
- Declares `metadata.category: interface` with either `metadata.type: interface` or `metadata.type: vocabulary`
- Selected and loaded when another skill needs artifact shape, schema, protocol, conventions, quality criteria, or storage rules; vocabulary packages are human-loaded instead
- Lives as direct packages under `src/interface/<name>/SKILL.md`
- Examples: `interface/spec`, `interface/rfc`, `interface/plan`, `interface/task`, `interface/code`, `interface/prose`, `interface/script`, `interface/prototype`, `interface/memory`, `interface/knowledge-base`, `interface/vocab`
- Defines the desired state of a noun-like artifact, protocol, domain, or context vocabulary
- May select an applicable domain from context, such as a script language or storage backend
- Loads the minimal selected reference/asset contents into context without emitting them in chat; when invoked alone, acknowledges only selected relative paths. Vocabulary packages remain human-loaded context.
- Domain- or intent-specific materials should be clearly named, e.g. `python_template.py`, `plan_quality.md`, `plan_checklist.md`, or `github_protocol.md`
- **Do NOT use if** the package performs artifact production, external retrieval, transformation, evaluation, persistence, or orchestration — it only supplies contract data or vocabulary context for other skills to apply

### vocabulary
Special interface-category packages that define project operational terms for human-loaded context.
- Declares `metadata.type: vocabulary` and `metadata.category: interface`
- Requires top-level `disable_model_invocations: true`
- Is loaded directly by a human before prompting; the model should not invoke or route to it
- Defines only terms that are not already owned by skill names or skill descriptions
- Keeps terms in the `description` trigger and body content; do not add frontmatter term metadata
- May include compact behavioral controls, but contains no formal inputs, processes, outputs, return contract, verification, or next-step behavior
- Project `vocab` is operational vocabulary; knowledge-base `glossary` content is domain-local terminology
- **Do NOT use if** the term needs structured inputs, formal outputs, verification criteria, or multi-step process — create or update a verb skill instead

### input
Skills that bring information into the working context from outside the current reasoning process.
- Reads, retrieves, fetches, or elicits source data
- Returns raw or structured context
- Does not usually rewrite or persist
- Examples: `input/investigate`, `input/lookup`, `input/remember`, `input/grill-me`
- **Do NOT use if** the skill primarily evaluates, prioritizes, restructures, or writes the data — it only brings source information in

### transform
Skills that operate on existing context or artifacts to derive, evaluate, restructure, prioritize, reduce, or convert information into a more useful intermediate form.
- Turns current context into decisions, findings, checks, rankings, summaries, or other working material
- May evaluate evidence, apply criteria, dedupe, compress, rank, or critique
- Does not primarily retrieve external data or persist final outputs
- Examples: `transform/check`, `transform/rank`, `transform/review`, `transform/learn`
- **Do NOT use if** the skill primarily retrieves source data, writes final artifacts, or orchestrates an end-to-end workflow

### output
Verb-shaped production skills that create, revise, persist, store, or deliver results outward.
- Performs production actions with dedicated contracts, such as record, memorize, annotate, or commit
- Consumes interface-defined artifact nouns and storage contracts when structure matters
- May write files, records, logs, or artifacts when requested
- **Do NOT use if** the skill only defines an artifact schema or canonical form — use an interface skill for nouns

### map
Workflow composition skills and protocols that orchestrate multiple steps.
- Combines other skills and/or direct file operations
- Owns end-to-end execution of a process
- Hosts `metadata.type: protocol` packages when the primary role is governing agent/user/tool/state transitions
- **Do NOT use if** the package performs a single focused task — it only orchestrates others

### protocol
Map-category packages that define governed interaction contracts rather than ordinary invocable behavior.
- Declares `metadata.type: protocol`, `metadata.category: map`, and top-level `disable_model_invocation: true`
- Defines safe transitions between agent, user, tools, and persistent or derived state
- May be mediated by a CLI, API, or compact instruction surface; CLIs are optional, not required by the type
- Uses its authoritative interface to expose workflow stages and legal operations when one exists
- Is not directly invocable by the model; it is loaded by a human/orchestrator as protocol context
- Examples: `map/step`
- **Do NOT use if** the package only performs a normal one-shot task — use `type: skill` instead

### persona
Skills that encode a consistent perspective, tradeoff-awareness, or output style across any pipeline stage.
- Provides perspective, voice, or evaluation criteria independent of data flow
- **Modifies how information flows** through the system — a persona skill wraps or augments a data-flow category
- Composable with any invocable skill
- Reduces total skill count by making each skill work across multiple viewpoints
- **Do NOT use if** the skill's primary role is data retrieval, transformation, persistence, orchestration, or contract definition — it only modifies perspective

## Composition Patterns

Interfaces define contract data that invocable skills consume:

- **interface/vocab** — Human-load project terms such as `study`, `outline`, `draft`, `modify`, `simplify`, or `lean` before the first prompt; reserve dedicated skills for verbs that need a specialized contract or workflow.
- **interface/spec + outline** — Outline a traceable future-state spec using the spec template.
- **interface/spec + draft** — Draft a generic future-state spec using the spec contract.
- **interface/code + modify** — Modify code while preserving code-brief boundaries and verification hints.
- **interface/knowledge-base + output/record** — Record durable knowledge using the KB root and entry contract.
- **interface/memory + output/memorize** — Append memory using the memory file and entry contract.

Personas modify how information is evaluated at any pipeline stage:

- **transform/review + persona/security** — Run `review` with the security persona as the evaluation lens.
- **input/grill-me + persona/adversarial** — Stress-test a design, then re-evaluate residual risks through the adversarial persona.
- **transform/check + persona/adversarial** — Validate whether claims, results, or outcomes survive a hostile reading of the criteria.

## Notes

- `metadata.type` describes how the package is used at runtime; `metadata.category` describes role and placement.
- Categories describe primary role. Packages may touch adjacent concerns, but their category reflects the dominant behavior.
- `interface` packages define shared contracts and are discoverable for model use. They load applicable conventions, checks, templates, schemas, or protocol rules into context without emitting their contents, but do not operate on the artifact themselves.
- `vocabulary` packages are not model-invocable; they are compact context definitions loaded by a human.
- Loading package-local interface references/assets is part of exposing contract data, not external retrieval.
- `transform` intentionally covers both evaluation and derivation; split it only if future usage shows a concrete need.
- Refer to [interface_template.md](interface_template.md), [vocab_template.md](vocab_template.md), [skill_template.md](skill_template.md), [protocol_template.md](protocol_template.md), and [persona_template.md](persona_template.md) for frontmatter format.
