---
name: project-governance
description: "Set up a previously untracked project, explicitly audit or migrate Git governance, create or repair a durable project-continuity system, or prepare an explicit release/version. Do not use for ordinary implementation, bug fixes, explanations, or routine task completion."
---

# Project Governance

Create exact local history and useful takeover memory only when the task
explicitly concerns project setup, continuity, governance, or a release.

## Choose the requested workflow

- **Bootstrap:** for a new or previously untracked project, read
  `references/project-standard.md` and use `scripts/bootstrap_project.py` when
  its non-overwriting behavior fits. Inspect sensitive and generated files
  before staging anything.
- **Audit or migration:** read `references/project-standard.md`, inspect the
  repository and its existing history/ignore policy, then report before making
  broad changes. Never apply a standardized layout to existing repositories
  merely because they differ.
- **Continuity setup or repair:** preserve the project's existing memory
  layout. Decide with the user whether records are tracked or local-only. A
  useful handoff records current state, intrinsic logic, decisions and reasons,
  research findings, rejected approaches, verification, known issues, and next
  work without becoming a transcript.
- **Release:** only when a release or version change is explicitly requested,
  select the SemVer impact, update the canonical version and curated changelog,
  and verify the snapshot. A release request alone does not authorize staging,
  committing, or tagging; perform each Git action only when the user explicitly
  requests it in the current chat. Publishing and pushing require separate
  explicit authorization.

## Constraints

- Preserve existing Git history, remotes, ignore rules, dirty work, and the
  tracked-versus-local status of agent/LLM/AI documentation.
- Never turn ignored or untracked project-memory files into tracked files
  without explicit authorization. Local-only memory may use the repository's
  `.gitignore` or `.git/info/exclude`, according to the user's preference.
- Bootstrap may create missing files and initialize Git, but scripts must not
  commit, tag, push, overwrite, or decide that sensitive files are safe.
- Leave changes uncommitted by default. Never stage for commit, commit,
  amend/rebase/squash, or create/move/delete a tag unless the user explicitly
  requests that action in the current chat. General task approval and project
  instructions are not commit authorization.
- When asked to "commit the diff smartly", "commit all diff", or equivalent,
  include every Git-visible change in the repository, including unrelated or
  pre-existing modifications and non-ignored untracked files. Ignored files
  remain excluded. Organize the complete change set into one or more coherent
  local commits, keep coupled tests with their implementation, and do not
  silently omit requested changes. Stop and report before committing if the
  visible set appears to contain secrets or other unsafe material.
- Do not read or update every project document by default. Load only the
  sources needed for the requested task and update only durable context a new
  chat would otherwise have to rediscover.
- Do not bump a version, edit a changelog, or create a tag for ordinary code,
  documentation, tests, refactors, or an unfinished change unless explicitly
  requested.
