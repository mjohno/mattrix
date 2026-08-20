# Skill Taxonomy

This repository uses a role-based skill taxonomy. Each category defines the skill's primary role in the system.

## Mental Model

- **Nouns are interfaces** — artifact schemas, storage contracts, protocols, and canonical shapes.
- **Communications are context** — human-loaded controls that shape LLM interpretation or generated communication without model invocation.
- **Specialized verbs are invocable skills** — skills that retrieve, produce, persist, or orchestrate work through a dedicated contract.
- **Protocols are governed interaction contracts** — stateful or approval-sensitive flows that agents follow through an authoritative interface.
- **Personas are lenses** — perspectives that modify how another skill evaluates or presents information.

## Metadata Model

Every package declares both type and category:

- `metadata.type` describes runtime treatment:
  - `interface` — passive contract provider selected and loaded for context
  - `communications` — human-loadable communication controls with model invocation disabled
  - `skill` — invocable behavior that retrieves, produces, writes, or orchestrates
  - `protocol` — governed interaction contract, usually map-category, that defines safe transitions between agent, user, tools, and state
  - `persona` — composable lens that changes evaluation or presentation
- `metadata.category` describes taxonomy placement and primary role.

Valid pairs:
- `type: interface`, `category: interface`
- `type: communications`, `category: interface`
- `type: skill`, `category: input|output|map`
- `type: protocol`, `category: map`, with top-level `disable_model_invocation: true`
- `type: persona`, `category: persona`

## Categories

### interface
Passive noun/domain contract packages that supply conventions, quality checks, templates, schemas, protocols, artifact shapes, or storage rules used by verb skills.
- Declares `metadata.type: interface` and `metadata.category: interface`
- Is selected and loaded when another skill needs artifact shape, schema, protocol, conventions, quality criteria, or storage rules
- Lives as direct packages under `../src/interface/<name>/SKILL.md`
- Examples: `interface/spec`, `interface/rfc`, `interface/plan`, `interface/code`, `interface/prose`, `interface/script`, `interface/prototype`, `interface/knowledge-base`
- Defines the desired state of a noun-like artifact, protocol, or domain
- May select an applicable domain from context, such as a script language or storage backend
- Loads the minimal selected reference/asset contents into context without emitting them in chat; when invoked alone, acknowledges only selected relative paths.
- Domain- or intent-specific materials should be clearly named, e.g. `python_template.py`, `plan_checklist.md`, or `github_protocol.md`
- **Do NOT use if** the package performs artifact production, external retrieval, evaluation, persistence, or orchestration — it only supplies contract data for other skills to apply

### communications
Special interface-category packages that define human-loaded LLM communication controls.
- Declares `metadata.type: communications` and `metadata.category: interface`
- Requires top-level `disable_model_invocations: true`
- Is loaded directly by a user at the start of, or during, a session; the model must not invoke or route to it
- Defines compact communication terms, language standards, or other declarative communication controls
- States its activation, scope, applicable exact-text exclusions, and higher-priority instruction precedence
- May include package-specific sections such as `Terms` or `Language Rules`, but contains no formal inputs, processes, outputs, return contract, verification, or next-step behavior
- Project `vocab` defines operational terms; `simplified-technical-english` defines generated-prose language rules; knowledge-base `glossary` content is domain-local terminology
- **Do NOT use if** the package needs an artifact schema, structured inputs, formal outputs, verification criteria, tool procedures, or a multi-step process — create or update an interface or verb skill instead

### input
Skills that bring information into the working context from outside the current reasoning process.
- Reads, retrieves, fetches, or elicits source data
- Returns raw or structured context
- Does not primarily judge, prioritize, or persist the data
- Examples: `input/investigate`, `input/lookup`, `input/grill-me`
- **Do NOT use if** the skill primarily produces a judgment, ranking, report, durable artifact, or workflow — it only brings source information in

### output
Verb-shaped production skills that turn working context into a communicated, derived, or durable result.
- Produces reports, validation results, rankings, decisions, revisions, records, logs, or artifacts
- May return its result in chat or write it to a requested destination
- Consumes interface-defined artifact nouns and storage contracts when structure matters
- Examples: `output/task`, `output/goal`, `output/check`, `output/rank`, `output/review`, `output/record`, `output/annotate`, `output/handoff`
- **Do NOT use if** the package only defines an artifact schema or canonical form — use an interface skill for nouns; if it primarily coordinates multiple skills or approvals, use map

### map
Workflow composition skills and protocols that orchestrate multiple steps.
- Combines other skills and/or direct file operations
- Owns end-to-end execution of a process
- Hosts `metadata.type: protocol` packages when the primary role is governing agent/user/tool/state transitions
- **Do NOT use if** the package performs one focused acquisition or production task — use input or output instead

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
- Applies priorities, tradeoffs, voice, and evaluation emphasis to another skill's work
- Provides perspective or evaluation criteria independent of data flow
- Composes with any invocable skill
- Reduces total skill count by letting one production skill work across multiple viewpoints
- **Do NOT use if** the package's primary role is retrieval, production, persistence, orchestration, or contract definition — it only changes how another skill interprets or presents information

## Classification Test

Classify a skill by its dominant state transition:

- External evidence → available working context: **input**
- Working context → constrained by a reusable contract: **interface**
- Working context → communicated, derived, or durable result: **output**
- Goal or context → ordered multi-step execution: **map**
- User-loaded communication controls → LLM interpretation or generated communication: **communications**
- Neutral processing → perspective-shaped processing: **persona**

A skill may touch adjacent concerns, but its category follows the primary result it owns. Reusable criteria belong in an interface; a skill that applies those criteria and reports findings is output.

## Composition Patterns

### Interface composition

Interfaces define contract data that invocable skills consume:

- **interface/spec + outline** — Outline a traceable future-state spec using the spec template.
- **interface/spec + draft** — Draft a generic future-state spec using the spec contract.
- **task** — Turn context into a concise, testable INVEST task statement.
- **goal** — Turn context into a concise, assessable SMART goal statement.
- **interface/code + modify** — Modify code while preserving code-brief boundaries and verification hints.
- **interface/knowledge-base + output/record** — Record durable knowledge using the KB root and entry contract.

### Communications context

A user loads communications packages as session context. Their location under `interface/` does not make them model-invocable.

- **interface/vocab** — User-load project terms such as `study`, `outline`, `draft`, `modify`, `simplify`, or `lean`. These terms control user-request interpretation and generated responses; reserve dedicated skills for verbs that need a specialized contract or workflow.
- **interface/simplified-technical-english** — User-load ASD-STE100 rules for generated chat prose only.
- **vocab + simplified-technical-english** — A user can load both packages. Apply vocab to request interpretation and response behavior, and apply STE only to generated chat prose. Keep exact text unchanged when either package excludes it, and follow higher-priority instructions if rules conflict.

Personas modify how information is evaluated at any pipeline stage:

- **output/review + persona/security** — Review an artifact through the security lens.
- **input/grill-me + persona/adversarial** — Stress-test a design, then re-evaluate residual risks through the adversarial persona.
- **output/check + persona/adversarial** — Validate whether claims, results, or outcomes survive a hostile reading of the criteria.

## Notes

- `metadata.type` describes how the package is used at runtime; `metadata.category` describes role and placement.
- Categories describe primary role. Packages may touch adjacent concerns, but their category reflects the dominant behavior.
- `interface` packages define shared contracts and are discoverable for model use. They load applicable conventions, checks, templates, schemas, or protocol rules into context without emitting their contents, but do not operate on the artifact themselves.
- `communications` packages are not model-invocable; they are compact context controls loaded by a user.
- Loading package-local interface references/assets is part of exposing contract data, not external retrieval.
- Refer to [interface_template.md](interface_template.md), [communications_template.md](communications_template.md), [skill_template.md](skill_template.md), [protocol_template.md](protocol_template.md), and [persona_template.md](persona_template.md) for frontmatter format.
