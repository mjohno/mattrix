# Lookup Bundle Discovery

Operational bundle discovery belongs to lookup. Knowledge provides passive MKF shape and manual discovery information; lookup resolves bundles for searching.

## Environment Variables

- `MKF_BUNDLES` is a semicolon-delimited list of bundle tokens.
- Split on `;`.
- Trim whitespace.
- Ignore empty entries, including trailing semicolon entries.
- Normalize tokens to uppercase.
- Treat `-` and `_` as equivalent by converting `-` to `_` for environment variable lookup.
- Resolve each normalized token through `MKF_<NAME>_BUNDLE`.
- If `MKF_BUNDLES` is unset or empty after splitting/trimming, no environment-configured bundles are available.

Example:

```sh
MKF_BUNDLES=GENERAL;PHOENIX;MY-BUNDLE;
MKF_GENERAL_BUNDLE=/knowledge/general
MKF_PHOENIX_BUNDLE=/knowledge/phoenix
MKF_MY_BUNDLE_BUNDLE=/knowledge/my-bundle
```

## Prompt Selectors

Lookup may accept:

- configured bundle names, e.g. `general`, `GENERAL`, `my-bundle`, `my_bundle`
- explicit filesystem paths to use directly as bundle roots
- multiple bundle selectors
- all-bundle requests

## Lookup Resolution Order

1. Use explicit prompt-provided filesystem paths directly when present and valid.
2. Match prompt selectors against normalized configured bundle names.
3. Use all configured bundles only when the operation explicitly supports or requests all-bundle behavior.
4. Report unresolved selectors, missing `MKF_<NAME>_BUNDLE` variables, and non-existent bundle paths clearly.

## Bundle Record

```yaml
name: GENERAL
root: /knowledge/general
source: env | prompt-path
```
