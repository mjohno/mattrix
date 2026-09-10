# Values Profile Contract

A values profile is a compact, standalone artifact that gives explicit priority guidance for decisions, reviews, plans, and specifications.

## Required Shape

```text
# VAL-<slug>: <Title>

## Scope
- <applicable decisions, work, or circumstances>

## Priorities
1. VPRI-001: <value> — <meaning and reason for this rank>

## Conflict Rules
- VCON-001: <rule for competing priorities>

## Context Adjustments
- VCTX-001: When <condition>, <changed priority rule>.

## Limits
- VLIM-001: <decision, policy, uncertainty, or authority boundary outside this profile>
```

## Rules

- The title starts with `VAL-<slug>`.
- `slug` is lowercase kebab-case and identifies one values profile.
- A values profile is self-contained. Do not import, extend, or reference another values profile.
- Scope states the applicable decisions, work, or circumstances, or contains exactly `Defer to task context`.
- List priorities from highest to lowest importance.
- Each priority has a stable, unique `VPRI-<three-digit sequence>` ID, a clear description, and a reason for its rank.
- Preserve priority IDs when their meaning remains materially the same, even if their rank changes.
- Conflict rules have stable, unique `VCON-<three-digit sequence>` IDs and state how to choose when priorities compete.
- Context adjustments are optional. When included, each has a stable, unique `VCTX-<three-digit sequence>` ID, names its condition, and states the changed priority rule. Otherwise, the section contains exactly `Defer to task context`.
- Limits are optional. When included, each has a stable, unique `VLIM-<three-digit sequence>` ID and states a boundary, uncertainty, or escalation need. Otherwise, the section contains exactly `Defer to task context`.
- A profile contains only current guidance. Do not add lifecycle, revision-history, default-profile, or profile-selection content.

## Consumer Rules

- A consuming skill uses a values profile only when the caller explicitly names it.
- A consuming skill applies the profile's ordering, conflict rules, applicable context adjustments, and limits.
- When no values profile is named, the consuming skill continues without values-specific guidance.
- A values profile guides decisions; it does not approve, execute, or record them.

## Minimal Example

```text
# VAL-public-api: Public API Decisions

## Scope
- Decisions about public API behavior and change design.

## Priorities
1. VPRI-001: User safety — Prevent user data loss and unsafe behavior. This is first because harm can be difficult or impossible to reverse.
2. VPRI-002: Compatibility — Preserve supported consumer behavior. This is second because unexpected breakage reduces user trust.

## Conflict Rules
- VCON-001: User safety takes priority over compatibility.

## Context Adjustments
- Defer to task context

## Limits
- VLIM-001: Legal and regulatory policy decisions require the responsible authority.
```
