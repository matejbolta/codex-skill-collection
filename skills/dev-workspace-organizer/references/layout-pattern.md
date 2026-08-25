# Development workspace layout pattern

Read this reference when designing a new multi-project workspace or proposing changes to an existing one.

## A calm default

```text
development/
|-- projects/
|-- extensions/
|-- tools/
|-- experiments/
|-- skills/
|-- misc/
`-- archive/       optional
```

This is a navigation system, not a package convention. The grouping folders normally contain independent repositories and should not themselves be Git repositories.

## Category decisions

| Category | Put it here when | Do not use it as |
| --- | --- | --- |
| `projects/` | It is a primary, long-lived product, service, application, or substantial body of work | A synonym for every repository |
| `extensions/` | Extensions are common enough that separating them materially improves navigation | A mandatory split for one small extension |
| `tools/` | It is a reusable utility with an operational job and a lifecycle of its own | A dumping ground for one-off snippets |
| `experiments/` | The work is exploratory, provisional, or intentionally disposable | A place where successful projects stay forever |
| `skills/` | It is reusable agent guidance, supporting resources, or a skill distribution | A home for arbitrary prompts and transcripts |
| `misc/` | It is small but durable and no stronger category is honest | An unreviewed trash folder |
| `archive/` | It is intentionally inactive, preserved, and unlikely to be edited | A substitute for version control or backups |

Omit empty categories that are unlikely to be used. Add a new category only when several items share a stable role, security boundary, or retrieval pattern.

## Classification questions

Use these in order:

1. Is the item an independent Git repository or a directory owned by another repository?
2. What does it produce or enable?
3. Is it primary work, reusable infrastructure, exploration, or retained history?
4. Will the category still make sense if the language or framework changes?
5. Does the move improve retrieval enough to justify broken paths and coordination?

Names alone are weak evidence. Inspect a repository's README, manifest, remote, and current instructions when its purpose is unclear.

## Boundaries that matter

- Keep each independent repository intact, including ignored and untracked local state.
- Never make the grouping root a monorepo unless the user is deliberately converting ownership and history, not merely tidying folders.
- A Git worktree may use a `.git` file that points elsewhere. Moving only one side can break it.
- Submodules, local path dependencies, editor workspaces, shell aliases, launch agents, CI scripts, databases, and browser-extension loaders may contain absolute paths.
- Symlinks can point outside the workspace. Resolve and report them before moving their parent.
- Do not merge two same-named destinations or silently invent suffixes.

## New workspace versus migration

For a new workspace, create the chosen empty grouping directories and start projects in the right place as they arise.

For an existing workspace, the safest good outcome may be an inventory plus a small number of high-confidence moves. Aesthetic consistency alone is not enough reason to disturb active repositories.
