---
name: dev-workspace-organizer
description: Plan, initialize, or safely reorganize a multi-project development workspace into durable top-level categories without crossing repository boundaries. Use for layouts such as projects, tools, experiments, skills, and misc; do not use for one repository's internal structure.
---

# Dev Workspace Organizer

Make a development workspace easy to navigate without pretending every person's work fits the same taxonomy.

## Choose the mode

- **New workspace:** Read [references/layout-pattern.md](references/layout-pattern.md), choose only categories the user needs, and dry-run `scripts/workspace_inventory.py` before creating directories.
- **Existing workspace audit:** Inventory the top level, nested Git repositories, symlinks, and uncategorized items. Report the structure and recommend only changes with a clear payoff.
- **Reorganization:** Read the layout reference, preserve each repository as a unit, and produce an exact move map before changing paths.

Useful commands:

```sh
python3 scripts/workspace_inventory.py /path/to/development
python3 scripts/workspace_inventory.py /path/to/development --init --dry-run
python3 scripts/workspace_inventory.py /path/to/development --init
```

`--init` creates missing category directories only. It never moves content, initializes Git, or writes project files.

## Preserve repository boundaries

- A grouping workspace is not itself a project. Never initialize Git at a root containing independent projects.
- Detect nested repositories and worktrees by both `.git` directories and `.git` files. Do not move files out of a repository to make the top level look tidier.
- Before moving an existing repository, inspect its status, remotes, symlinks, worktrees, submodules, local-only files, and path-dependent configuration. Read that repository's nearest instructions when the move requires project-specific changes.
- Do not stage, commit, rewrite history, alter remotes, or push merely because paths are being organized.

## Organize by role and lifecycle

Use category names as a starting vocabulary, not a mandate:

- `projects/` for primary, long-lived products or substantial applications;
- `extensions/` when browser or editor extensions form a meaningful body of work;
- `tools/` for reusable operational utilities with a clear job;
- `experiments/` for exploratory or disposable investigations;
- `skills/` for reusable agent skills and their publication collections;
- `misc/` for small durable work that does not justify a stronger category;
- `archive/` only for intentionally inactive work that still deserves preservation.

Prefer a few stable categories. Split by technology, client, or language only when that distinction repeatedly improves retrieval or permissions.

## Reorganize safely

1. Resolve the exact workspace root and inventory every immediate child.
2. Classify by actual purpose and lifecycle. When purpose is unclear, leave the item in place and ask or report the decision instead of guessing from its name.
3. Show an exact source-to-destination map, including items that will remain unchanged. Identify collisions and path references that may break.
4. Obtain explicit authorization before moves. Move repositories one at a time with resolved paths; do not use broad globs.
5. Verify every moved repository from its new location: Git root, status, remotes, expected ignored files, build entry points, and important absolute-path integrations.
6. Leave a concise workspace map only when the user wants one. Do not create a grouping-root repository merely to track that map.

Stop before a move when it would cross a volume, overwrite a destination, separate a worktree from its Git metadata, disturb dirty work, or require project-owner judgment.
