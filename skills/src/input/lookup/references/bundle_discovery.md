# Lookup Bundle Discovery

Operational bundle discovery belongs to lookup. Knowledge provides passive MKF shape and manual discovery information; lookup resolves bundle roots for searching.

## Environment Variable

`MKF_PATH` is a colon-delimited list of configured bundle-root paths:

```sh
MKF_PATH=/knowledge/general:/knowledge/phoenix:/knowledge/my-bundle
```

- Split on `:`.
- Trim whitespace and ignore empty entries, including repeated or trailing separators.
- Expand `~` and resolve each remaining entry as a bundle-root path.
- Preserve the resulting root order.
- If `MKF_PATH` is unset or empty after splitting and trimming, no environment-configured bundles are available.
- Derive each configured bundle's display name from its root directory basename. Duplicate basenames are allowed as roots but cannot be selected by name.

## Prompt Selectors

Lookup may accept:

- an explicit filesystem path, used directly as a bundle root
- a configured bundle-root basename, when it resolves to exactly one `MKF_PATH` root
- multiple selectors
- an all-bundle request

## Lookup Resolution Order

1. Use explicit prompt-provided filesystem paths directly when present and valid.
2. Match non-path prompt selectors against configured root basenames.
3. Reject a selector matching multiple configured roots as ambiguous.
4. Use all configured bundles only when the operation explicitly supports or requests all-bundle behavior.
5. Report unresolved selectors, ambiguous selectors, and non-existent bundle paths clearly.

## Bundle Record

```yaml
name: general
root: /knowledge/general
source: env | prompt-path
```
