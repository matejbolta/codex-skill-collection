#!/usr/bin/env python3
"""Audit an explicit project inventory for Git, continuity, and release consistency."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
MANAGEMENT_VALUES = {"managed", "grouping", "upstream", "empty"}
KIND_VALUES = {"software", "records"}
RELEASE_VALUES = {"none", "semver"}
ENTRY_FIELDS = {
    "name",
    "path",
    "management",
    "kind",
    "release_policy",
    "version_source",
    "require_current_tag",
}
CURRENT_INVENTORY_SCHEMA = 2
SUPPORTED_INVENTORY_SCHEMAS = {1, CURRENT_INVENTORY_SCHEMA}
EXAMPLE_INVENTORY = {
    "schema_version": CURRENT_INVENTORY_SCHEMA,
    "projects": [
        {
            "name": "example-app",
            "path": "projects/example-app",
            "management": "managed",
            "kind": "software",
            "release_policy": "semver",
            "version_source": "pyproject.toml",
            "require_current_tag": False,
        },
        {
            "name": "research-notes",
            "path": "records/research-notes",
            "management": "managed",
            "kind": "records",
            "release_policy": "none",
        },
    ]
}


class InventoryError(RuntimeError):
    """An invalid inventory or operational audit error."""


@dataclass
class Result:
    name: str
    path: str
    management: str
    kind: str
    release_policy: str
    git: bool
    repository_root: str | None
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
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--inventory", type=Path)
    source.add_argument(
        "--example-inventory",
        action="store_true",
        help="Print a complete example inventory and exit",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--allow-issues", action="store_true")
    return parser.parse_args()


def git(root: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def json_version(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = payload.get("version")
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def toml_version(path: Path) -> str | None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        value = payload.get("project", {}).get("version")
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return None
    return value if isinstance(value, str) and SEMVER.fullmatch(value) else None


def read_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    if path.name == "VERSION":
        value = path.read_text(encoding="utf-8").strip()
        return value if SEMVER.fullmatch(value) else None
    if path.suffix.lower() == ".toml":
        return toml_version(path)
    return json_version(path)


def versions(root: Path, source: str | None = None) -> dict[str, str]:
    if source is not None:
        value = read_version(root / source)
        return {source: value} if value else {}

    found: dict[str, str] = {}
    candidates = (
        "package.json",
        "pyproject.toml",
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


def resolve_project_path(raw: str, base: Path) -> Path:
    candidate = Path(raw).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


def validate_version_source(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        raise InventoryError(f"{label}.version_source must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("~"):
        raise InventoryError(f"{label}.version_source must stay inside the project")
    if path.name != "VERSION" and path.suffix.lower() not in {".json", ".toml"}:
        raise InventoryError(
            f"{label}.version_source must be VERSION, a JSON file, or a TOML file"
        )
    return path.as_posix()


def inventory_schema(payload: Any) -> int:
    if not isinstance(payload, dict):
        raise InventoryError("inventory must be an object")
    unknown = sorted(set(payload) - {"schema_version", "projects"})
    if unknown:
        raise InventoryError(
            f"inventory has unknown top-level field(s): {', '.join(unknown)}"
        )
    raw_schema = payload.get("schema_version", 1)
    if isinstance(raw_schema, bool) or not isinstance(raw_schema, int):
        raise InventoryError("inventory.schema_version must be an integer")
    if raw_schema not in SUPPORTED_INVENTORY_SCHEMAS:
        raise InventoryError(
            f"unsupported inventory schema_version {raw_schema}; "
            f"supported versions are {sorted(SUPPORTED_INVENTORY_SCHEMAS)}"
        )
    return raw_schema


def default_release_policy(schema: int, management: str, kind: str) -> str:
    if schema == 1 and management == "managed" and kind == "software":
        return "semver"
    return "none"


def validate_inventory(payload: Any, base: Path) -> list[dict[str, Any]]:
    schema = inventory_schema(payload)
    if "projects" not in payload:
        raise InventoryError("inventory must contain 'projects'")
    projects = payload["projects"]
    if not isinstance(projects, list):
        raise InventoryError("inventory.projects must be an array")

    validated: list[dict[str, Any]] = []
    names: set[str] = set()
    paths: set[Path] = set()
    for index, raw in enumerate(projects):
        label = f"projects[{index}]"
        if not isinstance(raw, dict):
            raise InventoryError(f"{label} must be an object")
        unknown = sorted(set(raw) - ENTRY_FIELDS)
        if unknown:
            raise InventoryError(f"{label} has unknown field(s): {', '.join(unknown)}")
        raw_path = raw.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip() or raw_path != raw_path.strip():
            raise InventoryError(f"{label}.path must be a non-empty trimmed string")
        root = resolve_project_path(raw_path, base)
        name = raw.get("name", root.name)
        if not isinstance(name, str) or not name.strip() or name != name.strip():
            raise InventoryError(f"{label}.name must be a non-empty trimmed string")
        if name in names:
            raise InventoryError(f"duplicate project name: {name}")
        if root in paths:
            raise InventoryError(f"duplicate project path: {root}")

        management = raw.get("management", "managed")
        kind = raw.get("kind", "software")
        if schema == CURRENT_INVENTORY_SCHEMA and "release_policy" not in raw:
            raise InventoryError(
                f"{label}.release_policy is required by schema_version "
                f"{CURRENT_INVENTORY_SCHEMA}"
            )
        release_policy = raw.get(
            "release_policy", default_release_policy(schema, management, kind)
        )
        if management not in MANAGEMENT_VALUES:
            raise InventoryError(f"{label}.management must be one of {sorted(MANAGEMENT_VALUES)}")
        if kind not in KIND_VALUES:
            raise InventoryError(f"{label}.kind must be one of {sorted(KIND_VALUES)}")
        if release_policy not in RELEASE_VALUES:
            raise InventoryError(f"{label}.release_policy must be one of {sorted(RELEASE_VALUES)}")
        version_source = validate_version_source(raw.get("version_source"), label)
        require_current_tag = raw.get("require_current_tag", False)
        if not isinstance(require_current_tag, bool):
            raise InventoryError(f"{label}.require_current_tag must be boolean")
        if management != "managed" and (
            release_policy != "none" or version_source or require_current_tag
        ):
            raise InventoryError(
                f"{label} release fields are valid only for management 'managed'"
            )
        if release_policy != "semver" and (version_source or require_current_tag):
            raise InventoryError(
                f"{label} version_source/require_current_tag require release_policy 'semver'"
            )

        entry = {
            "name": name,
            "path": str(root),
            "management": management,
            "kind": kind,
            "release_policy": release_policy,
            "version_source": version_source,
            "require_current_tag": require_current_tag,
        }
        names.add(name)
        paths.add(root)
        validated.append(entry)
    return validated


def latest_semver_tag(root: Path) -> str | None:
    output = git(root, "tag", "--list", "v*", "--sort=-version:refname")
    if not output:
        return None
    return next(
        (tag for tag in output.splitlines() if SEMVER.fullmatch(tag.removeprefix("v"))),
        None,
    )


def empty_result(
    entry: dict[str, Any], root: Path, issues: list[str], notes: list[str]
) -> Result:
    return Result(
        entry["name"],
        str(root),
        entry["management"],
        entry["kind"],
        entry["release_policy"],
        False,
        None,
        None,
        None,
        None,
        {},
        None,
        None,
        issues,
        notes,
    )


def audit(entry: dict[str, Any]) -> Result:
    root = Path(entry["path"])
    issues: list[str] = []
    notes: list[str] = []
    exists = root.is_dir()
    if not exists:
        issues.append("directory missing")

    management = entry["management"]
    if management == "empty":
        if exists and any(root.iterdir()):
            issues.append("marked empty but contains files")
        return empty_result(entry, root, issues, notes)
    if management in {"grouping", "upstream"}:
        notes.append("not governed as an ordinary independent project")
        return empty_result(entry, root, issues, notes)

    repository_root_text = git(root, "rev-parse", "--show-toplevel") if exists else None
    repository_root = Path(repository_root_text).resolve() if repository_root_text else None
    has_git = repository_root is not None
    if not has_git:
        issues.append("missing local Git repository")
    elif repository_root != root:
        issues.append(f"path is nested inside repository root {repository_root}")

    required = ["AGENTS.md", "CLAUDE.md", "README.md", "docs/HANDOFF.md"]
    if entry["release_policy"] == "semver":
        required.append("CHANGELOG.md")
    for relative in required:
        if not (root / relative).is_file():
            issues.append(f"missing {relative}")

    claude_file = root / "CLAUDE.md"
    if claude_file.is_file():
        try:
            pointer = claude_file.read_text(encoding="utf-8").rstrip("\r\n")
        except (OSError, UnicodeDecodeError):
            issues.append("CLAUDE.md is not readable UTF-8 text")
        else:
            if pointer != "@AGENTS.md":
                issues.append("CLAUDE.md must contain only @AGENTS.md")

    found_versions: dict[str, str] = {}
    version = None
    if entry["release_policy"] == "semver":
        found_versions = versions(root, entry["version_source"])
        unique_versions = sorted(set(found_versions.values()))
        version = unique_versions[0] if len(unique_versions) == 1 else None
        if not found_versions:
            if entry["version_source"]:
                issues.append(
                    f"version_source {entry['version_source']} is missing or not valid SemVer"
                )
            else:
                issues.append("missing semantic version source")
        elif len(unique_versions) > 1:
            pairs = ", ".join(
                f"{path}={value}" for path, value in found_versions.items()
            )
            issues.append(f"version mismatch: {pairs}")

    branch = None
    commits = None
    latest_tag = None
    dirty_paths = None
    if has_git:
        branch = git(root, "branch", "--show-current") or None
        count = git(root, "rev-list", "--count", "HEAD")
        commits = int(count) if count and count.isdigit() else 0
        latest_tag = latest_semver_tag(root)
        status = git(root, "status", "--porcelain")
        dirty_paths = len(status.splitlines()) if status else 0
        if entry["require_current_tag"] and version and not git(
            root, "rev-parse", "-q", "--verify", f"refs/tags/v{version}"
        ):
            issues.append(f"missing local tag v{version}")
        if dirty_paths:
            notes.append(f"working tree has {dirty_paths} changed paths")

    return Result(
        entry["name"],
        str(root),
        management,
        entry["kind"],
        entry["release_policy"],
        has_git,
        str(repository_root) if repository_root else None,
        branch,
        commits,
        version,
        found_versions,
        latest_tag,
        dirty_paths,
        issues,
        notes,
    )


def load_inventory(path: Path) -> tuple[list[dict[str, Any]], Path]:
    inventory_path = path.expanduser().resolve()
    try:
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InventoryError(f"cannot read inventory {inventory_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InventoryError(
            f"invalid JSON in {inventory_path} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    return validate_inventory(payload, inventory_path.parent), inventory_path


def main() -> int:
    args = parse_args()
    if args.example_inventory:
        print(json.dumps(EXAMPLE_INVENTORY, indent=2) + "\n", end="")
        return 0
    assert args.inventory is not None
    entries, _ = load_inventory(args.inventory)
    results = [audit(entry) for entry in entries]
    if args.as_json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            state = "OK" if not result.issues else "ISSUES"
            version = result.version or "-"
            print(
                f"{state:6} {result.name:28} {result.management:9} "
                f"git={'yes' if result.git else 'no ':3} release={result.release_policy:6} "
                f"version={version}"
            )
            for issue in result.issues:
                print(f"       issue: {issue}")
            for note in result.notes:
                print(f"       note:  {note}")
    issue_count = sum(len(result.issues) for result in results)
    print(f"Audited {len(results)} entries; {issue_count} issues.", file=sys.stderr)
    return 0 if args.allow_issues or issue_count == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InventoryError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
