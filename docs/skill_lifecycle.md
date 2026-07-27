# Skill Lifecycle

Full lifecycle for creating, verifying, and deploying skills.

## Context

Create or update a skill package that is structurally valid and beautifully simple.

## Inputs

1. Skill name, description, type, and category
2. Core purpose and goal

## Phase 1: Create

### Step 1 — Planning & Specification

1. **Identify Intent**: Determine the core purpose and goal of the skill.
2. **Name & Description**:
   - Use `kebab-case` for the name (must match directory name).
   - Provide a concise description that includes "Use when..." triggers.
3. **Determine Type**: Choose one runtime treatment from [taxonomy.md](taxonomy.md):
   - `interface` — passive contract provider selected and loaded for context
   - `vocabulary` — human-loadable term definitions with model invocation disabled
   - `skill` — invocable data-flow or workflow behavior
   - `protocol` — governed interaction contract for safe agent/user/tool/state transitions
   - `persona` — composable perspective lens
4. **Determine Category**: Choose the valid category for the selected type:
   - `interface` type → `interface` category
   - `vocabulary` type → `interface` category
   - `skill` type → `input`, `transform`, `output`, or `map`
   - `protocol` type → `map` category, with top-level `disable_model_invocation: true`
   - `persona` type → `persona` category
5. **Determine Interface Role**: If the package is an interface, ensure it defines artifact shape, schema, protocol, conventions, or quality criteria without performing operational work. It must select a minimal default contract reference, select optional references/assets only from explicit caller intent or domain clues, and load selected content silently into context. If the package is vocabulary, ensure it defines only non-skill-owned project terms, has `disable_model_invocations: true`, and contains no operational sections.
6. **Place the Package**:
   - Interface nouns and vocabulary packages live under `src/interface/<name>/SKILL.md`.
   - Invocable verb skills live under their data-flow category.
   - Protocol packages live under `src/map/<name>/SKILL.md`.
   - Persona lenses live under `src/persona/<name>/SKILL.md`.
7. **Component Identification**: Determine if the package requires `scripts/`, `references/`, or `assets/`.
8. **Constraint Check**: Verify the name uses `kebab-case` and every relative package-file path in `SKILL.md` is resolved from the directory containing that file; never use repository-root-relative package paths.

### Step 2 — Scaffolding

1. Create root directory `<category>/<name>/`.
2. Initialize SKILL.md:
   - **Interface packages** (`type: interface`): use [interface_template.md](interface_template.md)
   - **Vocabulary packages** (`type: vocabulary`): use [vocab_template.md](vocab_template.md)
   - **Invocable skills** (`type: skill`): use [skill_template.md](skill_template.md)
   - **Protocol packages** (`type: protocol`): use [protocol_template.md](protocol_template.md)
   - **Persona lenses** (`type: persona`): use [persona_template.md](persona_template.md)
3. Create sub-directories (`scripts/`, `references/`, `assets/`) as needed.

### Step 3 — Implementation & Refinement

#### Interface packages

- Define the desired state of a noun/domain and supply applicable conventions, checks, templates, schemas, or protocol rules.
- Stay passive: do not perform artifact production, external retrieval, transformation, evaluation, persistence, or orchestration.
- Default to one compact contract reference when possible.
- Select optional references/assets only from explicit context, such as check/review intent, language, backend, domain, or constraints.
- Load selected package-local references/assets into context without pasting, quoting, summarizing, or otherwise reproducing their contents in chat. When invoked alone, acknowledge only the selected relative paths; when composed, continue the consuming task without an interface-only response.
- Populate `references/` with compact contract rules and optional intent-specific details. Use names such as `<artifact>_contract.md`, `<artifact>_checklist.md`, `<artifact>_quality.md`, or `<domain>_contract.md`.
- Add templates or data to `assets/` only when they should not live inside the compact contract. Use domain-specific names such as `<domain>_template.<ext>` when a template is not generic.

#### Vocabulary packages

- Define compact project vocabulary for human-loaded context before prompting.
- Set `disable_model_invocations: true` in frontmatter.
- Use `metadata.type: vocabulary` and `metadata.category: interface`; do not add extra metadata or frontmatter term lists.
- Name terms in the description, e.g. `Use when terms like study, simplify, lean need definition.`
- Do not include terms that match existing skill names or meanings already defined by skill descriptions. General operational terms may be vocabulary-owned when no dedicated skill remains.
- Behavioral controls are allowed when they clarify intended meaning, e.g. `modify` means make the smallest coherent requested change while preserving unrelated content.
- Keep domain-local terminology in the relevant knowledge-base glossary.
- Avoid Selection, Return, Inputs, Processes, Outputs, Next Steps, and Examples sections.

#### Invocable skills

- Develop self-contained, idempotent behavior and scripts where needed.
- Consume interface-defined contracts when structure, schema, or quality criteria matter.
- **Quality reminder**: Remember the six simplicity principles — single responsibility, clear scope, graceful handoff, etc.

#### Protocol packages

- Define one governed interaction pattern with explicit transition, approval, ordering, state, or safety invariants.
- Set `disable_model_invocation: true` in frontmatter; protocol packages are loaded by humans/orchestrators rather than directly invoked by the model.
- Keep skill prose compact; if an authoritative interface exists, make the skill an adapter to that interface.
- CLIs, APIs, and scripts are optional for protocol packages, but when present they should expose the primary workflow and enforce state rules.
- Do not require agents to mutate protocol state outside the authoritative interface.

#### Persona skills

- Persona skills are pure documentation — no `scripts/`, `references/`, or `assets/` needed.
- Focus on writing a sharp Perspective statement, distinct Values & Priorities, honest Tradeoffs, and non-overlapping Focus Areas.
- **Quality reminder**: A persona is a *lens*, not a checklist. It should guide how the evaluator thinks, not produce a rigid rubric to fill in.

#### Anti-patterns to Avoid

- X Goals that say "help users understand X and Y and Z" — pick one
- X Process steps numbered 1–20 — if it takes this many, consider breaking into sub-skills
- X Non-goals that just repeat the goal in negative form ("We do not fail")
- X Interface skill that performs work instead of defining a contract
- X Interface skill that duplicates, pastes, quotes, summarizes, or otherwise reproduces selected reference/asset contents in chat
- X Interface skill that loads optional checklists, quality criteria, or templates by default without caller intent
- X Interface skill that produces a brief unless the noun itself is a brief
- X Vocabulary package that defines a specialized skill-owned verb such as `review`, `record`, or `commit`
- X Vocabulary package that includes process, input, output, or routing behavior
- X Knowledge-base domain glossary term placed in project vocab
- X Invocable skill that only defines an artifact schema instead of consuming an interface
- X Protocol package that duplicates a long CLI/API manual in SKILL.md instead of pointing to the authoritative interface
- X Protocol package that leaves approval or state-transition boundaries ambiguous
- X Persona encodes a narrow opinion rather than an established evaluation lens
- X Persona overlaps with another persona's focus areas
- X Persona becomes a full review rubric instead of a perspective

### Step 4 — Compliance Check

Run [compliance](#phase-2---comply) against the appropriate checklist:
- **Interface packages** → [interface_checklist.md](interface_checklist.md)
- **Vocabulary packages** → [vocab_checklist.md](vocab_checklist.md)
- **Invocable skills** → [skill_checklist.md](skill_checklist.md)
- **Protocol packages** → [protocol_checklist.md](protocol_checklist.md)
- **Persona lenses** → [persona_checklist.md](persona_checklist.md)

## Phase 2 — Comply

Assert a pass/fail test over an existing skill package against the appropriate checklist.

### Steps

1. **Read Frontmatter**: Extract `metadata.type` and `metadata.category` from SKILL.md.
   - Both are required. Missing or invalid → Critical failure.
   - Valid pairs: `interface/interface`, `vocabulary/interface`, `skill/input`, `skill/transform`, `skill/output`, `skill/map`, `protocol/map`, `persona/persona`.
   - `protocol/map` also requires top-level `disable_model_invocation: true`.
2. **Check Interface Contracts**: If `metadata.type: interface`, verify it exposes contract data only, selects a minimal default contract plus optional references/assets only when intent/domain requires them, and loads selected contents without emitting them in chat. If `metadata.type: vocabulary`, verify it is context-only, has `disable_model_invocations: true`, and does not overlap existing skill names or skill descriptions.
3. **Load Checklist**:
   - `metadata.type: interface` → [interface_checklist.md](interface_checklist.md)
   - `metadata.type: vocabulary` → [vocab_checklist.md](vocab_checklist.md)
   - `metadata.type: skill` → [skill_checklist.md](skill_checklist.md)
   - `metadata.type: protocol` → [protocol_checklist.md](protocol_checklist.md)
   - `metadata.type: persona` → [persona_checklist.md](persona_checklist.md)
4. **Run Checks**: Evaluate each item; record pass/fail with specific violations.
5. **Report**:
   - **Pass**: All CRITICAL items pass. Report "Compliance passed."
   - **Fail**: List passed/failed counts and each violation.

### Severity Classification

- **CRITICAL** — structural validity; must pass (category match, required sections, formatting)
- **QUALITY** — beautiful simplicity principles; should pass for excellence

A skill passes compliance if all CRITICAL items pass. A beautifully simple skill also passes QUALITY items.

## Phase 3 — Deploy

Synchronize a local skill directory to a `TARGET_DIRECTORY` for active use.

### Steps

1. **Pre-deploy Check**: Run compliance against the checklist. Do not deploy if any CRITICAL items fail.
2. **Identify Source**: Confirm the source skill directory.
3. **Identify Target**: Confirm the target directory.
4. **Choose Method**: Real-time Syncing (Symlinks/Junctions) or Manual Mirroring (Rsync/Robocopy).
5. **Confirm Plan**: State the source, target, and method to the user. Provide the exact command line.
   - *Windows Junction (CMD)*: `mklink /J "%USERPROFILE%\%TARGET_DIRECTORY%" "%CD%\src"`
   - *Windows Junction (PowerShell)*: `cmd /c mklink /J "%USERPROFILE%\%TARGET_DIRECTORY%" "%CD%\src"`
6. **User Approval**: Wait for explicit acceptance before executing.
7. **Execute & Verify**: Run the command; confirm files synchronized to target.

## Constraints

1. Must choose the correct checklist based on `metadata.type`: interface → interface_checklist, vocabulary → vocab_checklist, skill → skill_checklist, protocol → protocol_checklist, persona → persona_checklist
2. All checklists inherit shared rules from [base_checklist.md](base_checklist.md)
3. Must read `metadata.type` and `metadata.category` from frontmatter — never assume
4. Requires explicit user approval before deployment execution

## Outputs

- A complete skill package (create)
- Compliance report with pass/fail for each item (comply)
- Synchronized skill directory at target (deploy)
