#!/usr/bin/env python3
"""Safely add missing project-governance scaffolding and initialize local Git."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--kind", choices=("software", "records"), required=True)
    parser.add_argument("--name")
    parser.add_argument("--version", help="Required for software if no existing version is found")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_json_version(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text()).get("version")
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def discover_version(root: Path) -> tuple[str | None, str | None]:
    candidates = (
        root / "package.json",
        root / "public" / "manifest.json",
        root / "extension" / "manifest.json",
        root / "manifest.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            version = read_json_version(candidate)
            if version:
                return version, str(candidate.relative_to(root))
    version_file = root / "VERSION"
    if version_file.is_file():
        value = version_file.read_text().strip()
        if SEMVER.fullmatch(value):
            return value, "VERSION"
    return None, None


def render(template: Path, project_name: str, version: str | None) -> str:
    return (
        template.read_text()
        .replace("{{PROJECT_NAME}}", project_name)
        .replace("{{VERSION}}", version or "unversioned")
        .replace("{{DATE}}", date.today().isoformat())
    )


def validate_target(root: Path) -> None:
    resolved = root.resolve()
    forbidden = {Path("/"), Path.home(), Path.home() / "Documents", Path.home() / "Documents" / "Dev"}
    if resolved in forbidden:
        raise SystemExit(f"refusing broad target: {resolved}")
    if not resolved.is_dir():
        raise SystemExit(f"project directory does not exist: {resolved}")
    if not (resolved / ".git").exists():
        nested = [path for path in resolved.glob("**/.git") if path.parent != resolved]
        if nested:
            examples = ", ".join(str(path.parent) for path in nested[:3])
            raise SystemExit(f"refusing grouping directory containing nested repositories: {examples}")


def main() -> int:
    args = parse_args()
    root = args.path.resolve()
    validate_target(root)
    project_name = args.name or root.name
    discovered, source = discover_version(root)
    version = args.version or discovered
    if args.kind == "software" and not version:
        raise SystemExit("software projects require --version when no valid existing version is found")
    if version and not SEMVER.fullmatch(version):
        raise SystemExit(f"invalid semantic version: {version}")

    templates = {
        "AGENTS.md": TEMPLATE_ROOT / args.kind / "AGENTS.md",
        "README.md": TEMPLATE_ROOT / args.kind / "README.md",
        "docs/HANDOFF.md": TEMPLATE_ROOT / args.kind / "HANDOFF.md",
    }
    if args.kind == "software":
        templates["CHANGELOG.md"] = TEMPLATE_ROOT / "software" / "CHANGELOG.md"

    created: list[str] = []
    for relative, template in templates.items():
        destination = root / relative
        if destination.exists():
            continue
        created.append(relative)
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(render(template, project_name, version))

    # Claude Code reads CLAUDE.md, not AGENTS.md. Point it at the canonical file
    # so both agents share one set of instructions.
    claude_pointer = root / "CLAUDE.md"
    if not claude_pointer.exists():
        created.append("CLAUDE.md")
        if not args.dry_run:
            claude_pointer.write_text("@AGENTS.md\n")

    if args.kind == "software" and source is None and not (root / "VERSION").exists():
        created.append("VERSION")
        if not args.dry_run:
            (root / "VERSION").write_text(f"{version}\n")

    git_initialized = not (root / ".git").exists()
    if git_initialized and not args.dry_run:
        subprocess.run(["git", "init", "-b", "main", str(root)], check=True)

    action = "would create" if args.dry_run else "created"
    print(f"{action}: {', '.join(created) if created else '(no files)'}")
    print(f"git initialized: {git_initialized}")
    print(f"version: {version or '(not applicable)'}{f' from {source}' if source else ''}")
    print("No files were staged, committed, tagged, pushed, or overwritten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
