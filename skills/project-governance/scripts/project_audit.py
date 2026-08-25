#!/usr/bin/env python3
"""Audit an explicit project inventory for Git, version, and handoff consistency."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


@dataclass
class Result:
    name: str
    path: str
    management: str
    kind: str
    git: bool
    branch: str | None
    commits: int | None
    version: str | None
    version_sources: dict[str, str]
    latest_tag: str | None
    dirty_paths: int | None
    issues: list[str]
    notes: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--allow-issues", action="store_true")
    return parser.parse_args()


def git(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def json_version(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text()).get("version")
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def read_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    if path.name == "VERSION":
        value = path.read_text().strip()
        return value if SEMVER.fullmatch(value) else None
    return json_version(path)


def versions(root: Path, source: str | None = None) -> dict[str, str]:
    """Discover version sources under root.

    A repository that holds two independently released products cannot be
    described by one number. Set "version_source" on the inventory entry to
    name the single file this project is versioned by; the other product keeps
    its own version and is governed by its own AGENTS.md and CHANGELOG.
    """
    if source is not None:
        value = read_version(root / source)
        return {source: value} if value else {}

    found: dict[str, str] = {}
    candidates = (
        "package.json",
        "public/manifest.json",
        "extension/manifest.json",
        "manifest.json",
        "VERSION",
    )
    for relative in candidates:
        value = read_version(root / relative)
        if value:
            found[relative] = value
    return found


def audit(entry: dict[str, Any]) -> Result:
    root = Path(entry["path"]).expanduser()
    name = entry.get("name", root.name)
    management = entry.get("management", "managed")
    kind = entry.get("kind", "software")
    version_source = entry.get("version_source")
    issues: list[str] = []
    notes: list[str] = []
    exists = root.is_dir()
    if not exists:
        issues.append("directory missing")
    has_git = exists and (root / ".git").exists()

    if management == "empty":
        if exists and any(root.iterdir()):
            issues.append("marked empty but contains files")
        return Result(name, str(root), management, kind, has_git, None, None, None, {}, None, None, issues, notes)
    if management in {"grouping", "upstream"}:
        notes.append("not governed as an ordinary independent project")
        return Result(name, str(root), management, kind, has_git, None, None, None, versions(root, version_source), None, None, issues, notes)

    if not has_git:
        issues.append("missing local Git repository")
    required = ["AGENTS.md", "CLAUDE.md", "README.md", "docs/HANDOFF.md"]
    if kind == "software":
        required.append("CHANGELOG.md")
    for relative in required:
        if not (root / relative).is_file():
            issues.append(f"missing {relative}")

    found_versions = versions(root, version_source)
    unique_versions = sorted(set(found_versions.values()))
    version = unique_versions[0] if len(unique_versions) == 1 else None
    if kind == "software":
        if not found_versions:
            if version_source:
                issues.append(f"version_source {version_source} is missing or not a valid semantic version")
            else:
                issues.append("missing semantic version source")
        elif len(unique_versions) > 1:
            pairs = ", ".join(f"{path}={value}" for path, value in found_versions.items())
            issues.append(f"version mismatch: {pairs}")

    branch = None
    commits = None
    latest_tag = None
    dirty_paths = None
    if has_git:
        branch = git(root, "branch", "--show-current") or None
        count = git(root, "rev-list", "--count", "HEAD")
        commits = int(count) if count and count.isdigit() else 0
        latest_tag = git(root, "tag", "--sort=-version:refname")
        latest_tag = latest_tag.splitlines()[0] if latest_tag else None
        status = git(root, "status", "--porcelain")
        dirty_paths = len(status.splitlines()) if status else 0
        require_tag = entry.get("require_current_tag", False)
        if require_tag and version and not git(
            root, "rev-parse", "-q", "--verify", f"refs/tags/v{version}"
        ):
            issues.append(f"missing local tag v{version}")
        if dirty_paths:
            notes.append(f"working tree has {dirty_paths} changed paths")

    return Result(
        name,
        str(root),
        management,
        kind,
        has_git,
        branch,
        commits,
        version,
        found_versions,
        latest_tag,
        dirty_paths,
        issues,
        notes,
    )


def main() -> int:
    args = parse_args()
    payload = json.loads(args.inventory.read_text())
    results = [audit(entry) for entry in payload["projects"]]
    if args.as_json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            state = "OK" if not result.issues else "ISSUES"
            version = result.version or "-"
            print(f"{state:6} {result.name:28} {result.management:9} git={'yes' if result.git else 'no ':3} version={version}")
            for issue in result.issues:
                print(f"       issue: {issue}")
            for note in result.notes:
                print(f"       note:  {note}")
    issue_count = sum(len(result.issues) for result in results)
    print(f"Audited {len(results)} entries; {issue_count} issues.", file=sys.stderr)
    return 0 if args.allow_issues or issue_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
