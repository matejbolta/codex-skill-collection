# Recipient Install Prompts

## Install everything with another Codex agent

```text
Use $skill-installer to install the following Codex skills from https://github.com/matejbolta/codex-skill-collection at ref main:
- `skills/apple-inspired-product-ui`
- `skills/browser-visual-qa`
- `skills/dev-workspace-organizer`
- `skills/github-safe-publish`
- `skills/project-governance`
- `skills/skill-publisher`

Do not overwrite any existing skill. If a destination already exists, stop and report it. After installation, report which skills succeeded and remind me they become available on the next Codex turn.
```

## Install one skill

### apple-inspired-product-ui

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/apple-inspired-product-ui. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

### browser-visual-qa

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/browser-visual-qa. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

### dev-workspace-organizer

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/dev-workspace-organizer. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

### github-safe-publish

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/github-safe-publish. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

### project-governance

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/project-governance. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

### skill-publisher

```text
Use $skill-installer to install https://github.com/matejbolta/codex-skill-collection/tree/main/skills/skill-publisher. Do not overwrite an existing skill; stop and report if it is already installed. After installation, remind me it becomes available on the next Codex turn.
```

## Exact installer command

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo matejbolta/codex-skill-collection --ref main --path skills/apple-inspired-product-ui skills/browser-visual-qa skills/dev-workspace-organizer skills/github-safe-publish skills/project-governance skills/skill-publisher
```
