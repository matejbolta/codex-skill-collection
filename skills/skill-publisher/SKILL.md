---
name: skill-publisher
description: Package local Codex skills into a clean, validated, shareable collection with GitHub-compatible paths, recipient install prompts, and an optional zip archive. Use when preparing skills for another Codex user; do not publish, push, create remotes, or overwrite installed skills without explicit authorization.
---

# Skill Publisher

Prepare portable skill distributions without changing the source skills or silently expanding a local packaging request into a public release.

## Establish The Scope

- Identify the exact personal skills requested. Do not include bundled `.system` skills, plugin cache content, private fixtures, or unrelated local skills unless the user names them.
- Treat packaging and remote publication as separate actions. A request to make skills shareable authorizes a local collection or archive; creating a remote, committing, pushing, publishing, or choosing a license needs its own authorization.
- Preserve source skills. If a real portability defect is found, report it and modify the source only when that correction is within the user's request.
- Resolve the new collection directory, optional archive, future GitHub URL, ref, and title before packaging. The output and archive must not already exist or overlap one another or any source skill.

## Audit Before Copying

For every source skill:

- require a valid `SKILL.md` with matching folder and frontmatter names;
- run the bundled `skill-creator` validator when it is available;
- run or inspect any included scripts in proportion to their risk;
- check for machine-specific Unix or Windows user paths, credential-like assignments, private data, generated caches, nested repositories, and symlinks;
- preserve `agents/openai.yaml`, references, scripts, and assets that the skill actually needs;
- identify missing licensing rather than inventing a license for the owner.

The bundled portability and credential checks are heuristics, not a security guarantee. Review every finding in context without printing a matched credential value.

Generated caches such as `.DS_Store`, `.git`, `__pycache__`, `.pytest_cache`, and compiled Python files never belong in the distribution.

## Build The Collection

Use `scripts/package_skills.py` for repeatable packaging. It refuses to overwrite or nest outputs, resolves a symlinked top-level skill argument, rejects every nested symlink, detects common machine-specific paths and credential assignments, excludes generated caches, records licensing warnings, hashes the complete collection payload, and generates recipient prompts. Collection and archive files are built in temporary sibling paths before finalization. When every skill carries one identical conventional license, the packager also emits that license at the collection root.

Pass `--github-ci` for a public GitHub collection. It installs the bundled,
least-privilege validation workflow, which checks metadata, manifest coverage
and hashes, Python syntax, and every committed `tests/test_*.py` fixture. The
workflow installs PyYAML explicitly rather than assuming it exists on a runner.
For local validation, install `PyYAML>=6,<7` and run
`python .github/scripts/validate_collection.py` from the collection root; the
validator reports a concise installation hint when the dependency is absent.

Example:

```sh
python3 scripts/package_skills.py \
  --output /path/to/codex-skill-collection \
  --archive /path/to/codex-skill-collection.zip \
  --repo-url https://github.com/OWNER/REPO \
  --github-ci \
  --skill ~/.codex/skills/example-one \
  --skill ~/.codex/skills/example-two
```

The output layout is compatible with the bundled GitHub installer:

```text
codex-skill-collection/
|-- README.md
|-- INSTALL_PROMPTS.md
|-- LICENSE                 When every skill carries identical license terms
|-- manifest.json
|-- .github/
`-- skills/
    |-- example-one/
    `-- example-two/
```

If the final GitHub URL is not known, keep the generated `OWNER/REPO` placeholder. Do not guess an account, repository, branch, or visibility.

## Validate The Artifact

- Run the `skill-creator` validator against every packaged skill, not only the originals.
- Compare the packaged and source content while accounting for deliberately excluded caches.
- Inspect `manifest.json` and confirm that every collection payload file except the manifest itself has a byte count and SHA-256. Recompute representative hashes rather than trusting presence alone.
- Read the generated recipient prompts and verify that repository paths match the bundle layout.
- Exercise the packaging script in a temporary directory after changing it.

Tell the user exactly where the collection and archive were written, which skills they contain, what was excluded or made portable, licensing or audit warnings, and which external publication decision remains. Recipient-facing guidance should say the skills become available on the next Codex turn and should never instruct the installer to overwrite an existing destination.
