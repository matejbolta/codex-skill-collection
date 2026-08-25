---
name: github-safe-publish
description: Audit a local Git repository for secrets, personal data, risky history, and publication readiness, then create and push a GitHub remote only with explicit authorization. Use for first publication or a deliberate privacy/security review; do not use for routine pushes to an already-reviewed remote.
---

# GitHub Safe Publish

Treat the first external push as a security and privacy boundary. A clean working tree is not evidence that reachable history is safe.

## Establish explicit publication choices

Resolve these before mutation:

- the exact local repository root and branch or refs intended for publication;
- GitHub owner and repository name;
- public or private visibility and who should receive access;
- whether a license is desired and, if so, which one the owner selected;
- whether the user has authorized staging, committing, remote creation, and pushing.

These are separate choices. A request to audit or prepare does not authorize a commit, remote, visibility decision, or push. A request that explicitly supplies and authorizes all of them need not be reconfirmed.

## Audit before the network boundary

For first publication, read [references/security-review.md](references/security-review.md). Run the bundled read-only audit from the skill directory:

```sh
python3 scripts/prepublish_audit.py /path/to/repository --history-scope head
```

Use `--history-scope all` when the user intends to publish every branch or tag. Review findings rather than treating a zero exit as proof of safety; no pattern scanner can establish absence of secrets or personal information.

Inspect at least:

- tracked, staged, modified, untracked, and ignored paths;
- reachable history for the exact refs that will be pushed, including deleted files;
- secret-like content without printing detected values;
- private keys, environment files, credential stores, databases, exports, logs, fixtures, screenshots, recordings, and document/media metadata;
- absolute home paths, usernames, email addresses in file content, and commit author/committer emails;
- symlinks, submodules, Git LFS objects, nested repositories, release assets, workflow logs, and generated output;
- the complete staged change set, remote URL, branch, repository name, description, visibility, and license decision.

Use a dedicated secret scanner with redacted output when one is already available and appropriate. Do not download a new security tool, upload the repository to a scanner, or disclose matched values without authorization.

## Handle findings safely

- Never echo a suspected secret into chat, terminal output, a report, or a commit. Identify it by rule, file, and location with the value redacted.
- If a credential may be real, stop publication and revoke or rotate it first. Deleting it from the current file does not remove it from Git history.
- Treat history rewriting as a separate destructive operation. Explain its effects, work from a recoverable clone or backup, coordinate with collaborators, and obtain explicit authorization before rewriting or force-pushing.
- Do not dismiss a GitHub push-protection block merely to finish the push. Investigate the finding; bypass only when the user knowingly accepts a verified false positive or intentional test value.
- Private visibility reduces audience, not the impact of credential exposure. Remove real secrets from private repositories too.

## Publish narrowly

1. Inspect the authenticated GitHub identity without displaying tokens. Check whether the exact repository already exists; never overwrite or repurpose it silently.
2. Review every Git-visible change and the staged diff. Commit only when explicitly authorized, keeping unrelated visible changes within the user's stated scope.
3. Create the repository with the chosen visibility and no invented license. Use the narrowest credentials and permissions available.
4. Add a resolved remote URL without embedded credentials. Push only the authorized branch; do not add `--all`, `--mirror`, `--tags`, or force options by default.
5. Verify the remote visibility, default branch, HEAD SHA, published file set, and repository URL. For public software, review GitHub security features and add `SECURITY.md` when the project has a real vulnerability-reporting channel.
6. Report exactly what was published, what checks ran, remaining review items, and any security settings the user must decide.

Stop when ownership, visibility, a suspicious finding, an existing remote, a history rewrite, a force push, or access-control change requires user judgment.
