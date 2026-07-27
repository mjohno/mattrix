# Workspace Contract

## Terms

- **Workspace:** A top-level, selected local domain.
- **Remote:** A bare Git repository serving a project locally.
- **Project:** The working-copy home corresponding to a remote.
- **Checkout:** A named working tree for a project.

## Layout

```text
<workspace>/
  remotes/
    [<organization-directory>/...]
      <project>.git/
  projects/
    [<organization-directory>/...]
      <project>/
        <primary-checkout>/
        <checkout>/
```

`<organization-directory>` represents zero or more optional directories used to organize or group projects. Its names, meaning, and depth are unconstrained.

Example:

```text
<workspace>/
  remotes/
    <group-a>/
      <project-a>.git/
  projects/
    <group-a>/
      <project-a>/
        main/
        <task-checkout>/
```

## Invariants

1. A workspace is an isolation boundary; workspaces do not share project or remote paths.
2. Each project has one canonical local bare remote in the same workspace.
3. The relative organizational path beneath `remotes/` mirrors the relative path beneath `projects/`.
4. A remote’s `<project>.git` name corresponds to its project’s `<project>` directory name.
5. A primary checkout uses the project-established branch name, such as `main` or `master`.
6. Additional checkouts are siblings of the primary checkout.
