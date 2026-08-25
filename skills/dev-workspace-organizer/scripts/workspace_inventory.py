#!/usr/bin/env python3
"""Inventory or non-destructively initialize a multi-project workspace."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_CATEGORIES = (
    "projects",
    "extensions",
    "tools",
    "experiments",
    "skills",
    "misc",
)
PRUNE_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}


class WorkspaceError(RuntimeError):
    """A user-actionable workspace inventory failure."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Workspace grouping root")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=list(DEFAULT_CATEGORIES),
        help="Top-level category names to inspect or create",
    )
    parser.add_argument(
        "--init", action="store_true", help="Create missing category directories"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what --init would create"
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def validate_categories(values: list[str]) -> list[str]:
    categories: list[str] = []
    for value in values:
        if (
            not value
            or value != value.strip()
            or value in {".", ".."}
            or "/" in value
            or "\\" in value
            or not all(character.isprintable() for character in value)
        ):
            raise WorkspaceError(f"invalid top-level category: {value!r}")
        if value.startswith("."):
            raise WorkspaceError(f"refusing hidden category: {value!r}")
        if value not in categories:
            categories.append(value)
    return categories


def validate_root(path: Path, init: bool) -> Path:
    root = path.expanduser().resolve()
    filesystem_root = Path(root.anchor)
    if root == filesystem_root or root == Path.home().resolve():
        raise WorkspaceError(f"refusing broad workspace root: {root}")
    if root.exists() and not root.is_dir():
        raise WorkspaceError(f"workspace root is not a directory: {root}")
    if not root.exists() and not init:
        raise WorkspaceError(f"workspace root does not exist: {root}")
    if not root.exists() and not root.parent.is_dir():
        raise WorkspaceError(f"workspace parent does not exist: {root.parent}")
    return root


def git_toplevel(path: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode:
        return None
    return Path(completed.stdout.strip()).resolve()


def git_containment(root: Path) -> tuple[bool, str | None]:
    probe = root if root.exists() else root.parent
    top = git_toplevel(probe)
    if top is None:
        return False, None
    if root.exists() and top == root:
        return True, None
    try:
        root.relative_to(top)
    except ValueError:
        return False, None
    return False, str(top)


def find_git_roots(root: Path) -> list[dict[str, str]]:
    if not root.exists():
        return []
    repositories: list[dict[str, str]] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path != root and (".git" in dirs or ".git" in files):
            marker = "file" if ".git" in files else "directory"
            repositories.append(
                {"path": str(current_path.relative_to(root)), "git_marker": marker}
            )
            dirs[:] = []
            continue
        dirs[:] = [
            name
            for name in dirs
            if name not in PRUNE_NAMES and not (current_path / name).is_symlink()
        ]
    return sorted(repositories, key=lambda item: item["path"])


def entry_kind(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "other"


def category_state(
    root: Path, categories: list[str]
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    present: list[str] = []
    missing: list[str] = []
    collisions: list[dict[str, str]] = []
    for name in categories:
        path = root / name
        if not os.path.lexists(path):
            missing.append(name)
        elif path.is_dir() and not path.is_symlink():
            present.append(name)
        else:
            collisions.append({"category": name, "kind": entry_kind(path)})
    return present, missing, collisions


def inventory(
    root: Path, categories: list[str], init: bool, dry_run: bool
) -> dict[str, object]:
    root_existed = root.exists()
    root_repository, containing_repository = git_containment(root)
    present, missing, collisions = category_state(root, categories)
    if init and collisions:
        details = ", ".join(
            f"{item['category']} ({item['kind']})" for item in collisions
        )
        raise WorkspaceError(f"category path collision(s): {details}")
    if init and (root_repository or containing_repository):
        owner = str(root) if root_repository else containing_repository
        raise WorkspaceError(
            f"refusing to initialize grouping categories inside Git repository: {owner}"
        )

    created: list[str] = []
    root_created = init and not dry_run and not root_existed
    if init and not dry_run:
        if not root_existed:
            root.mkdir()
        for name in missing:
            (root / name).mkdir()
            created.append(name)

    children = (
        sorted(root.iterdir(), key=lambda item: item.name.lower()) if root.exists() else []
    )
    symlink_entries = [child for child in children if child.is_symlink()]
    ordinary_entries = [child for child in children if not child.is_symlink()]
    category_set = set(categories)
    other_directories = [
        child.name
        for child in ordinary_entries
        if child.is_dir() and child.name not in category_set
    ]
    top_level_files = [child.name for child in ordinary_entries if child.is_file()]
    symlinks = [
        {"path": child.name, "target": os.readlink(child)} for child in symlink_entries
    ]
    final_present, final_missing, final_collisions = category_state(root, categories)
    warnings: list[str] = []
    if root_repository:
        warnings.append("workspace grouping root is a Git repository")
    if containing_repository:
        warnings.append(f"workspace is contained by Git repository {containing_repository}")
    if symlinks:
        warnings.append("resolve top-level symlinks before moving their parents")
    if final_collisions:
        warnings.append("one or more category paths collide with non-directories")

    action_key = "would_create" if dry_run else "created"
    return {
        "root": str(root),
        "root_existed_before": root_existed,
        "root_exists_after": root.exists(),
        "root_repository": root_repository,
        "containing_repository": containing_repository,
        "categories": categories,
        "present_categories": final_present,
        "missing_categories": final_missing,
        "category_collisions": final_collisions,
        "other_directories": other_directories,
        "top_level_files": top_level_files,
        "top_level_symlinks": symlinks,
        "nested_repositories": find_git_roots(root),
        "would_create_root" if dry_run else "root_created": (
            init and not root_existed if dry_run else root_created
        ),
        action_key: list(missing) if dry_run else created,
        "warnings": warnings,
    }


def print_human(report: dict[str, object]) -> None:
    print(f"workspace: {report['root']}")
    print(f"root repository: {report['root_repository']}")
    print(f"containing repository: {report['containing_repository'] or '(none)'}")
    root_action = "would create root" if "would_create_root" in report else "root created"
    root_key = "would_create_root" if "would_create_root" in report else "root_created"
    print(f"{root_action}: {report[root_key]}")
    for key in (
        "present_categories",
        "missing_categories",
        "category_collisions",
        "other_directories",
        "top_level_files",
        "top_level_symlinks",
        "nested_repositories",
        "warnings",
    ):
        values = report[key]
        assert isinstance(values, list)
        rendered = ", ".join(
            json.dumps(value, sort_keys=True) if isinstance(value, dict) else str(value)
            for value in values
        )
        print(f"{key.replace('_', ' ')}: {rendered or '(none)'}")
    action_key = "would_create" if "would_create" in report else "created"
    values = report[action_key]
    assert isinstance(values, list)
    print(f"{action_key.replace('_', ' ')}: {', '.join(map(str, values)) if values else '(none)'}")


def main() -> int:
    args = parse_args()
    if args.dry_run and not args.init:
        raise WorkspaceError("--dry-run requires --init")
    categories = validate_categories(args.categories)
    root = validate_root(args.path, args.init)
    report = inventory(root, categories, args.init, args.dry_run)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, WorkspaceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
