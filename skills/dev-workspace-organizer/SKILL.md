---
name: dev-workspace-organizer
description: Plan, initialize, or safely reorganize a multi-project development workspace into durable top-level categories without crossing repository boundaries. Use for layouts such as projects, tools, experiments, skills, and misc; do not use for one repository's internal structure.
---

# Dev Workspace Organizer

Make a development workspace easy to navigate without pretending every person's work fits the same taxonomy.

## Choose the mode

- **New workspace:** Read [references/layout-pattern.md](references/layout-pattern.md), choose only categories the user needs, and dry-run `scripts/workspace_inventory.py` before creating directories.
- **Existing workspace audit:** Inventory the top level, containing and nested Git repositories, worktree markers, symlinks, category collisions, and uncategorized items. Keep the audit read-only and recommend only changes with a clear retrieval or ownership payoff.
- **Reorganization:** Read the layout reference, preserve each repository as a unit, and produce an exact move and rollback map before changing paths. An audit or plan does not authorize a move.

Useful commands:

```sh
python3 scripts/workspace_inventory.py /path/to/development
python3 scripts/workspace_inventory.py /path/to/development --json
python3 scripts/workspace_inventory.py /path/to/development --init --dry-run
python3 scripts/workspace_inventory.py /path/to/development --init
```

`--init` creates missing category directories only. It never moves content, initializes Git, or writes project files.

## Preserve repository boundaries

- A grouping workspace is not itself a project. Never initialize Git at a root containing independent projects.
- Detect a parent repository with Git itself and nested repositories or worktrees by both `.git` directories and `.git` files. Do not move files out of a repository to make the top level look tidier.
- Before moving an existing repository, inspect its status, remotes, symlinks, worktrees, submodules, local-only files, and path-dependent configuration. Read that repository's nearest instructions when the move requires project-specific changes.
- Treat a linked worktree, submodule, or directory owned by a parent repository as attached state, not a standalone folder. Stop rather than separating it from its Git metadata.
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
3. Show an exact source-to-destination map for proposed moves and summarize intentionally unchanged categories. For each move, identify repository/worktree type, collision status, dirty state, submodules or linked worktrees, dependent absolute paths, same-volume status, verification, and rollback.
4. Obtain explicit authorization before moves. Move repositories one at a time with resolved paths; do not use broad globs.
5. Verify every moved repository from its new location: Git root, status, remotes, expected ignored files, build entry points, and important absolute-path integrations.
6. Leave a concise workspace map only when the user wants one. Do not create a grouping-root repository merely to track that map.

Stop before a move when it would cross a volume, overwrite a destination, separate a worktree or submodule from its Git metadata, disturb dirty work, or require project-owner judgment. A cross-volume move is a copy-and-delete operation and needs an explicit recoverable procedure, not an ordinary rename.

Report the resolved workspace root, Git containment, categories, collisions, symlinks, nested repositories/worktrees, changes made, and verification. State clearly when the result is inventory-only or dry-run.
