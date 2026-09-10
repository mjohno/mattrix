# Values Profile Checklist

Use this checklist to check the quality of one standalone `VAL-<slug>` values profile.

## Required

- [ ] The profile has one stable `VAL-<slug>` identifier and a clear title.
- [ ] Priority, conflict-rule, context-adjustment, and limit IDs use `VPRI-`, `VCON-`, `VCTX-`, and `VLIM-` prefixes.
- [ ] The scope states the decisions, work, or circumstances where the profile applies, or explicitly says `Defer to task context`.
- [ ] Priorities are ordered from highest to lowest importance.
- [ ] Each priority has a description that explains its meaning and why it has its rank.
- [ ] Conflict rules state how to choose when two priorities compete.
- [ ] Context adjustments name their conditions and state the changed priority rule, or explicitly say `Defer to task context`.
- [ ] Limits state decisions or policies that the profile cannot decide, or explicitly say `Defer to task context`.
- [ ] The profile is complete and understandable without another values profile.
- [ ] The profile does not import, extend, or reference another values profile.

## Quality

- [ ] An explicit scope is neither too broad to guide a decision nor too narrow for its intended use.
- [ ] Priorities are distinct and do not repeat the same concern.
- [ ] The ordering and conflict rules do not contradict each other.
- [ ] Context adjustments are specific exceptions, not hidden replacement profiles.
- [ ] Limits identify material uncertainty, authority boundaries, or escalation needs.
- [ ] Rules use observable conditions and clear actions where possible.
- [ ] The profile contains only current guidance; it has no lifecycle or revision-history content.
- [ ] The profile is concise enough to apply during a decision, review, plan, or specification.
