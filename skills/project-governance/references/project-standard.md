# Project standard

Read this reference for bootstrap, audit, migration, continuity, or release
work. It defines a conservative starting point, not a layout to impose on an
established repository.

## Keep three permissions separate

Project governance has three independent layers:

1. **Continuity:** instructions, orientation, and current takeover context.
2. **Release governance:** an explicit version source, changelog, and release
   procedure for a product that actually ships versions.
3. **Git history mutation:** staging, committing, tagging, pushing, or
   publishing.

Authorization for one layer does not authorize another. Bootstrap can create
continuity files without choosing SemVer. Preparing release files does not
authorize a commit or tag. A local commit does not authorize a push.

## Continuity records

For a new software project or maintained record collection, this is a useful
minimal starting layout:

```text
AGENTS.md
CLAUDE.md
README.md
docs/HANDOFF.md
```

`AGENTS.md` is the canonical instruction file. `CLAUDE.md` is a one-line pointer
containing `@AGENTS.md`, because Claude Code reads `CLAUDE.md` rather than
`AGENTS.md`. Keep the instructions in `AGENTS.md` only; never duplicate them
into `CLAUDE.md`. Where `AGENTS.md` is local-only or ignored, treat `CLAUDE.md`
the same way.

Add `docs/ARCHITECTURE.md`, `docs/adr/`, `docs/RELEASE.md`, `SECURITY.md`, or
`CONTRIBUTING.md` only when the project actually needs them. Maintained notes or
data collections normally benefit from Git history and a handoff, but do not
need a changelog or SemVer unless they produce releases.

Do not impose this layout on an established repository. Preserve its existing
file names, ignore rules, and tracked-versus-local policy. If project memory is
local-only, keep it untracked. `.gitignore` is appropriate when the convention
should travel with the repository; `.git/info/exclude` is appropriate when even
the ignore rule should remain device-local.

## Release governance is explicit

Add `CHANGELOG.md`, a canonical version, and release instructions only when the
user requests a release model or the established project already has one that
must be repaired or audited. Do not infer a release lifecycle merely because
the project contains software.

For SemVer-governed software, prefer an existing ecosystem version source in
this order:

1. `package.json` for Node applications and built browser extensions;
2. `pyproject.toml` at `project.version` for packaged Python software;
3. the runtime `manifest.json` for dependency-free unpacked extensions;
4. `VERSION` for language-neutral applications and scripts.

When an ecosystem requires duplicate versions, identify one as canonical and
validate the others. Never maintain a display version separately when it can be
read from the canonical source. If multiple discovered sources disagree, stop
and resolve the inconsistency rather than choosing silently.

### Repositories that hold two products

A repository containing two independently released products can legitimately
have two versions. Do not force them to match. In an audit inventory, set
`version_source` to the file that versions the listed project:

```json
{
  "name": "scramble-set-insight",
  "path": "/path/to/projects/scramble-set-insight",
  "management": "managed",
  "kind": "software",
  "release_policy": "semver",
  "version_source": "VERSION"
}
```

The other product keeps its own version and governance. Use this exception only
for genuinely separate products; a build artifact or manifest that restates the
same product's version is a duplicate under the canonical-source rule.

## Honest baselines

For a non-empty project with no Git history:

1. inspect local state, ignored files, secrets, generated output, personal
   fixtures, databases, logs, and caches;
2. add or improve ignore policy only from verified project evidence;
3. initialize Git with branch `main` when bootstrap is authorized;
4. add truthful continuity records without pretending they existed earlier;
5. add release governance only when explicitly requested;
6. inspect every path before any separately authorized staging action;
7. if the user explicitly requests a baseline commit, explain that earlier
   exact history is not recoverable.

Do not backdate commits. A reconstructed changelog may summarize known earlier
versions only when it labels the reconstruction and its evidence.

## Changelog shape

For a SemVer-governed project, follow Keep a Changelog with `Unreleased` first
and release headings such as:

```markdown
## [1.2.0] - 2026-08-21

### Added

- Add the user-visible capability and state why it matters.
```

Use `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` as
needed. Curate for users; do not paste a Git log. Change the changelog and
canonical version together only during an explicitly requested release or
version operation.

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
  appears to contain secrets or other unsafe material, stop and report it before
  committing.
- Use a clear Conventional Commit subject and an explanatory body when the
  reason is not evident from the diff.
- Do not amend, rebase, squash, or move tags without explicit authorization.
- For an explicitly requested release, keep release tags annotated and named
  `vX.Y.Z`.
- Do not treat a remote or hosted release page as the canonical changelog.
