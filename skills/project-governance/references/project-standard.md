# Project standard

Read this reference for bootstrap, audit, migration, or release work.

## Continuity records

For a new software project, the following is a useful starting layout:

```text
AGENTS.md
CLAUDE.md
README.md
CHANGELOG.md
docs/HANDOFF.md
```

`AGENTS.md` is the canonical instruction file. `CLAUDE.md` is a one-line
pointer containing `@AGENTS.md`, because Claude Code reads `CLAUDE.md` and not
`AGENTS.md`. Keep the instructions in `AGENTS.md` only; never duplicate them
into `CLAUDE.md`. Where `AGENTS.md` is ignored, ignore `CLAUDE.md` the same way.

Add `docs/ARCHITECTURE.md`, `docs/adr/`, `docs/RELEASE.md`, `SECURITY.md`, or
`CONTRIBUTING.md` only when the project actually needs them.

Maintained notes or data collections normally need Git history and a handoff,
but do not require `CHANGELOG.md` or SemVer unless they produce releases.

Do not impose this layout on an established repository. Preserve its existing
file names, ignore rules, and tracked-versus-local policy. If project memory is
local-only, keep it ignored and never stage it. `.gitignore` is appropriate
when the local-only convention should travel with the repository;
`.git/info/exclude` is appropriate when even the ignore rule should remain
device-local.

Use existing ecosystem version sources in this order:

1. `package.json` for Node applications and built browser extensions;
2. `pyproject.toml` for packaged Python software;
3. the runtime `manifest.json` for dependency-free unpacked extensions;
4. `VERSION` for language-neutral applications and scripts.

When an ecosystem requires duplicate versions, identify one as canonical and
validate the others. Never maintain a display version separately when it can be
read from the canonical source.

### Repositories that hold two products

The rules above assume one released product per repository. A repository that
holds two independently released products has two legitimate version numbers,
and forcing them to match would falsify one product's history. Set
`version_source` on the inventory entry to name the file the parent project is
versioned by:

```json
{
  "name": "scramble-set-insight",
  "path": "/path/to/projects/scramble-set-insight",
  "management": "managed",
  "kind": "software",
  "version_source": "VERSION"
}
```

The audit then validates only that file. The second product keeps its own
version and stays governed by its own `AGENTS.md` and `CHANGELOG.md`. Use this
only for genuinely separate products; a build artifact or package manifest that
restates the same product's version is a duplicate and belongs under the
canonical-source rule above.

## Honest baselines

For a non-empty project with no Git history:

1. inspect local state, ignored files, secrets, generated output, personal
   fixtures, databases, logs, and caches;
2. add or improve `.gitignore` without discarding source;
3. initialize Git with branch `main`;
4. add truthful standard records without pretending they existed earlier;
5. inspect every staged path;
6. create one baseline commit explaining that pre-baseline history is not
   recoverable;
7. if a trustworthy current software version already exists, annotate the
   baseline with that version; otherwise choose a truthful starting version.

Do not backdate commits. A reconstructed changelog may summarize known earlier
versions only when it labels the reconstruction and its evidence.

## Changelog shape

Follow Keep a Changelog with `Unreleased` first and release headings such as:

```markdown
## [1.2.0] - 2026-08-21

### Added

- Add the user-visible capability and state why it matters.
```

Use `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` as
needed. Curate for users; do not paste a Git log.

## Handoff shape

Keep the project's existing handoff concise and current. After important work,
record only context that would prevent a future chat from repeating analysis:

1. current state and the intrinsic logic needed to navigate it;
2. significant decisions and why they were made;
3. research findings, evidence, and links to durable source material;
4. failed or rejected approaches when repeating them would waste time;
5. verification commands and the last known result;
6. known issues and concrete next work.

Keep long domain knowledge in dedicated project documentation and link to it
from the handoff. Do not copy chat transcripts or duplicate the same facts in
several files. Small fixes with no durable takeover context need no handoff
update.

## Git completion discipline

- Inspect `git status --short` before work. Leave changes uncommitted and
  unstaged by default.
- Never stage for commit, commit, amend/rebase/squash, or create/move/delete a
  tag unless the user explicitly requests that Git action in the current chat.
  Completing work, preparing a release, and project instructions do not count
  as authorization.
- When asked to commit the diff smartly, commit all diff, or equivalent, include
  all Git-visible modifications, deletions, renames, and non-ignored untracked
  files, including unrelated or pre-existing work. Split the complete set into
  coherent commits when that improves history, keep tests coupled to the code
  they verify, and do not silently omit requested changes. If the visible set
  appears to contain secrets or other unsafe material, stop and report it
  before committing.
- Use a clear Conventional Commit subject and an explanatory body when the
  reason is not evident from the diff.
- Do not amend, rebase, squash, or move tags without explicit authorization.
- For an explicitly requested release, keep release tags annotated and named
  `vX.Y.Z`.
- Do not treat a remote or hosted release page as the canonical changelog.
