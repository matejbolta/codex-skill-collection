# Matej's Codex Skill Collection

A portable collection of personal Codex skills. Each skill is self-contained under `skills/` and can be installed independently.

## Skills

- **$apple-inspired-product-ui** — Review, specify, or refine macOS, iPhone/iOS, or cross-platform product interfaces with Apple-inspired hierarchy, platform-native behavior, restraint, adaptive craft, and accessibility. Use when Apple-platform design discipline or a Mac- or iPhone-appropriate interaction model is desired; do not use to copy Apple trade dress or for generic brand-identity work.
- **$browser-visual-qa** — Visually inspect, test, and iterate on browser-rendered interfaces in a real browser. Use for UI/UX implementation or review, layout and styling changes, responsive behavior, browser-extension pages, interaction states, and local web-app visual verification; do not use for backend-only or otherwise nonvisual work.
- **$dev-workspace-organizer** — Plan, initialize, or safely reorganize a multi-project development workspace into durable top-level categories without crossing repository boundaries. Use for layouts such as projects, tools, experiments, skills, and misc; do not use for one repository's internal structure.
- **$github-safe-publish** — Audit a local Git repository for secrets, personal data, risky history, and publication readiness, then create and push a GitHub remote only with explicit authorization. Use for first publication or a deliberate privacy/security review; do not use for routine pushes to an already-reviewed remote.
- **$project-governance** — Set up a previously untracked project, explicitly audit or migrate Git governance, create or repair a durable project-continuity system, or prepare an explicit release/version. Do not use for ordinary implementation, bug fixes, explanations, or routine task completion.
- **$skill-publisher** — Package local Codex skills into a clean, validated, shareable collection with GitHub-compatible paths, recipient install prompts, and an optional zip archive. Use when preparing skills for another Codex user; do not publish, push, create remotes, or overwrite installed skills without explicit authorization.

## Install

Copy the ready-to-paste prompts from [INSTALL_PROMPTS.md](INSTALL_PROMPTS.md). They target `https://github.com/matejbolta/codex-skill-collection` at ref `main`.

The bundled installer refuses to replace an existing destination. Installed skills become available on the next Codex turn.

## Licensing note

The collection and every included skill are licensed under the [MIT License](LICENSE).

## Validation

Pull requests and pushes are checked by the bundled GitHub Actions workflow. It validates skill metadata, manifest coverage and hashes, Python syntax, and the committed regression tests.
