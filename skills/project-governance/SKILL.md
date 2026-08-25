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
  its non-overwriting behavior fits. Continuity files do not require a release
  scheme. Use its explicit `--with-releases` mode only when SemVer and a
  changelog are part of the requested governance. Inspect sensitive and
  generated files before staging anything.
- **Audit:** read `references/project-standard.md` and
  `references/inventory-schema.md`, then use `scripts/project_audit.py` for an
  explicit inventory when it fits. Keep the audit read-only and distinguish a
  repository's own conventions from actual inconsistencies. Preserve schema 1
  release semantics when reading an existing inventory; use explicit
  `release_policy` values in schema 2.
- **Migration:** inspect the repository, history, ignore policy, release model,
  and tracked/local status of governance files, then propose the exact changes
  before applying a broad standard. Never standardize an established repository
  merely because it differs from this skill's bootstrap defaults.
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
- Treat continuity setup, release preparation, and Git history mutation as
  separate permissions. A request for one does not authorize the others.
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

## Finish With An Exact Handoff

State which governance mode was performed, which files or Git facts changed,
what remained untouched, and which checks passed. For an audit, separate
objective inconsistencies from optional recommendations. For a bootstrap or
migration, identify whether the continuity files are tracked or local-only and
whether release governance is enabled. Never imply that unrequested staging,
committing, tagging, pushing, or publishing occurred.
