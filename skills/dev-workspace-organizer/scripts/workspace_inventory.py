#!/usr/bin/env python3
"""Inventory or non-destructively initialize a multi-project workspace."""

from __future__ import annotations

import argparse
import json
import os
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Workspace grouping root")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=list(DEFAULT_CATEGORIES),
        help="Top-level category names to inspect or create",
    )
    parser.add_argument("--init", action="store_true", help="Create missing category directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what --init would create")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser.parse_args()


def validate_categories(values: list[str]) -> list[str]:
    categories: list[str] = []
    for value in values:
        if not value or value in {".", ".."} or "/" in value or "\\" in value:
            raise SystemExit(f"invalid top-level category: {value!r}")
        if value.startswith("."):
            raise SystemExit(f"refusing hidden category: {value!r}")
        if value not in categories:
            categories.append(value)
    return categories


def validate_root(path: Path, init: bool) -> Path:
    root = path.expanduser().resolve()
    filesystem_root = Path(root.anchor)
    if root == filesystem_root or root == Path.home().resolve():
        raise SystemExit(f"refusing broad workspace root: {root}")
    if root.exists() and not root.is_dir():
        raise SystemExit(f"workspace root is not a directory: {root}")
    if not root.exists() and not init:
        raise SystemExit(f"workspace root does not exist: {root}")
    if not root.exists() and not root.parent.is_dir():
        raise SystemExit(f"workspace parent does not exist: {root.parent}")
    return root


def find_git_roots(root: Path) -> list[str]:
    if not root.exists():
        return []
    repositories: list[str] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path != root and (".git" in dirs or ".git" in files):
            repositories.append(str(current_path.relative_to(root)))
            dirs[:] = []
            continue
        dirs[:] = [
            name
            for name in dirs
            if name not in PRUNE_NAMES and not (current_path / name).is_symlink()
        ]
    return sorted(repositories)


def inventory(root: Path, categories: list[str], init: bool, dry_run: bool) -> dict[str, object]:
    existing = root.exists()
    children = sorted(root.iterdir(), key=lambda item: item.name.lower()) if existing else []
    child_names = {child.name for child in children}
    missing = [name for name in categories if name not in child_names]
    created: list[str] = []

    if init and not dry_run:
        if not root.exists():
            root.mkdir()
        for name in missing:
            (root / name).mkdir()
            created.append(name)
    elif init:
        created = list(missing)

    category_set = set(categories)
    other_directories = [
        child.name for child in children if child.is_dir() and child.name not in category_set
    ]
    top_level_files = [child.name for child in children if child.is_file()]
    symlinks = [
        {"path": child.name, "target": os.readlink(child)} for child in children if child.is_symlink()
    ]
    root_git = existing and (root / ".git").exists()
    warnings: list[str] = []
    if root_git:
        warnings.append("workspace grouping root contains .git")
    if symlinks:
        warnings.append("resolve top-level symlinks before moving their parents")

    return {
        "root": str(root),
        "root_exists": root.exists(),
        "root_git": root_git,
        "categories": categories,
        "present_categories": [name for name in categories if (root / name).is_dir()],
        "missing_categories": [name for name in categories if not (root / name).is_dir()],
        "other_directories": other_directories,
        "top_level_files": top_level_files,
        "top_level_symlinks": symlinks,
        "nested_repositories": find_git_roots(root),
        "would_create" if dry_run else "created": created,
        "warnings": warnings,
    }


def print_human(report: dict[str, object]) -> None:
    print(f"workspace: {report['root']}")
    print(f"grouping root has Git: {report['root_git']}")
    for key in (
        "present_categories",
        "missing_categories",
        "other_directories",
        "top_level_files",
        "nested_repositories",
        "warnings",
    ):
        values = report[key]
        assert isinstance(values, list)
        print(f"{key.replace('_', ' ')}: {', '.join(map(str, values)) if values else '(none)'}")
    action_key = "would_create" if "would_create" in report else "created"
    values = report[action_key]
    assert isinstance(values, list)
    print(f"{action_key.replace('_', ' ')}: {', '.join(map(str, values)) if values else '(none)'}")


def main() -> int:
    args = parse_args()
    if args.dry_run and not args.init:
        raise SystemExit("--dry-run requires --init")
    categories = validate_categories(args.categories)
    root = validate_root(args.path, args.init)
    report = inventory(root, categories, args.init, args.dry_run)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
