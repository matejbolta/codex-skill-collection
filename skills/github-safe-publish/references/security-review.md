# Security-conscious GitHub publication review

Read this reference for a repository's first publication, a private-to-public transition, or any suspected leak.

## Publication model

The material that crosses the boundary is not just the current directory. It may include:

- every ancestor commit of each pushed branch;
- any explicitly pushed tags or additional refs;
- Git LFS objects and submodule URLs;
- commit author and committer names and email addresses;
- release assets, workflow definitions, logs, and artifacts created after publication;
- binary metadata embedded in images, documents, recordings, archives, and databases.

Choose the refs first, then audit the exact reachable set. Do not use `--all`, `--mirror`, or `--tags` for convenience.

## Local review layers

### Repository boundary

- Resolve `git rev-parse --show-toplevel` and confirm it is the intended project, not a directory grouping several repositories.
- Inspect nested `.git` markers, worktrees, submodules, symlinks, and LFS configuration.
- Review existing remotes for the correct owner and ensure URLs contain no embedded credentials.

### File and state inventory

- Review tracked, staged, unstaged, untracked, and ignored files separately.
- Treat `.gitignore` as prevention, not evidence that a file was never committed.
- Investigate environment files, private keys, certificate bundles, cloud and package-manager credentials, browser profiles, cookies, session stores, SSH material, databases, backups, dumps, logs, exports, user fixtures, analytics, screenshots, and recordings.
- Inspect generated archives and build output before tracking them; they can contain source maps, environment values, local paths, or bundled credentials.

### Content and identity

- Scan for provider tokens, private-key headers, authenticated connection strings, passwords, and high-entropy credentials. Keep output redacted.
- Search for absolute home paths, system usernames, personal emails, phone numbers, addresses, customer data, private URLs, internal hostnames, and realistic test fixtures.
- Review commit author and committer emails across the refs being published. GitHub-provided `noreply` addresses are available when the author wants commit-email privacy, but changing local configuration affects future commits rather than rewriting existing ones.
- Check binary metadata with an appropriate local tool when media or office documents are included. Do not upload private artifacts to an online metadata service for inspection.

### History

- Scan all blobs reachable from the exact refs being pushed, not only files present at `HEAD`.
- If the repository has several branches or tags that will be published, audit all of them.
- A secret removed in a later commit remains retrievable from history.
- If a suspected credential is real, revoke or rotate it before attempting cleanup.

## When sensitive data has entered history

Stop the ordinary publication workflow. Establish whether the data was already pushed or shared and who has clones or forks.

History rewriting changes commit hashes, can invalidate signatures, disrupt pull requests, and can be recontaminated by old clones. Use a recoverable clone or backup, follow current GitHub guidance, coordinate with collaborators, and obtain explicit approval before rewriting or force-pushing. A local rewrite alone cannot remove data from other clones, forks, cached views, or pull-request references.

Authoritative guidance:

- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitHub: Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)
- [GitHub: Supported secret-scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns)

## Visibility, licensing, and identity decisions

Public visibility exposes the code and public activity to anyone and permits forks. A private-to-public change can also expose Actions history and logs, so audit hosted state as well as Git history before changing visibility.

Do not choose a license on the owner's behalf. A public repository without a license is viewable, but default copyright remains; public does not automatically mean open source.

Review the configured Git author email and existing commit history before publication. If privacy matters, let the owner choose a GitHub `noreply` address for future commits and decide whether old history justifies rewriting.

Authoritative guidance:

- [GitHub: Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [GitHub: Commit email addresses](https://docs.github.com/en/account-and-profile/concepts/email-addresses)

## After publication

Verify the remote SHA, visibility, default branch, files, releases, and Pages/Actions exposure. For public repositories, review the availability and suitability of:

- secret scanning and push protection;
- Dependabot alerts and security updates;
- code scanning for supported codebases;
- branch rules and required review for collaborative repositories;
- a `SECURITY.md` with a real private reporting route;
- minimal Actions permissions, pinned third-party actions, and protected environments where applicable.

GitHub recommends Dependabot alerts, secret scanning, push protection, and code scanning as baseline public-repository security features. Availability differs for private repositories and account plans; verify current settings rather than assuming they are enabled.

- [GitHub: Security and analysis settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository)
- [GitHub: Adding a security policy](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy)
