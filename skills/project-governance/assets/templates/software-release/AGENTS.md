# {{PROJECT_NAME}} Agent Instructions

Read `README.md`, `docs/HANDOFF.md`, and `CHANGELOG.md` before material work.

## Change discipline

- Preserve existing behavior unless the task requires changing it.
- Add or update proportionate verification for behavior changes.
- Keep the handoff current when architecture, operations, known issues, or next
  work changes.
- Change the changelog and canonical version only for an explicitly requested
  release or version operation; ordinary implementation remains under
  `Unreleased` when the project uses that section.
- Keep secrets, runtime state, logs, caches, generated output, and personal data
  out of Git.
