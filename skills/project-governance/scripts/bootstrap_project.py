#!/usr/bin/env python3
"""Safely add missing continuity files and optionally initialize local Git."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates"


class BootstrapError(RuntimeError):
    """A user-actionable bootstrap failure."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--kind", choices=("software", "records"), required=True)
    parser.add_argument("--name")
    parser.add_argument(
        "--with-releases",
        action="store_true",
        help="Add SemVer and changelog governance to a software project",
    )
    parser.add_argument(
        "--version",
        help="Initial SemVer for --with-releases when no version source exists",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_json_version(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("version")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def read_pyproject_version(path: Path) -> str | None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        value = payload.get("project", {}).get("version")
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def discover_versions(root: Path) -> dict[str, str]:
    readers = (
        ("package.json", read_json_version),
        ("pyproject.toml", read_pyproject_version),
        ("public/manifest.json", read_json_version),
        ("extension/manifest.json", read_json_version),
        ("manifest.json", read_json_version),
    )
    found: dict[str, str] = {}
    for relative, reader in readers:
        value = reader(root / relative)
        if value:
            found[relative] = value
    version_file = root / "VERSION"
    if version_file.is_file():
        value = version_file.read_text(encoding="utf-8").strip()
        if SEMVER.fullmatch(value):
            found["VERSION"] = value
    return found


def render(template: Path, project_name: str, version: str | None) -> str:
    return (
        template.read_text(encoding="utf-8")
        .replace("{{PROJECT_NAME}}", project_name)
        .replace("{{VERSION}}", version or "unversioned")
        .replace("{{DATE}}", date.today().isoformat())
    )


def git_toplevel(root: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode:
        return None
    return Path(completed.stdout.strip()).resolve()


def validate_target(root: Path) -> bool:
    resolved = root.resolve()
    home = Path.home().resolve()
    forbidden = {
        Path("/"),
        home,
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
    }
    if resolved in forbidden:
        raise BootstrapError(f"refusing broad target: {resolved}")
    if not resolved.is_dir():
        raise BootstrapError(f"project directory does not exist: {resolved}")

    containing_root = git_toplevel(resolved)
    if containing_root:
        if containing_root != resolved:
            raise BootstrapError(
                f"target is nested inside existing repository: {containing_root}"
            )
        return True

    nested = [path for path in resolved.glob("**/.git") if path.parent != resolved]
    if nested:
        examples = ", ".join(str(path.parent) for path in nested[:3])
        raise BootstrapError(
            f"refusing grouping directory containing nested repositories: {examples}"
        )
    return False


def validate_name(value: str) -> str:
    if not value or value != value.strip() or any(ord(char) < 32 for char in value):
        raise BootstrapError("project name must be one non-empty printable line")
    return value


def resolve_release_version(
    root: Path, with_releases: bool, requested: str | None
) -> tuple[str | None, dict[str, str]]:
    if requested and not with_releases:
        raise BootstrapError("--version requires --with-releases")
    if not with_releases:
        return None, {}
    if requested and not SEMVER.fullmatch(requested):
        raise BootstrapError(f"invalid semantic version: {requested}")

    found = discover_versions(root)
    unique = sorted(set(found.values()))
    if len(unique) > 1:
        pairs = ", ".join(f"{path}={value}" for path, value in found.items())
        raise BootstrapError(f"conflicting semantic version sources: {pairs}")
    discovered = unique[0] if unique else None
    if requested and discovered and requested != discovered:
        pairs = ", ".join(f"{path}={value}" for path, value in found.items())
        raise BootstrapError(
            f"--version {requested} conflicts with existing version source(s): {pairs}"
        )
    version = requested or discovered
    if not version:
        raise BootstrapError(
            "--with-releases requires --version when no valid version source exists"
        )
    return version, found


def main() -> int:
    args = parse_args()
    root = args.path.expanduser().resolve()
    has_git = validate_target(root)
    project_name = validate_name(args.name or root.name)
    if args.kind != "software" and args.with_releases:
        raise BootstrapError("--with-releases is supported only for --kind software")
    version, sources = resolve_release_version(root, args.with_releases, args.version)

    template_kind = "software-release" if args.with_releases else args.kind
    templates = {
        "AGENTS.md": TEMPLATE_ROOT / template_kind / "AGENTS.md",
        "README.md": TEMPLATE_ROOT / template_kind / "README.md",
        "docs/HANDOFF.md": TEMPLATE_ROOT / template_kind / "HANDOFF.md",
    }
    if args.with_releases:
        templates["CHANGELOG.md"] = TEMPLATE_ROOT / template_kind / "CHANGELOG.md"
    missing_templates = [str(path) for path in templates.values() if not path.is_file()]
    if missing_templates:
        raise BootstrapError(f"skill templates are missing: {', '.join(missing_templates)}")

    created: list[str] = []
    for relative, template in templates.items():
        destination = root / relative
        if destination.exists():
            continue
        created.append(relative)
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                render(template, project_name, version), encoding="utf-8"
            )

    claude_pointer = root / "CLAUDE.md"
    if not claude_pointer.exists():
        created.append("CLAUDE.md")
        if not args.dry_run:
            claude_pointer.write_text("@AGENTS.md\n", encoding="utf-8")

    if args.with_releases and not sources and not (root / "VERSION").exists():
        created.append("VERSION")
        if not args.dry_run:
            (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")

    git_would_initialize = not has_git
    if git_would_initialize and not args.dry_run:
        subprocess.run(["git", "init", "-b", "main", str(root)], check=True)

    action = "would create" if args.dry_run else "created"
    git_label = "git would initialize" if args.dry_run else "git initialized"
    print(f"{action}: {', '.join(created) if created else '(no files)'}")
    print(f"{git_label}: {git_would_initialize}")
    if args.with_releases:
        source_text = ", ".join(sources) if sources else "new VERSION"
        print(f"release governance: semver {version} from {source_text}")
    else:
        print("release governance: not enabled")
    print("No files were staged, committed, tagged, pushed, or overwritten.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BootstrapError, OSError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
